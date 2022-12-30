from typing import Type, TypeVar, Dict, Set, List, Tuple, Union, Any, Collection
import itertools
from multiprocessing import Pool, cpu_count
import numpy as np

# This aliasing is temporary, until the schema is finalized
key_image_pointer: Type = Union[int, str, Any]
output_pointer: Type = Union[int, str, Any]
ring_vector: Type = Set[output_pointer]
ring_bucket: Type = Dict[key_image_pointer, ring_vector]
edge: Type = Tuple[key_image_pointer, output_pointer]


def process_bucket_single_thread_core(
    rings: ring_bucket,
    index_pairs: Union[List[Tuple[int, int]], None],
) -> List[Tuple[key_image_pointer, output_pointer]]:
    """
    Core function - you do not need to interact with this directly, use `process_bucket()` below
    This takes a batch of index pairs and processes the rings in a single thread.

    :param rings: bucket of rings to analyze
    :param index_pairs: list of index pairs to process. If None provided, checks all possible combinations
    :return: identified transaction tree edges in the form of (key_image, output)
    """
    # If no index pairs are provided (could be None, (), {}, [], etc...), use all possible combinations
    if not index_pairs:
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


def process_bucket(
    rings: ring_bucket,
    index_pairs: Union[None, Collection[Tuple[int, int]]] = None,
    num_workers: Union[int, None] = None,
) -> List[Tuple[key_image_pointer, output_pointer]]:
    """
    This function takes a bucket of rings and processes them to identify transaction tree edges from singletons
    that arise from XORing ring pairs (i.e. symmetric set difference)

    :param rings: bucket of rings to analyze
    :param index_pairs: list of index pairs to process. If None provided, checks all possible combinations
    :param num_workers: number of workers to use. If None provided, uses all available cores
    :return: identified transaction tree edges in the form of (key_image, output)
    """
    # If no index pairs are provided, use all possible combinations
    if index_pairs is None:
        index_pairs = itertools.product(list(rings.keys()), list(rings.keys()))

    # Avoid redundant checks by only crunching the upper triangle of the index pair matrix
    key_image_pointer_pairs: List[Tuple[key_image_pointer, key_image_pointer]] = list(
        {tuple(sorted(ip)) for ip in index_pairs}
    )

    # Use all available cores unless specified otherwise
    if num_workers is None:
        num_workers: int = cpu_count()

    if num_workers <= 1:
        # If we only have one worker, just run the single-threaded version
        return process_bucket_single_thread_core(rings, index_pairs=key_image_pointer_pairs)
    else:
        # Split the work into chunks
        batches = [list(key_image_pointer_pairs)[i::num_workers] for i in range(num_workers)]
        iterable = [(rings, batch) for batch in batches]

        # Process the chunks in parallel
        with Pool(processes=num_workers) as pool:
            results: List[List[Tuple[key_image_pointer, output_pointer]]] = pool.starmap(
                process_bucket_single_thread_core,
                iterable,
            )
        # Combine the results
        edges: List[Tuple[key_image_pointer, output_pointer]] = []
        for result in results:
            edges.extend(result)
        return edges
