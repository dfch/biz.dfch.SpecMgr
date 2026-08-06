# Specification: SpecMgr Coding Conventions

This document defines the general coding requirements and conventions used throughout the SpecMgr project.

## Python Version and Types

**Requirement:** Use Python 3.11+ and modern Python type notation.

- Python version: 3.11 and later
- Prefer built-in types over typing module aliases:
  - Use `str` instead of `Str`
  - Use `list` instead of `List`
  - Use `dict` instead of `Dict`
  - Use `bool` instead of `Bool`
  - Use `tuple` instead of `Tuple`
  - Use `set` instead of `Set`
  - Use `bytes` instead of `Bytes`
  - Use `int`, `float`, etc. directly over `Integer`, `Float`, etc.

**Example:**
```python
# ✓ Modern Python (3.11+)
def process_items(items: list[str], filter_enabled: bool = True) -> str | None:
    if filter_enabled:
        result = [item.upper() for item in items]
    else:
        result = items.copy()
    return result
```

## Assert Statements

**Rule 1:** Always use `assert` to validate all input parameters in public methods and functions.

**Rule 2:** Use assert statements for input parameter validation, preconditions, and program invariants only.

**Rule 3:** Do not use assert for user-controlled flow control; use it only for program invariants and input validation.

**Example:**
```python
def calculate_discount(value: str, price: float, discount_rate: float) -> float:

    assert isinstance(value, str), type(value)
    assert value.strip()
    assert isinstance(price, float), type(price)
    assert 0 <= price, price

    discount_rate = 0.05

    result = price * (1 - discount_rate)

    return result
```

**Best Practices:**
- Define numeric and string constants for thresholds, minimums, maximums, and standard states
- Place constants at module level with clear documentation
- Use constants in assert statements to make conditions self-documenting and maintainable

## Variable Naming Convention

**Requirement:** When a function or method returns a value, use the variable name "result" in the function body.

- Use `result: Type = value` pattern for return values
- Only use different variable names for special cases where the name is more descriptive
- Follow this convention consistently for all return value assignments

**Example:**
```python
def get_status() -> str:
    result = "active"
    return result


def calculate_total(items: list[str]) -> int:
    result = 0
    for item in items:
        result += len(item)
    return result
```

**Exception:** For functions with a clear, single purpose that justifies a more descriptive name, use that name:

```python
def format_username(user_id: int) -> str:
    formatted = f"user_{user_id}"
    return formatted
```

## Comparison Constants

**Requirement:** Use named constants for values used in comparisons (lvalue-side constants).

- When comparing variables against string literals or values used as a standard for comparison, define those values as constants
- This improves readability and makes it easier to update the comparison value later
- Apply this pattern to all equality checks (`==`, `!=`, `is`, `is not`), inequality checks (`<`, `>`, `<=`, `>=`), and membership checks (`in`, `not in`)

**Example:**
```python
# ✓ Use constant for comparison value
VALID_STATUS = "active"
user_status = "inactive"
if user_status == VALID_STATUS:
    print("Status is valid")

# ✓ Use constant for threshold comparison
MAX_RETRY_ATTEMPTS = 3
attempt = 5
if attempt >= MAX_RETRY_ATTEMPTS:
    raise RuntimeError("Max attempts exceeded")

# ✓ Use constant for membership checks
ALLOWED_FILE_EXT = {".md", ".txt", ".py"}
filename = "document.md"
if filename.endswith(tuple(ALLOWED_FILE_EXT)):
    print("File type is allowed")

# ✗ Avoid inline string values in comparisons
# if user_status == "active":  # Hard to maintain
#     print("Status is valid")
```

**Best Practices:**
- Place constants at the top of the module or in a dedicated configuration section
- Use `ALL_CAPS` naming convention for constants to distinguish them from variables
- Group related constants together for easy maintenance
- Document the purpose and allowed values of each constant

**Example Module-Level Constants:**
```python
# Constants for string comparisons
DEFAULT_ENCODING = "utf-8"
INDENTATION = "    "

# Constants for numeric comparisons
MIN_USER_ID = 1
MAX_BATCH_SIZE = 1000

# Constants for status checks
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_PENDING = "pending"
```

## Type Hints

**Requirement:** Always use type hints for all function signatures, parameters, and variables.

- Type hints are mandatory for:
  - Function and method parameters
  - Return types
  - Variables that are assigned specific types in functions/methods
  - Variables outside functions when they are not inferred from context

**Example:**
```python
def load_config(filename: str) -> dict[str, str]:
    content: str = ""

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    result: dict[str, str] = {}
    for line in content.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result
```

## Documentation Requirements

**Requirement:** Include docstrings for classes, their attributes, and method/function parameters/returns.

- Classes: Document purpose and behavior in class docstrings
- Attributes: Document class attributes using inline comments
- Functions/methods: Document parameters and return types
- Maintain formal, concise documentation; avoid obvious statements

**Example:**
```python
class DataProcessor:
    """Process and validate data entries.

    Attributes:
        max_items: Maximum number of items allowed per batch.
    """

    max_items: int = 100

    def __init__(self, max_items: int) -> None:
        """Initialize the processor.

        Args:
            max_items: Maximum batch size.
        """
        self.max_items = max_items

    def process(self, items: list[str]) -> str:
        """Process a batch of items.

        Args:
            items: List of items to process.

        Returns:
            Summary string of processed items.
        """
        assert len(items) > 0
        result = f"Processed {len(items)} items"
        return result
```

## Additional Best Practices

### Import Organization

```python
# Standard library imports
import os
from pathlib import Path

# Third-party imports
from pydantic import BaseModel

# Local imports
from biz.dfch.specmgr.models import Adr
```

### Docstring Style

```python
def process_data(data: list[str]) -> str:
    """
    Process a list of strings and return a summary.

    Args:
        data: The list of strings to process.

    Returns:
        A summary string of the processed data.

    Example:
        >>> process_data(["hello", "world"])
        "Processed 2 items"
    """
    assert len(data) > 0, "Data list cannot be empty"
    result = "Processed items"
    return result
```

### Error Handling

```python
from pathlib import Path


def load_file(path: str) -> str:
    """Load content from a file.

    Args:
        path: Path to the file to load.

    Returns:
        File content as a string.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        UnicodeDecodeError: If the file cannot be decoded.
    """
    file_path = Path(path)
    result = file_path.read_text(encoding="utf-8")
    return result
```

## TODO

* use unittest, do not use pytest
* use "uv", do not use "pip"
" use "setuptools", do not use "hatchling"

## Rationale

These conventions were chosen to:

 1. **Simplicity:** Modern Python types are more intuitive than typing aliases
 2. **Clarity:** Assert statements provide clear preconditions and invariants
 3. **Consistency:** `result` variable name makes return values obvious
 4. **Type Safety:** Mandatory type hints ensure code is self-documenting and catch type errors early
 5. **Readability:** Followed conventions make the codebase easier to understand and maintain

## Changelog

- **2026-08-06:** Initial version created
- **2026-08-06:** Added Python 3.11+ type requirements
- **2026-08-06:** Added assert statement requirement
- **2026-08-06:** Added variable naming convention requirement
- **2026-08-06:** Added mandatory type hints requirement
- **2026-08-06:** Added documentation requirements with reference to AGENTS.md