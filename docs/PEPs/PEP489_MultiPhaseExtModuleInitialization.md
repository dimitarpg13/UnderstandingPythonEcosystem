# PEP 489: Multi-phase extension module initialization

## Abstract 

This PEP proposes a redesign of the way in which built-in and extension modules interact with the import machinery.
This was last revised for Python 3 in PEP 3121 but did not solve all problems at the time. The goal is to solve 
import related problems by bringing extension modules closer to the way Python modules beahve; specifically to hook
into the ModuleSpec-based loading mechanism introduced in [PEP-451](https://peps.python.org/pep-0451/).

This proposal draws inspiration from PyType_Spec of [PEP-384](https://peps.python.org/pep-0384/) allowing the extension
authors to define only features they need, and to allow future additions to extension module declarations.

Extension modules are created in two-step process fitting better into the ModuleSpec architecture, with parallels to 
`__new__` and `__init__` of classes.

Extension modules can safely store arbitrary `C`-level per-module state in the module that is covered by normal 
garbage collection and supports reloading and sub-interpreters. Extension authors are encouraged to take these issues
into account when using the new API.

## Motivation

Python modules and extension modules are not being set up in the same way. For Python modules, the module object is
created and set up first, then the module code is being executed ([PEP-302](https://peps.python.org/pep-0302/)). 
A ModuleSpec object ([PEP-451](https://peps.python.org/pep-0451/)) is used to hold information about the module, and
passed to the relevant hooks.

For extensions (i.e. shared libraries) and built-in modules, the module init function is executed straight away and 
does both the creation and initalization. The initialization function is not passed the ModuleSpec or any information
it contains, such as the `__file__` or fully-qualified name. This hinders relative imports and resource loading. 


