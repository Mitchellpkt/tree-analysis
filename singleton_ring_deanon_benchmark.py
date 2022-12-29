# Don't take this file too seriously, it's a very rough approximation with sloppy assumptions
# Stripped down for compatibility with python 3.11
# Expect extra overhead for a full implementation and intra-transaction rings

from load_transactions import get_processed_transaction
from typing import Dict, List, Tuple, Set
from multiprocessing import Pool
from time import perf_counter

n_samples: int = 5573404
n_workers: int = 64

# Pick two transactions
tx_hash_left: str = "48ab24a942778d0c7d79d8bbc7076329ae45b9b7c8cc7c15d105e135b4746587"
tx_hash_right: str = "71879ba6099ea18d456cd31694b0860f3649ebeb28ce5630ccb1be312c0cc8cb"
tx_rings_left: Dict[str, Set[str]] = get_processed_transaction(tx_hash_left)
tx_rings_right: Dict[str, Set[str]] = get_processed_transaction(tx_hash_right)


def wrapper(rings_left, rings_right):
    results = []
    for key_image_left, ring_left in rings_left.items():
        for key_image_right, ring_right in rings_right.items():
            # Do we have a singleton?
            if len(ring_left & ring_right) == len(ring_left) - 1:
                results.append((key_image_left, (ring_left - ring_right).pop()))
                results.append((key_image_right, (ring_right - ring_left).pop()))
    return results


all_rings_left: List[Dict[str, Set[str]]] = [tx_rings_left] * n_samples
all_rings_right: List[Dict[str, Set[str]]] = [tx_rings_right] * n_samples
iterator: List[Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]] = list(zip(all_rings_left, all_rings_right))

tic: float = perf_counter()
with Pool(n_workers) as p:
    results = p.starmap(wrapper, iterator)
toc: float = perf_counter()
time_sec: float = toc - tic

print(f"Example results:\n{[subitem for item in results for subitem in item][:5]}")

num_rings: int = (len(tx_rings_left) * len(tx_rings_right)) * n_samples
print(f"Processed {num_rings} ring pairs in {time_sec:.2f} seconds on {n_workers} cores")
