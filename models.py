from pydantic import BaseModel
from enum import Enum, auto
from typing import List, Dict, Any, Callable


############################
# Transaction model and
# its components
############################

class Output(BaseModel):
    """ An output is referenced by its index """
    output_index: int  # In order of appearance on the blockchain


class Ring(BaseModel):
    """ A ring consumes outputs and creates a key image """
    outputs_consumed: List[Output]
    key_image: str

    def ring_size(self) -> int:
        """ Helper function that returns the ring size"""
        return len(self.outputs_consumed)

    def output_indices(self) -> List[int]:
        """ Helper function that returns the indices of the outputs """
        return [output.output_index for output in self.outputs_consumed]

    # Analysis helper: detect cached ring members anomaly by comparing ring members against list of such known outputs
    def check_ring_for_cached_output_use(self, cached_output_indices: List[int]) -> bool:
        """ True if N-1 of the inputs are from the list known to be used in cache-defective transactions """
        matches: List[int] = [i for i in self.output_indices() if i in cached_output_indices]
        return matches == self.ring_size() - 1

    # Analysis helper: [ONLY for rings with cached ring anomaly] return output index NOT on list of such outputs
    def real_spend(self, cached_output_indices: List[int]) -> int:
        """ For transactions that used cached rings, get the real ring member """
        if not self.check_ring_for_cached_output_use(cached_output_indices):
            raise ValueError(f"real_spend_output_index_from_cached_ring() can only be used on cached-output rings")
        return [i for i in self.output_indices() if i not in cached_output_indices][0]


class Transaction(BaseModel):
    """ A transaction has inputs and outputs """
    inputs: List[Ring]
    outputs: List[Output]


############################
# Misc for analysis
# (label management)
############################

class ConfusionMatrixLabel(Enum):
    TRUE_POSITIVE = auto()
    TRUE_NEGATIVE = auto()
    FALSE_POSITIVE = auto()
    FALSE_NEGATIVE = auto()
    UNKNOWN_LABEL = auto()


class Labels(BaseModel):
    cached_output_indices: List[int]  # Get this from Neptune's recent output use count results
    known_spends: Dict[int, str] = None  # key: output index, value: key image of the ring that consumed it


############################
# Main workspace for
# transaction tree analysis
############################

class TransactionTreeAnalysis(BaseModel):
    """ This is the main class for storing the transaction tree and the labels we apply to various nodes and edges """
    transactions: List[Transaction]
    labels: Labels

    ############################
    # Build known spends records
    # by analyzing transactions
    ############################

    def ingest_transaction_and_update_self(self, transaction: Transaction) -> None:
        """ Processes and records a transaction """
        if transaction not in self.transactions:
            # Add the transaction to our list if not already known
            self.transactions.append(transaction)
        for ring in transaction.inputs:
            if ring.check_ring_for_cached_output_use(self.labels.cached_output_indices):
                # When a cached ring is encountered, ensure that we made a note of the true spend
                self.labels.known_spends[ring.real_spend(self.labels.cached_output_indices)] = ring.key_image

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Ingest all the transactions when initialized
        for transaction in self.transactions:
            self.ingest_transaction_and_update_self(transaction)

    ############################
    # Model validation helpers
    # (use on organic rings too)
    ############################

    def validate_model_with_a_ring(self, model: Callable[[Ring], Output], ring: Ring) -> List[ConfusionMatrixLabel]:
        """
        Validates model prediction a ring - returns a vector of confusion matrix labels (one for each ring member!)
        :param model: model whose input is a ring and whose output is a prediction of the true spend in that ring
        :param ring: ring to be used for validation
        :return: list of confusion matrix labels, one per ring member

        (Note: confusion matrix code is written for illustration not efficiency; refactor to better complexity for prod)
        """
        label_vector: List[ConfusionMatrixLabel] = []
        model_prediction: Output = model(ring)

        for ring_member in ring.outputs_consumed:

            # If we do not know the spend state of that output, then we can't use it to score the model
            if ring_member.output_index not in self.labels.known_spends:
                label_vector.append(ConfusionMatrixLabel.UNKNOWN_LABEL)

            else:
                # Is this the ring where whe output was really spent?
                is_this_real_spend_truth: bool = ring.key_image == self.labels.known_spends[ring_member.output_index]

                # Did the model think this is the ring where the output was really spent?
                is_this_real_spend_model: bool = ring.key_image == model_prediction

                # Compare model to ground truth
                if is_this_real_spend_model and is_this_real_spend_truth:
                    label_vector.append(ConfusionMatrixLabel.TRUE_POSITIVE)
                elif is_this_real_spend_model and (not is_this_real_spend_truth):
                    label_vector.append(ConfusionMatrixLabel.FALSE_POSITIVE)
                elif (not is_this_real_spend_model) and is_this_real_spend_truth:
                    label_vector.append(ConfusionMatrixLabel.FALSE_NEGATIVE)
                elif (not is_this_real_spend_model) and (not is_this_real_spend_truth):
                    label_vector.append(ConfusionMatrixLabel.TRUE_NEGATIVE)

        return label_vector

    def validate_model_over_all_rings(self, model: Callable[[Ring], Output]) -> Dict[ConfusionMatrixLabel, int]:
        """
        Validate a model over all rings
        :param model: Any model that predicts which output in a ring is most likely to be the real spend
        :return: Dictionary with confusion matrix, looks like:
            {
                TRUE_POSITIVE: 55
                TRUE_NEGATIVE: 37
                FALSE_POSITIVE: 15500
                FALSE_NEGATIVE: 583
                UNKNOWN: 239956
            }
        """
        all_rings: List[Ring] = []
        for transaction in self.transactions:
            all_rings += transaction.inputs

        all_labels: List[ConfusionMatrixLabel] = []
        for ring in all_rings:
            all_labels += self.validate_model_with_a_ring(model, ring)

        return {label: all_labels.count(label) for label in set(all_labels)}


def foo_model(ring: Ring) -> Output:
    """ Some model with this general shape:
        :param ring: ring to analyze
        :return: output index for the ring member with the highest probability of being the true spend

        It does NOT matter what this model is or what heuristics it is using. It could be using any combination of:
        - Guess newest heuristic
        - Defect chain analysis (unusual fees, tx_extra, unlock time, etc)
        - Data from a flood attack
        - Timing heuristics
        - [Redacted]
        - Topological analysis
        - Data from merchants and markets
        - Data from devices
        - etc

        Personally I would approach this in a multi-step manner:
            > 1) Begin by inferring the ring decoy selection algorithm type:
                - cached rings?
                - juvenile spend?
                - uniform distribution?
                - plausibly reference algorithm?
            > 2) Run the transaction metadata (not included here) through a series of fungibility defect classifiers
            > 3) Apply a model based on the ring distribution type, taking into account priors and fungibility defects

        To avoid distracting from the matter at hand, we'll use a foo model. This simply returns
        the output corresponding to whichever ring member is in the position of 42 mod ring size
    """
    return ring.outputs_consumed[42 % ring.ring_size()]
