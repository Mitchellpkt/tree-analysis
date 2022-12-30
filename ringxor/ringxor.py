from typing import Type, TypeVar, Dict, Set, List, Tuple, Union, Any, Collection
import itertools

key_image_pointer: Type = Union[int, str, Any]
output_pointer: Type = Union[int, str, Any]
ring_vector: Type = Set[output_pointer]
ring_bucket: Type = Dict[key_image_pointer, ring_vector]
edge: Type = Tuple[key_image_pointer, output_pointer]


def process_bucket_single_thread(
    rings: ring_bucket, index_pairs: Collection[Tuple[int, int]] = None,
) -> List[Tuple[key_image_pointer, output_pointer]]:

    # If no index pairs are provided, use all possible combinations
    if index_pairs is None:
        index_pairs = itertools.product(list(rings.keys()), list(rings.keys()))

    # Avoid redundant checks by only crunching the upper triangle of the index pair matrix
    key_image_pointer_pairs: Set[Tuple[key_image_pointer, key_image_pointer]] = {
        tuple(sorted(ip)) for ip in index_pairs
    }

    # Process the bucket
    edges: List[Tuple[key_image_pointer, output_pointer]] = []
    for key_image_pointer_left, key_image_pointer_right in key_image_pointer_pairs:
        ring_left: ring_vector = rings[key_image_pointer_left]
        ring_right: ring_vector = rings[key_image_pointer_right]
        # Do we have a singleton?
        if len(ring_left & ring_right) == len(ring_left) - 1:
            edges.append((key_image_pointer_left, (ring_left - ring_right).pop()))
            edges.append((key_image_pointer_right, (ring_right - ring_left).pop()))

    return edges
