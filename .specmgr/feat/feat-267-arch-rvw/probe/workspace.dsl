workspace "c4-probe" "Probe of the property, perspective, tag, docs and decision conventions of the Architecture Model TXT 30983f27, section 8. Task 120.110, issue 267." {

    !identifiers hierarchical
    !docs docs

    model {
        properties {
            "review.safety.relevant" "yes"
            "review.safety.justification" "Probe value: the system emits radio frequency energy."
            "origin" "Proposed"
            "provenance" "probe"
        }

        user = person "User" "A user of the shop." {
            properties {
                "origin" "Proposed"
                "provenance" "probe"
            }
        }

        partner = softwareSystem "Payment provider" "External system." {
            tags "External"
            properties {
                "origin" "Proposed"
                "provenance" "probe"
                "trust.boundary" "internet"
            }
        }

        shop = softwareSystem "Shop" "System under review." {
            properties {
                "origin" "Proposed"
                "provenance" "probe"
            }
            !docs docs
            !adrs adrs madr

            web = container "Web" "Web front end." "Java" {
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                    "trust.level" "public"
                }
                login = component "Login" "Authenticates users." "Java" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "probe"
                        "trust.level" "public"
                    }
                }
                admin = component "Admin console" "Back-office functions." "Java" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "probe"
                        "trust.level" "administrator"
                    }
                }
                plugin = component "Plugin host" "Loads third-party extensions." "Java" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "probe"
                        "trust.level" "plugin"
                    }
                }
                admin -> plugin "Loads extensions with" "function call" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "probe"
                    }
                }
                login -> admin "Hands over the session to" "function call" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "probe"
                    }
                }
            }
            db = container "Database" "Orders and users." "PostgreSQL" {
                tags "Database"
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                }
            }
            otel = container "Collector" "Receives telemetry." "OpenTelemetry Collector" {
                tags "Monitoring"
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                }
            }
            tx = container "Transmitter control" "Switches the transmitter. Part of safety function SF-1." "C, MCU" {
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                    "safety.function" "SF-1"
                }
            }
            power = container "Power control" "Switches the amplifier rails. Part of safety function SF-1." "C, MCU" {
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                    "safety.function" "SF-1"
                }
            }

            web -> db "Reads and writes orders" "JDBC" {
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                }
            }
            web -> otel "Sends traces" "OTLP" {
                tags "Telemetry"
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                }
            }
            db -> otel "Sends metrics" "OTLP" {
                tags "Telemetry"
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                }
            }
            tx -> power "Requests rail shutdown" "GPIO" {
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                    "safety.function" "SF-1"
                }
            }
        }

        user -> shop.web "Buys goods" "HTTPS" {
            properties {
                "origin" "Proposed"
                "provenance" "probe"
                "trust.boundary.crossing" "yes"
            }
        }
        shop.web -> partner "Charges the card" "HTTPS" {
            properties {
                "origin" "Proposed"
                "provenance" "probe"
                "trust.boundary.crossing" "yes"
            }
        }

        live = deploymentEnvironment "Live" {
            cluster = deploymentNode "Cluster" "Kubernetes cluster." "Kubernetes" {
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                    "failure.domain.region" "eu-1"
                    "trust.boundary" "cluster"
                }
                perspectives {
                    "VP06-RE-100" "Documented. Database has no replica. Rating for the environment." "Unsatisfactory"
                    "VP06-RE-110" "Documented. Pods placed by the scheduler, no spread rule." "Unsatisfactory"
                }
                zoneA = deploymentNode "Zone A" "Availability zone." "Cloud zone" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "probe"
                        "failure.domain.zone" "eu-1a"
                    }
                    webPod = deploymentNode "Web pod" "Placed by the scheduler." "Pod" {
                        instances 3
                        properties {
                            "origin" "Proposed"
                            "provenance" "probe"
                            "failure.domain.placement" "scheduler"
                        }
                        perspectives {
                            "VP06-RE-100" "Documented. Three replicas. Evidence for the environment rating." "Satisfactory"
                        }
                        webInstance = containerInstance shop.web
                    }
                    dbPod = deploymentNode "Database pod" "Pinned to one host." "Pod" {
                        properties {
                            "origin" "Proposed"
                            "provenance" "probe"
                            "failure.domain.placement" "fixed"
                            "failure.domain.host" "node-7"
                        }
                        perspectives {
                            "VP06-RE-100" "Documented. One replica, no failover. Evidence for the environment rating." "Unsatisfactory"
                        }
                        dbInstance = containerInstance shop.db
                    }
                    otelPod = deploymentNode "Collector pod" "Placed by the scheduler." "Pod" {
                        properties {
                            "origin" "Proposed"
                            "provenance" "probe"
                            "failure.domain.placement" "scheduler"
                        }
                        containerInstance shop.otel
                    }
                    lb = infrastructureNode "Load balancer" "Terminates TLS." "Ingress" {
                        properties {
                            "origin" "Proposed"
                            "provenance" "probe"
                            "trust.boundary" "dmz"
                        }
                    }
                }
            }
            device = deploymentNode "Radar head" "Field device." "MCU board" {
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                    "failure.domain.host" "radar-head-1"
                    "failure.domain.region" "eu-1"
                }
                containerInstance shop.tx
                containerInstance shop.power
            }
            live.cluster.zoneA.lb -> live.cluster.zoneA.webPod.webInstance "Routes requests to" "HTTPS" {
                properties {
                    "origin" "Proposed"
                    "provenance" "probe"
                }
            }
        }
    }

    views {
        systemContext shop "context" "VP01 Context" {
            include *
            properties {
                "viewpoint" "VP01"
            }
        }
        container shop "containers" "VP02 Functional, telemetry excluded" {
            include *
            exclude "relationship.tag==Telemetry"
            properties {
                "viewpoint" "VP02"
            }
        }
        container shop "monitoring" "VP07 Operational, telemetry only" {
            include *
            exclude "relationship.tag!=Telemetry"
            properties {
                "viewpoint" "VP07"
            }
        }
        component shop.web "components" "VP02 Functional" {
            include *
            properties {
                "viewpoint" "VP02"
            }
        }
        deployment shop live "deployment" "VP06 Deployment" {
            include *
            properties {
                "viewpoint" "VP06"
            }
        }

        styles {
            element "External" {
                background #999999
            }
            relationship "Telemetry" {
                dashed true
            }
        }
    }

    configuration {
        scope softwaresystem
    }
}
