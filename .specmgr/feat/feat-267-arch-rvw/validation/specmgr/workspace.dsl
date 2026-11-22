workspace "specmgr" "Phase 120 validation run 1 (extra class: local tool): specmgr itself (baseline feat-267-arch-rvw, 2026-11-22)" {

    !identifiers hierarchical

    model {
        properties {
            "review.safety.relevant" "no"
            "review.safety.justification" "A local document manager for specifications. It controls no equipment and no decision with a direct safety consequence."
            "origin" "Extracted"
            "provenance" "AGENTS.md, pyproject.toml, server.py, commands/mcp.py, _envregistry.py"
        }

        author = person "Author" "A requirements engineer, architect or developer who writes and reviews specification documents." {
            properties {
                "origin" "Extracted"
                "provenance" "README.md, AGENTS.md Project Shape"
            }
        }

        agentHost = softwareSystem "Agent harness" "An MCP host with an LLM agent, for example OpenCode or Claude Code. Calls the specmgr tools, reads resources and prompts." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "README.md Add to OpenCode, .opencode/"
            }
        }

        plantumlSrv = softwareSystem "PlantUML source" "A PlantUML jar, binary or server. Optional. First set wins: SPECMGR_PLANTUML_JAR, _BIN, _URL." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "plantuml/chain.py, _envregistry.py"
            }
        }

        modelHub = softwareSystem "Embedding model source" "The download source of the fastembed bge-small model. Only with the similarity extra, on first use." {
            tags "External"
            properties {
                "origin" "Inferred"
                "provenance" "general/tools/_similarity_search.py uses fastembed; fastembed downloads the model when the cache is empty"
            }
        }

        git = softwareSystem "Git repository" "The repository that holds the documents. Versioning, review and history of the documents are done with git, not by specmgr." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "AGENTS.md Development Artifacts, DEC 33c5ab08 filesystem is the sole source of truth"
            }
        }

        specmgr = softwareSystem "specmgr" "Artifact manager for system specifications: schema-validated markdown documents of 14 types, served to agents over MCP and to people over a CLI." {
            properties {
                "origin" "Extracted"
                "provenance" "AGENTS.md, pyproject.toml"
            }

            mcpServer = container "MCP server" "Registers the tools, resources and prompts listed in docs/MCP.md. Parses, validates, lists, updates and renders documents. One process per host session." "Python 3.11+, mcp SDK, pydantic" {
                properties {
                    "origin" "Extracted"
                    "provenance" "server.py, commands/mcp.py"
                }

                domains = component "Domain packages" "One package per document type (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs, txt, set): tools, resources, prompts, versioned models." "Python" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "src/biz/dfch/specmgr/<domain>/"
                    }
                }
                generic = component "Generic tools" "update, edit, set_status, set_classification, delete, validate, list_references, diagrams, i18n. Dispatch by type to the domain adapters." "Python" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "general/tools/"
                    }
                }
                mdEngine = component "Markdown model engine" "Parses markdown with YAML frontmatter into pydantic models. Shared section building blocks." "Python, markdown-it, pydantic" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "models/md/"
                    }
                }
                cache = component "Document cache" "Process-local, per domain, validated by the content hash on every access. Plus a frontmatter-only stage for feat." "Python" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "general/tools/_doc_cache.py, feat/tools/_cache.py"
                    }
                }
                warmup = component "Startup warmup" "One daemon thread: feat frontmatter, feat full parse, similarity index." "Python thread" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "general/tools/_startup_warmup.py"
                    }
                }
                similarity = component "Similarity search" "find_related, find_similar_text over local sentence embeddings. Optional extra." "fastembed" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "general/tools/_similarity_search.py"
                    }
                }
                plantumlLib = component "PlantUML library" "Import-free: encoder, structure checker, validation chain over jar, bin or URL." "Python stdlib" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "plantuml/"
                    }
                }

                generic -> domains "Dispatches to the adapter of" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "general/tools/update.py _ADAPTERS"
                    }
                }
                domains -> mdEngine "Parses and validates with" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "<domain>/models/v*/parser.py"
                    }
                }
                domains -> cache "Reads through" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "<domain>/tools/_cache.py"
                    }
                }
                warmup -> cache "Fills" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "feat/tools/_warmup.py"
                    }
                }
                warmup -> similarity "Builds the index of" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "general/tools/_startup_warmup.py"
                    }
                }
                domains -> plantumlLib "Renders and checks diagrams with" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "uc/tools/validate_plantuml.py"
                    }
                }
            }

            cli = container "CLI" "specmgr command: mcp, lint, docs, diagram, plantuml-check, harness-bundle, version. Several commands import the MCP server code in-process." "Python, Typer" {
                properties {
                    "origin" "Extracted"
                    "provenance" "cli.py, commands/"
                }
            }

            docStore = container "Document store" "Markdown files with YAML frontmatter: docs/{type}/[{language}/]{type}-{uuid}-{slug}.md and .specmgr/feat/{id}/README.md. The filesystem is the only source of truth." "Filesystem" {
                tags "Database"
                properties {
                    "origin" "Extracted"
                    "provenance" "general/tools/_doc_paths.py, feat/tools/_paths.py, SPECMGR_DOCS_DIR, SPECMGR_FEAT_DIR"
                }
            }

            modelCache = container "Embedding model cache" "Local copy of the bge-small model and its files." "Filesystem" {
                tags "Database"
                properties {
                    "origin" "Extracted"
                    "provenance" "FASTEMBED_CACHE_PATH in _envregistry.py"
                }
            }
        }

        author -> agentHost "Works through" "chat" {
            properties {
                "origin" "Extracted"
                "provenance" "README.md"
            }
        }
        author -> specmgr.cli "Runs" "shell" {
            properties {
                "origin" "Extracted"
                "provenance" "README.md, AGENTS.md CLI"
            }
        }
        agentHost -> specmgr.mcpServer "Calls tools, reads resources and prompts" "MCP over stdio, SSE or streamable HTTP" {
            properties {
                "origin" "Extracted"
                "provenance" "commands/mcp.py --transport"
            }
        }
        agentHost -> specmgr.docStore "Reads and writes files directly (feat plans, repair)" "host file tools" {
            properties {
                "origin" "Extracted"
                "provenance" "general prompt repair, AGENTS.md feat bullet"
            }
        }
        specmgr.cli -> specmgr.mcpServer "Starts (mcp) or imports in-process (lint, diagram)" "process start, Python import" {
            properties {
                "origin" "Extracted"
                "provenance" "commands/mcp.py, commands/lint.py, commands/diagram.py"
            }
        }
        specmgr.mcpServer.domains -> specmgr.docStore "Reads and writes documents" "file I/O, per-domain thread lock" {
            properties {
                "origin" "Extracted"
                "provenance" "general/tools/_lock.py, general/tools/_doc_paths.py"
            }
        }
        specmgr.mcpServer.similarity -> specmgr.modelCache "Loads the model from" "file I/O" {
            properties {
                "origin" "Extracted"
                "provenance" "general/tools/_similarity_search.py"
            }
        }
        specmgr.mcpServer.similarity -> modelHub "Downloads the model on first use" "HTTPS" {
            properties {
                "origin" "Inferred"
                "provenance" "fastembed behaviour with an empty cache; not read in the specmgr code"
                "trust.boundary.crossing" "yes"
            }
        }
        specmgr.mcpServer.plantumlLib -> plantumlSrv "Validates and renders diagrams" "subprocess (jar, bin) or HTTPS (URL)" {
            properties {
                "origin" "Extracted"
                "provenance" "plantuml/backends.py, plantuml/url.py"
                "trust.boundary.crossing" "yes"
            }
        }
        author -> git "Commits, reviews and merges documents" "git" {
            properties {
                "origin" "Extracted"
                "provenance" "AGENTS.md pre-commit, specmgr lint hook"
            }
        }
        git -> specmgr.docStore "Holds the working tree of" "filesystem" {
            properties {
                "origin" "Extracted"
                "provenance" "docs/ and .specmgr/ are tracked files"
            }
        }

        workstation = deploymentEnvironment "Workstation" {
            laptop = deploymentNode "Developer workstation" "One machine of one author. Linux, macOS or Windows." "Any OS" {
                properties {
                    "origin" "Extracted"
                    "provenance" "README.md install sections"
                    "failure.domain.host" "workstation"
                    "trust.boundary" "user"
                }
                perspectives {
                    "VP06-RE-100" "Documented. One host, one process per harness session, no replica. Single point of failure for the author's own work only. No availability target is stated, so the effect on a target cannot be judged." "Partially"
                    "VP06-RE-110" "Documented. One failure domain (the workstation). No redundancy, so no placement question." "Inapplicable"
                    "VP06-RE-130" "Documented. All state is markdown in the git working tree. Backup and restore are git push and clone. No recovery target is stated." "Partially"
                }

                harness = deploymentNode "Agent harness process" "The MCP host. Starts the specmgr process over stdio and owns its lifetime." "OpenCode, Claude Code" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "README.md Add to OpenCode"
                    }
                    softwareSystemInstance agentHost
                }
                server = deploymentNode "specmgr MCP process" "Started by the harness over stdio, or run as a local HTTP server. Installed with uvx or pip from PyPI." "Python 3.11 to 3.13" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "commands/mcp.py, README.md, .github/workflows/publish.yml"
                    }
                    containerInstance specmgr.mcpServer
                }
                shell = deploymentNode "Shell" "Runs one CLI command and ends. Also the pre-commit hooks and CI." "bash, zsh, PowerShell" {
                    properties {
                        "origin" "Inferred"
                        "provenance" "Typer CLI entry point specmgr"
                    }
                    containerInstance specmgr.cli
                }
                fs = deploymentNode "Local filesystem" "The git working tree with the documents, and the model cache." "Any filesystem" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "SPECMGR_DOCS_DIR default docs/ under the current directory"
                    }
                    containerInstance specmgr.docStore
                    containerInstance specmgr.modelCache
                }
            }
            remote = deploymentNode "Git hosting" "Remote repository, pull requests and CI." "GitHub" {
                properties {
                    "origin" "Extracted"
                    "provenance" "github.com/dfch/biz.dfch.SpecMgr, .github/workflows/"
                    "failure.domain.region" "github"
                    "trust.boundary" "internet"
                }
                softwareSystemInstance git
            }
        }
    }

    views {
        systemContext specmgr "context" "VP01 Context" {
            include *
            autoLayout lr
        }
        container specmgr "containers" "VP02 Functional, structure of the runtime elements" {
            include *
            autoLayout lr
        }
        component specmgr.mcpServer "components" "VP02 Functional and VP05 Development (in part)" {
            include *
            autoLayout lr
        }
        deployment specmgr workstation "deployment" "VP06 Deployment and VP07 Operational (in part)" {
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
