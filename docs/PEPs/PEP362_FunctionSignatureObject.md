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

* **bind(*args, **kwargs)** -> **BoundArguments**
    Creates a mapping from positional and keyword arguments to parameters. Raises a `TypeError` if the passed arguments do not match the signature.

* **bind_partial(*args, **kwargs)** -> **BoundArguments**

