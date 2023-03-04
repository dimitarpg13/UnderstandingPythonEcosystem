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

Annotations for nested parameters always follow the name of the parameter, not the last parenthesis. Annotating all parameters of a nested parameter is not required:

```python
def foo((x1, y1: expression),
        (x2: expression, y2: expression)=(None, None)):
    ...
```

### Return Values

The examples thus far have omitted examples of how to annotate the type of a function's return value. This is done like so:

```python
def sum() -> expression:
    ...
```

That is, the parameter list can now be followed by a literal `->` and a Python expression. Like the annotations for parameters, this expression will be evaluated when the function definition is executed. The grammar for function definitions is now:

```python
decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
decorators: decorator+
funcdef: [decorators] 'def' NAME parameters ['->' test] ':' suite
parameters: '(' [typedargslist] ')'
typedargslist: ((tfpdef ['=' test] ',')*
                ('*' [tname] (',' tname ['=' test])* [',' '**' tname]
                 | '**' tname)
                | tfpdef ['=' test] (',' tfpdef ['=' test])* [','])
tname: NAME [':' test]
tfpdef: tname | '(' tfplist ')'
tfplist: tfpdef (',' tfpdef)* [',']
```

### Lambda

`lambda`'s syntax does not support annotations. The syntax of `lambda` could be changed to support annotations, by requiring parentheses around the parameter list. However, it was decided not to make this change because:

1. it would be an incompatible change
2. Lambdas are neuered anyway
3. The lambda can always be changed to a function.

## Accessing Function Annotations

Once compiled, a function's annotations are available via the function's `__annotations__` attribute. This attribute is a mutable dictionary, mapping parameter names to an object representing the evaluated annotation expression.

There is a special key in the `__annotations__` mapping, `"return"`. This key is present only if an annotation was supplied for the function's return value.

For example, the following annotation:

```python
def foo(a: 'x', b: 5 + 6, c: list) -> max(2, 9):
    ...
```

would result in an `__annotations__` mapping of

```python
{'a': 'x',
 'b': 11,
 'c': list,
 'return': 9}
```

The `return` key was chosen because it cannot conflict with the name of a parameter; any attempt to use `return` as a parameter name would result in a `SyntaxError`.

`__annotations__` is an empty, mutable dictionary if there are no annotations on the function or if the functions was created from a `lambda` expression.

### Use Cases

In the course of discussing annotations, a number of use-cases have been raised. Some of these are presented here, grouped by what kind of information they convey. Also included are examples of existing products and packages that could make use of annotations.

* Providing typing information
  ** Type checking 
  ** Let IDEs show what types a function expects and returns
  ** Function overloading / generic functions
  ** Foreign-language bridges
  ** Adaptation
  ** Predicate logic functions
  ** Database query mapping
  ** RPC paramter marshaling
* Other information
  ** Documentation for parameters and return values
