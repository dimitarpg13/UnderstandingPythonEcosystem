import pandas as pd
import numpy as np

arrays = [
        ["bar", "bar", "baz", "baz", "foo", "foo", "qux", "qux"],
        ["one", "two", "one", "two", "one", "two", "one", "two"],
]

tuples = list(zip(*arrays))

print("Tuples: {}".format(tuples))

index = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])

print("Index: {}".format(index))

s = pd.Series(np.random.randn(8), index=index)

print("Series: {}".format(s))

iterables = [["bar", "baz", "foo", "qux"], ["one", "two"]]

print("list of lists Iterables: {}".format(iterables))

mi = pd.MultiIndex.from_product(iterables, names=["first", "second"])

print("MultiIndex from product Iterables: {}".format(mi))
