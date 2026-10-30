# Structurizr Mermaid export - rendering test

Every fenced block below is the **verbatim** output of
`docker run --rm -v /tmp/structurizr-spike:/usr/local/structurizr structurizr/structurizr:2026.10.26-noble export -w workspace.dsl -f mermaid -o out-mermaid`
(structurizr v2026.10.26, v2 DSL). No lines were changed.

**Render this file and report per section: renders correctly / renders but labels broken (HTML stripped) / syntax error, and copy the exact error text if any.**

Section 0 shows the renderer's Mermaid version (the word `info` is a built-in mermaid diagram).

## 0. Mermaid version probe

```mermaid
info
```
## 1. System Context View

```mermaid
graph LR
  linkStyle default fill:#ffffff

  subgraph diagram ["System Context View: Shop"]
    style diagram fill:#ffffff,stroke:#ffffff

    1["<div style='font-weight: bold'>Alice</div><div style='font-size: 70%; margin-top: 0px'>[Person]</div><div style='font-size: 80%; margin-top:10px'>A customer of the shop</div>"]
    style 1 fill:#ffffff,stroke:#444444,color:#444444
    2["<div style='font-weight: bold'>Shop</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>The e-commerce shop</div>"]
    style 2 fill:#ffffff,stroke:#444444,color:#444444
    6["<div style='font-weight: bold'>Payment Provider</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>Processes card payments</div>"]
    style 6 fill:#ffffff,stroke:#444444,color:#444444

    2-. "<div>Charges cards</div><div style='font-size: 70%'>[HTTPS/JSON]</div>" .->6
    1-. "<div>Places orders</div><div style='font-size: 70%'>[HTTPS]</div>" .->2

  end
```
## 2. Container View

```mermaid
graph LR
  linkStyle default fill:#ffffff

  subgraph diagram ["Container View: Shop"]
    style diagram fill:#ffffff,stroke:#ffffff

    1["<div style='font-weight: bold'>Alice</div><div style='font-size: 70%; margin-top: 0px'>[Person]</div><div style='font-size: 80%; margin-top:10px'>A customer of the shop</div>"]
    style 1 fill:#ffffff,stroke:#444444,color:#444444
    6["<div style='font-weight: bold'>Payment Provider</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>Processes card payments</div>"]
    style 6 fill:#ffffff,stroke:#444444,color:#444444

    subgraph 2 ["Shop"]
      style 2 fill:#ffffff,stroke:#444444,color:#444444

      3["<div style='font-weight: bold'>Web App</div><div style='font-size: 70%; margin-top: 0px'>[Container: Web]</div><div style='font-size: 80%; margin-top:10px'>The shop website and checkout</div>"]
      style 3 fill:#ffffff,stroke:#444444,color:#444444
      4["<div style='font-weight: bold'>Database</div><div style='font-size: 70%; margin-top: 0px'>[Container: PostgreSQL]</div><div style='font-size: 80%; margin-top:10px'>Holds products and orders</div>"]
      style 4 fill:#ffffff,stroke:#444444,color:#444444
    end

    3-. "<div>Reads and writes</div><div style='font-size: 70%'>[SQL]</div>" .->4
    1-. "<div>Places orders</div><div style='font-size: 70%'>[HTTPS]</div>" .->3
    3-. "<div>Charges cards</div><div style='font-size: 70%'>[HTTPS/JSON]</div>" .->6

  end
```
## 3. Deployment View (Live)

```mermaid
graph LR
  linkStyle default fill:#ffffff

  subgraph diagram ["Deployment View: Shop - Live"]
    style diagram fill:#ffffff,stroke:#ffffff

    subgraph 11 ["App Server"]
      style 11 fill:#ffffff,stroke:#444444,color:#444444

      12["<div style='font-weight: bold'>Web App</div><div style='font-size: 70%; margin-top: 0px'>[Container: Web]</div><div style='font-size: 80%; margin-top:10px'>The shop website and checkout</div>"]
      style 12 fill:#ffffff,stroke:#444444,color:#444444
    end

    subgraph 13 ["DB Server"]
      style 13 fill:#ffffff,stroke:#444444,color:#444444

      14["<div style='font-weight: bold'>Database</div><div style='font-size: 70%; margin-top: 0px'>[Container: PostgreSQL]</div><div style='font-size: 80%; margin-top:10px'>Holds products and orders</div>"]
      style 14 fill:#ffffff,stroke:#444444,color:#444444
    end

    12-. "<div>Reads and writes</div><div style='font-size: 70%'>[SQL]</div>" .->14

  end
```
## 4. Dynamic View: Checkout (collaboration, default)

```mermaid
graph LR
  linkStyle default fill:#ffffff

  subgraph diagram ["Checkout"]
    style diagram fill:#ffffff,stroke:#ffffff

    subgraph 2 ["Shop"]
      style 2 fill:#ffffff,stroke:#444444,color:#444444

      3["<div style='font-weight: bold'>Web App</div><div style='font-size: 70%; margin-top: 0px'>[Container: Web]</div><div style='font-size: 80%; margin-top:10px'>The shop website and checkout</div>"]
      style 3 fill:#ffffff,stroke:#444444,color:#444444
      4["<div style='font-weight: bold'>Database</div><div style='font-size: 70%; margin-top: 0px'>[Container: PostgreSQL]</div><div style='font-size: 80%; margin-top:10px'>Holds products and orders</div>"]
      style 4 fill:#ffffff,stroke:#444444,color:#444444
    end

    1["<div style='font-weight: bold'>Alice</div><div style='font-size: 70%; margin-top: 0px'>[Person]</div><div style='font-size: 80%; margin-top:10px'>A customer of the shop</div>"]
    style 1 fill:#ffffff,stroke:#444444,color:#444444
    6["<div style='font-weight: bold'>Payment Provider</div><div style='font-size: 70%; margin-top: 0px'>[Software System]</div><div style='font-size: 80%; margin-top:10px'>Processes card payments</div>"]
    style 6 fill:#ffffff,stroke:#444444,color:#444444

    1-. "<div>1. Submits the order</div><div style='font-size: 70%'>[HTTPS]</div>" .->3
    3-. "<div>2. Persists the order</div><div style='font-size: 70%'>[SQL]</div>" .->4
    3-. "<div>3. Charges the card</div><div style='font-size: 70%'>[HTTPS/JSON]</div>" .->6

  end
```
## 5. Dynamic View: Checkout (sequence, mermaid.sequenceDiagram true)

```mermaid
sequenceDiagram

  participant 1 as Alice<br />[Person]
  participant 3 as Web App<br />[Container: Web]
  participant 4 as Database<br />[Container: PostgreSQL]
  participant 6 as Payment Provider<br />[Software System]

  1->>3: Submits the order<br />[HTTPS]
  3->>4: Persists the order<br />[SQL]
  3->>6: Charges the card<br />[HTTPS/JSON]
```
