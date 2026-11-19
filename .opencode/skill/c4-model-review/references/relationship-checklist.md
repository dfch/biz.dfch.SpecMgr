# Relationship checklist

Walk every relationship in the model: its label, its technology, and its
direction.

## Labels

- [ ] Every relationship has a label describing **intent** — what is
  communicated in that direction, not just "uses".
- [ ] Labels match the arrow direction (the source does X **to** the
  destination).
- [ ] No vague labels. Flag any relationship whose label states nothing
  about what happens: the classic set is "Uses", "Connects to", "Interacts
  with", "Communicates with" — each is a **Warning**; name the two elements
  involved and ask what the label should actually say.

Suggest specific alternatives for vague labels:

| Vague | Ask | Better example |
|-------|-----|----------------|
| "Uses" | What does it use it for? | "queries order history from" |
| "Connects to" | What data flows? | "sends email notifications via" |
| "Interacts with" | What's the interaction? | "submits search queries to" |
| "Communicates with" | What's communicated? | "publishes order events to" |

## Technology

- [ ] Inter-container relationships specify a protocol or technology (e.g.
  "JSON/HTTPS", "SQL/TCP", "gRPC", "AMQP").
- [ ] Person-to-container relationships specify the interface technology
  (e.g. "HTTPS", "WebSocket").
- [ ] Intra-container relationships (component to component) may omit the
  technology.

## Direction

- [ ] Arrows point in the direction of dependency or data flow.
- [ ] No bidirectional relationships (split them into two if needed).
- [ ] Implied relationships make sense (e.g. person to container implies
  person to system).
