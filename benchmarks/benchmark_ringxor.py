import itertools
import json
import pathlib
from time import perf_counter
from typing import List, Tuple

from ringxor import ringxor

# Settings
num_ring_pairs: int = 1_000_000
num_workers_list: List[int] = [1, 2, 4, 8, 16, 32, 64]

# Load the test data
data_path: pathlib.Path = pathlib.Path.cwd() / ".." / "data" / "demo_rings.json"
with open(data_path, "r") as f:
    all_rings_raw = json.load(f)
print(f"Loaded data from {data_path}")

timing_results: List[Tuple[int, float]] = []
for num_workers in num_workers_list:
    # The code uses sets, but they can't be serialized to json, so we convert back here from temporary list representation
    all_rings_original: ringxor.ring_bucket = {
        key_image: set(ring) for key_image, ring in all_rings_raw.items()
    }

    # Mock up into more rings by adding an index to the key image
    all_rings: ringxor.ring_bucket = dict()
    i: int = 0
    while len(all_rings) ** 2 / 2 < num_ring_pairs:
        all_rings.update({f"{k}_{i}": v for k, v in all_rings_original.items()})
        i += 1
    print(f"{len(all_rings)} rings generated")

    index_tuples_all: List[Tuple[ringxor.key_image_pointer, ringxor.key_image_pointer]] = list(
        itertools.combinations(all_rings.keys(), 2)
    )
    print(f"{len(index_tuples_all)} index tuples generated")

    index_tuples = index_tuples_all[:num_ring_pairs]
    print(f"{len(index_tuples)} index tuples to be used")

    tic: float = perf_counter()
    results = sorted(ringxor.process_bucket(all_rings, index_pairs=index_tuples, num_workers=num_workers))
    toc: float = perf_counter()
    wall_time_sec = toc - tic

    print(f"Processed {len(index_tuples)} ring pairs in {wall_time_sec:.2f} seconds on {num_workers} cores")
    iter_per_sec: float = len(index_tuples) / wall_time_sec
    print(f"({iter_per_sec:.2f} ring par checks per second)\n")
    timing_results.append((num_workers, iter_per_sec))

print("\n")
for num, rate in sorted(timing_results):
    print(f"{num} cores: {rate:.2f} ring pair checks per second")
