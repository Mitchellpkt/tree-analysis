from load_transactions import get_processed_transaction
from typing import Dict, List, Set

# Pick two transactions
tx_hash_left: str = "48ab24a942778d0c7d79d8bbc7076329ae45b9b7c8cc7c15d105e135b4746587"
tx_hash_right: str = "71879ba6099ea18d456cd31694b0860f3649ebeb28ce5630ccb1be312c0cc8cb"

rings_left: Dict[str, Set[str]] = get_processed_transaction(tx_hash_left)
rings_right: Dict[str, Set[str]] = get_processed_transaction(tx_hash_right)

results = []
for key_image_left, ring_left in rings_left.items():
    for key_image_right, ring_right in rings_right.items():
        # Do we have a singleton?
        if len(ring_left & ring_right) == len(ring_left) - 1:
            results.append((key_image_left, (ring_left - ring_right).pop()))
            results.append((key_image_right, (ring_right - ring_left).pop()))

summary: str = "".join([f"----\n{result}\n\n" for result in results])
print(f"Identified {len(results)} true spends:\n\n{summary}")
