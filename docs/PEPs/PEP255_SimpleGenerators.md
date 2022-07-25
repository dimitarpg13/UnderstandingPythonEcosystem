# PEP 255 - Simple Generators

## Abstract

This PEP introduces the concept of generators to Python, as well as a new statement used in conjuction with them,
the `yield` statement.

## Motivation

When a producer function has a hard enough job that it requires maintaing state between values produced, most programming
languages offer no pleasant and efficient solution beyond adding a callback function to the producer's argument list, 
to be called with each value produced.

For example, `tokenize.py` in the standard library takes this approach: the caller must pass a _tokeneater_ function to
`tokenize()`, called whenever `tokenize()` finds the next token. This allows tokenize to be coded in a natural way, but
programs calling tokenize are typically convoluted by the need to remember between callbacks which token(s) were seen
last. The _tokeneater_ function in `tabnanny.py` is a good example of that, maintaining a state machine in global 
variables, to remember across callbacks what it has already seen and what it hopes to see next. This was difficult to get
working correctly, and is still difficult for people to understand. Unfortunately, that's typical of this approach.

An alternative would have been for tokenize to produce an entire parse of the Python program at once, in a large list.
Then _tokenize_ clients could be written in a natural way, using local variables and local control flow (such as loops and
nested `if` statements) to keep track of their state. But this is not practical: programs can be very large, so no a priori
bound can be placed on the memory needed to materialize the whole parse; and some _tokenize_ clients only want to see
weather something specific appears early in the program (e.g. a future statement, or , as is done in IDLE, just the first
indented statement), and then parsing the whole program first is a sever waste of time.

Another alternative would be to make tokenize an iterator, delivering the next token whenever its `.next()` method is
invoked. This is pleasant for the caller in the same way a large list of results would be, but without the memory and
"what if I want to get out early?" drawbacks. However, this shifts the burden on tokenize to remember _its_ state 
between `.next()` invocations, and the reader need only glance at `tokenize.tokenize_loop()` to realize what a horrid
chore that would be. Or picture a recursive algorithm for producing the nodes of a general tree structure: to cast that 
into an iterator framework requires removing the recursion manually and maintaining the state of the traversal by hand.


