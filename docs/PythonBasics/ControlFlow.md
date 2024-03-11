# Python control flow tools

## The `match` Statement

Introduced with Python 3.10.

related PEP documents:

* [PEP 634](https://peps.python.org/pep-0634/) - Structural Pattern Matching: Specification
* [PEP 636](https://peps.python.org/pep-0636/) - Structural Pattern Matching: Tutorial

The match statement is used for pattern matching with the following syntax:

```
match_stmt ::= 'match' subject_expr ":" NEWLINE INDENT case_block+ DEDENT
subject_expr ::= star_named_expression "," star_named_expressions?
                 | named_expression
case_block ::= 'case' patterns [guard] ":" block
```

