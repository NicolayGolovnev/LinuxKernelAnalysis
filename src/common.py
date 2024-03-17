import itertools


def split_iterator(iterator, n):
    iterators = itertools.tee(iterator, n)
    return [itertools.islice(it, i, None, n) for i, it in enumerate(iterators)]

def split_non_copy_iterator(init_iterator, n):
    return [itertools.islice(init_iterator(), i, None, n) for i in range(n)]