# PEP 362 - Function Signature Object

## Abstract

Python has always supported powerful introspection capabilities, including introspecting functions and methods (for the rest of this PEP, "function" refers to both functions and methods). By examining a function object you can fully reconstruct the function signature. Unfortunatelly this information is stored in an inconvenient manner and is spread across a half dozen deeply nested attributes.

This PEP proposes a new representation for function signatures. The new representation contains all necessary information about a function and its parameters, and makes introspection easy and straightforward.

However, this object does not replace the existing function metadata, which is used by Python itself to execute those functions. The new metadata object is intedend solely to make function introspection easier.

## Signature Object

A Signature object represents the call signature of a function and its return annotation. For each parameter accepted by the function it stores a Parameter object on its `parameters` collection.

A Signature object has the following public attributes and methods:

* **return_annotation** : **object**
    The "return" annotation for the function. If the function has no "return" annotation, this attribute is set to `Signature.empty`.

* **parameters** : **OrderedDict**
    An ordered mapping of parameters' names to the corresponding Parameter objects

* __bind(*args, **kwargs)__ -> __BoundArguments__
    Creates a mapping from positional and keyword arguments to parameters. Raises a `TypeError` if the passed arguments do not match the signature.

* __bind_partial(*args, **kwargs)__ -> __BoundArguments__
    Work in the same way as `bind()`, but allows the omission of some required arguments (mimics `functools.partial` behavior). Raises a `TypeError` if the passed arguments do not match the signature.

* __replace(parameters=<optional>,*,return_annotation=<optional>)__ -> __Signature__
    Creates a new Signature instance based on the instance `replace` was invoked on. It is possible to pass different `parameters` and/or `return_annotation` to override the corresponding properties of the base signature. To remove `return_annotation` from the copied `Signature`, pass in `Signature.empty`.

    Note that the `'=<optional>'` notation, means that the argument is optional. This notation applies to the rest of this PEP.

Signature objects are immutable. Use `Signature.replace()` to make a modified copy:

```python
>>> def foo() -> None:
...     pass
>>> sig = signature(foo)

>>> new_sig = sig.replace(return_annotation="new return annotation")
>>> new_sig is not sig
True
>>> new_sig.return_annotation != sig.return_annotation
True
>>> new_sig.parameters == sig.parameters
True

>>> new_sig = new_sig.replace(return_annotation=new_sig.empty)
>>> new_sig.return_annotation is Signature.empty
True
```

There are two ways to instantiate a Signature class:

* __Signature(parameters=<optional>,*,return_annotation=Signature.empty)__
    Default Signature constructor. Accepts an optional sequence of `Parameter` objects, and an optional `return_annotation`. Parameters sequence is validated to check that there are no parameters with duplicate names, and that the parameters are in the right order, i.e. positional =-only first, then positional-or-keyword, etc.

* __Signature.from_function(function)__
    Returns a Signature object reflecting the signature of the function passed in.

It's possible to test Signatures for equality. Two signatures are equal when their parameters are equal, their positional and positional-only parameters appear in the same order, and they have equal return annotations.

Changes to the Signature object, or to any of its data members, do not affect the function itself. 
Signature also implements `__str__`:

```python
>>> str(Signature.from_function((lambda *args: None)))
'(*args)'

>>> str(Signature())
'()'
```

## Parameter Object

Python's expressive syntax means functions can accept many different kinds of parameters with many subtle semantic differences. We propose a rich Parameter object designed to represent any possible function parameter.
A Parameter object has the following public attributes and methods:

* __name__ : __str__
    The name of the parameter as a string. Must be a valid python identifier name (with the exception of `POSITIONAL_ONLY` parameters, which can have it set to `None`)

* __default__ : __object__
    The default value for the parameter. If the parameter has no default value, this attribute is set `Parameter.empty`.

* __annotation__ : __object__
    The annotation for the parameter. If the parameter has no annotation, this attribute is set to `Parameter.empty`.

* __kind__
    Describes how argument values are bound to the parameter. Possible values:
    * `Parameter.POSITIONAL_ONLY` - value must be supplied as a positional argument.
    Python has no explicit syntax for defining positional-only parameters, but many built-in and extension module functions (especially those that accept only one or two parameters) accept them.
    * `Parameter.POSITIONAL_OR_KEYWORD` - value may be supplied as either a keyword or positional argument (this is the standard binding behavior for functions implemented in Python)
    * `Parameter.KEYWORD_ONLY` - value must be supplied as a keyword argument. Keyword only parameters are those which appear after a "*" or "*args" entry in a Python function definition.
    * `Parameter.VAR_POSITIONAL` - a tuple of positional arguments that aren't bound to any other parameter. This corresponds to a "**kwargs" parameter in a Python function definition.
    Always use `Parameter.*` constants for setting and checking value of the `kind` attribute.

* __replace(*,name=<optional>,kind=<optional>,default=<optional>,annotation=<optional>)__ -> __Parameter__
    Creates a new Parameter instance based on the instance `replaced` was invoked on. To override a Parameter attribute, pass the corresponding argument. To remove from a `Parameter`, pass `Parameter.empty`.

Parameter constructor:

* __Parameter(name,kind,*,annotation=Parameter.empty,default=Parameter.empty)__
    Instantiates a Parameter object. `name` and `kind` are required, while `annotation` and `default` are optional.

Two parameters are equal when they have equal names, kinds, defaults, and annotations.

Parameter objects are immutable. Instead of midofying a Parameter object, you can use `Parameter.replace()` to create a modified copy like so:

```python
>>> param = Parameter('foo', Parameter.KEYWORD_ONLY, default=42)
>>> str(param)
'foo=42'

>>> str(param.replace())
'foo=42'

>>> str(param.replace(default=Parameter.empty, annotation='spam'))
"foo:'spam'"
```

## BoundArguments Object

Result of a `Signature.bind` call. Holds the mapping of arguments to the function's parameters.
Has the following public attributes:

* __arguments__ : __OrderedDict__
    An ordered, mutable mapping of parameters' names to arguments' values. Contains only explicitly bound arguments. Arguments for which `bind()` relied on a default value are skipped.

* __args__ : __tuple__
    Tuple of positional arguments values. 

