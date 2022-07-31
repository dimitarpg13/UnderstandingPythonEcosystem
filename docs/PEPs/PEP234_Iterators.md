# PEP-234 - Iterators

## Abstract 

This document proposes an iteration interface that objects can provide to control the behavior of `for` loops.
Looping is customized by providing a method that produces an iterator object. The iterator provides a _get next value_ 
operation that produces the next item in the sequence each time it is called, raising an exception when no more
items are available.

In addition, specific iterators over the keys of a dictionary and over the lines of a file are proposed and
a proposal is made to allow spelling `dict.has_key(key)` as `key in dict`.

## C API Specification

A new exception is defined, `StopIteration`, which can be used to signal the end of the iteration.

A new slot named `tp_iter` for requesting an iterator is added to the type object structure. This should be a function
of one `PyObject *` argument returning a `PyObject *` or `NULL`. To use this slot, a new C API function `PyObject_GetIter()`
is added, with the same signature as the `tp_iter` slot function.



