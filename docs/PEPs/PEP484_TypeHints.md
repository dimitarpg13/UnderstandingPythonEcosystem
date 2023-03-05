# PEP 484 - Type Hints

## Abstract 
[PEP 3107](PEP3107_FunctionAnnotations.md) introduced the syntax for function annotations, but the semantics were deliberately left undefined. There has now been enough 3rd party usage for static type analysis that the community would benefit from a standard vocabulary and baseline tools within the standard library.

This PEP introduces a provisional module to provide these standard definitions and tools, along with some conventions for situations where annotations are not avaialable.

Note that this PEP still explicitly does __not__ prevent other uses of annotations, nor does it require (or forbid) any particular processing of annotations, even when they conform to this specification. It simply enables better coordination, as PEP 333 did for web frameworks. 
