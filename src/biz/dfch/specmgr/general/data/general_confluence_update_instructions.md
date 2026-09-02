Call the `confluence_update` MCP tool now, with exactly these two arguments:

- `page_url_or_id`: $page_url_or_id
- `markdown_file_path`: $markdown_file_path

This renders the Markdown file at `markdown_file_path` to an HTML fragment
and writes it into the Confluence page identified by `page_url_or_id`,
incrementing that page's version number. Any local image the Markdown file
references (a relative or absolute filesystem path, not an `http(s)://`
URL) is uploaded as a Confluence attachment and its `<img>` tag rewritten
into Confluence's `<ac:image>`/`<ri:attachment>` storage-format macro, on a
best-effort basis -- a missing local file or a failed upload only leaves
that one image unrewritten, it never aborts the page update.

Do not read the Markdown file yourself, do not render it yourself, and do
not call any other Confluence tool first -- `confluence_update` handles
resolving the page id, fetching the current version/title, rendering, the
image uploads, and the final write in one call.

After the call returns, report back to the user:

- the new `version` number the tool returned;
- the full `failed_images` list the tool returned -- if it is non-empty,
  tell the user exactly which local images could not be uploaded/rewritten
  (each entry's `src` and `error`), since those `<img>` tags were left
  unrewritten in the page.
