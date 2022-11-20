# Indexing and selecting data

The axis labeling information in pandas objects serves many purposes:

* identifies data (i.e. provides _metadata_) using known indicators
* enables automatic and explicit data alignment
* allows intuitive getting and setting of subsets of the data set

Note: The Python and NumPy indexing operators `[]` and attribute operator `.` provide quick and easy access to pandas data structures across a wide range of use cases. This makes interactive work intuitive, as there's little new to learn if you already know how to deal with Python dictionaries and NumPy arrays. However, since the type of the data to be accessed isn't known in advance, directly using standard operators has some optimization limits. 

Warning: whether a copy or a reference is returned for a setting operation, may depend on the context. This is sometimes called _chained assignment_ and should be avoided.
A bit of perspective on the _chained assignment_ is provided in the section _Returning a view versus a copy_ below:

## Notes on chained indexing

### Returning a view versus a copy

When setting values in a pandas object, care must be taken to avoid what is called _chained indexing_. Here is an example:

```python
In ...: dfmi = pd.DataFrame([list('abcd'),
                             list('efgh'),
                             list('ijkl'),
                             list('mnop')],
                            columns=pd.MultiIndex.from_product([['one', 'two'], 
                                                                ['first', 'second']]))

In ...: dfmi

Out ...:

       one            two
  first second   first  second
0    a      b      c      d
1    e      f      g      h
2    i      j      k      l
3    m      n      o      p

```

Compare these two access methods:

```python
In ...: dfmi['one']['second']
Out ...:
0    b
1    f
2    j
3    n
Name: second, dtype: object
```
and
```python
In ...: dfmi.loc[:, ('one', 'second')]
Out ...:
0    b
1    f
2    j
3    n
Name: (one, second), dtype: object
```
These both yield the same results, so which should you use? It is instructive to understand the order of operations on these and why method 2 (`.loc`) is much preferred over method 1 (chained `[]`).

`dfmi['one']` selects the first level of the columns and returns a DataFrame that is singly-indexed. Then another Python operation `dfmi_with_one['second']` selects the series indexed by `second'`. This is indicated by the variable `dfmi_with_one` becuase pandas sees these operations as separate events. e.g. separate calls to `__getitem__`, so it has to treat them as linear operations, they happen one after another. 

Contrast this to `df.loc[:,('one','second')]` which passes a nested tuple of `(slice(None),('one','second'))` to a single call to `__getitem__`. This allows pandas to deal with this as a single entity. Furthermore, this order of operations can be significantly faster, and allows one to index _both_ axes if so desired.

### Why does assignment fail when using chained indexing?

The problem in the previous section is just a performance issue. What's up with the `SettingWithCopy` warning? We don't **usually** throw warnings aorund when you do something that might cost a few extra milliseconds!

It turns out that assigning to the product of chained indexing has inherently unpredicatble results. To see this, think about how the Python interpreter executes this code:

```python
dfmi.loc[:, ('one', 'second')] = value
# becomes
dfmi.loc.__setitem__((slice(None), ('one', 'second')), value)
```
But this code is handled differently:
```python
dfmi['one']['second'] = value
# becomes
dfmi.__getitem__('one').__setitem__('second', value)
```

The problem is with `__getitem__`. Outside of simple cases, it is very hard to predict whether it will return a view or a copy (it depends on the memory layout of the array, about which pandas makes no guarantees), and therefore whether the `__setitem__` will modify `dfmi` or a temporary object that gets thrown out immeditely afterward. That's what `SettingWithCopy` is warning about.
For comparison, `dfmi.loc` is guaranteed to be `dfmi` itself with modified indexing behavior, so `dfmi.loc.__getitem__` / `dfmi.loc.__setitem__` operate on `dfmi` directly. Of course, `dfmi.loc.__getitem__(idx)` may be a view or a copy of `dfmi`.

Sometimes a `SettingWithCopy` warning will arise at times when there's no obvious chained indexing going on. **These** are the bugs that `SettingWithCopy` is designed to catch. pandas is probably trying to warn you that you've done this:

```python
def do_something(df):
    foo = df[['bar', 'baz']]  # is foo a view or a copy? nobody knows
    # ... many lines here ...
    # we don't know whether this will modify df or not
    foo['quux'] = value
    return foo
```

### Evaluation order matters

When you use chained indexing, the order and type of the indexing operation partially determine whether the result is a slice into the original object, or a copy of the slice.

pandas has the `SettingWithCopyWarnin` because assignin to a copy of a slice is frequently not intentional, but a mistake caused by chained indexing returning a copy where a slice was expected.

If you would like pandas to be more or less trusting about assignent to a chained indexing expression, you can set the option `mode.chained_assignment` to one of these values:

* `'warn'`, the default, means a `SettingWithCopyWarning` is printed
* `'raise'` means pandas will raise a `SettingWithCopyError` you have to deal with
* `None` will supress the warnings entirely

```python
In ...: dfb = pd.DataFrame({'a': ['one', 'one', 'two'
                                  'three', 'two', 'one', 'six'],
                            'c': np.arange(7)})
# This will show the SettingWithCopyWarning
# but the frame values will be set
In ...: dfb['c'][dfb['a'].str.startswith('o')] = 42
```
This however is operating on a copy and will not work.

```python
>>> pd.set_option('mode.chained_assignment', 'warn')
>>> dfb[dfb['a'].str.startswith('o')]['c'] = 42
```

A chained assignment can also crop up in setting in a mixed dtype frame.
The following is the recommended access method using `.loc` for multiple items (using `mask`) and a single item using a fixed index:

```python
In ...: dfc = pd.DataFrame({'a': ['one', 'one', 'two', 'three', 'two', 'one', 'six'],
                            'c': np.arange(7)})
In ...: dfd = dfc.copy()

# Setting multipe items using a mask
In ...: mask = dfd['a'].str.startswith('o')
In ...: dfd.loc[mask, 'c'] = 42

Out ...:
    a     c
0   one  42
1   one  42
2   two   2
3  three  3
4   two   4
5   one  42
6   six   6

# Setting a single item
In ...: dfd = dfc.copy()

In ...: dfd.loc[2, 'a'] = 11

In ...: dfd
Out ...:

     a   c
0   one  0
1   one  1
2   11   2
3  three 3
4   two  4
5   one  5
6   six  6
```
The following can work at times, but it is not guaranteed to, and therefore should be avoided:
```python
In ...: dfd = dfc.copy()
In ...: dfd['a'][2] = 111

     a   c
 0   one  0
 1   one  1
 2   11   2
 3  three 3
 4   two  4
 5   one  5
 6   six  6
```
Last, the subsequent example will **not** work at all, and should be avoided:
```python
>>> pd.set_option('mode.chained_assignment','raise')
>>> dfd.loc[0]['a'] = 111
```

## Different choices for indexing

Object selection has had a number of user-requested additions in order to support more explicit location based indexing. pandas now supports three types of multi-axis indexing.

* `.loc` is primarily label based, but may also be used with a boolean array. `.loc` will raise `KeyError` when the items are not found. Allowed inputs are:
  > * a single label, e.g. `5` or `'a'` (Note that `5` is interpreted as a _label_ of the index. This use is **not** an integer position along the index)
  > * a list of array of labels `['a', 'b', 'c']`
  > * a slice object with labels `'a':'f'` (Note that contrary to usual Python slices, **both** the start and the stop are included, when present in the index.)
  > * a boolean array (any `NA` values will be treated as `False`)
  > * a `callable` function with one argument (the calling Series or DataFrame) and that returns valid output for indexing (one of the above).

* `.iloc` is primarily integer position based (from `0` to `length-1` of the axis), but may also be used with a boolean array. `.iloc` will raise `IndexError` if a requested indexer is out-of-bounds, except _slice_ indexers which allow out-of-bounds indexing. Allowed inputs are:
  > * an integer e.g. `5`
  > * a list or array of integers `[4, 3, 0]`
  > * a slice object with `int`'s `1:7`
  > * a boolean array (any `NA` values will be treated as `False`)
  > * a `callable` function with one argument (the calling Series or DataFrame) and that returns valid output for indexing 

* `.loc`, `.iloc`, and also `[]` indexing can accept a `callable` as indexer. 

Getting values from an object with multi-axes selection uses the following notation (using `.loc` as an example, but the following applies to `.iloc` as well). Any of the axes accessors may be the null slice `:`. Axes left out of the specification are assumed to be `:`, e.g. `p.loc['a']` is equivalent to `p.loc['a', :]`.

|Object Type |  Indexers                             |
|------------|---------------------------------------|
| Series     | `s.loc[indexer]`                      | 
|            |                                       |
| DataFrame  | `df.loc[row_indexer, column_indexer]` |

## Basics

The primary function of indexing with `[]` (aka `__getitem__`) is selecting out lower-dimensional slices. The following table shows return type values when indexing pandas objects with `[]`:

|Object Type    | Selection       |  Return Value Type                |
|---------------|-----------------|-----------------------------------|
| Series        |`series[label]`  | scalar value                      |
| DataFrame     |`frame[colname]` | `Series` corresponding to colname |

Here we construct a simple time series data set to use for illustrating the indexing functionality:

```python
In ...: dates = pd.date_range('1/1/2000', periods=8)

In ...: df = pd.DataFrame(np.random.randn(8, 4),
                          index=dates, columns=['A', 'B', 'C', 'D'])
```
Using the above code we show the most basic indexing using `[]`:

```python
In ...: s = df['A']
In ...: s[dates[5]]
```

You can pass a list of columns to `[]` to select columns in that order. If a column is not contained in the DataFrame, an exception will be raised. Multiple columns can also be set in this manner:

```python
In ...: df[['B', 'A']] = df[['A', 'B']]
```
You may find this usefu for applying a transform (in-place) to a subset of the columns

**Warning**: pandas aligns all AXES when setting `Series` and `DataFrame` from `.loc` and `.iloc`.
This will **not** modify `df` because the column alignment is before value assignment.

```python
df.loc[:, ['B', 'A']] = df[['A', 'B']]
```

The correct way to swap column values is by using raw values:

```python
df.lox[:, ['B', 'A']] = df[['A', 'B']].to_numpy()
```

## Attribute access

You may access an index on a `Series` or column on a `DataFrame` directly as an attribute.

```python
In ...: sa = pd.Series([1, 2, 3], index=list('abc'))

In ...: dfa = df.copy()

In ...: sa.b
Out ...: 2

In ...: dfa.A
Out ...: 
2000-01-01    0.469112
2000-01-02    1.212112
2000-01-03   -0.861849
...
Freq: D, Name: A, dtype: float64
```
```python
In ...: sa.a = 5
In ...: sa
Out ...:
a    5
b    2
c    3
dtype: int64

In ...: dfa.A = list(range(len(dfa.index))) # ok if A already exists

In ...: dfa
Out ...:

            A         B         C         D
2000-01-01  0 -0.282863 -1.509059 -1.135632
2000-01-02  1 -0.173215  0.119209 -1.044236
2000-01-03  2 -2.104569 -0.494929  1.071804
2000-01-04  3 -0.706771 -1.039575  0.271860

In ...: dfa['A'] = list(range(len(dfa.index))) # use this form to create a new column

In ...: dfa
Out ...:

            A         B         C         D
2000-01-01  0 -0.282863 -1.509059 -1.135632
2000-01-02  1 -0.173215  0.119209 -1.044236
2000-01-03  2 -2.104569 -0.494929  1.071804
2000-01-04  3 -0.706771 -1.039575  0.271860
```

**Warning**:




