workspace "OpenTelemetry Demo" "Phase 120 validation run 2 (class: distributed cloud-native platform): OpenTelemetry Astronomy Shop, opentelemetry-demo main fc7f2a68 (2026-11-21), Helm chart opentelemetry-demo 0.42.7 (helm-charts main 5e7ca838)" {

    !identifiers hierarchical

    model {
        properties {
            "review.safety.relevant" "no"
            "review.safety.justification" "A demonstration web shop with simulated payment, shipping and email. It controls no equipment and no real transaction, and no decision with a safety consequence depends on its output."
            "origin" "Extracted"
            "provenance" "opentelemetry-demo@fc7f2a68 README.md, opentelemetry.io content/en/docs/demo/architecture.md, opentelemetry.io docs/demo/requirements/architecture.md"
        }

        shopper = person "Shopper" "Uses the Astronomy Shop web front end or the mobile app." {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md Internet -> frontend-proxy"
            }
        }
        operator = person "Demo operator" "Runs the demo, switches fault flags, reads traces, metrics and logs." {
            properties {
                "origin" "Inferred"
                "provenance" "opentelemetry-demo@fc7f2a68 src/frontend-proxy/envoy.tmpl.yaml routes /feature, /grafana/, /jaeger/, /loadgen/ on the public listener"
            }
        }
        llm = softwareSystem "LLM provider" "OpenAI-compatible LLM endpoint for the agent layer. Optional. Recorded cassettes (USE_VCR) replace it in tests." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry-demo@fc7f2a68 compose.agent.yaml LLM_BASE_URL, API_KEY, USE_VCR"
            }
        }
        vendor = softwareSystem "Observability vendor backend" "Optional OTLP backend of a vendor fork. Added through the collector extras configuration." {
            tags "External"
            properties {
                "origin" "Inferred"
                "provenance" "opentelemetry-demo@fc7f2a68 README.md Demos featuring the Astronomy Shop, src/otel-collector/otelcol-config-extras.yml"
            }
        }

        shop = softwareSystem "Astronomy Shop" "Microservice web shop that demonstrates OpenTelemetry instrumentation, with fault injection by feature flags. Docker Compose layers core, full, observability, agent; Helm chart for Kubernetes." {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry-demo@fc7f2a68 README.md, compose.yaml header comment"
            }

            frontendProxy = container "frontend-proxy" "Single ingress. Routes / to the frontend and /feature, /grafana/, /jaeger/, /loadgen/, /otlp-http/, /images/, /flagservice/, /chatbot/ to the other services. One HTTP listener, no TLS configured." "Envoy" {
                tags "Ingress"
                properties {
                    "origin" "Extracted"
                    "provenance" "src/frontend-proxy/envoy.tmpl.yaml, compose.yaml frontend-proxy"
                    "service.criticality" "critical"
                }
            }
            frontend = container "frontend" "Web UI and API routes (/api/cart, /api/checkout, ...). Calls the backend services through gRPC and HTTP gateways." "TypeScript, Next.js" {
                properties {
                    "origin" "Extracted"
                    "provenance" "src/frontend/pages/api/, src/frontend/gateways/"
                }
            }
            mobile = container "react-native-app" "Mobile client of the shop. Calls the frontend-proxy over HTTP." "TypeScript, React Native" {
                tags "Client"
                properties {
                    "origin" "Extracted"
                    "provenance" "src/react-native-app/, opentelemetry.io content/en/docs/demo/architecture.md"
                }
            }
            ad = container "ad" "Returns contextual ads (AdService.GetAds)." "Java" {
                properties {
                    "origin" "Extracted"
                    "provenance" "pb/demo.proto AdService, src/ad/"
                }
            }
            cart = container "cart" "Shopping cart (CartService AddItem, GetCart, EmptyCart). Stateless; cart state in valkey-cart." "C#, .NET" {
                properties {
                    "origin" "Extracted"
                    "provenance" "pb/demo.proto CartService, src/cart/src/cartstore/ValkeyCartStore.cs"
                }
            }
            checkout = container "checkout" "Orchestrates PlaceOrder: cart, catalog, currency, shipping quote, payment, ship, empty cart, email, publish order to Kafka. Synchronous orchestration, no compensation step." "Go" {
                properties {
                    "origin" "Extracted"
                    "provenance" "pb/demo.proto CheckoutService, src/checkout/main.go PlaceOrder"
                    "service.criticality" "critical"
                }
            }
            currency = container "currency" "Currency conversion (CurrencyService Convert, GetSupportedCurrencies)." "C++" {
                properties {
                    "origin" "Extracted"
                    "provenance" "pb/demo.proto CurrencyService, src/currency/"
                }
            }
            email = container "email" "Sends the order confirmation (simulated). HTTP POST /send_order_confirmation." "Ruby" {
                properties {
                    "origin" "Extracted"
                    "provenance" "src/checkout/main.go sendOrderConfirmation, src/email/"
                }
            }
            payment = container "payment" "Charges the credit card (simulated, PaymentService.Charge)." "JavaScript, Node.js" {
                properties {
                    "origin" "Extracted"
                    "provenance" "pb/demo.proto PaymentService, src/payment/"
                }
            }
            productCatalog = container "product-catalog" "Product list, product lookup, search (ProductCatalogService). Reads astronomy-db." "Go" {
                properties {
                    "origin" "Extracted"
                    "provenance" "pb/demo.proto ProductCatalogService, compose.yaml product-catalog DB_CONNECTION_STRING"
                }
            }
            quote = container "quote" "Computes the shipping cost for shipping." "PHP" {
                properties {
                    "origin" "Extracted"
                    "provenance" "src/quote/, opentelemetry.io content/en/docs/demo/architecture.md shipping -> quote"
                }
            }
            recommendation = container "recommendation" "Product recommendations (RecommendationService). Calls product-catalog. Java, Spring Boot 4 since the rewrite of issue 1368; opentelemetry.io architecture.md still says Python." "Java, Spring Boot" {
                properties {
                    "origin" "Extracted"
                    "provenance" "src/recommendation/, .chloggen/1368-recommendation-spring-boot-4.yaml"
                }
            }
            shipping = container "shipping" "Shipping quote and ship order over HTTP (/get-quote, /ship-order). Calls quote." "Rust" {
                properties {
                    "origin" "Extracted"
                    "provenance" "src/checkout/main.go quoteShipping, shipOrder; src/shipping/"
                }
            }
            accounting = container "accounting" "Consumes orders from Kafka (consumer group accounting, auto commit) and writes them to astronomy-db. Skips a duplicate order on a unique-key violation." "C#, .NET" {
                properties {
                    "origin" "Extracted"
                    "provenance" "src/accounting/Consumer.cs, compose.full.yaml accounting"
                    "service.criticality" "low"
                }
            }
            fraudDetection = container "fraud-detection" "Consumes orders from Kafka (consumer group fraud-detection, max.poll.records 30) and records order metrics." "Kotlin, JVM" {
                properties {
                    "origin" "Extracted"
                    "provenance" "src/fraud-detection/src/main/kotlin/frauddetection/main.kt, compose.full.yaml"
                    "service.criticality" "low"
                }
            }
            imageProvider = container "image-provider" "Serves the product images." "nginx" {
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.yaml image-provider, .env IMAGE_PROVIDER_PORT"
                }
            }
            loadGenerator = container "load-generator" "Synthetic shopper traffic against the frontend-proxy. Web UI behind /loadgen/." "Python, Locust" {
                tags "Test driver"
                properties {
                    "origin" "Extracted"
                    "provenance" "src/load-generator/, .env LOCUST_HOST"
                }
            }
            flagd = container "flagd" "OpenFeature flag evaluation (gRPC 8013, OFREP 8016). Reads demo.flagd.json from a mounted file. 21 fault flags." "Go, flagd v0.16.0" {
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.yaml flagd, src/flagd/demo.flagd.json, .env FLAGD_IMAGE"
                    "service.criticality" "low"
                }
            }
            flagdUi = container "flagd-ui" "Web UI to change the flags. Writes the same flag file that flagd reads." "Elixir, Phoenix" {
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.yaml flagd-ui volumes ./src/flagd:/app/data"
                    "service.criticality" "low"
                }
            }
            telemetryDocs = container "telemetry-docs" "Serves the generated documentation of the telemetry schema (Weaver registry)." "static web server" {
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.yaml telemetry-docs, AGENTS.md Telemetry conventions"
                }
            }
            agent = container "agent" "LLM agent layer (optional, compose.agent.yaml). Uses MCP tools against the shop." "Python" {
                tags "Optional"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.agent.yaml agent, opentelemetry.io content/en/docs/demo/architecture.md"
                }
            }
            mcp = container "mcp" "MCP server that exposes shop operations to the agent (optional)." "Python" {
                tags "Optional"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.agent.yaml mcp, opentelemetry.io content/en/docs/demo/architecture.md mcp -> frontend"
                }
            }
            chatbot = container "chatbot" "Chat UI for the agent (optional), behind /chatbot/." "Python" {
                tags "Optional"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.agent.yaml chatbot, src/frontend-proxy/envoy.tmpl.yaml"
                }
            }
            kafka = container "kafka" "Message broker, topic orders. Single broker in KRaft mode (controller quorum 1@kafka), PLAINTEXT listener." "Apache Kafka" {
                tags "Queue"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.full.yaml kafka, .env KAFKA_TOPIC=orders"
                }
            }
            valkeyCart = container "valkey-cart" "Cart store." "Valkey 9" {
                tags "Database"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.yaml valkey-cart, .env VALKEY_ADDR"
                }
            }
            astronomyDb = container "astronomy-db" "Products and accounting orders. Users astronomy_user and monitoring_user with passwords fixed in init.sql." "PostgreSQL 18" {
                tags "Database"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.yaml astronomy-db, src/postgresql/init.sql"
                }
            }
            otelCollector = container "otel-collector" "Receives OTLP (gRPC, HTTP with CORS for all origins), scrapes valkey, postgresql, nginx, ad, docker stats and host metrics, exports to Jaeger, Prometheus, OpenSearch. Runs as user 0:0 with the docker socket and the host filesystem mounted read-only." "OpenTelemetry Collector contrib 0.160.0" {
                tags "Observability"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.yaml otel-collector, src/otel-collector/otelcol-config.yml, otelcol-config-observability.yml"
                }
            }
            jaeger = container "jaeger" "Trace store and UI. In-memory storage, max 25000 traces in the Helm chart." "Jaeger 2.21" {
                tags "Observability"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.observability.yaml jaeger; opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml jaeger.storage.type memory"
                }
            }
            prometheus = container "prometheus" "Metric store, OTLP receiver." "Prometheus 3.13" {
                tags "Observability"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.observability.yaml prometheus, otelcol-config-observability.yml otlp_http/prometheus"
                }
            }
            opensearch = container "opensearch" "Log store. Single node, security plugin disabled, no persistence in the Helm chart." "OpenSearch" {
                tags "Observability"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.observability.yaml opensearch; opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml opensearch"
                }
            }
            grafana = container "grafana" "Dashboards and one alert rule set (cart service) over Prometheus, Jaeger, OpenSearch." "Grafana 13" {
                tags "Observability"
                properties {
                    "origin" "Extracted"
                    "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo grafana/provisioning/"
                }
            }
            opampServer = container "opamp-server" "OpAMP server that manages the collector (and the cart OpAMP client)." "OpAMP" {
                tags "Observability"
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.observability.yaml opamp-server, otelcol-config-observability.yml extensions opamp, src/cart/src/OpAmpClientSetup.cs"
                }
            }
        }

        shopper -> shop.frontendProxy "Browses and buys" "HTTP (no TLS configured)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md Internet -> frontend-proxy; envoy.tmpl.yaml"
                "trust.boundary.crossing" "yes"
            }
        }
        shopper -> shop.mobile "Uses" "mobile app" {
            properties {
                "origin" "Extracted"
                "provenance" "src/react-native-app/"
            }
        }
        shop.mobile -> shop.frontendProxy "Calls the shop API" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md react-native-app -> frontend-proxy"
                "trust.boundary.crossing" "yes"
            }
        }
        operator -> shop.frontendProxy "Opens flagd-ui, Grafana, Jaeger, load generator UI on the same listener" "HTTP" {
            properties {
                "origin" "Inferred"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
                "trust.boundary.crossing" "yes"
            }
        }
        shop.loadGenerator -> shop.frontendProxy "Generates synthetic traffic" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" ".env LOCUST_HOST, opentelemetry.io content/en/docs/demo/architecture.md"
            }
        }
        shop.loadGenerator -> shop.flagd "Reads loadGeneratorFloodHomepage" "HTTP (OFREP)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md load-generator -> flagd"
            }
        }
        shop.frontendProxy -> shop.frontend "Routes / to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.imageProvider "Routes /images/ to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.flagdUi "Routes /feature to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.chatbot "Routes /chatbot/ to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.grafana "Routes /grafana/ to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.jaeger "Routes /jaeger/ to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.loadGenerator "Routes /loadgen/ to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.otelCollector "Routes /otlp-http/ to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.telemetryDocs "Routes /telemetry/ to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.opampServer "Routes /opamp/ to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontendProxy -> shop.flagd "Routes /flagservice/ to" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend-proxy/envoy.tmpl.yaml"
            }
        }
        shop.frontend -> shop.ad "Calls GetAds" "gRPC, protobuf pb/demo.proto" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend/gateways/rpc/, opentelemetry.io content/en/docs/demo/architecture.md"
            }
        }
        shop.frontend -> shop.cart "Calls AddItem, GetCart, EmptyCart" "gRPC, protobuf pb/demo.proto" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend/gateways/rpc/, opentelemetry.io content/en/docs/demo/architecture.md"
            }
        }
        shop.frontend -> shop.currency "Calls Convert, GetSupportedCurrencies" "gRPC, protobuf pb/demo.proto" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend/gateways/rpc/, opentelemetry.io content/en/docs/demo/architecture.md"
            }
        }
        shop.frontend -> shop.checkout "Calls PlaceOrder" "gRPC, protobuf pb/demo.proto" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend/gateways/rpc/, opentelemetry.io content/en/docs/demo/architecture.md"
            }
        }
        shop.frontend -> shop.productCatalog "Calls ListProducts, GetProduct, SearchProducts" "gRPC, protobuf pb/demo.proto" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend/gateways/rpc/, opentelemetry.io content/en/docs/demo/architecture.md"
            }
        }
        shop.frontend -> shop.recommendation "Calls ListRecommendations" "gRPC, protobuf pb/demo.proto" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend/gateways/rpc/, opentelemetry.io content/en/docs/demo/architecture.md"
            }
        }
        shop.frontend -> shop.shipping "Gets a shipping quote" "HTTP, JSON" {
            properties {
                "origin" "Extracted"
                "provenance" "src/frontend/gateways/http/Shipping.gateway.ts"
            }
        }
        shop.checkout -> shop.cart "GetCart, EmptyCart" "gRPC, insecure credentials" {
            properties {
                "origin" "Extracted"
                "provenance" "src/checkout/main.go mustCreateClient, getUserCart, emptyUserCart"
            }
        }
        shop.checkout -> shop.productCatalog "GetProduct per cart item" "gRPC, insecure credentials" {
            properties {
                "origin" "Extracted"
                "provenance" "src/checkout/main.go prepOrderItems"
            }
        }
        shop.checkout -> shop.currency "Convert item prices and shipping cost" "gRPC, insecure credentials" {
            properties {
                "origin" "Extracted"
                "provenance" "src/checkout/main.go convertCurrency"
            }
        }
        shop.checkout -> shop.payment "Charge" "gRPC, insecure credentials" {
            properties {
                "origin" "Extracted"
                "provenance" "src/checkout/main.go chargeCard"
            }
        }
        shop.checkout -> shop.shipping "POST /get-quote, POST /ship-order" "HTTP, JSON, no client timeout" {
            properties {
                "origin" "Extracted"
                "provenance" "src/checkout/main.go quoteShipping, shipOrder, httpClient without Timeout"
            }
        }
        shop.checkout -> shop.email "POST /send_order_confirmation, 1 s timeout, failure only logged" "HTTP, JSON" {
            properties {
                "origin" "Extracted"
                "provenance" "src/checkout/main.go sendOrderConfirmation, emailRequestTimeout"
            }
        }
        shop.checkout -> shop.kafka "Publishes OrderResult to topic orders, waits for the producer success channel" "Kafka protocol, protobuf, PLAINTEXT, RequiredAcks NoResponse" {
            properties {
                "origin" "Extracted"
                "provenance" "src/checkout/main.go sendToPostProcessor, src/checkout/kafka/producer.go"
            }
        }
        shop.shipping -> shop.quote "Gets the shipping cost" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md shipping -> quote, .env QUOTE_ADDR"
            }
        }
        shop.recommendation -> shop.productCatalog "ListProducts" "gRPC" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md recommendation -> product-catalog"
            }
        }
        shop.productCatalog -> shop.astronomyDb "Reads products" "SQL, sslmode=disable" {
            properties {
                "origin" "Extracted"
                "provenance" "compose.yaml product-catalog DB_CONNECTION_STRING"
            }
        }
        shop.cart -> shop.valkeyCart "Stores carts" "RESP" {
            properties {
                "origin" "Extracted"
                "provenance" "src/cart/src/cartstore/ValkeyCartStore.cs, .env VALKEY_ADDR"
            }
        }
        shop.accounting -> shop.kafka "Polls orders (group accounting, auto commit)" "Kafka protocol, PLAINTEXT" {
            properties {
                "origin" "Extracted"
                "provenance" "src/accounting/Consumer.cs GroupId, EnableAutoCommit"
            }
        }
        shop.accounting -> shop.astronomyDb "Writes orders, order items, shipping" "SQL, Entity Framework" {
            properties {
                "origin" "Extracted"
                "provenance" "src/accounting/Consumer.cs SaveChanges, compose.full.yaml DB_CONNECTION_STRING"
            }
        }
        shop.fraudDetection -> shop.kafka "Polls orders (group fraud-detection)" "Kafka protocol, PLAINTEXT" {
            properties {
                "origin" "Extracted"
                "provenance" "src/fraud-detection/src/main/kotlin/frauddetection/main.kt"
            }
        }
        shop.ad -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.cart -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.checkout -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.productCatalog -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.email -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.shipping -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.payment -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.recommendation -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.fraudDetection -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.frontendProxy -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.agent -> shop.flagd "Evaluates feature flags" "gRPC (OpenFeature flagd provider)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md <service> -> flagd"
            }
        }
        shop.flagdUi -> shop.flagd "Writes the flag file that flagd reads (shared mount ./src/flagd)" "file" {
            properties {
                "origin" "Extracted"
                "provenance" "compose.yaml flagd and flagd-ui volumes"
            }
        }
        shop.chatbot -> shop.agent "Sends chat turns" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md chatbot -> agent"
            }
        }
        shop.agent -> shop.mcp "Calls shop tools" "HTTP (MCP)" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md agent -> mcp"
            }
        }
        shop.mcp -> shop.frontend "Calls the shop API" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry.io content/en/docs/demo/architecture.md mcp -> frontend"
            }
        }
        shop.agent -> llm "Calls the LLM" "HTTPS, API key" {
            properties {
                "origin" "Extracted"
                "provenance" "compose.agent.yaml LLM_BASE_URL, API_KEY, LLM_TLS_VERIFY"
                "trust.boundary.crossing" "yes"
            }
        }
        shop.frontend -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=frontend"
            }
        }
        shop.ad -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=ad"
            }
        }
        shop.cart -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=cart"
            }
        }
        shop.checkout -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=checkout"
            }
        }
        shop.currency -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=currency"
            }
        }
        shop.email -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=email"
            }
        }
        shop.payment -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=payment"
            }
        }
        shop.productCatalog -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=productCatalog"
            }
        }
        shop.quote -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=quote"
            }
        }
        shop.recommendation -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=recommendation"
            }
        }
        shop.shipping -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=shipping"
            }
        }
        shop.accounting -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=accounting"
            }
        }
        shop.fraudDetection -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=fraudDetection"
            }
        }
        shop.kafka -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=kafka"
            }
        }
        shop.flagd -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=flagd"
            }
        }
        shop.flagdUi -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=flagdUi"
            }
        }
        shop.frontendProxy -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=frontendProxy"
            }
        }
        shop.loadGenerator -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=loadGenerator"
            }
        }
        shop.agent -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=agent"
            }
        }
        shop.mcp -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=mcp"
            }
        }
        shop.chatbot -> shop.otelCollector "Sends traces, metrics and logs" "OTLP" {
            properties {
                "origin" "Extracted"
                "provenance" "compose*.yaml OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME=chatbot"
            }
        }
        shop.otelCollector -> shop.valkeyCart "Scrapes" "redis receiver" {
            properties {
                "origin" "Extracted"
                "provenance" "src/otel-collector/otelcol-config.yml receivers.redis"
            }
        }
        shop.otelCollector -> shop.astronomyDb "Scrapes metrics and query samples (monitoring_user)" "postgresql receiver, tls insecure" {
            properties {
                "origin" "Extracted"
                "provenance" "src/otel-collector/otelcol-config.yml receivers.postgresql"
            }
        }
        shop.otelCollector -> shop.imageProvider "Scrapes /status" "nginx receiver" {
            properties {
                "origin" "Extracted"
                "provenance" "src/otel-collector/otelcol-config.yml receivers.nginx"
            }
        }
        shop.otelCollector -> shop.jaeger "Exports traces" "OTLP gRPC, sending queue" {
            properties {
                "origin" "Extracted"
                "provenance" "otelcol-config-observability.yml otlp_grpc/jaeger"
            }
        }
        shop.otelCollector -> shop.prometheus "Exports metrics" "OTLP HTTP, sending queue" {
            properties {
                "origin" "Extracted"
                "provenance" "otelcol-config-observability.yml otlp_http/prometheus"
            }
        }
        shop.otelCollector -> shop.opensearch "Exports logs" "HTTP, sending queue" {
            properties {
                "origin" "Extracted"
                "provenance" "otelcol-config-observability.yml opensearch"
            }
        }
        shop.otelCollector -> shop.opampServer "Reports status, receives configuration" "OpAMP" {
            properties {
                "origin" "Extracted"
                "provenance" "otelcol-config-observability.yml extensions opamp"
            }
        }
        shop.otelCollector -> vendor "Exports telemetry (vendor fork only)" "OTLP" {
            properties {
                "origin" "Inferred"
                "provenance" "src/otel-collector/otelcol-config-extras.yml, README.md"
                "trust.boundary.crossing" "yes"
            }
        }
        shop.grafana -> shop.prometheus "Queries" "PromQL" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo grafana/provisioning/datasources/default.yaml"
            }
        }
        shop.grafana -> shop.jaeger "Queries" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo grafana/provisioning/datasources/jaeger.yaml"
            }
        }
        shop.grafana -> shop.opensearch "Queries" "HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo grafana/provisioning/datasources/opensearch.yaml"
            }
        }

        k8s = deploymentEnvironment "Kubernetes (Helm chart defaults)" {
            cluster = deploymentNode "Kubernetes cluster" "Any conformant cluster. Node count, zones and region are not set by the chart." "Kubernetes" {
                properties {
                    "origin" "Extracted"
                    "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo Chart.yaml 0.42.7, values.yaml default.schedulingRules affinity {}"
                    "trust.boundary" "cluster"
                }
                perspectives {
                    "VP06-RE-090" "Missing. No availability or recovery target in the repo, in opentelemetry.io docs/demo/requirements (system, architecture, application, opentelemetry) or in the chart. Searched completely. Finding C-05 (confirms V-07)." "Unassessable"
                    "VP06-RE-100" "Documented (values.yaml, Author). default.replicas 1 and no override for any of the 25 enabled components (firepit disabled); Kafka quorum 1@kafka; astronomy-db, valkey-cart single Deployment. Every node is a single point of failure for the checkout path. No target to measure against. Finding C-02." "Unsatisfactory"
                    "VP06-RE-110" "Documented (values.yaml, _objects.tpl). No redundant instances, affinity {}, no topology spread, no PodDisruptionBudget. Placement across hosts and zones is left to the scheduler. Rated Applicable, not Inapplicable: no redundancy is the finding here, not the reason to skip. Finding C-03." "Unsatisfactory"
                    "VP06-RE-120" "Documented. Compose defines healthchecks for most services, the Helm values define no livenessProbe or readinessProbe for any component, so Kubernetes restarts only on process exit. No failover (one replica). Finding C-04." "Unsatisfactory"
                    "VP06-RE-140" "Documented (code). External dependency LLM provider, optional, replaced by cassettes. Inside the deployment: email failure degrades gracefully (1 s timeout, logged); shipping and Kafka have no client timeout; a shipping failure after Charge leaves a charged order without compensation. Finding C-06." "Partially"
                    "VP06-RE-150" "Insufficient for a practice criterion (minimum Demonstrated). 21 fault flags exist (Documented) and run-telemetry-tests runs on PRs (Pipeline), but the tests check telemetry, not recovery. No failure or recovery test result. Finding C-07." "Unassessable"
                }
                frontendProxyPod = deploymentNode "Deployment frontend-proxy" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.frontend-proxy, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    perspectives {
                        "VP06-RE-100" "Documented. One replica of the only ingress, for the shop and every admin UI." "Unsatisfactory"
                    }
                    containerInstance shop.frontendProxy
                }
                frontendPod = deploymentNode "Deployment frontend" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.frontend, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.frontend
                }
                adPod = deploymentNode "Deployment ad" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.ad, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.ad
                }
                cartPod = deploymentNode "Deployment cart" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.cart, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.cart
                }
                checkoutPod = deploymentNode "Deployment checkout" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.checkout, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    perspectives {
                        "VP06-RE-100" "Documented. One replica of the only order orchestrator, initContainer waits for Kafka. Its loss stops every order." "Unsatisfactory"
                    }
                    containerInstance shop.checkout
                }
                currencyPod = deploymentNode "Deployment currency" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.currency, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.currency
                }
                emailPod = deploymentNode "Deployment email" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.email, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.email
                }
                paymentPod = deploymentNode "Deployment payment" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.payment, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.payment
                }
                productCatalogPod = deploymentNode "Deployment product-catalog" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.product-catalog, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.productCatalog
                }
                quotePod = deploymentNode "Deployment quote" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.quote, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.quote
                }
                recommendationPod = deploymentNode "Deployment recommendation" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.recommendation, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.recommendation
                }
                shippingPod = deploymentNode "Deployment shipping" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.shipping, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.shipping
                }
                accountingPod = deploymentNode "Deployment accounting" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.accounting, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.accounting
                }
                fraudDetectionPod = deploymentNode "Deployment fraud-detection" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.fraud-detection, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.fraudDetection
                }
                imageProviderPod = deploymentNode "Deployment image-provider" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.image-provider, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.imageProvider
                }
                loadGeneratorPod = deploymentNode "Deployment load-generator" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.load-generator, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.loadGenerator
                }
                telemetryDocsPod = deploymentNode "Deployment telemetry-docs" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.telemetry-docs, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.telemetryDocs
                }
                agentPod = deploymentNode "Deployment agent" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.agent, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.agent
                }
                mcpPod = deploymentNode "Deployment mcp" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.mcp, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.mcp
                }
                chatbotPod = deploymentNode "Deployment chatbot" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.chatbot, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.chatbot
                }
                opampServerPod = deploymentNode "Deployment opamp-server" "Kubernetes Deployment, replicas from default.replicas." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.opamp-server, default.replicas 1, templates/_objects.tpl kind Deployment"
                    }
                    containerInstance shop.opampServer
                }
                flagdPod = deploymentNode "Deployment flagd" "flagd with flagd-ui as a sidecar container in the same pod, sharing the flag file (volume config-rw)." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.flagd replicas 1, sidecarContainers flagd-ui"
                    }
                    containerInstance shop.flagd
                    containerInstance shop.flagdUi
                }
                kafkaPod = deploymentNode "Deployment kafka" "Single broker and controller. A Deployment, not a StatefulSet; no volume claim in the chart templates." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.kafka replicas 1, KAFKA_CONTROLLER_QUORUM_VOTERS 1@kafka:9093"
                    }
                    perspectives {
                        "VP06-RE-100" "Documented. One broker, one controller. Checkout waits for it at start (initContainer)." "Unsatisfactory"
                        "VP06-RE-130" "Inferred from the templates: no PersistentVolumeClaim, so the orders topic is lost when the pod is rescheduled. No backup." "Unsatisfactory"
                    }
                    containerInstance shop.kafka
                }
                astronomyDbPod = deploymentNode "Deployment astronomy-db" "PostgreSQL as a Deployment with an init ConfigMap; no volume claim in the chart templates." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.astronomy-db replicas 1, mountedConfigMaps postgresql-init"
                    }
                    perspectives {
                        "VP06-RE-100" "Documented. One instance, shared by product-catalog (read path) and accounting (write path)." "Unsatisfactory"
                        "VP06-RE-130" "Inferred from the templates: no PersistentVolumeClaim; products are re-seeded from init.sql, accounting orders are lost on reschedule. No backup or restore design." "Unsatisfactory"
                    }
                    containerInstance shop.astronomyDb
                }
                valkeyPod = deploymentNode "Deployment valkey-cart" "Valkey as a Deployment." "Kubernetes Deployment" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml components.valkey-cart replicas 1"
                    }
                    perspectives {
                        "VP06-RE-130" "Inferred: no volume claim, so carts are lost on restart. Acceptable for a cart only if stated; no target says so." "Partially"
                    }
                    containerInstance shop.valkeyCart
                }
                collectorDs = deploymentNode "DaemonSet otel-collector" "One collector per worker node (opentelemetry-collector subchart, mode daemonset)." "Kubernetes DaemonSet" "1..N" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml opentelemetry-collector.mode daemonset"
                    }
                    containerInstance shop.otelCollector
                }
                jaegerPod = deploymentNode "Jaeger (subchart)" "Jaeger with in-memory storage." "jaeger chart 4.13.1" 1 {
                    properties {
                        "origin" "Inferred"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo Chart.yaml dependency jaeger; instance count from subchart defaults, not read"
                    }
                    perspectives {
                        "VP06-RE-130" "Documented. storage.type memory, MEMORY_MAX_TRACES 25000: traces are lost on restart by design." "Partially"
                    }
                    containerInstance shop.jaeger
                }
                prometheusPod = deploymentNode "Prometheus (subchart)" "Prometheus server." "prometheus chart 29.30.2" 1 {
                    properties {
                        "origin" "Inferred"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo Chart.yaml dependency prometheus; instance count not read"
                    }
                    containerInstance shop.prometheus
                }
                grafanaPod = deploymentNode "Grafana (subchart)" "Grafana with provisioned dashboards." "grafana chart 13.2.5" 1 {
                    properties {
                        "origin" "Inferred"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo Chart.yaml dependency grafana; instance count not read"
                    }
                    containerInstance shop.grafana
                }
                opensearchPod = deploymentNode "OpenSearch (subchart)" "singleNode true, persistence disabled, security plugin disabled." "opensearch chart 3.8.0" 1 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "opentelemetry-helm-charts@5e7ca838 charts/opentelemetry-demo values.yaml opensearch.singleNode, persistence.enabled false, DISABLE_SECURITY_PLUGIN"
                    }
                    containerInstance shop.opensearch
                }
            }
            llmNode = deploymentNode "LLM endpoint" "Outside the cluster." "HTTPS" {
                properties {
                    "origin" "Extracted"
                    "provenance" "compose.agent.yaml LLM_BASE_URL"
                    "trust.boundary" "internet"
                }
                softwareSystemInstance llm
            }
        }
    }

    views {
        systemContext shop "context" "VP01 Context" {
            include *
            autoLayout lr
        }
        container shop "containers" "VP02 Functional, runtime elements and connectors" {
            include *
            autoLayout lr
        }
        container shop "observability" "VP07 Operational (in part): the telemetry pipeline" {
            include element.tag==Observability
            include ->shop.otelCollector->
            autoLayout lr
        }
        dynamic shop "checkout" "VP04 Concurrency (in part): one PlaceOrder, synchronous steps 3 to 14, asynchronous consumers after step 14" {
            shopper -> shop.frontendProxy "POST /api/checkout"
            shop.frontendProxy -> shop.frontend "Routes /"
            shop.frontend -> shop.checkout "PlaceOrder"
            shop.checkout -> shop.cart "GetCart"
            shop.checkout -> shop.productCatalog "GetProduct per item"
            shop.checkout -> shop.currency "Convert per item"
            shop.checkout -> shop.shipping "POST /get-quote"
            shop.shipping -> shop.quote "Quote"
            shop.checkout -> shop.currency "Convert shipping cost"
            shop.checkout -> shop.payment "Charge"
            shop.checkout -> shop.shipping "POST /ship-order (failure here leaves a charged order)"
            shop.checkout -> shop.cart "EmptyCart (error ignored)"
            shop.checkout -> shop.email "POST /send_order_confirmation (1 s, failure logged)"
            shop.checkout -> shop.kafka "Publish OrderResult to orders"
            {
                {
                    shop.accounting -> shop.kafka "Poll orders (group accounting)"
                    shop.accounting -> shop.astronomyDb "Insert order, skip duplicate"
                }
                {
                    shop.fraudDetection -> shop.kafka "Poll orders (group fraud-detection)"
                }
            }
            autoLayout lr
        }
        deployment shop k8s "deployment" "VP06 Deployment and VP07 Operational (in part)" {
            include *
            autoLayout lr
        }

        styles {
            element "Element" {
                shape roundedbox
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Database" {
                shape cylinder
            }
            element "Queue" {
                shape pipe
            }
            element "Person" {
                shape person
            }
        }
    }

    configuration {
        scope softwaresystem
    }
}
