# Code Analyzer

Welcome to Code Analyzer, a comprehensive tool designed to extract essential features from source code across multiple programming languages. Our analyzer focuses on providing detailed insights by extracting the following elements:

1. Variables - Identifying all variables used in the code.
2. Methods - Listing the methods defined in the source code.
3. Method Signatures - Extracting the signature of each method, detailing parameters and return types.
4. Operators - Identifying operators used throughout the code.
5. Keywords - Listing programming-specific keywords utilized.
6. Conditional Names - Extracting names used within `if`, `else`, and `while` statements.
7. Conditional Operators - Identifying operators within `if`, `else`, and `while` statements.

## Supported Languages

Currently, Code Analyzer supports three major programming languages:

- Python
- Java
- C++

## Dependencies

To make full use of Code Analyzer, you must install certain dependencies. Please ensure you have the following packages installed:

```bash
$ pip install javalang clang==14.0.0
