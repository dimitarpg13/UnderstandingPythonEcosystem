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

A fourth option is to run the producer and consumer in separate threads. This allows both to maintain their states in 
natural ways, and so is pleasant for both. Indeed, `Demo/threads/Generator.py` in the Python source distribution provides
a usable synchronized-communication class for doing that in a general way. This does not work on platforms without threads,
though and is very slow on platforms that do (compared to what is achievable without threads).

Pleasant solution: provide a kind of function that can return an intermediate result("the next value") to its caller, but 
maintaining the function's local state so that the function can be resumed again right where it left off. A very simple 
example:

```python
def fib():
    a, b = 0, 1
    while 1:
        yield b
        a, b = b, a+b
```

When `fib()` is first invoked, it sets `a` to `0` and `b` to `1`, then yields `b` back to its caller. The caller sees `1`. When `fib` is
resumed, from its point of view the `yield` statement is really the same as, say a `print` statement: `fib` continues after
the yield with all local state intact. `a` and `b` become `1` and `1`, and `fib` loops back to the `yield`, yielding `1` to its
invoker. From `fib`'s point of view it is just delivering a sequence of results, as if via callback. But from it caller point of 
view,the `fib` invocation is an iterable object that can be resumed at will. As in the thread approach, this allows both sides
to be coded in the most natural way; but unlike the thread approach, this can be done efficiently and on all platforms. Indeed,
resuming a generator should be no more expensive than a function call.

The same kind of approach applies to many producer/consumer functions. For example, `tokenize.py` could yield the next token 
instead of invoking a callback function with it as an argument, and tokenize clients could iterate over the tokens in a natural
way: a Python generator is a kind of Python iterator, but an especially powerful kind.

## Specification: Yield

A new statement is introduced:

```
yield_stmt: "yield" expression list
```

The `yield` statement may only be used inside functions. A function that contains a `yield` statement is called a generator function.
A generator function is an ordinary function in all respects, but has the new `CO_GENERATOR` flag set in the code object's `co_flags`
member.

When a generator function is called, the actual arguments are bound to function-local formal argument names in the usual waym but
no code in the body of the function is executed. Instead a generator-iterator object is returned; this conforms to the iterator protocol,
so in particular can be used in for-loops in a natural way. Note that when the intent is clear from context, the unqualified name
"generator" may be used to refer to a generator-function or a generator-iterator.

Each time the `.next()` method of a generator-iterator is invoked, the code in the body of the generator-function is 
executed until a `yield` or `return` statement (see below) is encountered, or until the end of the body is reached.

If a `yield` statement is encountered, the state of the function is frozen, and the value of _expression_list_ is returned to `.next()`'s
caller. By "frozen" we mean that all local state is retained, including the current bindings of local variables, the instruction pointer,
and the internal evaluation stack: enough information is saved so that the next time `.next()` is invoked, the function can proceed exactly
as if the `yield` statement were just another external call. 

_Restriction_: A `yield` statement is not allowed in the `try` clause of a `try/finally` construct. The difficulty is that there's no 
guarantee the generator will ever be resumed hence no guarantee that the finally block will ever get executed; that is too much a
violation of `finally`'s purpose to bear. 

_Restriction_: A generator cannot be resumed while it is actively running:

```python
>>> def g():
...     i = me.next()
...     yield i
>>> me = g()
>>> me.next()
Traceback (most recent call last):
 ...
 File "<string>", line 2, in g
ValueError: generator already executing
```

## a Note on `try-finally` block

Let us consider the following example code:

```python
from sys import argv

try:
   x = argv[1]  # set x to the first argument if one is passed
finally:
   x = 'default'  # if no argument is passed (throwing an exception above) set x to 'default'

print(x)
```

Executing the code above does not print `default` instead an `IndexError` is raised.

```python
Traceback (most recent call last):
  File ".\foo.py", line 4, in <module>
    x = argv[1]
IndexError: list index out of range
```

This is expected behavior as `try:...finally:...` alone *doesn't catch exceptions*. Only the `except` clause of a
`try:...except:...` does.
`try:...finally:...` only guarantees that the statements under `finally` are always executed, whatever happens in the `try` section, 
whether the block succeeds or is exited because of a `break`, `continue`, `return` or an exception. So `try:...finally:...` is 
_great_ for cleaning up resources; This code runs no matter what happens in the block (but note that the `with` statement and
context managers let you encapsulate cleanup behavior too).

If one needs to handle an `IndexError` exception in a `try` block, the one _must_ use an `except` clause. 

## Specification: Return

A generator function can also contain return statements of the form:

```python
   return
```
Note that an _expression list_ is not allowed on return statements in the body of a generator (although they may apppear in the 
bodies of non-generator functions nested within the generator).

When a return statement is encountered, control proceeds as in any function return, executing the appropriate `finally` clauses
(if any exist). Then a `StopIteration` exception is raised, signalling that the iterator is exhausted. A `StopIteration` exception is 
also raised if control flows off the end of the generator without an explicit return.

Note that return means "I'm done, and have nothing interesting to return", for both generator functions and non-generator functions.

Note that return isn't always equivalent to raising `StopIteration`: the difference lies in how enclosing `try/except` constructs
are treated. For example:

```python
>>> def f1():
...    try:
...        return
...    except:
...        yield 1
>>> print list(f1())
[]
```

because, as in any function, `return` simply exists, but:

```python
>>> def f2():
...    try:
...    
```
