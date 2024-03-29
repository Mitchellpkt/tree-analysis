from transaction_cache_raw import transactions_raw
from typing import Dict, List, Any, Set


def process_raw_transaction_text(s: str) -> Dict[str, Set[str]]:
    """Process the raw text into a dict of dicts."""
    lines: List[str] = s.splitlines()
    return_dictionary: Dict[str, Set[str]] = dict()

    key_image: str = ""
    this_ring: Set[str] = set()

    for line in lines:
        if "key image" in line:
            # Save the last result
            if key_image != "":
                return_dictionary[key_image.strip()] = this_ring

            # Prep for the next ring
            key_image: str = line.split(":")[1].split("\t")[0]
            this_ring: Set[str] = set()

        elif line.startswith("-"):
            this_ring.add(line.split(":")[1].split("\t")[0].strip())

    return return_dictionary


def get_processed_transactions() -> Dict[str, Dict[str, Set[str]]]:
    """Return the processed transactions."""
    transactions_db: Dict[str, Dict[str, Set[str]]] = dict()
    for txn_hash, txn_blob in transactions_raw.items():
        transactions_db[txn_hash] = process_raw_transaction_text(txn_blob)
    return transactions_db


def get_processed_transaction(tx_id: str) -> Dict[str, Set[str]]:
    """Return the processed transactions."""
    return process_raw_transaction_text(transactions_raw[tx_id])
