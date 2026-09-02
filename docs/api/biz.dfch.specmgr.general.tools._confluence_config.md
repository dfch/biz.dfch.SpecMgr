# `biz.dfch.specmgr.general.tools._confluence_config`

Shared Confluence base-URL/bearer-token configuration, used by both
``confluence_fetch`` and (later) ``confluence_update``.

Extracted out of the former ``webfetch.py`` (ADR
a156fdf9-052c-4f43-93a2-eeec04a91eac) so both Confluence tools read the same
two environment variables (:data:`CONFLUENCE_BASE_URL_ENV_VAR`,
:data:`CONFLUENCE_BEARER_ENV_VAR`) through one place, mirroring this
codebase's existing ``_doc_paths.py``/``_path_safety.py``/``_splice.py``
shared-private-helper convention -- no ``pydantic-settings``, no in-memory
caching.

## Classes

### `ConfluenceNotConfiguredError`

:data:`CONFLUENCE_BASE_URL_ENV_VAR` and/or :data:`CONFLUENCE_BEARER_ENV_VAR` are not set.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `confluence_config() -> 'tuple[str, str]'`

Return the configured ``(base_url, bearer_token)`` pair.

Reads :data:`CONFLUENCE_BASE_URL_ENV_VAR` and :data:`CONFLUENCE_BEARER_ENV_VAR`
directly from the environment on every call -- no caching, consistent with
this codebase's "the environment is the sole source of truth" config
style (mirrors ``adr.tools._paths.adr_base_dir``).

Returns
-------
tuple[str, str]
    The configured ``(base_url, bearer_token)`` pair.

Raises
------
ConfluenceNotConfiguredError
    If either environment variable is unset or blank.

