# PEP 380 - Syntax for Delegating to a Subgenerator

## Abstract

A syntax is proposed for a generator to delegate part of its operations to another generator. This allows a section of
code containing `yield` to be factored out and placed in another generator. Additionally, the subgenerator is allowed
to return with a value, and the value is made available to the delegating generator.


