# Indexing and selecting data

The axis labeling information in pandas objects serves many purposes:

* identifies data (i.e. provides _metadata_) using known indicators
* enables automatic and explicit data alignment
* allows intuitive getting and setting of subsets of the data set

Note: The Python and NumPy indexing operators `[]` and attribute operator `.` provide quick and easy access to pandas data structures across a wide range of use cases. This makes interactive work intuitive, as there's little new to learn if you already know how to deal with Python dictionaries and NumPy arrays. However, since the type of the data to be accessed isn't known in advance, directly using standard operators has some optimization limits. 

Warning: whether a copy or a reference is returned for a setting operation, may depend on the context. This is sometimes called _chained assignment_ and should be avoided.
A bit of perspective on the _chained assignment_ is provided in the section _Returning a view versus a copy_ below:

## Returning a view versus a copy

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


