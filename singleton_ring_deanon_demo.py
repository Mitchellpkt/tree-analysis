from load_transactions import get_processed_transaction
from typing import Dict, List

# Pick two transactions
tx_hash_left: str = "48ab24a942778d0c7d79d8bbc7076329ae45b9b7c8cc7c15d105e135b4746587"
tx_hash_right: str = "71879ba6099ea18d456cd31694b0860f3649ebeb28ce5630ccb1be312c0cc8cb"

tx_rings_left: Dict[str, List[str]] = get_processed_transaction(tx_hash_left)
tx_rings_right: Dict[str, List[str]] = get_processed_transaction(tx_hash_right)

results: List[str] = []
for key_image_left, ring_left in tx_rings_left.items():
    for key_image_right, ring_right in tx_rings_right.items():
        # Do we have a singleton?
        if len(set(ring_left) & set(ring_right)) == len(ring_left) - 1:
            left_singleton: str = list(set(ring_left) - set(ring_right))[0]
            right_singleton: str = list(set(ring_right) - set(ring_left))[0]
            results.append(
                f"Txn: {tx_hash_left}\nKey Image: {key_image_left}\nSpends output: {left_singleton}"
            )
            results.append(
                f"Txn: {tx_hash_right}\nKey Image: {key_image_right}\nSpends output: {right_singleton}"
            )

summary: str = "".join([f"----\n{result}\n\n" for result in results])
print(f"Identified {len(results)} true spends:\n\n{summary}")
