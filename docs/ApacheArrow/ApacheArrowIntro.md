# Apache Arrow

Apache Arrow is a development platform for in-memory analytics. It contains a set of technologies that enable big data systems to process and move data fast. It specifies a standardized lang-independent columnar memory format for flat and hierarchical data, organized for efficient analytic operations.

The Apache Arrow project is developing multi-language collection of libraries for solving systems problems related to in-memory analytical processing. This includes topics as:

* zero-copy shared memory and RPC-based data movement
* reading and writing file formats (like CSV, Apache ORC, Apache Parquet)
* in-memory analytics and query processing

## Arrow Columnar Format

The "Arrow Columnar Format" includes a language agnostic in-memory data structure specification, metadata serialization, and a protocol for serialization and generic data transport.

Apache Arrow utilizes Google Flatbuffers project for metadata serialization. [Flatbuffer protocol definition files](https://github.com/apache/arrow/tree/master/format) will be referred in the Arrow Columnar format discussion.

Key features of the columnar format

* data adjacency for sequential access (scans)
* O(1) (constant time) random access
* SIMD and vectorization friendly
* relocatable without ["pointer swizzling"](https://en.wikipedia.org/wiki/Pointer_swizzling), allowing for true zero-copy access in shared memory

The Arrow columnar format provides analytical performance and data locality guarantees in exchange for comparatively more expensive mutation operations. The Arrow specification is concerned only with in-memory data representation and serialization details; issues such as coordinating mutation of data structures are left to be handled by implementations.

### Few definitions

* **Array** or **Vector**: a sequence of values with known length all having the same type. These terms are used interchangeably in different Arrow implementations but we use "array" in this specification.
* **Slot**: a single logical value in an array of some particular data type
* **Buffer** or **Contiguous memory region**: a sequential virtual address space with a given length. Any byte can be reached via a single pointer offset less than the region's length. 
* **Physical Layout**: The underlying memory layout for an array without taking into account any value semantics. For example, a 32-bit signed integer array and 32-bit floating point array have the same layout.
* **Parent** and **child arrays**: names to express relationships between physical value arrays in a nested type structure. For example, a `List<T>`-type parent array has `T`-type array as its child (see more on lists below).
* **Primitive type**: a data type having no child types. This includes such types as fixed bit-width, variable size binary and null types.
* **Nested type**: a data type whose full strcutre depends on one or more other child types. Two fully-specified nested types are equal if and only if their child types are equal. For example, `List<U>` is distinct from `List<V>` iff `U` and `V` are different types.
* **Logical Type**: an application facing semantic value type that is implemented using some physical layout. For example, Decimal values are stored as 16 bytes in a fixed size binary  layout. Similarly, strings can be stored as `List<1-byte>`. A timestamp may be stored as 64 bit fixed size layout.

### Physical Memory Layout

Arrays are defined by a few pieces of metadata and data:

* A logical data type
* A sequence of buffers
* A length as a 64 bit signed integer. Implementations are permitted to be limitted to 32 bit lengths
* A null count as a 64 bit signed integer.
* An optional **dictionary**, for dictionary-encoded arrays

Nested arrays additionally have a sequence of one or more sets of these items called the **child arrays**.

Each logical data type has a well-defined physical layout. Here are the different physical layouts defined by Arrow:

* **Primitive (fixed-size)**: a sequence of values each having the same byte or bit width
* **Variable-size Binary**: a sequence of values each having a variable byte length. Two variants of this layout are supported using 32 bit and 64 bit length encoding.
* **Fixed size List**: a nested layout where each value has the same number of elements taken from a child data type.
* **Variable-size List**: a nested layout where each value is a variable-length sequence of values taken from a child data type. Two variants of this layout are supported using 32 bit and 64 bit length encoding.
* **Struct**: a nested layout consisting of a collection of named child **fields** each having the same length but possibly different types. 
* **Sparse and Dense Union**: a nested layout representing a sequence of values, each of which can have type chosen from a collection of child array types.
* **Null**: a sequence of all null values, having null logical type

The Arrow columnar memory layout only applies to _data_ and not _metadata_. Implementations are free to represent metadata in-memory in whichever form is convenient for them. We handle metadata **serialization** in an implementation-independent way using [Flatbuffers](https://github.com/google/flatbuffers).

### Buffer Alignment and Padding

Implementations are recommended to allocate memory on aligned addresses (multiple of 8- or 64-bytes) and pad (overallocate) to a length that is multiple of 8 or 64 bytes. When serializing Arrow data for interprocess communication, these alignment and padding requirements are enforced. If possible, we suggest that you prefer using 64-byte alignment and padding. Unless otherwise noted, padded bytes  do not need to have a specific value. 

The alignment requirement follows best practices for optimized memory access:

* Elements in numeric arrays will be guaranteed to be retrieved via aligned access
* On some architectures alignment can help limit partially used cache lines

The recommendation for 64 byte alignment comes from the [Intel performance guide](https://github.com/dimitarpg13/UnderstandingPandasAndNumpySourceCode/blob/main/docs/Intel/64-ia-32-architectures-optimization-manual.pdf). For details see the section "11.6.1 Align Data to 32 Bytes". The specific padding length was chosen because it matches the largest SIMD instruction registers available on widely deployed x86 architecture (Intel AVX-512).

The recommended padding of 64 bytes allows for using SIMD instructions consistently in loops without additional conditional checks. This should allow for simpler, efficient and CPU cache-friendly code. In other words, we can load the entire 64-byte buffer into a 512-bit wide SIMD register and get data-level parallelism on all the columnar values packed into the 64-byte buffer. Guaranteed padding can also allow certain compilers to generate more optimized code directly e.g. one can safely
use Intel's `-qopt-assume-safe-padding`).

### Array lengths

Array lengths are represented in the Arrow metadata as a 64-bit signed integer. An implementation of Arrow is considered valid even if it only supports lengths up to the maximum 32-but signed integer, though. If using Arrow in a multi-language environment , this spec recommends limiting lengths to 2^31 - 1 elements or less. Larger data sets can be represented using multiple array chunks.

### Null count

The number of null count value slots is a property of the physical array and considered part of the data structure. The null count is represented in the Arrow metadata as a 64 bit signed integer, as it may be as large as the array length.



