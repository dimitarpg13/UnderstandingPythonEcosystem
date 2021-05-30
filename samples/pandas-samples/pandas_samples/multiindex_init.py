import pandas as pd
import numpy as np

arrays = [
        ["bar", "bar", "baz", "baz", "foo", "foo", "qux", "qux"],
        ["one", "two", "one", "two", "one", "two", "one", "two"],
]

tuples = list(zip(*arrays))

print("Tuples:\n{}".format(tuples))

index = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])

print("Index:\n {}".format(index))

s = pd.Series(np.random.randn(8), index=index)

print("Series:]\n{}".format(s))

iterables = [["bar", "baz", "foo", "qux"], ["one", "two"]]

print("list of arrays Iterables: {}".format(iterables))

mi = pd.MultiIndex.from_product(iterables, names=["first", "second"])

print("MultiIndex from product Iterables:\n{}".format(mi))

df = pd.DataFrame(
        [["bar", "one"], ["bar", "two"], ["foo", "one"], ["foo", "two"]],
        columns=["first", "second"])

print("DataFrame from lists:\n{}", df)

mi2 = pd.MultiIndex.from_frame(df)

print("MultiIndex from frame:\n{}".format(mi2))

print("Constructing MultiIndex automatically in a Series from a list of arrays:")

arrays = [
        np.array(["bar", "bar", "baz", "baz", "foo", "foo", "qux", "qux"]),
        np.array(["one", "two", "one", "two", "one", "two", "one", "two"]),
        ]

s = pd.Series(np.random.randn(8), index=arrays)

print("Random series with multi index made from list of arrays:\n{}".format(s))

df2 = pd.DataFrame(np.random.randn(8, 4), index=arrays)

print("Random frame with multi index made from list of arrays:\n{}".format(df2))

df3 = pd.DataFrame(np.random.randn(3, 8), index=["A", "B", "C"], columns=index)

print("DataFrame with random data which uses MultiIndex as column labels:\n{}".format(df3))

df4 = pd.DataFrame(np.random.randn(6, 6), index=index[:6], columns=index[:6])

print("DataFrame with random data which uses MultiIndex as index and as column "
      "labels:\n{}".format(df4)) 


