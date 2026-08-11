# `biz.dfch.specmgr.models.md.alias_type`

Alias type enumeration for MarkdownStr class name transformation.

This module defines how class name aliases should be interpreted and transformed
when generating display names for MarkdownStr subclasses via the @annotate decorator.

## Classes

### `AliasType`

Enum defining how class name aliases should be interpreted and transformed.

This enum controls how the `alias` parameter in the `@annotate` decorator
is processed when generating display names for MarkdownStr subclasses.

The three alias types allow for different naming conventions and transformations:
- Automatic space-separated formatting from PascalCase names
- Explicit literal string overrides
- Regular expression pattern matching for complex transformations

Attributes:
    SPACE_SEPARATED: Converts PascalCase/camelCase class names to space-separated
                    words in title case. For example:
                    - 'RequiredInformation' → 'Required Information'
                    - 'GoalInContext' → 'Goal In Context'
                    - 'CharacteristicInformation' → 'Characteristic Information'
                    Ignores any explicit `alias` parameter when used.

    LITERAL: Treats the `alias` parameter as an exact, literal string to use as
            the display name. If no `alias` is provided, the class name is used
            without any transformation. Most suitable for custom display names
            (e.g. a heading carrying a "(required)"/"(optional)" suffix, or
            inline formatting markup). Not the default: `@alias`'s own default
            `type` is `SPACE_SEPARATED` (see `alias.py`), and a class with no
            `@alias` decorator at all also defaults to `SPACE_SEPARATED`'s
            derivation of its own class name, not a `LITERAL` match (ADR
            832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0).

    REGEX: Treats the `alias` parameter as a regular expression pattern that can
          be used to match or transform class names. Useful for complex naming
          conventions or pattern-based transformations that don't fit into the
          SPACE_SEPARATED or LITERAL categories.

Example:
    Space-separated formatting (automatic):
    >>> from biz.dfch.specmgr.models.md import annotate, AliasType
    >>> @annotate(type="paragraph_open", alias_type=AliasType.SPACE_SEPARATED)
    ... class RequiredInformation(MarkdownStr): ...
    >>> RequiredInformation._metadata['alias']
    'Required Information'

    Literal override (explicit):
    >>> @annotate(type="heading_open", alias="Custom Title", alias_type=AliasType.LITERAL)
    ... class Title(MarkdownStr): ...
    >>> Title._metadata['alias']
    'Custom Title'

    Regex pattern matching:
    >>> @annotate(
    ...     type="inline",
    ...     alias=r"^(Goal|Scope).*",
    ...     alias_type=AliasType.REGEX
    ... )
    ... class GoalInContext(MarkdownStr): ...
    >>> GoalInContext._metadata['alias_type']
    'REGEX'

**Methods:**

- `capitalize(self, /)`
  Return a capitalized version of the string.

  More specifically, make the first character have upper case and the rest lower
  case.

- `casefold(self, /)`
  Return a version of the string suitable for caseless comparisons.

- `center(self, width, fillchar=' ', /)`
  Return a centered string of length width.

  Padding is done using the specified fill character (default is a space).

- `count(...)`

- `encode(self, /, encoding='utf-8', errors='strict')`
  Encode the string using the codec registered for encoding.

  encoding
    The encoding in which to encode the string.
  errors
    The error handling scheme to use for encoding errors.
    The default is 'strict' meaning that encoding errors raise a
    UnicodeEncodeError.  Other possible values are 'ignore', 'replace' and
    'xmlcharrefreplace' as well as any other name registered with
    codecs.register_error that can handle UnicodeEncodeErrors.

- `endswith(...)`

- `expandtabs(self, /, tabsize=8)`
  Return a copy where all tab characters are expanded using spaces.

  If tabsize is not given, a tab size of 8 characters is assumed.

- `find(...)`

- `format(self, /, *args, **kwargs)`
  Return a formatted version of the string, using substitutions from args and kwargs.
  The substitutions are identified by braces ('{' and '}').

- `format_map(self, mapping, /)`
  Return a formatted version of the string, using substitutions from mapping.
  The substitutions are identified by braces ('{' and '}').

- `index(...)`

- `isalnum(self, /)`
  Return True if the string is an alpha-numeric string, False otherwise.

  A string is alpha-numeric if all characters in the string are alpha-numeric and
  there is at least one character in the string.

- `isalpha(self, /)`
  Return True if the string is an alphabetic string, False otherwise.

  A string is alphabetic if all characters in the string are alphabetic and there
  is at least one character in the string.

- `isascii(self, /)`
  Return True if all characters in the string are ASCII, False otherwise.

  ASCII characters have code points in the range U+0000-U+007F.
  Empty string is ASCII too.

- `isdecimal(self, /)`
  Return True if the string is a decimal string, False otherwise.

  A string is a decimal string if all characters in the string are decimal and
  there is at least one character in the string.

- `isdigit(self, /)`
  Return True if the string is a digit string, False otherwise.

  A string is a digit string if all characters in the string are digits and there
  is at least one character in the string.

- `isidentifier(self, /)`
  Return True if the string is a valid Python identifier, False otherwise.

  Call keyword.iskeyword(s) to test whether string s is a reserved identifier,
  such as "def" or "class".

- `islower(self, /)`
  Return True if the string is a lowercase string, False otherwise.

  A string is lowercase if all cased characters in the string are lowercase and
  there is at least one cased character in the string.

- `isnumeric(self, /)`
  Return True if the string is a numeric string, False otherwise.

  A string is numeric if all characters in the string are numeric and there is at
  least one character in the string.

- `isprintable(self, /)`
  Return True if all characters in the string are printable, False otherwise.

  A character is printable if repr() may use it in its output.

- `isspace(self, /)`
  Return True if the string is a whitespace string, False otherwise.

  A string is whitespace if all characters in the string are whitespace and there
  is at least one character in the string.

- `istitle(self, /)`
  Return True if the string is a title-cased string, False otherwise.

  In a title-cased string, upper- and title-case characters may only
  follow uncased characters and lowercase characters only cased ones.

- `isupper(self, /)`
  Return True if the string is an uppercase string, False otherwise.

  A string is uppercase if all cased characters in the string are uppercase and
  there is at least one cased character in the string.

- `join(self, iterable, /)`
  Concatenate any number of strings.

  The string whose method is called is inserted in between each given string.
  The result is returned as a new string.

  Example: '.'.join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'

- `ljust(self, width, fillchar=' ', /)`
  Return a left-justified string of length width.

  Padding is done using the specified fill character (default is a space).

- `lower(self, /)`
  Return a copy of the string converted to lowercase.

- `lstrip(self, chars=None, /)`
  Return a copy of the string with leading whitespace removed.

  If chars is given and not None, remove characters in chars instead.

- `maketrans(...)`

- `partition(self, sep, /)`
  Partition the string into three parts using the given separator.

  This will search for the separator in the string.  If the separator is found,
  returns a 3-tuple containing the part before the separator, the separator
  itself, and the part after it.

  If the separator is not found, returns a 3-tuple containing the original string
  and two empty strings.

- `removeprefix(self, prefix, /)`
  Return a str with the given prefix string removed if present.

  If the string starts with the prefix string, return string[len(prefix):].
  Otherwise, return a copy of the original string.

- `removesuffix(self, suffix, /)`
  Return a str with the given suffix string removed if present.

  If the string ends with the suffix string and that suffix is not empty,
  return string[:-len(suffix)]. Otherwise, return a copy of the original
  string.

- `replace(self, old, new, /, count=-1)`
  Return a copy with all occurrences of substring old replaced by new.

    count
      Maximum number of occurrences to replace.
      -1 (the default value) means replace all occurrences.

  If the optional argument count is given, only the first count occurrences are
  replaced.

- `rfind(...)`

- `rindex(...)`

- `rjust(self, width, fillchar=' ', /)`
  Return a right-justified string of length width.

  Padding is done using the specified fill character (default is a space).

- `rpartition(self, sep, /)`
  Partition the string into three parts using the given separator.

  This will search for the separator in the string, starting at the end. If
  the separator is found, returns a 3-tuple containing the part before the
  separator, the separator itself, and the part after it.

  If the separator is not found, returns a 3-tuple containing two empty strings
  and the original string.

- `rsplit(self, /, sep=None, maxsplit=-1)`
  Return a list of the substrings in the string, using sep as the separator string.

    sep
      The separator used to split the string.

      When set to None (the default value), will split on any whitespace
      character (including \n \r \t \f and spaces) and will discard
      empty strings from the result.
    maxsplit
      Maximum number of splits.
      -1 (the default value) means no limit.

  Splitting starts at the end of the string and works to the front.

- `rstrip(self, chars=None, /)`
  Return a copy of the string with trailing whitespace removed.

  If chars is given and not None, remove characters in chars instead.

- `split(self, /, sep=None, maxsplit=-1)`
  Return a list of the substrings in the string, using sep as the separator string.

    sep
      The separator used to split the string.

      When set to None (the default value), will split on any whitespace
      character (including \n \r \t \f and spaces) and will discard
      empty strings from the result.
    maxsplit
      Maximum number of splits.
      -1 (the default value) means no limit.

  Splitting starts at the front of the string and works to the end.

  Note, str.split() is mainly useful for data that has been intentionally
  delimited.  With natural text that includes punctuation, consider using
  the regular expression module.

- `splitlines(self, /, keepends=False)`
  Return a list of the lines in the string, breaking at line boundaries.

  Line breaks are not included in the resulting list unless keepends is given and
  true.

- `startswith(...)`

- `strip(self, chars=None, /)`
  Return a copy of the string with leading and trailing whitespace removed.

  If chars is given and not None, remove characters in chars instead.

- `swapcase(self, /)`
  Convert uppercase characters to lowercase and lowercase characters to uppercase.

- `title(self, /)`
  Return a version of the string where each word is titlecased.

  More specifically, words start with uppercased characters and all remaining
  cased characters have lower case.

- `translate(self, table, /)`
  Replace each character in the string using the given translation table.

    table
      Translation table, which must be a mapping of Unicode ordinals to
      Unicode ordinals, strings, or None.

  The table must implement lookup/indexing via __getitem__, for instance a
  dictionary or list.  If this operation raises LookupError, the character is
  left untouched.  Characters mapped to None are deleted.

- `upper(self, /)`
  Return a copy of the string converted to uppercase.

- `zfill(self, width, /)`
  Pad a numeric string with zeros on the left, to fill a field of the given width.

  The string is never truncated.

