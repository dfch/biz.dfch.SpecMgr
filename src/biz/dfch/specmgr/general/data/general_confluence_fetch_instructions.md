Call the `confluence_fetch` MCP tool now, with exactly these arguments:

- `url`: $url
- `destination_path`: $destination_path

This fetches `url` over HTTP GET with the configured bearer token, but only
if `url` matches the configured base URL. A normal, browsable Confluence
page URL (Cloud-style `/pages/<id>/<title>` or Server-style `?pageId=<id>`)
is automatically converted into the equivalent REST API URL before
fetching; a `/x/<tinyid>` tiny link is rejected outright, since it cannot
be resolved to a page id without an authenticated browser session.

`destination_path` is only required when the fetched content turns out to
be binary/non-text (e.g. an image or other attachment) -- the tool raises
`ConfluenceDestinationPathRequiredError` in that case if no
`destination_path` was given. For a normal Confluence page fetch (text/
JSON/XML), `destination_path` is ignored even if given.

Do not construct or rewrite the URL yourself -- `confluence_fetch` handles
the browsable-URL-to-REST-URL conversion, the tiny-link rejection, and the
redirect/host check in one call.

After the call returns, report back to the user what the tool returned:
either the raw response body text (for a normal page/text fetch), or the
`destination_path` the binary content was written to.
