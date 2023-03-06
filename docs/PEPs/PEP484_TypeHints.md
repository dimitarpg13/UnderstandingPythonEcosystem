# PEP 484 - Type Hints

## Abstract 
[PEP 3107](PEP3107_FunctionAnnotations.md) introduced the syntax for function annotations, but the semantics were deliberately left undefined. There has now been enough 3rd party usage for static type analysis that the community would benefit from a standard vocabulary and baseline tools within the standard library.

This PEP introduces a provisional module to provide these standard definitions and tools, along with some conventions for situations where annotations are not avaialable.

Note that this PEP still explicitly does __not__ prevent other uses of annotations, nor does it require (or forbid) any particular processing of annotations, even when they conform to this specification. It simply enables better coordination, as PEP 333 did for web frameworks.

For example, here is a simple function whose argument and return type are declared in the annotations:

```python
def greeting(name: str) -> str:
    return 'Hello' + name
```
While these annotations are available at runtime through the usual `__annotatons__` attribute, _no type checking happens at runtime_. Instead, the proposal assumes the existence of a separate off-line type checker which users can run over their source code voluntarily. Essentially, such a type checker acts as a very powerful linter. (While it would of course be possible for individual users to employ a similar checker at run time for Design By Contract enforcement or JIT optimization,
those tools are not yet as mature.)

The proposal is strongly inspired by [mypy](https://mypy-lang.org/). For example, the type "sequence of integers" can be written as `Sequence[int]`. The square brackets mean that no new syntax needs to be added to the language The example here uses a custom type `Sequence`, imported from a pure-Python module `typing`. The `Sequence[int]` notation works at runtime by implementing `__getitem__()` in the metaclass (but its significance is primarily to an offline type checker).



