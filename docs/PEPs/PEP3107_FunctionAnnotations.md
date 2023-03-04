# PEP 3107 - Function Annotations

## Fundamentals of Function Annotations

Note on what function annotations are and what they are not:

1. Function annotations, both for parents and return values, are completely optional.
2. Function annotations are nothing more than a way of associating arbitrary Python expressions with various parts of a function at compile time.
By itself, Python does not attach any particular meaning or significance to annotations. Left to its own, Python simply makes these expression available as described in Accessing Function Annotations below.

The only way that annotations take on meaning is when they are interpreted by third-party libraries. These annotation consumers can do anything they want with a function's annotations. For example, one library might use string-based annotations to provide improved help mesages, like so:

```python

def compile(source: "something compilable",
            filename: "where the compilable thing comes from",
            mode: "is this a single statement or a suite?"):
    ...
``` 

Another library might be used to provide typechecking for Python functions and methods. This library could use annotations to indicate the function's expected input and return types, possibly something like:

```python
def haul(item: Haulablem *vargs: PackAnimal) -> Distance:
    ...
```
However, neither the strings in the first example nor the type information in the second example have any meaning on their own; meaning comes from third party libraries alone.

3. Following from point 2, this PEP makes no attempt to introduce any kind of standard semantics, even for the built-in types. This work will be left to third party libraries.

## Syntax

### Parameters

Annotations for parameters take the form of optional expressions that follow the parameter name:

```python
def foo(a: expression, b: expression = 5):
    ...
```

In pseudo-grammar, parameters now look like `indentifier [: expression] [= expression]`. That is, annotations always precede a parameter's default value and both annotations adand default values are optional. Just like how equal signs are used to indicate a default value, colons are used to mark annotations. All nnotation expressions are evaluated when the function definition is executed, just like default values.

Annotations for excess parameters (i.e. `*args` and `**kwargs`) are indicated similarly:

```python
def foo(*args: expression, **kwargs: expression):
```


