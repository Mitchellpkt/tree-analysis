import pytest
import json
from ringxor import ringxor
from itertools import product
import os

print(f"{os.getcwd()=}")
# Load the test data
with open("demo_rings.json", "r") as f:
    all_rings_raw = json.load(f)

# The code uses sets, but they can't be serialized to json, so we convert back here from temporary list representation
all_rings: ringxor.ring_bucket = {key_image: set(ring) for key_image, ring in all_rings_raw.items()}


def test_ringxor_process_bucket_single_thread():
    # Run the ringxor algorithm
    results = sorted(ringxor.process_bucket_single_thread(all_rings, index_pairs=None))

    assert len(results) == 54
    assert results[0] == (
        "056189f0c3ed7806bc17655152613b3288dfa496b6566b9bbef930efaa87975f",
        "416e9438f9f69410cf42959dc8ee515318ea6710e5bf8eb76f69c6183a09bded",
    )
    assert results[53] == (
        "fdfcbe3f85e480905d5db681bf89e5b81dc514871f0735c8a8cc7dffb6d7cde8",
        "6d1fe6224bfccbb5f660d08bdb23fba89e75cf7d367b16bc40bcb3d337e12b0e",
    )