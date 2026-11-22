workspace "Apache OFBiz" "Phase 120 validation run 2 (class: traditional enterprise application): Apache OFBiz, ofbiz-framework trunk at cdea248b (2026-11-22)" {

    !identifiers hierarchical

    model {
        properties {
            "review.safety.relevant" "no"
            "review.safety.justification" "A general-purpose ERP for accounting, order, product, party and manufacturing data. It controls no equipment, and it supports business decisions without a direct safety consequence. An installation that plans production of safety-relevant goods must decide again."
            "origin" "Extracted"
            "provenance" "ofbiz-framework@cdea248b: README.md, SECURITY.md, framework/component-load.xml, applications/component-load.xml"
        }

        backOffice = person "Back-office user" "An employee who works in the accounting, order, catalog, facility, party, manufacturing, marketing, humanres and workeffort webapps." {
            properties {
                "origin" "Extracted"
                "provenance" "applications/*/ofbiz-component.xml webapp elements with base-permission OFBTOOLS; README.md Visit OFBiz through your browser"
            }
        }

        administrator = person "Administrator" "Holds administrative permissions (ENTITY_MAINT, SERVICE_MAINT, SECURITY_ADMIN and others). Fully trusted: equivalent to code execution in the JVM." {
            properties {
                "origin" "Extracted"
                "provenance" "SECURITY.md Administrative Access"
            }
        }

        operator = person "Deployer and operator" "Builds, configures, starts and stops the installation. Responsible for host, network exposure, logs, plugins and integrations." {
            properties {
                "origin" "Extracted"
                "provenance" "SECURITY.md Security Assumptions, Network Exposure; README.md Production setup"
            }
        }

        apiClient = softwareSystem "API client" "Another system that calls the REST API with a JWT bearer token." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "framework/rest-api/ofbiz-component.xml mount-point /rest; framework/rest-api/src/main/java/org/apache/ofbiz/ws/rs/security/auth/APIAuthFilter.java; security.properties security.jwt.token.expireTime"
            }
        }

        mailServer = softwareSystem "SMTP relay" "Outgoing mail for notifications. Disabled by default (mail.notifications.enabled=N)." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "framework/common/config/general.properties mail.smtp.relay.host, mail.notifications.enabled"
            }
        }

        ldap = softwareSystem "LDAP directory" "Optional external authentication. Disabled by default (security.ldap.enable=false)." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "framework/security/config/security.properties security.ldap.enable"
            }
        }

        jmsBroker = softwareSystem "JMS broker" "Optional. Used for the distributed entity cache clear between instances. The configuration is commented out by default." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "framework/service/config/serviceengine.xml jms-service in comment; framework/entityext/servicedef/services.xml distributedClear* engine jms; entityengine.xml distributed-cache-clear-enabled=false"
            }
        }

        mavenRepos = softwareSystem "Dependency repositories" "Maven repositories and Gradle plugin portal. Needed on the first build; offline afterwards from the Gradle cache." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "README.md Running gradle tasks without an Internet connection; build.gradle repositories"
            }
        }

        ofbiz = softwareSystem "Apache OFBiz" "ERP framework and applications: accounting, order, product, party, content, workeffort, manufacturing, marketing, humanres. One JVM with embedded Tomcat, an entity engine and a service engine." {
            properties {
                "origin" "Extracted"
                "provenance" "README.md, repository description, framework/component-load.xml, applications/component-load.xml"
            }

            server = container "OFBiz server" "One JVM process (org.apache.ofbiz.base.start.Start). Loads 13 framework and 12 application components in the order of component-load.xml and mounts 21 webapps in one embedded Tomcat." "Java 25, embedded Tomcat, Groovy, FreeMarker" {
                properties {
                    "origin" "Extracted"
                    "provenance" "docs/asciidoc/developer-manual.adoc Main systems; build.gradle mainClass; framework/catalina/ofbiz-component.xml catalina-container; count of webapp elements in framework/*/ofbiz-component.xml and applications/*/ofbiz-component.xml (21)"
                }

                webFramework = component "Web framework" "Request controller, widget renderer (screens, forms, menus), session and login handling, CSRF and host-header checks, upload filtering." "Java, FreeMarker" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/webapp, framework/widget, framework/common; security.properties host-headers-allowed, csrf.defense.strategy, deniedWebShellTokens"
                    }
                }
                securityFw = component "Security framework" "User login, password hashing, permissions, impersonation, JWT and login secrets." "Java" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/security; security.properties password.encrypt.hash.type, security.disable.impersonation, security.token.key"
                    }
                }
                serviceEngine = component "Service engine" "Dispatches 3510 declared services by name to 12 engines (entity-auto, java, groovy, simple and others). Service ECA rules (321). Job poller with a database lease." "Java, mini-lang, Groovy" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/service/config/serviceengine.xml; tool count over */servicedef/*.xml (services 3510, eca 321)"
                    }
                }
                entityEngine = component "Entity engine" "Generic data access by entity name. Delegators map entity groups to datasources. Entity cache, entity ECA rules, field encryption." "Java, JDBC, DBCP, Geronimo TM" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/entity/config/entityengine.xml delegator default, group-map, connection-factory, transaction-factory"
                    }
                }
                dataModel = component "Data model" "Entity definitions of all applications in one component: 845 entities and 274 view entities in total." "XML entity definitions" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "applications/datamodel/README.adoc; tool count over */entitydef/*.xml"
                    }
                }
                applications = component "Business applications" "accounting, order, product, party, content, workeffort, manufacturing, marketing, humanres, securityext, commonext. Services, screens and Java or Groovy code per component." "Java, Groovy, XML" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "applications/component-load.xml"
                    }
                }
                webtools = component "Webtools" "Administration: entity data maintenance, entity import and export, SQL processor, program export, service and cache maintenance." "Java, Groovy" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/webtools/webapp/webtools/WEB-INF/controller.xml request-map EntitySQLProcessor, ProgramExport, EntityImport"
                    }
                }
                restApi = component "REST API" "Exposes services as REST resources under /rest with an OpenAPI description under /docs. JWT authentication filter." "Java, JAX-RS" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/rest-api/ofbiz-component.xml, framework/rest-api/src/main/java/org/apache/ofbiz/ws/rs/"
                    }
                }
                adminServer = component "Admin server" "Socket for status and shutdown commands. Disabled until ofbiz.admin.key is set." "Java socket" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/start/src/main/resources/org/apache/ofbiz/base/start/start.properties ofbiz.admin.port=10523, ofbiz.admin.key"
                    }
                }

                webFramework -> securityFw "Authenticates and authorises requests with" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/webapp/src/main/java/org/apache/ofbiz/webapp/control/LoginWorker.java"
                    }
                }
                webFramework -> serviceEngine "Calls services by name" "in-process dispatch" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "controller.xml event type service in the webapps"
                    }
                }
                restApi -> serviceEngine "Calls services by name" "in-process dispatch" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/rest-api/src/main/java/org/apache/ofbiz/ws/rs/"
                    }
                }
                webtools -> entityEngine "Reads, writes, imports and exports any entity" "in-process call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/webtools controller.xml EntityImport, EntitySQLProcessor"
                    }
                }
                applications -> serviceEngine "Define and call services" "in-process dispatch" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "applications/*/servicedef/*.xml, applications/*/ofbiz-component.xml service-resource"
                    }
                }
                applications -> entityEngine "Read and write entities by name" "in-process call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "applications/*/src/main/java imports of org.apache.ofbiz.entity (tool check, see validation record)"
                    }
                }
                serviceEngine -> entityEngine "Persists jobs and runs entity-auto services through" "in-process call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "serviceengine.xml engine entity-auto, thread-pool poll-db-millis and lease-*"
                    }
                }
                entityEngine -> dataModel "Loads the entity definitions of" "XML read at start" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "applications/datamodel/ofbiz-component.xml entity-resource; entityengine.xml entity-model-reader main"
                    }
                }
                securityFw -> entityEngine "Reads user logins and permissions through" "in-process call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "framework/security/entitydef/entitymodel.xml, framework/common/entitydef/entitymodel.xml UserLoginHistory"
                    }
                }
            }

            buildTool = container "Gradle build and admin tasks" "Build, distTar, loadAll, createTenant, loadTenant, generateSecretKeys, rotateSecretKeys, OWASP check. Runs in its own JVM and ends." "Gradle 9 wrapper, Groovy DSL" {
                properties {
                    "origin" "Extracted"
                    "provenance" "build.gradle tasks; gradle/wrapper/gradle-wrapper.properties gradle-9.8.2; README.md Quick reference, Data loading tasks, Create a new tenant"
                }
            }

            mainDb = container "Main database" "Entity group org.apache.ofbiz: all business and framework data. Default embedded H2 file database; PostgreSQL, MySQL and other datasources are predefined." "RDBMS (H2 default, PostgreSQL in the Docker example)" {
                tags "Database"
                properties {
                    "origin" "Extracted"
                    "provenance" "entityengine.xml group-map org.apache.ofbiz -> localh2, datasource elements; docker/templates/postgres-entityengine.xml"
                }
            }
            olapDb = container "OLAP database" "Entity group org.apache.ofbiz.olap: reporting star schema." "RDBMS" {
                tags "Database"
                properties {
                    "origin" "Extracted"
                    "provenance" "entityengine.xml group-map org.apache.ofbiz.olap -> localh2olap; DOCKER.adoc OFBIZ_POSTGRES_OLAP_DB"
                }
            }
            tenantDb = container "Tenant database" "Entity group org.apache.ofbiz.tenant: Tenant, TenantDataSource, TenantDomainName, TenantKeyEncryptingKey. Locates the database of each tenant when multitenant=Y." "RDBMS" {
                tags "Database"
                properties {
                    "origin" "Extracted"
                    "provenance" "entityengine.xml group-map org.apache.ofbiz.tenant; framework/entity/entitydef/entitymodel.xml Tenant*; general.properties multitenant=N; README.md Create a new tenant"
                }
            }
            runtimeFs = container "Runtime files" "runtime/: logs (access log, application log, may hold sensitive data), uploads, tmp, H2 data files, Lucene indexes, Tomcat work files." "Filesystem" {
                tags "Database"
                properties {
                    "origin" "Extracted"
                    "provenance" "runtime/ directory tree; catalina access-log-dir runtime/logs; security.properties content.data.local.file.allowed.paths; SECURITY.md Logging and Sensitive Information"
                }
            }
        }

        backOffice -> ofbiz.server.webFramework "Uses the back-office webapps" "HTTPS 8443 (HTTP 8080 for non-secure requests)" {
            properties {
                "origin" "Extracted"
                "provenance" "framework/catalina/ofbiz-component.xml connectors 8080 and 8443"
                "trust.boundary.crossing" "yes"
            }
        }
        administrator -> ofbiz.server.webtools "Maintains data, services, caches and security" "HTTPS 8443" {
            properties {
                "origin" "Extracted"
                "provenance" "SECURITY.md Administrative Access; framework/webtools/ofbiz-component.xml mount-point /webtools"
                "trust.boundary.crossing" "yes"
            }
        }
        operator -> ofbiz.buildTool "Builds, loads data, creates tenants, generates secret keys" "shell" {
            properties {
                "origin" "Extracted"
                "provenance" "README.md Quick start, Production setup"
            }
        }
        operator -> ofbiz.server.adminServer "Gets status and shuts down" "TCP 127.0.0.1:10523 with admin key" {
            properties {
                "origin" "Extracted"
                "provenance" "start.properties; README.md Shutdown OFBiz, Get OFBiz status"
            }
        }
        apiClient -> ofbiz.server.restApi "Calls services" "HTTPS, REST, JWT" {
            properties {
                "origin" "Extracted"
                "provenance" "framework/rest-api; security.properties security.jwt.*"
                "trust.boundary.crossing" "yes"
            }
        }
        ofbiz.server.entityEngine -> ofbiz.mainDb "Reads and writes business data" "JDBC, DBCP pool max 250, ReadCommitted" {
            properties {
                "origin" "Extracted"
                "provenance" "entityengine.xml datasource localh2 inline-jdbc pool-maxsize, isolation-level"
            }
        }
        ofbiz.server.entityEngine -> ofbiz.olapDb "Reads and writes reporting data" "JDBC" {
            properties {
                "origin" "Extracted"
                "provenance" "entityengine.xml group-map org.apache.ofbiz.olap"
            }
        }
        ofbiz.server.entityEngine -> ofbiz.tenantDb "Resolves the tenant delegator and datasource" "JDBC" {
            properties {
                "origin" "Extracted"
                "provenance" "framework/webapp/src/main/java/org/apache/ofbiz/webapp/control/ContextFilter.java TenantDomainName lookup"
            }
        }
        ofbiz.server.webFramework -> ofbiz.runtimeFs "Writes access logs and uploads" "file I/O" {
            properties {
                "origin" "Extracted"
                "provenance" "catalina access-log-dir runtime/logs; general.properties http.upload.tmprepository runtime/tmp"
            }
        }
        ofbiz.server.serviceEngine -> mailServer "Sends notification mail" "SMTP" {
            properties {
                "origin" "Extracted"
                "provenance" "general.properties mail.smtp.relay.host=localhost, mail.notifications.enabled=N"
                "trust.boundary.crossing" "yes"
            }
        }
        ofbiz.server.securityFw -> ldap "Authenticates users against (optional)" "LDAP" {
            properties {
                "origin" "Extracted"
                "provenance" "security.properties security.ldap.enable=false"
                "trust.boundary.crossing" "yes"
            }
        }
        ofbiz.server.serviceEngine -> jmsBroker "Publishes distributed cache clear messages (optional)" "JMS topic" {
            properties {
                "origin" "Extracted"
                "provenance" "serviceengine.xml jms-service (commented); framework/entityext/servicedef/services.xml distributedClearAllEntityCaches"
                "trust.boundary.crossing" "yes"
            }
        }
        ofbiz.buildTool -> mavenRepos "Downloads dependencies and plugins" "HTTPS" {
            properties {
                "origin" "Extracted"
                "provenance" "README.md Running gradle tasks without an Internet connection, Pull a plugin automatically"
                "trust.boundary.crossing" "yes"
            }
        }
        ofbiz.buildTool -> ofbiz.mainDb "Loads seed, demo and tenant data" "JDBC through the entity engine" {
            properties {
                "origin" "Extracted"
                "provenance" "README.md Data loading tasks (loadAll, loadTenant, --load-data)"
            }
        }

        dockerDemo = deploymentEnvironment "Docker postgres-demo" {
            dockerHost = deploymentNode "Docker host" "One host with Docker Compose. The example of the project, with demo data and a self-signed certificate." "Docker Compose" {
                properties {
                    "origin" "Extracted"
                    "provenance" "docker/examples/postgres-demo/docker-compose.yml"
                    "failure.domain.host" "docker-host"
                    "trust.boundary" "deployer-network"
                }
                perspectives {
                    "VP06-RE-090" "Missing. No availability or recovery target in README.md, DOCKER.adoc, SECURITY.md or docs/ (searched for availability, SLA, RTO, RPO). SECURITY.md puts the infrastructure with the deployer." "Unassessable"
                    "VP06-RE-100" "Demonstrated (Tool: recorded read of docker-compose.yml, two services, no replicas, no restart policy). Every node is a single point of failure. The effect on a target cannot be shown, because there is no target." "Partially"
                    "VP06-RE-110" "Insufficient. Multi-instance support exists only as commented configuration (Tomcat DeltaManager cluster, JMS cache clear) and the DB job lease. No deployment with redundancy is described." "Unassessable"
                    "VP06-RE-120" "Demonstrated (Tool: no HEALTHCHECK in Dockerfile or docker-compose.yml, no restart key for ofbiz, db restart no). No failure detection and no failover are defined for the reference deployment." "Unsatisfactory"
                    "VP06-RE-130" "Missing. State is in PostgreSQL and in runtime/ volumes. No backup or restore description in the repository (searched README.md, DOCKER.adoc, docker/)." "Unassessable"
                    "VP06-RE-140" "Insufficient. The database is mandatory; SMTP, LDAP and JMS are optional and off by default (Documented). The behaviour when the database is unavailable is not described or tested." "Unassessable"
                    "VP06-RE-150" "Missing. No failure or recovery test found. CI runs unit and integration tests only (.github/workflows/gradle.yml)." "Unassessable"
                }

                ofbizCt = deploymentNode "ofbiz container" "Image ofbiz-docker, runs as user ofbiz, mem_limit 1600M. Publishes 8443. The image also exposes 8009 (AJP) and 5005 (debug)." "eclipse-temurin:25" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Dockerfile EXPOSE 8443 8009 5005, USER ofbiz; docker-compose.yml ports 8443:8443"
                        "trust.boundary" "application"
                    }
                    serverInst = containerInstance ofbiz.server
                    containerInstance ofbiz.runtimeFs
                }
                dbCt = deploymentNode "db container" "PostgreSQL 13 with three databases: ofbiz, ofbizolap, ofbiztenant. mem_limit 300M." "postgres:13" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "docker-compose.yml service db; DOCKER.adoc OFBIZ_POSTGRES_*_DB"
                        "trust.boundary" "data"
                    }
                    containerInstance ofbiz.mainDb
                    containerInstance ofbiz.olapDb
                    containerInstance ofbiz.tenantDb
                }
                proxy = infrastructureNode "Reverse proxy and firewall" "Recommended by SECURITY.md to control access to public, internal and administrative endpoints. Not part of the example." "Not specified" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "SECURITY.md Network Exposure"
                        "trust.boundary" "perimeter"
                    }
                }
                proxy -> ofbizCt.serverInst "Forwards filtered HTTPS requests to" "HTTPS 8443" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "SECURITY.md Network Exposure (firewalls, reverse proxies, network segmentation)"
                        "trust.boundary.crossing" "yes"
                    }
                }
            }
        }
    }

    views {
        systemContext ofbiz "context" "VP01 Context" {
            include *
            autoLayout lr
        }
        container ofbiz "containers" "VP02 Functional, structure of the runtime elements, and VP03 Information (stores only)" {
            include *
            autoLayout lr
        }
        component ofbiz.server "components" "VP02 Functional and VP05 Development (in part)" {
            include *
            autoLayout lr
        }
        deployment ofbiz dockerDemo "deployment" "VP06 Deployment and VP07 Operational (in part)" {
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
        }
    }

    configuration {
        scope softwaresystem
    }
}
