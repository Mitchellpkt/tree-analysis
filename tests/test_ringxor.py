import json
from multiprocessing import cpu_count
from ringxor import ringxor
import pathlib

# Load the test data
data_path: pathlib.Path = pathlib.Path.cwd() / ".." / "data" / "demo_rings.json"
with open(data_path, "r") as f:
    all_rings_raw = json.load(f)

# The code uses sets, but they can't be serialized to json, so we convert back here from temporary list representation
all_rings: ringxor.ring_bucket = {key_image: set(ring) for key_image, ring in all_rings_raw.items()}


def test_ringxor_process_bucket_single_thread_core():
    results = sorted(ringxor.process_bucket_single_thread_core(all_rings, index_pairs=None))

    assert len(results) == 54
    assert results[0] == (
        "056189f0c3ed7806bc17655152613b3288dfa496b6566b9bbef930efaa87975f",
        "416e9438f9f69410cf42959dc8ee515318ea6710e5bf8eb76f69c6183a09bded",
    )
    assert results[53] == (
        "fdfcbe3f85e480905d5db681bf89e5b81dc514871f0735c8a8cc7dffb6d7cde8",
        "6d1fe6224bfccbb5f660d08bdb23fba89e75cf7d367b16bc40bcb3d337e12b0e",
    )


def test_ringxor_process_bucket_1_worker():
    results = sorted(ringxor.process_bucket(all_rings, index_pairs=None, num_workers=1))

    assert len(results) == 54
    assert results[0] == (
        "056189f0c3ed7806bc17655152613b3288dfa496b6566b9bbef930efaa87975f",
        "416e9438f9f69410cf42959dc8ee515318ea6710e5bf8eb76f69c6183a09bded",
    )
    assert results[53] == (
        "fdfcbe3f85e480905d5db681bf89e5b81dc514871f0735c8a8cc7dffb6d7cde8",
        "6d1fe6224bfccbb5f660d08bdb23fba89e75cf7d367b16bc40bcb3d337e12b0e",
    )


def test_ringxor_process_bucket_N_worker():
    if cpu_count() == 1:
        print("Skipping test_ringxor_process_bucket_N_worker because only 1 CPU is available")
    else:
        results = sorted(ringxor.process_bucket(all_rings, index_pairs=None, num_workers=2))

        assert len(results) == 54
        assert results[0] == (
            "056189f0c3ed7806bc17655152613b3288dfa496b6566b9bbef930efaa87975f",
            "416e9438f9f69410cf42959dc8ee515318ea6710e5bf8eb76f69c6183a09bded",
        )
        assert results[53] == (
            "fdfcbe3f85e480905d5db681bf89e5b81dc514871f0735c8a8cc7dffb6d7cde8",
            "6d1fe6224bfccbb5f660d08bdb23fba89e75cf7d367b16bc40bcb3d337e12b0e",
        )
