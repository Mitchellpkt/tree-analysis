# This a very rough estimate, probably good within an order or two of magnitude?
# Expect extra overhead for a full implementation and intra-transaction rings

from load_transactions import get_processed_transaction
from typing import Dict, List
from isthmuslib import process_queue, Tuple
from time import perf_counter

n_samples: int = 10_000
n_workers: int = 64

# Pick two transactions
tx_hash_left: str = "48ab24a942778d0c7d79d8bbc7076329ae45b9b7c8cc7c15d105e135b4746587"
tx_hash_right: str = "71879ba6099ea18d456cd31694b0860f3649ebeb28ce5630ccb1be312c0cc8cb"
tx_rings_left: Dict[str, List[str]] = get_processed_transaction(tx_hash_left)
tx_rings_right: Dict[str, List[str]] = get_processed_transaction(tx_hash_right)


def wrapper(
    rings_left: Dict[str, List[str]], rings_right: Dict[str, List[str]]
) -> List[Tuple[str, str, str]]:
    results: List[Tuple[str, str, str]] = []
    for key_image_left, ring_left in rings_left.items():
        for key_image_right, ring_right in rings_right.items():
            # Do we have a singleton?
            if len(set(ring_left) & set(ring_right)) == len(ring_left) - 1:
                left_singleton: str = list(set(ring_left) - set(ring_right))[0]
                right_singleton: str = list(set(ring_right) - set(ring_left))[0]
                results.append((tx_hash_left, key_image_left, left_singleton))
                results.append((tx_hash_right, key_image_right, right_singleton))
    return results


all_rings_left: List[Dict[str, List[str]]] = [tx_rings_left] * n_samples
all_rings_right: List[Dict[str, List[str]]] = [tx_rings_right] * n_samples
iterator: List[Tuple[Dict[str, List[str]], Dict[str, List[str]]]] = list(zip(all_rings_left, all_rings_right))

tic: float = perf_counter()
process_queue(wrapper, iterator, num_workers=n_workers)
toc: float = perf_counter()
time_sec: float = toc - tic

num_rings: int = (len(tx_rings_left) * len(tx_rings_right)) * n_samples
print(f"Processed {num_rings} ring pairs in {time_sec:.2f} seconds on {n_workers} cores")
