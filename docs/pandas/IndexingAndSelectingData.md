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
* Attribute access can be used only if the index element is a valid Python idenitifier e.g. `s.1` is not allowed.
* The attribute will not be available if it conflicts with an existing method name e.g. `s.min` is not allowed, but `s['min']` is possible.
* Similarly, the attribute will not be available if it conflicts with any of the following list: `index`, `major_axis`, `minor_axis`, `items`.
* In any of these cases, standard indexing will still work e.g. `s['1']`, `s['min']` and `s['index']` will access the corresponding element or column.

You can also assign a `dict` to a row of a `DataFrame`:
```python
In ...: x = pd.DataFrame({'x': [1, 2, 3], 'y': [3, 4, 5]})

In ...: x.iloc[1] = {'x': 9, 'y': 99}

In ...: x

Out ...:
   x   y
0  1   3
1  9  99
2  3   5
```
Attribute access can be used to modify an existing element of a Series or column of a DataFrame. However if Attribute Access is used to create a new column, it creates a new attribute rather than a new column. In pandas `0.21.0` and later this will raise a `UserWarning`:

```python
In ...: df = pd.DataFrame({'one': [1., 2., 3.]})
In ...: df.two = [4, 5, 6]
UserWarning: Pandas doesn't allow Series to be assigned into nonexistent columns
In ...: df
Out ...:
   one
0  1.0
1  2.0
2  3.0
```

## Slicing ranges

The most robust and consistent way of slicing ranges along arbitrary axes is described in the section [Selection by position](#selection-by-position) detailing the `.iloc` method. Here we discuss the semantics of slicing  using the `[]` operator.

With Series, the syntax works exactly as with an ndarray, returning a slice of the values and the corresponding labels:

```python
In ...: s[:5]
Out ...:
2000-01-01    0.469112
2000-01-02    1.212112
2000-01-03   -0.861849
2000-01-04    0.721555
2000-01-05   -0.424972
Freq: D, Name: A, dtype: float64

In ...: s[::2]
Out ...:
2000-01-01    0.469112
2000-01-03   -0.861849
2000-01-05   -0.424972
2000-01-07    0.404705
Freq: 2D, Name: A, dtype: float64

In ...: s[::-1]
Out ...:
2000-01-08   -0.370647
2000-01-07    0.404705
2000-01-06   -0.673690
2000-01-05   -0.424972
2000-01-04    0.721555
2000-01-03   -0.861849
2000-01-02    1.212112
2000-01-01    0.469112
Freq: -1D, Name: A, dtype: float64
```

Note that setting works as well:

```python
In ...: s2 = s.copy()
In ...: s2[:5] = 0

In ...: s2
Out ...:
2000-01-01    0.000000
2000-01-02    0.000000
2000-01-03    0.000000
2000-01-04    0.000000
2000-01-05    0.000000
2000-01-06   -0.673690
2000-01-07    0.404705
2000-01-08   -0.370647
Freq: D, Name: A, dtype: float64
```

With DataFrame, slicing inside of `[]` *slices the rows*. This is provided largely as a convenience since it is such a common operation.

```python
In ...: df[:3]
Out ...:
                   A         B         C         D
2000-01-01  0.469112 -0.282863 -1.509059 -1.135632
2000-01-02  1.212112 -0.173215  0.119209 -1.044236
2000-01-03 -0.861849 -2.104569 -0.494929  1.071804

In ...: df[::-1]
Out ...:
                   A         B         C         D
2000-01-08 -0.370647 -1.157892 -1.344312  0.844885
2000-01-07  0.404705  0.577046 -1.715002 -1.039268
2000-01-06 -0.673690  0.113648 -1.478427  0.524988
2000-01-05 -0.424972  0.567020  0.276232 -1.087401
2000-01-04  0.721555 -0.706771 -1.039575  0.271860
2000-01-03 -0.861849 -2.104569 -0.494929  1.071804
2000-01-02  1.212112 -0.173215  0.119209 -1.044236
2000-01-01  0.469112 -0.282863 -1.509059 -1.135632
```

## Selection by label

> **Warning:**
> Weather a copy or a reference is returned for a setting operation, may depend on the context. This is the mentioned before `chained assignment` and it should be avoided.

> **Warning:**
> `.loc` is strict when you present slicers that are not compatible (or convertible) with the index type. For example using integers in a `DatetimeIndex`. These will raise a `TypeError`. 
> ```python
> In ...: dfl = pd.DataFrame(np.random.randn(5, 4),
>                            columns=list('ABCD'),
>                            index=pd.date_range('20130101', periods=5))
>
> In ...: dfl
> Out ...:
>
>                    A         B         C         D
> 2013-01-01  1.075770 -0.109050  1.643563 -1.469388
> 2013-01-02  0.357021 -0.674600 -1.776904 -0.968914
> 2013-01-03 -1.294524  0.413738  0.276662 -0.472035
> 2013-01-04 -0.013960 -0.362543 -0.006154 -0.923061
> 2013-01-05  0.895717  0.805244 -1.206412  2.565646
>
> In ...: dfl.loc[2:3]
> TypeError: cannot do slice indexing on <class 'pandas.tseries.index.DatetimeIndex'> with these indexers [2] of <type 'int'>
> ```
> String likes in slicing can be convertible to the type of the index and lead to natural slicing.
> ```python
> In ...: dfl.loc['20130102':'20130104']
> Out ...:
>                    A         B         C         D
> 2013-01-02  0.357021 -0.674600 -1.776904 -0.968914
> 2013-01-03 -1.294524  0.413738  0.276662 -0.472035
> 2013-01-04 -0.013960 -0.362543 -0.006154 -0.923061
> ```

> **Warning**
> _Changed in version 1.0.0_
> pandas will raise `KeyError` if indexing with a list with missing labels. 


## Selection by position

> **Warning**
> Whether a copy or a reference is returned for a setting operation, may depend on the context. This is sometimes called __chained assignment__ and it should be avoided.

pandas provides a suite of methods in order to get **purely integer based indexing**. The semantics follow closely Python and NumPy slicing. These are `0-based` indexing. When slicing, the start bound is __included__, while the upper bound is __excluded__. Trying to use a non-integer, even a **valid** label will raise `IndexError`.

The `.iloc` attribute is the primary access method. The following are valid inputs:

* an integer e.g. `5`
* a list of array of integers `[4, 3, 0]`
* a slice object with ints `1:7`
* a boolean array
* a `callable`

```python
In ...: s1 = pd.Series(np.random.randn(5), index=list(range(0, 10, 2)))

In ...: s1
Out ...:
0    0.695775
2    0.341734
4    0.959726
6   -1.110336
8   -0.619976
dtype: float64

In ...: s1.iloc[:3]
Out ...:
0    0.695775
2    0.341734
4    0.959726
dtype: float64

In ...: s1.iloc[3]
Out ...: -1.110336102891167
```

Note that setting works as well:

```python
In ...: s1.iloc[:3] = 0

In ...: s1
Out ...:
0    0.000000
2    0.000000
4    0.000000
6   -1.110336
8   -0.619976
dtype: float64
```

With a DataFrame:
```python
In ...: df1 = pd.DataFrame(np.random.randn(6, 4),
                           index=list(range(0, 12, 2)),
                           columns=list(range(0, 8, 2)))
In ...: df1
Out ...:
           0         2         4         6
0   0.149748 -0.732339  0.687738  0.176444
2   0.403310 -0.154951  0.301624 -2.179861
4  -1.369849 -0.954208  1.462696 -1.743161
6  -0.826591 -0.345352  1.314232  0.690579
8   0.995761  2.396780  0.014871  3.357427
10 -0.317441 -1.236269  0.896171 -0.487602
```
Selected via integer slicing:
```python
In ...: df1.iloc[:3]
Out...:
          0         2         4         6
0  0.149748 -0.732339  0.687738  0.176444
2  0.403310 -0.154951  0.301624 -2.179861
4 -1.369849 -0.954208  1.462696 -1.743161

In ...: df1.iloc[1:5, 2:4]
Out ...:
          4         6
2  0.301624 -2.179861
4  1.462696 -1.743161
6  1.314232  0.690579
8  0.014871  3.357427
```
Select via integer list:
```python
In ...: df1.iloc[[1,3, 5], [1, 3]]
Out ...:
           2         6
2  -0.154951 -2.179861
6  -0.345352  0.690579
10 -1.236269 -0.487602
```

```python
In ...: df1.iloc[1:3, :]
Out ...:
          0         2         4         6
2  0.403310 -0.154951  0.301624 -2.179861
4 -1.369849 -0.954208  1.462696 -1.743161
```
```python
In...: df1.iloc[:, 1:3]
Out...:
           2         4
0  -0.732339  0.687738
2  -0.154951  0.301624
4  -0.954208  1.462696
6  -0.345352  1.314232
8   2.396780  0.014871
10 -1.236269  0.896171
```

```python
# this is also equivalent to `df.iat[1,1]`
In...: df1.iloc[1, 1]
Out...: -0.1549507744249032
```
For getting a cross section using an integer position (equiv to `df.xs(1)`):
```python
In...: df1.iloc[1]
Out...:
0    0.403310
2   -0.154951
4    0.301624
6   -2.179861
Name: 2, dtype: float64
```
Out of range slice indexes are handled gracefully just as in Python/NumPy
```python
# these are allowed in Python/NumPy
In...: x = list('abcdef')

In...: x
Out...: ['a', 'b', 'c', 'd', 'e', 'f']

In...: x[4:10]
Out...: ['e', 'f']

In...: x[8:10]
Out...: []

In...: s = pd.Series[x]

In...: s
Out...:
0    a
1    b
2    c
3    d
4    e
5    f
dtype: object

In...: s.iloc[4:10]
Out...:
4    e
5    f
dtype: object

In...: s.iloc[8:10]
Out...: Series([], dtype: object)
```
Note that using slices that go out of bounds can result in an empty axis (e.g. an empty DataFrame being returned).
```python
In...: dfl = pd.DataFrame(np.random.randn(5, 2), columns=list('AB'))
In...: dfl
Out...:
          A         B
0 -0.082240 -2.182937
1  0.380396  0.084844
2  0.432390  1.519970
3 -0.493662  0.600178
4  0.274230  0.132885

In...: dfl.iloc[:, 2:3]
Out...:
Empty DataFrame
Columns: []
Index: [0, 1, 2, 3, 4]

In...: dfl.iloc[:, 1:3]
Out:
          B
0 -2.182937
1  0.084844
2  1.519970
3  0.600178
4  0.132885

In...: dfl.iloc[4:6]
Out...:
         A         B
4  0.27423  0.132885
```
A single indexer that is out of bounds will raise an `IndexError`. A list of indexers where any element is out of bounds will raise an `IndexError`.
```python
>>> dfl.iloc[[4,5,6]]
IndexError: positional indexers are out-of-bounds

>>> dfl.iloc[:, 4]
IndexError: single positional indexer is out-of-bounds
```

## Selection by callable

`.loc`, `.iloc`, and also `[]` indexing can accept a `callable` as indexer. The `callable` must be a function with one argument (the calling Series or DataFrame) that returns valid output for indexing.

```python

```

