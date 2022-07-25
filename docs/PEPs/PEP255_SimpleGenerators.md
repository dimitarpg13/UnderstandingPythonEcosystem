# PEP 255 - Simple Generators

## Abstract

This PEP introduces the concept of generators to Python, as well as a new statement used in conjuction with them,
the `yield` statement.

## Motivation

When a producer function has a hard enough job that it requires maintaing state between values produced,
most programming languages offer no pleasant and efficient solution beyond adding a callback function to
the producer's argument list, to be called with each value produced.


