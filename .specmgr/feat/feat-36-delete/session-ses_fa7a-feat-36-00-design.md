# Feature 36 delete design & worktree plan

**Session ID:** ses_fa7a047ceffe063N5AanMXG8LX
**Created:** 8/31/2026, 5:11:03 PM
**Updated:** 8/31/2026, 6:10:40 PM

______________________________________________________________________

## User

I want to create and design a new feature. but not yet implement it. See https://github.com/dfch/biz.dfch.SpecMgr/issues/36

Examine what we want to do. How this can be done and make a plan.

I want the feature in a separate git worktree branch. There is already a sibling dir for that. The branch and feature name is "feat-36-delete".

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 15.0s)

_Thinking:_

Let's start by understanding the task. The user wants to create and design a new feature (not implement it yet). I'll refer to the GitHub issue at https://github.com/dfch/biz.dfch.SpecMgr/issues/36. What the user wants is:

1. Investigate what they want to do
2. How it can be done, and create a plan
3. Place the feature in a separate git worktree branch. There is already a sibling directory for that purpose.
4. The branch and feature name is "feat-36-delete"

I'm currently in plan mode, so I'm read-only. Let me first fetch the GitHub issue and investigate the codebase.

Let me start with parallel actions:

1. Fetch the GitHub issue
2. Investigate the current git state
3. Look at sibling directories
4. Investigate the structure of existing features

Let me execute these.

Wait, plan mode is read-only. Let me confirm — fetching a GitHub issue is read-only, so that's fine. Checking git state is read-only, so that's fine too. Let's proceed.

Let me start with multiple parallel calls.

I'll start by examining the GitHub issue and the current state of the repository.

**Tool: webfetch**

**Input:**

```json
{
  "url": "https://github.com/dfch/biz.dfch.SpecMgr/issues/36",
  "format": "markdown"
}
```

**Output:**

```
                                                                                                                                                         Replace domain specific delete with generic delete tool · Issue #36 · dfch/biz.dfch.SpecMgr · GitHub                                              

[Skip to content](#start-of-content)    

           

## Navigation Menu

[](/)

[Sign in](/login?return_to=https%3A%2F%2Fgithub.com%2Fdfch%2Fbiz.dfch.SpecMgr%2Fissues%2F36)

Appearance settings

-   Platform
    
    -   AI CODE CREATION
        
        -   [GitHub CopilotWrite better code with AI](https://github.com/features/copilot)
        -   [GitHub Copilot appDirect agents from issue to merge](https://github.com/features/ai/github-app)
        -   [MCP RegistryIntegrate external tools](https://github.com/mcp)
        
    -   DEVELOPER WORKFLOWS
        
        -   [ActionsAutomate any workflow](https://github.com/features/actions)
        -   [CodespacesInstant dev environments](https://github.com/features/codespaces)
        -   [IssuesPlan and track work](https://github.com/features/issues)
        -   [Code ReviewManage code changes](https://github.com/features/code-review)
        -   [Code QualityEnforce quality at merge](https://github.com/features/code-quality)
        
    -   APPLICATION SECURITY
        
        -   [GitHub Advanced SecurityFind and fix vulnerabilities](https://github.com/security/advanced-security)
        -   [Code securitySecure your code as you build](https://github.com/security/advanced-security/code-security)
        -   [Secret protectionStop leaks before they start](https://github.com/security/advanced-security/secret-protection)
        
    -   EXPLORE
        
        -   [Why GitHub](https://github.com/why-github)
        -   [Documentation](https://docs.github.com)
        -   [Blog](https://github.blog)
        -   [Changelog](https://github.blog/changelog)
        -   [Marketplace](https://github.com/marketplace)
        
    
    [View all features](https://github.com/features)
    
-   Solutions
    
    -   BY COMPANY SIZE
        
        -   [Enterprises](https://github.com/enterprise)
        -   [Small and medium teams](https://github.com/team)
        -   [Startups](https://github.com/enterprise/startups)
        -   [Nonprofits](https://github.com/solutions/industry/nonprofits)
        
    -   BY USE CASE
        
        -   [App Modernization](https://github.com/solutions/use-case/app-modernization)
        -   [DevSecOps](https://github.com/solutions/use-case/devsecops)
        -   [DevOps](https://github.com/solutions/use-case/devops)
        -   [CI/CD](https://github.com/solutions/use-case/ci-cd)
        -   [View all use cases](https://github.com/solutions/use-case)
        
    -   BY INDUSTRY
        
        -   [Healthcare](https://github.com/solutions/industry/healthcare)
        -   [Financial services](https://github.com/solutions/industry/financial-services)
        -   [Manufacturing](https://github.com/solutions/industry/manufacturing)
        -   [Government](https://github.com/solutions/industry/government)
        -   [View all industries](https://github.com/solutions/industry)
        
    
    [View all solutions](https://github.com/solutions)
    
-   Resources
    
    -   EXPLORE BY TOPIC
        
        -   [AI](https://github.com/resources/articles?topic=ai)
        -   [Software Development](https://github.com/resources/articles?topic=software-development)
        -   [DevOps](https://github.com/resources/articles?topic=devops)
        -   [Security](https://github.com/resources/articles?topic=security)
        -   [View all topics](https://github.com/resources/articles)
        
    -   EXPLORE BY TYPE
        
        -   [Customer stories](https://github.com/customer-stories)
        -   [Events & webinars](https://github.com/resources/events)
        -   [Ebooks & reports](https://github.com/resources/whitepapers)
        -   [Business insights](https://github.com/solutions/executive-insights)
        -   [GitHub Skills](https://skills.github.com)
        
    -   SUPPORT & SERVICES
        
        -   [Documentation](https://docs.github.com)
        -   [Customer support](https://support.github.com)
        -   [Community forum](https://github.com/orgs/community/discussions)
        -   [Trust center](https://github.com/trust-center)
        -   [Partners](https://github.com/partners)
        
    
    [View all resources](https://github.com/resources)
    
-   Open Source
    
    -   COMMUNITY
        
        -   [GitHub SponsorsFund open source developers](https://github.com/open-source/sponsors)
        
    -   PROGRAMS
        
        -   [Security Lab](https://securitylab.github.com)
        -   [Maintainer Community](https://maintainers.github.com)
        -   [GitHub Stars](https://stars.github.com)
        -   [Archive Program](https://archiveprogram.github.com)
        
    -   REPOSITORIES
        
        -   [Topics](https://github.com/topics)
        -   [Trending](https://github.com/trending)
        -   [Collections](https://github.com/collections)
        
    
-   Enterprise
    
    -   ENTERPRISE SOLUTIONS
        
        -   [Enterprise platformAI-powered developer platform](https://github.com/enterprise)
        
    -   AVAILABLE ADD-ONS
        
        -   [GitHub Advanced SecurityEnterprise-grade security features](https://github.com/security/advanced-security)
        -   [Copilot for BusinessEnterprise-grade AI features](https://github.com/features/copilot/copilot-business)
        -   [Premium SupportEnterprise-grade 24/7 support](https://github.com/enterprise/premium-support)
        
    
-   [Pricing](https://github.com/pricing)

Search/

[Sign in](/login?return_to=https%3A%2F%2Fgithub.com%2Fdfch%2Fbiz.dfch.SpecMgr%2Fissues%2F36)

[Sign up](/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F%3Cuser-name%3E%2F%3Crepo-name%3E%2Fvoltron%2Fissues_fragments%2Fissue_layout&source=header-repo&source_repo=dfch%2Fbiz.dfch.SpecMgr)

Appearance settings

You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert

[dfch](/dfch) / **[biz.dfch.SpecMgr](/dfch/biz.dfch.SpecMgr)** Public

-   [Notifications](/login?return_to=%2Fdfch%2Fbiz.dfch.SpecMgr) You must be signed in to change notification settings
-   [Fork 0](/login?return_to=%2Fdfch%2Fbiz.dfch.SpecMgr)
-   [Star 1](/login?return_to=%2Fdfch%2Fbiz.dfch.SpecMgr)
    

-   [Code](/dfch/biz.dfch.SpecMgr)
-   [Issues 6](/dfch/biz.dfch.SpecMgr/issues)
-   [Pull requests 0](/dfch/biz.dfch.SpecMgr/pulls)
-   [Actions](/dfch/biz.dfch.SpecMgr/actions)
-   [Projects](/dfch/biz.dfch.SpecMgr/projects)
-   [Security and quality 0](/dfch/biz.dfch.SpecMgr/security)
-   [Insights](/dfch/biz.dfch.SpecMgr/pulse)

Additional navigation options

-   [Code](/dfch/biz.dfch.SpecMgr)
-   [Issues](/dfch/biz.dfch.SpecMgr/issues)
-   [Pull requests](/dfch/biz.dfch.SpecMgr/pulls)
-   [Actions](/dfch/biz.dfch.SpecMgr/actions)
-   [Projects](/dfch/biz.dfch.SpecMgr/projects)
-   [Security and quality](/dfch/biz.dfch.SpecMgr/security)
-   [Insights](/dfch/biz.dfch.SpecMgr/pulse)

# Replace domain specific delete with generic delete tool #36

New issue

Copy link

New issue

Copy link

Open

Open

[Replace domain specific delete with generic delete tool](#top)#36

Copy link

## Description

[![@dfch](https://avatars.githubusercontent.com/u/8310360?u=ed8e0a6057780ebb162ba768467675a5070878ea&v=4&size=48)](https://github.com/dfch)

[dfch](https://github.com/dfch)

opened [on Aug 31, 2026](https://github.com/dfch/biz.dfch.SpecMgr/issues/36#issue-5301607107)

Issue body actions

At this time, every domain (except ADR ?) has a `delete_<domain>` tool. This tool is not implemented. It returns "not implemented".

We want to add a generic tool `delete` (like `set_status`) that uses:

-   a type
-   a uuid

This will then create the respective path and find the artifact to be deleted.

We will then remove all other existing `delete_<domain>` tools.

We also must update the respective decisions and documents that require a domain to provide the "old" delete tool and note, that from now on, all domains must implement an adapter in the new generic `delete` tool.

When we delete, we must be careful. We must make sure, no one can "inject" relative paths with either type or uuid. We must make sure that the input are `str`. We also must make sure that we have a lock in place when we find the file and delete it. We also must gracefully handle any exception. Example: pass them on to the caller with a meaningful error message.

Reactions are currently unavailable

## Metadata

## Metadata

### Assignees

No one assigned

### Labels

No labels

No labels

### Projects

No projects

### Milestone

No milestone

### Relationships

None yet

### Development

No branches or pull requests

## Issue actions

-   ![](https://github.githubassets.com/assets/github-copilot-app-light-15ad5534265eeacd.svg)Open in GitHub Copilot app

## Footer

[](https://github.com)© 2026 GitHub, Inc.

### Footer navigation

-   [Terms](https://docs.github.com/site-policy/github-terms/github-terms-of-service)
-   [Privacy](https://docs.github.com/site-policy/privacy-policies/github-privacy-statement)
-   [Security](https://github.com/security)
-   [Status](https://www.githubstatus.com/)
-   [Community](https://github.community/)
-   [Docs](https://docs.github.com/)
-   [Contact](https://support.github.com?tags=dotcom-footer)
-   Manage cookies
-   Do not share my personal information

You can’t perform that action at this time.
```

**Tool: bash**

**Input:**

```json
{
  "command": "git -C /home/user/src/biz.dfch.SpecMgr status && echo \"---BRANCH---\" && git -C /home/user/src/biz.dfch.SpecMgr branch -a && echo \"---WORKTREE---\" && git -C /home/user/src/biz.dfch.SpecMgr worktree list"
}
```

**Output:**

```
On branch dev
Your branch is up to date with 'origin/dev'.

nothing to commit, working tree clean
---BRANCH---
* dev
  feat-15-add-artifact-type-risk
  feat-18-goal
  feat-21
  feat-22
+ feat-32-sysrs
+ feat-33-vcr
  feat-7
  main
  remotes/origin/HEAD -> origin/dev
  remotes/origin/dev
  remotes/origin/feat-32-sysrs
  remotes/origin/feat-33-vcr
  remotes/origin/main
---WORKTREE---
/home/user/src/biz.dfch.SpecMgr                          44d649c [dev]
/home/user/src/biz.dfch.SpecMgr.worktrees/feat-32-sysrs  4a4fc62 [feat-32-sysrs]
/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr    5ab4d20 [feat-33-vcr]

```

**Tool: bash**

**Input:**

```json
{
  "command": "ls -la /home/user/src/ && echo \"---SIBLING---\" && ls -la /home/user/src/ | grep -i spec"
}
```

**Output:**

```
total 11084
drwxrwxr-x 14 user user     4096 Aug 31 10:18 .
drwxr-x--- 36 user user     4096 Aug 31 11:42 ..
-rwxrwxr-x  1 user user 11290744 Feb  4  2026 AsdSte100Lookup-v1.10.0-debian-amd64
drwxrwxr-x 11 user user     4096 Mai 24 00:04 biz.dfch.AsdSte100Lookup
drwxrwxr-x  4 user user     4096 Aug 18 11:53 biz.dfch.AsdSte100TechnicalWords
drwxrwxr-x  7 user user     4096 Mai 21 17:44 biz.dfch.IncoseIso25010Refiner
drwxrwxr-x  8 user user     4096 Aug 28 07:09 biz.dfch.LlmOps
drwxrwxr-x 16 user user     4096 Aug 31 17:04 biz.dfch.SpecMgr
drwxrwxr-x  4 user user     4096 Aug 31 10:07 biz.dfch.SpecMgr.worktrees
drwxrwxr-x  6 user user     4096 Mai 24 15:51 dev-toolchain
drwxrwxr-x  7 user user     4096 Mai 24 10:56 esp-pi-101
drwxrwxr-x  4 user user     4096 Jun  2 16:50 huggingface-cli
drwxrwxr-x  8 user user     4096 Aug 31 10:20 ktbe-sv-pst
drwxrwxr-x 31 user user     4096 Jun  3 12:00 llama.cpp
drwxrwxr-x  3 user user     4096 Mai 21 17:44 reqs
---SIBLING---
drwxrwxr-x 16 user user     4096 Aug 31 17:04 biz.dfch.SpecMgr
drwxrwxr-x  4 user user     4096 Aug 31 10:07 biz.dfch.SpecMgr.worktrees

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 21.2s)

_Thinking:_

Now I understand the task. Let me analyze the GitHub issue #36:

**Issue: Replace domain-specific deletes with a generic delete tool**

Key points:

1. Currently, all domains (excluding ADR?) have a `delete_<domain>` tool, which is unimplemented and returns "not implemented".
2. We want to add a generic tool `delete` (like `set_status`) that uses the following:
   - Type
   - UUID
3. This creates the corresponding path and finds the artifact to be deleted.
4. We remove all other existing `delete_<domain>` tools.
5. We update the corresponding decisions and documents that require domains to provide the "old" delete tool, and note that from now on, all domains must implement adapters in the new generic `delete` tool.
6. When deleting, be careful:
   - Ensure that no one can "inject" relative paths via either type or uuid.
   - Ensure that the input is `str`.
   - Ensure that a lock is in place when finding and deleting the file.
   - Gracefully handle all exceptions and pass them along to the caller with a meaningful error message.

Next, let's explore the codebase to understand:

1. The existing `delete_<domain>` stubs
2. The generic `set_status` tool
3. The generic `update` tool
4. Path handling (`_doc_paths.py`, `_paths.py`)
5. How documents are stored
6. The relevant ADRs/decisions that need updating
7. Existing lock mechanisms

The user's requirements:

- Place the feature in a separate git worktree branch. There is already a sibling directory for that (`biz.dfch.SpecMgr.worktrees`).
- Branch and feature name is "feat-36-delete".

So, we need to create a plan. This is plan mode, so we should:

1. Explore the codebase thoroughly
2. Understand the patterns
3. Create a comprehensive plan

The worktree needs to be set up at `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete`, and we need to create a branch `feat-36-delete`.

To understand the codebase patterns, let's look at existing features. I'll explore:

- The generic `set_status` tool
- The generic `update` tool
- The `delete_<domain>` stubs
- Path resolution
- Locks
- Relevant ADRs

To be thorough, let's use explore agents in parallel while also directly looking at important files. First, let me check the structure of the source directory.

I'll do this efficiently. I'll launch an explore agent for a broad overview while reading specific files myself.

First, let me check the source structure and the generic tools.

Let me examine the issue requirements and explore the codebase structure in parallel.

**Tool: bash**

**Input:**

```json
{
  "command": "find /home/user/src/biz.dfch.SpecMgr/src -type d | sort && echo \"---GENERAL TOOLS---\" && ls -la /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/"
}
```

**Output:**

```
/home/user/src/biz.dfch.SpecMgr/src
/home/user/src/biz.dfch.SpecMgr/src/biz
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/commands
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/commands/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/models/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz_dfch_specmgr.egg-info
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/models/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/models/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/adr
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/adr/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/adr/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/adr/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/models/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/models/v2
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/models/v2/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/models/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/models/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/models/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/models/v1/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/models/v2
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/models/v2/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/resources/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/tools
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/tools/__pycache__
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/data
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/models
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/models/v1
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/prompts
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/resources
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/tools
---GENERAL TOOLS---
total 124
drwxrwxr-x 3 user user  4096 Aug 31 17:04 .
drwxrwxr-x 8 user user  4096 Aug 31 13:39 ..
-rw-rw-r-- 1 user user  8102 Aug 25 20:34 _doc_paths.py
-rw-rw-r-- 1 user user  1933 Aug 27 20:20 __init__.py
-rw-rw-r-- 1 user user  3098 Aug 25 20:34 mdformat.py
-rw-rw-r-- 1 user user  5151 Aug 25 20:34 _packaged_data.py
-rw-rw-r-- 1 user user  5381 Aug 25 20:34 _paging.py
drwxrwxr-x 2 user user  4096 Aug 31 15:03 __pycache__
-rw-rw-r-- 1 user user 26632 Aug 31 17:04 set_status.py
-rw-rw-r-- 1 user user  7055 Aug 27 20:20 _splice.py
-rw-rw-r-- 1 user user 32994 Aug 31 17:04 update.py
-rw-rw-r-- 1 user user  5583 Aug 25 20:34 webfetch.py

```

**Tool: bash**

**Input:**

```json
{
  "command": "echo \"=== delete stubs ===\" && grep -rn \"delete\" /home/user/src/biz.dfch.SpecMgr/src --include=\"*.py\" | grep -i \"def \\|@mcp\\|NotImplemented\\|not implemented\\|Stub\" | head -60"
}
```

**Output:**

```
=== delete stubs ===
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/delete_rsk.py:18:"""``@mcp.tool()`` wrapper: delete_rsk (Task 3.6).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/delete_rsk.py:20:Registered stub only -- reserves the ``delete_rsk`` name/slot in the RSK
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/delete_rsk.py:44:def delete_rsk(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/delete_rsk.py:58:    raise NotImplementedError("delete_rsk is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/__init__.py:41:body untouched. ``delete_rsk`` is a registered stub -- always raises
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/tools/delete_vcr.py:18:"""``@mcp.tool()`` wrapper: delete_vcr (Task 2.1).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/tools/delete_vcr.py:20:Registered stub only -- reserves the ``delete_vcr`` name/slot in the VCR
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/tools/delete_vcr.py:23:else -- undecided, matching every other domain's own ``delete_*`` stubs, a
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/tools/delete_vcr.py:45:def delete_vcr(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/tools/delete_vcr.py:59:    raise NotImplementedError("delete_vcr is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/tools/__init__.py:40:``delete_vcr`` is a registered stub -- always raises
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/tools/delete_uc.py:18:"""``@mcp.tool()`` wrapper: delete_uc (Task 3.1.5).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/tools/delete_uc.py:20:Registered stub only -- reserves the ``delete_uc`` name/slot in the UC
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/tools/delete_uc.py:43:def delete_uc(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/tools/delete_uc.py:57:    raise NotImplementedError("delete_uc is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/tools/__init__.py:41:``delete_uc`` (Task 3.1.5) is a registered stub -- always raises
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/delete_gol.py:18:"""``@mcp.tool()`` wrapper: delete_gol (Task 3.6).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/delete_gol.py:20:Registered stub only -- reserves the ``delete_gol`` name/slot in the GOL
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/delete_gol.py:23:else -- undecided, matching the other five domains' own ``delete_*`` stubs,
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/delete_gol.py:45:def delete_gol(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/delete_gol.py:59:    raise NotImplementedError("delete_gol is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/__init__.py:39:``delete_gol`` (Task 3.6) is a registered stub -- always raises
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/option_delete.py:18:"""``@mcp.tool()`` wrapper: option_delete (plan §5, §8, §9a, §10 item 4).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/option_delete.py:47:def option_delete(id: str, full_title: str) -> list[str]:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/delete_req.py:18:"""``@mcp.tool()`` wrapper: delete_req (Task 3.15).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/delete_req.py:20:Registered stub only -- reserves the ``delete_req`` name/slot in the REQ
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/delete_req.py:44:def delete_req(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/delete_req.py:58:    raise NotImplementedError("delete_req is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/__init__.py:42:``delete_req`` (Task 3.15) is a registered stub -- always raises
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/delete_feat.py:18:"""``@mcp.tool()`` wrapper: delete_feat (Task 2.3).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/delete_feat.py:20:Registered stub only -- reserves the ``delete_feat`` name/slot in the FEAT
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/delete_feat.py:24:other domain's own ``delete_*`` stub, a shared cross-domain decision
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/delete_feat.py:45:def delete_feat(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/delete_feat.py:59:    raise NotImplementedError("delete_feat is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/__init__.py:48:``delete_feat`` is a registered stub -- always raises
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/__init__.py:39:``delete_feat`` (stub), ``validate_feat``, plus ``type="feat"`` entries in
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/delete_qa.py:18:"""``@mcp.tool()`` wrapper: delete_qa (Phase 4, Task 4.1).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/delete_qa.py:20:Registered stub only -- reserves the ``delete_qa`` name/slot in the QA
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/delete_qa.py:44:def delete_qa(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/delete_qa.py:58:    raise NotImplementedError("delete_qa is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/__init__.py:39:``updated``, leaving the body untouched. ``delete_qa`` is a registered stub
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/delete_prb.py:18:"""``@mcp.tool()`` wrapper: delete_prb (Task 3.6).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/delete_prb.py:20:Registered stub only -- reserves the ``delete_prb`` name/slot in the PRB
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/delete_prb.py:44:def delete_prb(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/delete_prb.py:58:    raise NotImplementedError("delete_prb is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/__init__.py:39:``delete_prb`` is a registered stub -- always raises
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/tools/delete_dec.py:18:"""``@mcp.tool()`` wrapper: delete_dec (Task 2.2).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/tools/delete_dec.py:20:Registered stub only -- reserves the ``delete_dec`` name/slot in the DEC
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/tools/delete_dec.py:23:else -- undecided, matching the other six domains' own ``delete_*`` stubs,
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/tools/delete_dec.py:45:def delete_dec(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/tools/delete_dec.py:59:    raise NotImplementedError("delete_dec is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/tools/__init__.py:39:``delete_dec`` is a registered stub -- always raises
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/tools/delete_sop.py:18:"""``@mcp.tool()`` wrapper: delete_sop (Task 2.2).
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/tools/delete_sop.py:20:Registered stub only -- reserves the ``delete_sop`` name/slot in the SOP
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/tools/delete_sop.py:23:else -- undecided, matching the other domains' own ``delete_*`` stubs, a
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/tools/delete_sop.py:45:def delete_sop(id: str) -> NoReturn:
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/tools/delete_sop.py:59:    raise NotImplementedError("delete_sop is not yet implemented")
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/tools/__init__.py:34:(``sop.tools._paths``/``_io``). ``delete_sop`` is a registered stub --
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py:177:``delete_prb`` (stub, not yet implemented), ``validate_prb``.
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py:181: ``delete_gol`` (stub, not yet implemented), ``validate_gol``.

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 14.5s)

_Thinking:_

Now I have a good overall picture of the domain and the delete stubs. Next, let's read the important files:

1. The generic `set_status.py` (the closest analog)
2. The generic `update.py`
3. `_doc_paths.py` (shared path resolution)
4. One of the delete stubs (e.g., `delete_rsk.py`)
5. The `__init__.py` files that register the tools

I'll read these in parallel.

Now let me read the key files: the generic `set_status`/`update` tools, the shared path resolver, and a representative delete stub.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """``@mcp.tool()`` wrapper: set_status (feat-22-consolidate-mutation-tools, Phase 4).
19: 
20: The generic, cross-domain status-change tool for all twelve document types
21: (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``adr``).
22: It dispatches on the explicit ``type`` parameter to a private per-domain
23: adapter (``_set_status_<d>``), each a **verbatim port** of the
24: corresponding per-domain status tool's function body (same domain lock,
25: same ``load_by_id``, same raw-body re-read and verbatim re-persistence,
26: same frontmatter reconstruction through the domain's own
27: ``XFrontmatter`` constructor -- so the domain's closed status vocabulary
28: validates -- and the same domain ``XNotFoundError``; those per-domain
29: tools were retired in feat-22 Phase 4). The ADR adapter ports the
30: previous per-domain ADR status tool's function body (same ``adr_lock``,
31: ``load_by_id``, and ``write_adr`` render round-trip,
32: ``AdrNotFoundError``) including its delegation to
33: ``models.adr.v1.mutations.set_status``, which composes ``status`` as
34: ``"superseded by {superseded_by}"`` when ``superseded_by`` is given.
35: ``sop`` is the first domain built dispatch-only from day one (ADR
36: 36905d5b): its ``_set_status_sop`` adapter was written directly in this
37: shape rather than ported from a retired per-domain tool.
38: 
39: The ``feat`` adapter (``_set_status_feat``) diverges from the other ten
40: whole-body domains' identical shape in the same way ``_update_feat``
41: (in ``update.py``) does: it resolves ``id`` via
42: ``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
43: flat-file directory scan (see
44: ``.specmgr/feat/feat-31-feature/README.md`` Design Notes). It bumps
45: ``updated`` to the same microsecond timestamp as every other domain --
46: an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date) was
47: reversed for cross-domain consistency; see that feature's Decisions Made.
48: 
49: The parameter is intentionally named ``type`` (it matches the frontmatter
50: field vocabulary the client already knows); no enabled ruff rule objects
51: to the builtin shadow. The 12-way union return type is annotation-only --
52: the MCP input schema is built from the parameters, and the SDK
53: serializes whichever concrete document is returned.
54: 
55: ``superseded_by`` is accepted only for ``type="adr"``: the
56: "superseded by X" status pattern is ADR-specific (no other domain's
57: ``XFrontmatter.status`` accepts it). The public :func:`set_status`
58: rejects it for any other ``type`` with a ``ValueError`` before any file
59: access.
60: 
61: Neither any ``create_<d>`` tool nor the generic :func:`update` tool
62: accepts a ``status`` argument at all -- this tool is the sole
63: status-change entry point for every domain.
64: 
65: ``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
66: because the pure, in-memory operation it delegates to shares this
67: wrapper's own name.
68: """
69: 
70: from __future__ import annotations
71: 
72: from collections.abc import Callable
73: from datetime import datetime
74: from typing import Literal
75: 
76: import frontmatter
77: 
78: from ...adr.tools._io import load_by_id as load_adr_by_id
79: from ...adr.tools._io import write_adr
80: from ...adr.tools._lock import adr_lock
81: from ...adr.tools._paths import adr_base_dir
82: from ...dec.models.v1 import DecDocument, DecFrontmatter
83: from ...dec.tools._io import load_by_id as load_dec_by_id
84: from ...dec.tools._lock import dec_lock
85: from ...dec.tools._paths import dec_base_dir
86: from ...dec.tools._write import write_dec_file
87: from ...feat.models.v1 import FeatDocument, FeatFrontmatter
88: from ...feat.tools._io import load_by_id as load_feat_by_id
89: from ...feat.tools._lock import feat_lock
90: from ...feat.tools._paths import feat_base_dir
91: from ...feat.tools._write import write_feat_file
92: from ...gol.models.v1 import GolDocument, GolFrontmatter
93: from ...gol.tools._io import load_by_id as load_gol_by_id
94: from ...gol.tools._lock import gol_lock
95: from ...gol.tools._paths import gol_base_dir
96: from ...gol.tools._write import write_gol_file
97: from ...models.adr import Adr
98: from ...models.adr.v1 import mutations
99: from ...prb.models.v1 import PrbDocument, PrbFrontmatter
100: from ...prb.tools._io import load_by_id as load_prb_by_id
101: from ...prb.tools._lock import prb_lock
102: from ...prb.tools._paths import prb_base_dir
103: from ...prb.tools._write import write_prb_file
104: from ...qa.models.v2 import QaDocument, QaFrontmatter
105: from ...qa.tools._io import load_by_id as load_qa_by_id
106: from ...qa.tools._lock import qa_lock
107: from ...qa.tools._paths import qa_base_dir
108: from ...qa.tools._write import write_qa_file
109: from ...req.models.v1 import ReqDocument, ReqFrontmatter
110: from ...req.tools._io import load_by_id as load_req_by_id
111: from ...req.tools._lock import req_lock
112: from ...req.tools._paths import req_base_dir
113: from ...req.tools._write import write_req_file
114: from ...rsk.models.v1 import RskDocument, RskFrontmatter
115: from ...rsk.tools._io import load_by_id as load_rsk_by_id
116: from ...rsk.tools._lock import rsk_lock
117: from ...rsk.tools._paths import rsk_base_dir
118: from ...rsk.tools._write import write_rsk_file
119: from ...server import mcp
120: from ...sop.models.v1 import SopDocument, SopFrontmatter
121: from ...sop.tools._io import load_by_id as load_sop_by_id
122: from ...sop.tools._lock import sop_lock
123: from ...sop.tools._paths import sop_base_dir
124: from ...sop.tools._write import write_sop_file
125: from ...tsk.models.v1 import TskDocument, TskFrontmatter
126: from ...tsk.tools._io import load_by_id as load_tsk_by_id
127: from ...tsk.tools._lock import tsk_lock
128: from ...tsk.tools._paths import tsk_base_dir
129: from ...tsk.tools._write import write_tsk_file
130: from ...uc.models.v2 import UcDocument, UcFrontmatter
131: from ...uc.tools._io import load_by_id as load_uc_by_id
132: from ...uc.tools._lock import uc_lock
133: from ...uc.tools._paths import uc_base_dir
134: from ...uc.tools._write import write_uc_file
135: from ...vcr.models.v1 import VcrDocument, VcrFrontmatter
136: from ...vcr.tools._io import load_by_id as load_vcr_by_id
137: from ...vcr.tools._lock import vcr_lock
138: from ...vcr.tools._paths import vcr_base_dir
139: from ...vcr.tools._write import write_vcr_file
140: 
141: __all__ = ["set_status"]
142: 
143: #: The only ``type`` whose status can be composed via ``superseded_by``
144: #: (the ``"superseded by X"`` pattern is ADR-specific).
145: _TYPE_ADR = "adr"
146: 
147: #: The generic tool's 12-way return union -- annotation-only (see module docstring).
148: _SetStatusDocument = (
149:     ReqDocument
150:     | UcDocument
151:     | TskDocument
152:     | QaDocument
153:     | PrbDocument
154:     | GolDocument
155:     | RskDocument
156:     | DecDocument
157:     | FeatDocument
158:     | SopDocument
159:     | VcrDocument
160:     | Adr
161: )
162: 
163: 
164: def _set_status_req(id_: str, status: str, superseded_by: str | None) -> ReqDocument:
165:     """Replace the status of the requirement identified by ``id_``.
166: 
167:     Verbatim port of the previous per-domain requirement status tool's
168:     function body (same ``req_lock``, ``load_by_id``, raw-body re-read via
169:     the established ``frontmatter.loads(...).content`` mechanism and
170:     verbatim re-persistence, frontmatter reconstructed through
171:     :class:`ReqFrontmatter`'s own constructor so the closed status
172:     vocabulary validates, ``write_req_file``, ``ReqNotFoundError``; that
173:     per-domain tool was retired in feat-22 Phase 4). ``superseded_by`` is
174:     never used here -- the public :func:`set_status` guard rejects it for
175:     every non-``adr`` type before dispatch.
176:     """
177:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
178: 
179:     base_dir = req_base_dir()
180:     with req_lock(id_):
181:         path, existing = load_req_by_id(base_dir, id_)
182:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
183: 
184:         now = datetime.now().isoformat(timespec="microseconds")
185:         fm_data = existing.frontmatter.model_dump()
186:         fm_data["status"] = status
187:         fm_data["updated"] = now
188:         new_frontmatter = ReqFrontmatter(**fm_data)
189:         new_doc = ReqDocument(frontmatter=new_frontmatter, body=existing.body)
190:         write_req_file(path, new_frontmatter, raw_body)
191:     return new_doc
192: 
193: 
194: def _set_status_uc(id_: str, status: str, superseded_by: str | None) -> UcDocument:
195:     """Replace the status of the use case identified by ``id_``.
196: 
197:     Verbatim port of the previous per-domain use-case status tool's
198:     function body (same ``uc_lock``, ``load_by_id``, ``write_uc_file``,
199:     ``UcNotFoundError``; that per-domain tool was retired in feat-22
200:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
201:     """
202:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
203: 
204:     base_dir = uc_base_dir()
205:     with uc_lock(id_):
206:         path, existing = load_uc_by_id(base_dir, id_)
207:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
208: 
209:         now = datetime.now().isoformat(timespec="microseconds")
210:         fm_data = existing.frontmatter.model_dump()
211:         fm_data["status"] = status
212:         fm_data["updated"] = now
213:         new_frontmatter = UcFrontmatter(**fm_data)
214:         new_doc = UcDocument(frontmatter=new_frontmatter, body=existing.body)
215:         write_uc_file(path, new_frontmatter, raw_body)
216:     return new_doc
217: 
218: 
219: def _set_status_tsk(id_: str, status: str, superseded_by: str | None) -> TskDocument:
220:     """Replace the status of the task list identified by ``id_``.
221: 
222:     Verbatim port of the previous per-domain task list status tool's
223:     function body (same ``tsk_lock``, ``load_by_id``, ``write_tsk_file``,
224:     ``TskNotFoundError``; that per-domain tool was retired in feat-22
225:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
226:     """
227:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
228: 
229:     base_dir = tsk_base_dir()
230:     with tsk_lock(id_):
231:         path, existing = load_tsk_by_id(base_dir, id_)
232:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
233: 
234:         now = datetime.now().isoformat(timespec="microseconds")
235:         fm_data = existing.frontmatter.model_dump()
236:         fm_data["status"] = status
237:         fm_data["updated"] = now
238:         new_frontmatter = TskFrontmatter(**fm_data)
239:         new_doc = TskDocument(frontmatter=new_frontmatter, body=existing.body)
240:         write_tsk_file(path, new_frontmatter, raw_body)
241:     return new_doc
242: 
243: 
244: def _set_status_qa(id_: str, status: str, superseded_by: str | None) -> QaDocument:
245:     """Replace the status of the QA document identified by ``id_``.
246: 
247:     Verbatim port of the previous per-domain QA document status tool's
248:     function body (same ``qa_lock``, ``load_by_id``, ``write_qa_file``,
249:     ``QaNotFoundError``; that per-domain tool was retired in feat-22
250:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
251:     """
252:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
253: 
254:     base_dir = qa_base_dir()
255:     with qa_lock(id_):
256:         path, existing = load_qa_by_id(base_dir, id_)
257:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
258: 
259:         now = datetime.now().isoformat(timespec="microseconds")
260:         fm_data = existing.frontmatter.model_dump()
261:         fm_data["status"] = status
262:         fm_data["updated"] = now
263:         new_frontmatter = QaFrontmatter(**fm_data)
264:         new_doc = QaDocument(frontmatter=new_frontmatter, body=existing.body)
265:         write_qa_file(path, new_frontmatter, raw_body)
266:     return new_doc
267: 
268: 
269: def _set_status_prb(id_: str, status: str, superseded_by: str | None) -> PrbDocument:
270:     """Replace the status of the problem statement identified by ``id_``.
271: 
272:     Verbatim port of the previous per-domain problem statement status
273:     tool's function body (same ``prb_lock``, ``load_by_id``,
274:     ``write_prb_file``, ``PrbNotFoundError``; that per-domain tool was
275:     retired in feat-22 Phase 4) -- see :func:`_set_status_req` for the
276:     full semantics.
277:     """
278:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
279: 
280:     base_dir = prb_base_dir()
281:     with prb_lock(id_):
282:         path, existing = load_prb_by_id(base_dir, id_)
283:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
284: 
285:         now = datetime.now().isoformat(timespec="microseconds")
286:         fm_data = existing.frontmatter.model_dump()
287:         fm_data["status"] = status
288:         fm_data["updated"] = now
289:         new_frontmatter = PrbFrontmatter(**fm_data)
290:         new_doc = PrbDocument(frontmatter=new_frontmatter, body=existing.body)
291:         write_prb_file(path, new_frontmatter, raw_body)
292:     return new_doc
293: 
294: 
295: def _set_status_gol(id_: str, status: str, superseded_by: str | None) -> GolDocument:
296:     """Replace the status of the goal identified by ``id_``.
297: 
298:     Verbatim port of the previous per-domain goal status tool's function
299:     body (same ``gol_lock``, ``load_by_id``, ``write_gol_file``,
300:     ``GolNotFoundError``; that per-domain tool was retired in feat-22
301:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
302:     """
303:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
304: 
305:     base_dir = gol_base_dir()
306:     with gol_lock(id_):
307:         path, existing = load_gol_by_id(base_dir, id_)
308:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
309: 
310:         now = datetime.now().isoformat(timespec="microseconds")
311:         fm_data = existing.frontmatter.model_dump()
312:         fm_data["status"] = status
313:         fm_data["updated"] = now
314:         new_frontmatter = GolFrontmatter(**fm_data)
315:         new_doc = GolDocument(frontmatter=new_frontmatter, body=existing.body)
316:         write_gol_file(path, new_frontmatter, raw_body)
317:     return new_doc
318: 
319: 
320: def _set_status_rsk(id_: str, status: str, superseded_by: str | None) -> RskDocument:
321:     """Replace the status of the risk identified by ``id_``.
322: 
323:     Verbatim port of the previous per-domain risk status tool's function
324:     body (same ``rsk_lock``, ``load_by_id``, ``write_rsk_file``,
325:     ``RskNotFoundError``; that per-domain tool was retired in feat-22
326:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
327:     """
328:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
329: 
330:     base_dir = rsk_base_dir()
331:     with rsk_lock(id_):
332:         path, existing = load_rsk_by_id(base_dir, id_)
333:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
334: 
335:         now = datetime.now().isoformat(timespec="microseconds")
336:         fm_data = existing.frontmatter.model_dump()
337:         fm_data["status"] = status
338:         fm_data["updated"] = now
339:         new_frontmatter = RskFrontmatter(**fm_data)
340:         new_doc = RskDocument(frontmatter=new_frontmatter, body=existing.body)
341:         write_rsk_file(path, new_frontmatter, raw_body)
342:     return new_doc
343: 
344: 
345: def _set_status_dec(id_: str, status: str, superseded_by: str | None) -> DecDocument:
346:     """Replace the status of the decision identified by ``id_``.
347: 
348:     Verbatim port of the previous per-domain decision status tool's
349:     function body (same ``dec_lock``, ``load_by_id``, ``write_dec_file``,
350:     ``DecNotFoundError``; that per-domain tool was retired in feat-22
351:     Phase 8, when the DEC domain -- merged from dev while still on the
352:     old per-domain mechanism -- was converted to the generic tools) --
353:     see :func:`_set_status_req` for the full semantics.
354:     """
355:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
356: 
357:     base_dir = dec_base_dir()
358:     with dec_lock(id_):
359:         path, existing = load_dec_by_id(base_dir, id_)
360:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
361: 
362:         now = datetime.now().isoformat(timespec="microseconds")
363:         fm_data = existing.frontmatter.model_dump()
364:         fm_data["status"] = status
365:         fm_data["updated"] = now
366:         new_frontmatter = DecFrontmatter(**fm_data)
367:         new_doc = DecDocument(frontmatter=new_frontmatter, body=existing.body)
368:         write_dec_file(path, new_frontmatter, raw_body)
369:     return new_doc
370: 
371: 
372: def _set_status_feat(id_: str, status: str, superseded_by: str | None) -> FeatDocument:
373:     """Replace the status of the feature identified by ``id_``.
374: 
375:     Mirrors :func:`_set_status_dec`'s shape (same ``feat_lock``,
376:     ``load_by_id``, ``write_feat_file``, ``FeatNotFoundError``) -- see
377:     :func:`_set_status_req` for the full semantics -- with the same
378:     feat-only divergence ``_update_feat`` (in ``update.py``) documents:
379:     ``id_`` resolves via ``feat.tools._paths``'s bespoke folder-per-document
380:     shortcut, not a flat-file directory scan. ``updated`` is bumped to the
381:     same microsecond timestamp as every other domain.
382:     """
383:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
384: 
385:     base_dir = feat_base_dir()
386:     with feat_lock(id_):
387:         path, existing = load_feat_by_id(base_dir, id_)
388:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
389: 
390:         now = datetime.now().isoformat(timespec="microseconds")
391:         fm_data = existing.frontmatter.model_dump()
392:         fm_data["status"] = status
393:         fm_data["updated"] = now
394:         new_frontmatter = FeatFrontmatter(**fm_data)
395:         new_doc = FeatDocument(frontmatter=new_frontmatter, body=existing.body)
396:         write_feat_file(path, new_frontmatter, raw_body)
397:     return new_doc
398: 
399: 
400: def _set_status_sop(id_: str, status: str, superseded_by: str | None) -> SopDocument:
401:     """Replace the status of the SOP identified by ``id_``.
402: 
403:     Verbatim-shape port of :func:`_set_status_dec` (same ``sop_lock``,
404:     ``load_by_id``, ``write_sop_file``, ``SopNotFoundError``; ``sop`` is the
405:     first domain built dispatch-only from day one per ADR 36905d5b, so there
406:     was never a per-domain ``set_status_sop`` tool to port -- this adapter
407:     was written directly in this shape) -- see :func:`_set_status_req` for
408:     the full semantics.
409:     """
410:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
411: 
412:     base_dir = sop_base_dir()
413:     with sop_lock(id_):
414:         path, existing = load_sop_by_id(base_dir, id_)
415:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
416: 
417:         now = datetime.now().isoformat(timespec="microseconds")
418:         fm_data = existing.frontmatter.model_dump()
419:         fm_data["status"] = status
420:         fm_data["updated"] = now
421:         new_frontmatter = SopFrontmatter(**fm_data)
422:         new_doc = SopDocument(frontmatter=new_frontmatter, body=existing.body)
423:         write_sop_file(path, new_frontmatter, raw_body)
424:     return new_doc
425: 
426: 
427: def _set_status_vcr(id_: str, status: str, superseded_by: str | None) -> VcrDocument:
428:     """Replace the status of the verification case record identified by ``id_``.
429: 
430:     Mirrors :func:`_set_status_dec`'s shape (same ``vcr_lock``,
431:     ``load_by_id``, ``write_vcr_file``, ``VcrNotFoundError``) -- see
432:     :func:`_set_status_req` for the full semantics. ``vcr`` is not
433:     ``adr``, so ``superseded_by`` must never be given.
434:     """
435:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
436: 
437:     base_dir = vcr_base_dir()
438:     with vcr_lock(id_):
439:         path, existing = load_vcr_by_id(base_dir, id_)
440:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
441: 
442:         now = datetime.now().isoformat(timespec="microseconds")
443:         fm_data = existing.frontmatter.model_dump()
444:         fm_data["status"] = status
445:         fm_data["updated"] = now
446:         new_frontmatter = VcrFrontmatter(**fm_data)
447:         new_doc = VcrDocument(frontmatter=new_frontmatter, body=existing.body)
448:         write_vcr_file(path, new_frontmatter, raw_body)
449:     return new_doc
450: 
451: 
452: def _set_status_adr(id_: str, status: str, superseded_by: str | None) -> Adr:
453:     """Replace the status of the ADR identified by ``id_``.
454: 
455:     Port of the previous per-domain ADR status tool's function body
456:     (same ``adr_lock``, ``load_by_id``, delegation to
457:     ``models.adr.v1.mutations.set_status`` -- which composes ``status`` as
458:     ``"superseded by {superseded_by}"`` when ``superseded_by`` is given --
459:     and the ``write_adr`` render round-trip, ``AdrNotFoundError``; that
460:     per-domain tool was retired in feat-22 Phase 4).
461:     """
462:     base_dir = adr_base_dir()
463:     with adr_lock(id_):
464:         path, adr = load_adr_by_id(base_dir, id_)
465:         new_adr = mutations.set_status(adr, status, superseded_by)
466:         write_adr(path, new_adr)
467:     return new_adr
468: 
469: 
470: #: Dispatch table mapping the ``type`` value to its private adapter.
471: _ADAPTERS: dict[str, Callable[[str, str, str | None], _SetStatusDocument]] = {
472:     "req": _set_status_req,
473:     "uc": _set_status_uc,
474:     "tsk": _set_status_tsk,
475:     "qa": _set_status_qa,
476:     "prb": _set_status_prb,
477:     "gol": _set_status_gol,
478:     "rsk": _set_status_rsk,
479:     "dec": _set_status_dec,
480:     "feat": _set_status_feat,
481:     "sop": _set_status_sop,
482:     "vcr": _set_status_vcr,
483:     _TYPE_ADR: _set_status_adr,
484: }
485: 
486: 
487: @mcp.tool(
488:     name="set_status",
489:     title="Set document status",
490:     description=(
491:         "Replace the status of an existing document across all twelve domains (`type` is one of "
492:         "req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, adr), also bumping `updated` (the eleven "
493:         "whole-body domains) and leaving the body untouched. The new `status` must be one of the "
494:         "domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); "
495:         "anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is "
496:         'accepted only for `type="adr"` -- it composes the status as "superseded by '
497:         '{superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor '
498:         "the generic `update` tool accepts a `status` argument at all -- this is the sole "
499:         "status-change entry point."
500:     ),
501: )
502: def set_status(
503:     id: str,
504:     type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr", "adr"],
505:     status: str,
506:     superseded_by: str | None = None,
507: ) -> _SetStatusDocument:
508:     """Replace the status of an existing document, across all twelve domains.
509: 
510:     Cross-domain generic for every document type
511:     (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``adr``);
512:     dispatches on ``type`` to the domain's own ported adapter (same lock,
513:     same id resolution, same body handling, same domain not-found error).
514: 
515:     For the eleven whole-body domains the existing file's frontmatter is
516:     carried over with every field preserved except ``status`` (replaced)
517:     and ``updated`` (bumped to the current microsecond timestamp); the
518:     body is never touched -- its raw, on-disk markdown (not a render of
519:     the parsed model) is re-read and re-persisted verbatim. For
520:     ``type="adr"`` the change delegates to
521:     ``models.adr.v1.mutations.set_status`` (which composes ``status`` as
522:     ``"superseded by {superseded_by}"`` when ``superseded_by`` is given)
523:     and re-renders the full file via the ``write_adr`` round-trip.
524: 
525:     The new ``status`` must be in the domain's own closed vocabulary: the
526:     frontmatter is reconstructed through the domain's own
527:     ``XFrontmatter`` constructor, so the domain's own validator enforces
528:     its set. Where that set lives is documented per domain -- see each
529:     ``XFrontmatter.status`` field (the eleven whole-body domains'
530:     ``models/<v>/frontmatter.py`` and ``models/adr/v1/frontmatter.py``)
531:     rather than any list in this docstring.
532: 
533:     Parameters
534:     ----------
535:     id:
536:         The document's specmgr-assigned identifier.
537:     type:
538:         The document type / domain: one of ``req``, ``uc``, ``tsk``,
539:         ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
540:         ``vcr``, ``adr``.
541:     status:
542:         The new status. Must be one of the dispatched domain's own
543:         accepted values (see its ``XFrontmatter.status`` field). For
544:         ``adr``, ignored when ``superseded_by`` is given.
545:     superseded_by:
546:         ADR only. When given (with ``type="adr"``), ``status`` is
547:         composed as ``f"superseded by {superseded_by}"`` instead of being
548:         used verbatim. A ``ValueError`` for any other ``type``.
549: 
550:     Returns
551:     -------
552:     ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
553:     GolDocument | RskDocument | DecDocument | FeatDocument | SopDocument |
554:     VcrDocument | Adr
555:         The updated document of the dispatched domain type.
556: 
557:     Raises
558:     ------
559:     ValueError
560:         ``superseded_by`` given with a ``type`` other than ``"adr"``
561:         (raised before any file access). Nothing is written.
562:     pydantic.ValidationError
563:         ``status`` is not in the dispatched domain's closed vocabulary
564:         (for ``adr``: not one of its six values and not a
565:         ``"superseded by ..."`` string). Nothing is written.
566:     ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
567:     PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
568:     FeatNotFoundError / SopNotFoundError / VcrNotFoundError / AdrNotFoundError
569:         No document of the dispatched ``type`` has this id -- the
570:         domain's own not-found error, unchanged from the per-domain tools.
571:     """
572:     if superseded_by is not None and type != _TYPE_ADR:
573:         raise ValueError(
574:             f'superseded_by is only accepted for type={_TYPE_ADR!r} (the "superseded by X" '
575:             f"pattern is ADR-specific), got type={type!r} with superseded_by={superseded_by!r}"
576:         )
577: 
578:     adapter = _ADAPTERS[type]
579:     result = adapter(id, status, superseded_by)
580:     return result

(End of file - total 580 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_doc_paths.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_doc_paths.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Generic, doc-type-agnostic base directory resolution, filename slugification,
19: and id -> path lookup (plan Task 3.10).
20: 
21: Generalizes ``adr.tools._paths``'s shape into a single module shared across
22: document domains (REQ now, UC later) instead of a copy per domain: one root
23: env var (:data:`DOCS_DIR_ENV_VAR`, default :data:`DEFAULT_DOCS_ROOT`) holds
24: every doc type's own subdirectory (``{root}/{type_name}/``, e.g. ``docs/req/``
25: for ``type_name="req"``).
26: 
27: **ADR is deliberately left untouched** -- it keeps its own
28: ``SPECMGR_ADR_DIR``/``docs/adr`` env var and default (``adr.tools._paths``).
29: Migrating ADR onto this shared module is optional future cleanup, not
30: bundled into this change.
31: 
32: As with ``adr.tools._paths``, this module has no ``mcp``/file-write
33: dependency beyond read-only directory listing: :func:`doc_base_dir` never
34: creates the directory (a read-only tool shouldn't have that side effect),
35: only :func:`ensure_doc_base_dir` does. There is deliberately no in-memory
36: id -> path cache either -- every lookup re-scans the base directory and
37: re-parses each file, matching this codebase's "the on-disk file is the sole
38: source of truth" design.
39: """
40: 
41: from __future__ import annotations
42: 
43: import os
44: import re
45: from collections.abc import Callable, Iterator
46: from pathlib import Path
47: from typing import TypeVar
48: 
49: __all__ = [
50:     "DEFAULT_DOCS_ROOT",
51:     "DOCS_DIR_ENV_VAR",
52:     "DocNotFoundError",
53:     "doc_base_dir",
54:     "ensure_doc_base_dir",
55:     "find_doc_path_by_id",
56:     "iter_doc_paths",
57:     "slugify",
58: ]
59: 
60: #: Environment variable that overrides the shared documents root directory.
61: DOCS_DIR_ENV_VAR = "SPECMGR_DOCS_DIR"
62: 
63: #: Default documents root directory, relative to the current working directory.
64: DEFAULT_DOCS_ROOT = Path("docs")
65: 
66: #: Anything that isn't a lowercase ASCII letter or digit, run-collapsed.
67: _NON_ALNUM_RUN_PATTERN = re.compile(r"[^a-z0-9]+")
68: 
69: #: Maximum length of a slugified title (mirrors ``adr.tools._paths``'s filename scheme).
70: _SLUG_MAX_LENGTH = 60
71: 
72: #: Fallback slug used when a title has no alphanumeric characters at all.
73: _FALLBACK_SLUG = "doc"
74: 
75: #: Parsed-document type returned by a caller-supplied ``parse_fn``.
76: _DocT = TypeVar("_DocT")
77: 
78: 
79: class DocNotFoundError(LookupError):
80:     """No document file found matching the given id, under a given base directory."""
81: 
82: 
83: def _docs_root() -> Path:
84:     """Return the configured documents root directory, without creating it."""
85:     value = os.environ.get(DOCS_DIR_ENV_VAR)
86:     result = Path(value) if value else DEFAULT_DOCS_ROOT
87:     return result
88: 
89: 
90: def doc_base_dir(type_name: str) -> Path:
91:     """Return the base directory for ``type_name`` documents, without creating it.
92: 
93:     Reads :data:`DOCS_DIR_ENV_VAR` from the environment, falling back to
94:     :data:`DEFAULT_DOCS_ROOT`, then appends ``type_name`` as a subdirectory
95:     (e.g. ``docs/req`` for ``type_name="req"``). Read-only tools/resources
96:     use this so merely reading never has the side effect of creating the
97:     directory -- see :func:`ensure_doc_base_dir` for the write path.
98: 
99:     Parameters
100:     ----------
101:     type_name:
102:         The document type's subdirectory name, e.g. ``"req"``.
103: 
104:     Returns
105:     -------
106:     Path
107:         The resolved base directory for ``type_name`` documents.
108:     """
109:     assert isinstance(type_name, str), type(type_name)
110:     assert type_name.strip()
111: 
112:     result = _docs_root() / type_name
113:     return result
114: 
115: 
116: def ensure_doc_base_dir(type_name: str) -> Path:
117:     """Return the base directory for ``type_name`` documents, creating it if missing.
118: 
119:     Only a doc type's ``create_*`` tool should call this -- every other
120:     tool/resource uses the read-only :func:`doc_base_dir` instead.
121: 
122:     Parameters
123:     ----------
124:     type_name:
125:         The document type's subdirectory name, e.g. ``"req"``.
126: 
127:     Returns
128:     -------
129:     Path
130:         The resolved, now-guaranteed-to-exist base directory for
131:         ``type_name`` documents.
132:     """
133:     assert isinstance(type_name, str), type(type_name)
134:     assert type_name.strip()
135: 
136:     result = doc_base_dir(type_name)
137:     result.mkdir(parents=True, exist_ok=True)
138:     return result
139: 
140: 
141: def slugify(title: str) -> str:
142:     """Derive a filename-safe slug from a document title.
143: 
144:     Ported from ``adr.tools._paths.slugify`` unchanged: lowercases
145:     ``title``, collapses every run of non-``[a-z0-9]`` characters into a
146:     single ``-``, strips leading/trailing ``-``, truncates to
147:     :data:`_SLUG_MAX_LENGTH` characters (stripping a trailing ``-`` again in
148:     case the truncation lands mid-run), and falls back to
149:     :data:`_FALLBACK_SLUG` if the result would otherwise be empty (e.g. a
150:     title with no alphanumeric characters at all).
151: 
152:     Parameters
153:     ----------
154:     title:
155:         The document title to slugify.
156: 
157:     Returns
158:     -------
159:     str
160:         The filename-safe slug.
161:     """
162:     assert isinstance(title, str), type(title)
163: 
164:     slug = _NON_ALNUM_RUN_PATTERN.sub("-", title.lower()).strip("-")
165:     slug = slug[:_SLUG_MAX_LENGTH].strip("-")
166:     result = slug or _FALLBACK_SLUG
167:     return result
168: 
169: 
170: def iter_doc_paths(base_dir: Path) -> Iterator[Path]:
171:     """Yield every ``*.md`` file directly under ``base_dir``, sorted by name.
172: 
173:     Yields nothing (rather than raising) if ``base_dir`` does not exist.
174: 
175:     Parameters
176:     ----------
177:     base_dir:
178:         The directory to scan for ``*.md`` files.
179: 
180:     Returns
181:     -------
182:     Iterator[Path]
183:         An iterator over the matching, sorted paths.
184:     """
185:     assert isinstance(base_dir, Path), type(base_dir)
186: 
187:     if not base_dir.exists():
188:         return iter(())
189:     result = iter(sorted(base_dir.glob("*.md")))
190:     return result
191: 
192: 
193: def find_doc_path_by_id(
194:     base_dir: Path,
195:     id_: str,
196:     parse_fn: Callable[[str], _DocT],
197:     get_id_fn: Callable[[_DocT], str | None],
198: ) -> Path:
199:     """Resolve an ``id`` to its on-disk file path, for any doc type.
200: 
201:     Scans every ``*.md`` file under ``base_dir``, parsing each via
202:     ``parse_fn`` and comparing ``get_id_fn(parsed)`` against ``id_``. A file
203:     that fails to parse (``AssertionError`` or ``ValueError``, which
204:     ``pydantic.ValidationError`` and every parser-specific error in this
205:     codebase -- e.g. ``AdrParseError`` -- subclass) is silently skipped --
206:     one broken file must not prevent lookup of a different, valid id.
207: 
208:     Parameters
209:     ----------
210:     base_dir:
211:         The directory to scan for ``*.md`` files.
212:     id_:
213:         The id to look up.
214:     parse_fn:
215:         Parses a file's full text into a document object (e.g. ``parse_adr``,
216:         ``parse_req``).
217:     get_id_fn:
218:         Extracts the id (or ``None``) from a parsed document object (e.g.
219:         ``lambda doc: doc.frontmatter.id``).
220: 
221:     Returns
222:     -------
223:     Path
224:         The resolved file path.
225: 
226:     Raises
227:     ------
228:     DocNotFoundError
229:         If no file's parsed id matches ``id_``.
230:     """
231:     assert isinstance(base_dir, Path), type(base_dir)
232:     assert isinstance(id_, str), type(id_)
233:     assert id_.strip()
234: 
235:     for path in iter_doc_paths(base_dir):
236:         try:
237:             doc = parse_fn(path.read_text(encoding="utf-8"))
238:         except (AssertionError, ValueError):
239:             continue
240:         if get_id_fn(doc) == id_:
241:             return path
242:     raise DocNotFoundError(
243:         f"no document found with id {id_!r} under {base_dir}. The id must be the bare document UUID, without "
244:         f"a domain prefix."
245:     )

(End of file - total 245 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/delete_rsk.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/delete_rsk.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """``@mcp.tool()`` wrapper: delete_rsk (Task 3.6).
19: 
20: Registered stub only -- reserves the ``delete_rsk`` name/slot in the RSK
21: lifecycle tool surface without committing to a deletion strategy yet
22: (soft-delete via ``status``, archival, hard removal from disk, or something
23: else -- undecided, mirroring ``tsk.tools.delete_tsk``'s own open question).
24: Always raises ``NotImplementedError`` unconditionally, without resolving
25: ``id`` or touching the filesystem at all, so it cannot be mistaken for a
26: working no-op.
27: """
28: 
29: from __future__ import annotations
30: 
31: from typing import NoReturn
32: 
33: from ...server import mcp
34: 
35: 
36: @mcp.tool(
37:     name="delete_rsk",
38:     title="Delete risk (not yet implemented)",
39:     description="Stub only -- always raises NotImplementedError. Reserves the name for a future implementation.",
40:     # `NoReturn` has no pydantic-serializable schema; this stub never returns anyway, so
41:     # skip structured-output schema derivation entirely rather than lying with a fake return type.
42:     structured_output=False,
43: )
44: def delete_rsk(id: str) -> NoReturn:
45:     """Always raise ``NotImplementedError``; deletion is not yet implemented.
46: 
47:     Parameters
48:     ----------
49:     id:
50:         The document's specmgr-assigned identifier. Unused -- accepted only
51:         to fix this tool's future signature; never resolved or validated.
52: 
53:     Raises
54:     ------
55:     NotImplementedError
56:         Always.
57:     """
58:     raise NotImplementedError("delete_rsk is not yet implemented")

(End of file - total 58 lines)
</content>
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 21.9s)

_Thinking:_

With this, I've got a solid grasp of the pattern. Let me investigate the following:

1. How each domain's `_io.py` and `_lock.py` work (the `load_by_id` used in the adapters)
2. The path handling in `feat/tools/_paths.py` (the special folder-per-document approach)
3. The `__init__.py` files that register the delete stubs (so I can figure out what to remove)
4. The ADRs that document the "delete stub" decisions
5. The docstring in `server.py` (an authoritative list)
6. Existing test patterns for the generic tools (tests for `set_status` and `update`)

First, let me look at the domains' `_io.py`, `_lock.py`, and `_paths.py`. To understand the differences between flat-file domains (like rsk) and feat, I'll check the rsk tools directory and the feat tools directory.

Let me look at several files in parallel.

Let me examine the per-domain `_io`/`_lock`/`_paths` modules (flat-file vs. feat's bespoke layout) and how delete stubs are registered.

**Tool: bash**

**Input:**

```json
{
  "command": "for d in rsk feat adr; do echo \"===== $d/tools =====\"; ls /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/$d/tools/ | grep -v __pycache__; done"
}
```

**Output:**

```
===== rsk/tools =====
create_rsk.py
delete_rsk.py
get_rsk_example.py
get_rsk.py
get_rsk_template.py
__init__.py
_io.py
list_rsk.py
_lock.py
parse_rsk.py
_paths.py
validate_rsk.py
_write.py
===== feat/tools =====
create_feat.py
delete_feat.py
get_feat_example.py
get_feat.py
get_feat_template.py
__init__.py
_io.py
list_feat.py
_lock.py
parse_feat.py
_paths.py
validate_feat.py
_write.py
===== adr/tools =====
create_adr.py
get_adr.py
__init__.py
_io.py
list_adr.py
_lock.py
option_create.py
option_delete.py
option_list.py
option_read.py
option_update.py
_paths.py
update_frontmatter.py
update_section.py
validate_adr.py

```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/_io.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/_io.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Thin file read helpers over ``parse_rsk`` (Task 3.1).
19: 
20: Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
21: is no ``write_rsk``/``render_rsk`` counterpart here, since ``create_rsk``
22: and the generic ``update`` tool in ``general.tools`` persist the caller's
23: already-validated body markdown byte-for-byte rather than rendering it back
24: out from a parsed model -- no renderer is needed for that shape, so none is
25: added speculatively here.
26: Mirrors ``tsk.tools._io`` file-for-file.
27: 
28: No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
29: separate from any future ``@mcp.tool()``-decorated function so they stay
30: independently testable.
31: """
32: 
33: from __future__ import annotations
34: 
35: from pathlib import Path
36: 
37: from ..models.v1 import RskDocument, parse_rsk
38: from ._paths import find_rsk_path
39: 
40: __all__ = ["load_by_id", "read_rsk"]
41: 
42: 
43: def read_rsk(path: Path) -> RskDocument:
44:     """Read and parse the risk at ``path``.
45: 
46:     Parameters
47:     ----------
48:     path:
49:         The filesystem path to the risk ``.md`` file.
50: 
51:     Returns
52:     -------
53:     RskDocument
54:         The parsed, validated document.
55:     """
56:     assert isinstance(path, Path), type(path)
57: 
58:     result = parse_rsk(path.read_text(encoding="utf-8"))
59:     return result
60: 
61: 
62: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, RskDocument]:
63:     """Resolve ``id_`` under ``base_dir`` and read the matching risk.
64: 
65:     Parameters
66:     ----------
67:     base_dir:
68:         The directory to scan for ``*.md`` files.
69:     id_:
70:         The id to look up.
71: 
72:     Returns
73:     -------
74:     tuple[Path, RskDocument]
75:         The resolved file path and the parsed document -- callers that
76:         mutate the document need the path to write it back afterward.
77: 
78:     Raises
79:     ------
80:     RskNotFoundError
81:         If no file matches (propagated from :func:`._paths.find_rsk_path`).
82:     """
83:     assert isinstance(base_dir, Path), type(base_dir)
84:     assert isinstance(id_, str), type(id_)
85:     assert id_.strip()
86: 
87:     path = find_rsk_path(base_dir, id_)
88:     result = (path, read_rsk(path))
89:     return result

(End of file - total 89 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/_lock.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/_lock.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Per-document in-process lock guarding risk mutations.
19: 
20: Ported from ``tsk.tools._lock.tsk_lock`` unchanged except for naming -- see
21: that module's own docstring for the full rationale (the read-modify-write
22: race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
23: to when an MCP host dispatches two overlapping calls against the same id).
24: The generic ``update`` and ``set_status`` tools in ``general.tools``
25: (``type="rsk"``) wrap their whole sequence in ``with rsk_lock(id):``.
26: 
27: Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id
28: -> path lookup plumbing was generalized because it was already shared,
29: read-only, dependency-light code; a lock, by contrast, is a mutation-time
30: correctness primitive. Kept as its own small, RSK-specific module for now,
31: mirroring REQ's/TSK's own non-generalized precedent; migrating them all onto
32: one shared module remains optional future cleanup.
33: """
34: 
35: from __future__ import annotations
36: 
37: import threading
38: from collections.abc import Iterator
39: from contextlib import contextmanager
40: 
41: __all__ = ["rsk_lock"]
42: 
43: #: Guards creation of/lookup into `_locks` -- held only for the instant it
44: #: takes to get-or-create a per-id lock, never for the duration of a
45: #: mutation itself.
46: _registry_lock = threading.Lock()
47: 
48: #: One lock per risk id, created lazily on first use and never
49: #: removed -- the id space is small and long-lived relative to a server
50: #: process's lifetime, so there is no meaningful growth/cleanup concern here.
51: _locks: dict[str, threading.Lock] = {}
52: 
53: 
54: def _lock_for(id_: str) -> threading.Lock:
55:     """Return the (lazily created) lock instance for ``id_``."""
56:     with _registry_lock:
57:         lock = _locks.get(id_)
58:         if lock is None:
59:             lock = threading.Lock()
60:             _locks[id_] = lock
61:         return lock
62: 
63: 
64: @contextmanager
65: def rsk_lock(id_: str) -> Iterator[None]:
66:     """Serialize the read-modify-write mutation sequence for risk ``id_``.
67: 
68:     Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
69:     sequence in ``with rsk_lock(id):`` so two concurrent calls targeting the
70:     same id run one after another instead of interleaving, preventing the
71:     lost-update race described in this module's docstring.
72:     """
73:     lock = _lock_for(id_)
74:     with lock:
75:         yield

(End of file - total 75 lines)
</content>
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 20.7s)

_Thinking:_

With this I've understood the domain structure. Each domain has the following:

- `_io.py` with `load_by_id(base_dir, id_)`
- `_lock.py` with `<d>_lock(id_)`
- `_paths.py` with `find_<d>_path(base_dir, id_)` and `<d>_base_dir()`
- `_write.py` with `write_<d>_file(path, frontmatter, raw_body)`

Next, I'll check the following:

1. feat's `_paths.py` (the special folder layout)
2. The domain's `_paths.py` (rsk)
3. The `__init__.py` of a domain that registers delete (rsk/tools/__init__.py)
4. The ADRs that mandate delete stubs

Let me also check the error class for each domain. I'll look at rsk's `_paths.py` and the model, and find the definition of `RskNotFoundError`.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/_paths.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/_paths.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Risk base directory resolution and id -> path lookup (Task 3.1).
19: 
20: A thin, risk-specific layer over the generic ``general.tools._doc_paths``
21: module, rather than a second hand-written copy of ``req.tools._paths`` -- the
22: base-directory/id-lookup plumbing is identical in shape, only the parsed
23: document type and its id accessor differ. Mirrors ``tsk.tools._paths``
24: file-for-file.
25: 
26: Mirrors ``tsk.tools._paths``'s read-only/write split: :func:`rsk_base_dir`
27: never creates the directory (a read-only tool shouldn't have that side
28: effect), only :func:`ensure_rsk_base_dir` does, for ``create_rsk``. There is
29: deliberately no in-memory id -> path cache either -- every lookup re-scans
30: the base directory and re-parses each file, matching this codebase's "the
31: on-disk file is the sole source of truth" design.
32: """
33: 
34: from __future__ import annotations
35: 
36: from collections.abc import Iterator
37: from pathlib import Path
38: 
39: from ...general.tools._doc_paths import (
40:     DocNotFoundError,
41:     doc_base_dir,
42:     ensure_doc_base_dir,
43:     find_doc_path_by_id,
44:     iter_doc_paths,
45: )
46: from ..models.v1 import RskDocument, parse_rsk
47: 
48: __all__ = [
49:     "RSK_TYPE_NAME",
50:     "RskNotFoundError",
51:     "ensure_rsk_base_dir",
52:     "find_rsk_path",
53:     "iter_rsk_paths",
54:     "rsk_base_dir",
55: ]
56: 
57: #: The doc-type subdirectory name passed to ``general.tools._doc_paths``
58: #: (``{docs root}/rsk/``, e.g. ``docs/rsk``).
59: RSK_TYPE_NAME = "rsk"
60: 
61: 
62: class RskNotFoundError(LookupError):
63:     """No risk file found matching the given id.
64: 
65:     A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
66:     a subclass of it -- the same relationship ``tsk.tools._paths.TskNotFoundError``
67:     has to nothing generic, so callers can keep catching a risk-specific
68:     exception type without depending on the generic module's own exception.
69:     """
70: 
71: 
72: def rsk_base_dir() -> Path:
73:     """Return the configured risk base directory, without creating it.
74: 
75:     Thin wrapper over ``general.tools._doc_paths.doc_base_dir(RSK_TYPE_NAME)``
76:     -- see that function's own docstring for the env var/default it reads.
77: 
78:     Returns
79:     -------
80:     Path
81:         The resolved risk base directory.
82:     """
83:     result = doc_base_dir(RSK_TYPE_NAME)
84:     return result
85: 
86: 
87: def ensure_rsk_base_dir() -> Path:
88:     """Return the configured risk base directory, creating it if missing.
89: 
90:     Only ``create_rsk`` should call this -- every other tool/resource uses
91:     the read-only :func:`rsk_base_dir` instead.
92: 
93:     Returns
94:     -------
95:     Path
96:         The resolved, now-guaranteed-to-exist risk base directory.
97:     """
98:     result = ensure_doc_base_dir(RSK_TYPE_NAME)
99:     return result
100: 
101: 
102: def iter_rsk_paths() -> Iterator[Path]:
103:     """Yield every risk ``*.md`` file under :func:`rsk_base_dir`, sorted by name.
104: 
105:     Yields nothing (rather than raising) if the base directory does not exist.
106: 
107:     Returns
108:     -------
109:     Iterator[Path]
110:         An iterator over the matching, sorted paths.
111:     """
112:     result = iter_doc_paths(rsk_base_dir())
113:     return result
114: 
115: 
116: def _get_rsk_id(doc: RskDocument) -> str | None:
117:     """Extract the id from a parsed :class:`RskDocument` (``find_doc_path_by_id``'s ``get_id_fn``)."""
118:     result = doc.frontmatter.id
119:     return result
120: 
121: 
122: def find_rsk_path(base_dir: Path, id_: str) -> Path:
123:     """Resolve an ``id`` to its on-disk file path under ``base_dir``.
124: 
125:     Scans every ``*.md`` file under ``base_dir``, parsing each via
126:     :func:`~biz.dfch.specmgr.rsk.models.v1.parse_rsk` and comparing
127:     ``frontmatter.id`` against ``id_``. A file that fails to parse
128:     (``AssertionError``/``pydantic.ValidationError``) is silently skipped --
129:     one broken file must not prevent lookup of a different, valid id.
130:     Mirrors ``tsk.tools._paths.find_tsk_path``'s own skip-on-parse-failure
131:     rule.
132: 
133:     Parameters
134:     ----------
135:     base_dir:
136:         The directory to scan for ``*.md`` files.
137:     id_:
138:         The id to look up.
139: 
140:     Returns
141:     -------
142:     Path
143:         The resolved file path.
144: 
145:     Raises
146:     ------
147:     RskNotFoundError
148:         If no file's ``frontmatter.id`` matches ``id_``.
149:     """
150:     assert isinstance(base_dir, Path), type(base_dir)
151:     assert isinstance(id_, str), type(id_)
152:     assert id_.strip()
153: 
154:     try:
155:         result = find_doc_path_by_id(base_dir, id_, parse_rsk, _get_rsk_id)
156:     except DocNotFoundError as ex:
157:         raise RskNotFoundError(
158:             f"no risk found with id {id_!r}. The id must be the bare document UUID, without a domain "
159:             f"prefix (use '<uuid>', not 'rsk-<uuid>')."
160:         ) from ex
161:     return result

(End of file - total 161 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/_paths.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/_paths.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Feature (FEAT) base directory resolution and id -> path lookup (Task 2.1).
19: 
20: **Hand-rolled, ADR-style** (mirrors ``adr.tools._paths``), deliberately
21: **not** built on the shared, flat-file ``general.tools._doc_paths`` --
22: that module assumes one file per document directly under the base
23: directory (``<base>/<type>-<uuid>-<slug>.md``); ``feat`` is folder-per-
24: document instead (``<base>/<id>/README.md``, a fixed filename), and
25: ``id`` is a chosen ``feat-NNN-slug`` string, not a server-generated UUID.
26: See ``.specmgr/feat/feat-31-feature/README.md`` Design Notes
27: ("Addressing") for the full rationale.
28: 
29: Mirrors ``adr.tools._paths``'s read-only/write split: :func:`feat_base_dir`
30: never creates the directory (a read-only tool shouldn't have that side
31: effect), only :func:`ensure_feat_base_dir` does, for ``create_feat``. There
32: is deliberately no in-memory id -> path cache either -- every lookup
33: re-reads whatever is currently on disk, matching this codebase's "the
34: on-disk file is the sole source of truth" design.
35: 
36: **The key behavioral divergence from every other (UUID-addressed) domain**:
37: since ``id`` *is* the containing folder's own name by convention (REQ-004),
38: :func:`find_feat_path_by_id` shortcuts directly to ``<base>/<id_>/README.md``
39: instead of scanning every document under the base directory and comparing
40: each one's parsed ``frontmatter.id`` -- there is no directory scan, and
41: therefore no partial-id-match support either (a bare ``"feat-31"`` never
42: resolves to ``"feat-31-feature"``; see this feature's own Decisions Made log
43: for why that was considered and explicitly rejected).
44: 
45: **Parse-failure handling on the shortcut read.** Every other domain's
46: ``find_*_path`` scans multiple files and *skips* a file that fails to parse
47: (``AssertionError``/``pydantic.ValidationError``) so one broken file never
48: blocks lookup of a different, valid id -- there is no "different file" to
49: fall back to here, since the shortcut only ever reads one path. A parse
50: failure on that single target file is therefore treated the same as the
51: file not existing at all: both raise :class:`FeatNotFoundError`, just with
52: a message that distinguishes "the folder/file is missing" from "the folder
53: exists but its content is unparseable, or its frontmatter ``id`` does not
54: match the folder name it lives in" -- so ``load_by_id``/``get_feat``/every
55: mutating tool built on this module gets one single, consistent
56: not-found-shaped error to handle, without needing to separately catch
57: ``AssertionError``/``ValidationError`` themselves.
58: """
59: 
60: from __future__ import annotations
61: 
62: import os
63: import re
64: from collections.abc import Iterator
65: from pathlib import Path
66: 
67: from pydantic import ValidationError
68: 
69: from ...general.tools._doc_paths import slugify
70: from ..models.v1 import parse_feat
71: 
72: __all__ = [
73:     "DEFAULT_FEAT_DIR",
74:     "FEAT_DIR_ENV_VAR",
75:     "FEAT_TYPE_NAME",
76:     "README_FILENAME",
77:     "FeatNotFoundError",
78:     "ensure_feat_base_dir",
79:     "feat_base_dir",
80:     "feature_title",
81:     "find_feat_path_by_id",
82:     "iter_feat_paths",
83:     "slugify",
84: ]
85: 
86: #: Environment variable that overrides the feature base directory. Mandatory-
87: #: equivalent, like every other domain's own env var (``SPECMGR_ADR_DIR``,
88: #: the shared ``SPECMGR_DOCS_DIR``) -- without it, tests would have no way
89: #: to avoid reading/writing the real ``.specmgr/feat/`` (this very feature
90: #: plan's own folder).
91: FEAT_DIR_ENV_VAR = "SPECMGR_FEAT_DIR"
92: 
93: #: Default feature base directory, relative to the current working
94: #: directory -- the same folder this feature's own plan file lives in, in
95: #: production.
96: DEFAULT_FEAT_DIR = Path(".specmgr/feat")
97: 
98: #: The doc-type name, for symmetry with every other domain's own
99: #: ``<D>_TYPE_NAME`` constant (e.g. ``dec.tools._paths.DEC_TYPE_NAME``),
100: #: even though it plays no role in path construction here (unlike the
101: #: generic ``general.tools._doc_paths`` domains, ``feat``'s base directory
102: #: is not ``{docs root}/feat`` -- it *is* the configured base directory
103: #: itself).
104: FEAT_TYPE_NAME = "feat"
105: 
106: #: The fixed filename every feature document is stored under, inside its
107: #: own ``<base>/<id>/`` folder.
108: README_FILENAME = "README.md"
109: 
110: #: The literal prefix every well-formed ``Feature`` H1 heading carries.
111: #: ``Feature.text`` (inherited from ``MarkdownSection``) always returns the
112: #: *whole* heading line, e.g. ``"Feature: My Title"`` -- not just the
113: #: free-form title after the colon -- because `Feature`'s own ``@alias``
114: #: regex (``"^Feature: .+$"``) matches the entire line, and `Feature`
115: #: declares no ``title`` computed field of its own (unlike `Phase`/
116: #: `UpdateEntry`/`DecisionEntry`, each of which does). Both `create_feat`
117: #: (folder-name slug derivation) and `list_feat` (`FeatSummary.title`) need
118: #: just the free-form part, so :func:`feature_title` strips it once here
119: #: rather than duplicating the same two lines in both tools.
120: _TITLE_PREFIX = "Feature: "
121: 
122: #: Matches a ``feat-NNN-...`` folder name, capturing the numeric ``NNN``
123: #: part (unpadded, matching this very plan's own "Phase 0".."Phase 5"
124: #: numbering convention). Used by ``create_feat`` to derive the next id.
125: FEAT_FOLDER_PATTERN = re.compile(r"^feat-(\d+)-")
126: 
127: 
128: class FeatNotFoundError(LookupError):
129:     """No feature folder/document found matching the given id.
130: 
131:     Raised both when ``<base>/<id_>/README.md`` does not exist at all, and
132:     when it exists but fails to parse or its frontmatter ``id`` does not
133:     match the folder name it was found under -- see this module's own
134:     docstring for why both cases collapse to the same exception type here.
135:     """
136: 
137: 
138: def feat_base_dir() -> Path:
139:     """Return the configured feature base directory, without creating it.
140: 
141:     Reads :data:`FEAT_DIR_ENV_VAR` from the environment, falling back to
142:     :data:`DEFAULT_FEAT_DIR`. Read-only tools (``get_feat``, ``list_feat``,
143:     ...) use this so merely reading never has the side effect of creating
144:     the directory -- see :func:`ensure_feat_base_dir` for the write path.
145: 
146:     Returns
147:     -------
148:     Path
149:         The resolved feature base directory.
150:     """
151:     value = os.environ.get(FEAT_DIR_ENV_VAR)
152:     result = Path(value) if value else DEFAULT_FEAT_DIR
153:     return result
154: 
155: 
156: def ensure_feat_base_dir() -> Path:
157:     """Return the configured feature base directory, creating it if missing.
158: 
159:     Only ``create_feat`` should call this -- every other tool uses the
160:     read-only :func:`feat_base_dir` instead.
161: 
162:     Returns
163:     -------
164:     Path
165:         The resolved, now-guaranteed-to-exist feature base directory.
166:     """
167:     path = feat_base_dir()
168:     path.mkdir(parents=True, exist_ok=True)
169:     return path
170: 
171: 
172: def feature_title(text: str) -> str:
173:     """Strip the literal ``"Feature: "`` prefix off a ``Feature.text`` heading value.
174: 
175:     Parameters
176:     ----------
177:     text:
178:         A ``Feature.text`` value, e.g. ``"Feature: My Title"``.
179: 
180:     Returns
181:     -------
182:     str
183:         ``text`` with the literal ``"Feature: "`` prefix removed, if
184:         present (it always is for any ``Feature`` that parsed
185:         successfully, since the prefix is enforced by `Feature`'s own
186:         ``@alias`` regex) -- returned unchanged otherwise.
187:     """
188:     assert isinstance(text, str), type(text)
189: 
190:     result = text.removeprefix(_TITLE_PREFIX)
191:     return result
192: 
193: 
194: def iter_feat_paths(base_dir: Path) -> Iterator[Path]:
195:     """Yield every ``<base_dir>/*/README.md`` path, sorted by folder name.
196: 
197:     Unlike every generic-``_doc_paths``-based domain's ``iter_*_paths``
198:     (which globs ``*.md`` directly under the base directory), this globs
199:     one level deeper -- ``*/README.md`` -- since ``feat`` is folder-per-
200:     document, not flat-file. Yields nothing (rather than raising) if
201:     ``base_dir`` does not exist.
202: 
203:     Parameters
204:     ----------
205:     base_dir:
206:         The feature base directory to scan (typically :func:`feat_base_dir`'s
207:         return value).
208: 
209:     Returns
210:     -------
211:     Iterator[Path]
212:         An iterator over the matching, sorted paths.
213:     """
214:     assert isinstance(base_dir, Path), type(base_dir)
215: 
216:     if not base_dir.exists():
217:         return iter(())
218:     result = iter(sorted(base_dir.glob(f"*/{README_FILENAME}")))
219:     return result
220: 
221: 
222: def find_feat_path_by_id(base_dir: Path, id_: str) -> Path:
223:     """Resolve ``id_`` to its on-disk ``README.md`` path under ``base_dir``.
224: 
225:     Shortcuts directly to ``<base_dir>/<id_>/README.md`` -- since ``id`` is,
226:     by REQ-004's addressing convention, the containing folder's own name,
227:     there is no need (and deliberately no support) for a full directory
228:     scan or partial-id matching (see this module's own docstring).
229: 
230:     Parameters
231:     ----------
232:     base_dir:
233:         The feature base directory (typically :func:`feat_base_dir`'s
234:         return value).
235:     id_:
236:         The id to look up -- must be the *exact* folder name, e.g.
237:         ``"feat-31-feature"``, not a bare ``"feat-31"`` prefix.
238: 
239:     Returns
240:     -------
241:     Path
242:         The resolved ``README.md`` path.
243: 
244:     Raises
245:     ------
246:     FeatNotFoundError
247:         If ``<base_dir>/<id_>/README.md`` does not exist, if it exists but
248:         fails to parse (``AssertionError``/``pydantic.ValidationError``),
249:         or if it parses but its frontmatter ``id`` does not match ``id_``
250:         (a folder/frontmatter mismatch, surfaced rather than silently
251:         worked around).
252:     """
253:     assert isinstance(base_dir, Path), type(base_dir)
254:     assert isinstance(id_, str), type(id_)
255:     assert id_.strip()
256: 
257:     path = base_dir / id_ / README_FILENAME
258:     if not path.exists():
259:         raise FeatNotFoundError(
260:             f"no feature found with id {id_!r}: {path} does not exist. The id must be the exact "
261:             f"containing folder's name (e.g. 'feat-31-feature'), not a bare prefix like 'feat-31' -- "
262:             f"use list_feat to discover the exact id first."
263:         )
264: 
265:     try:
266:         doc = parse_feat(path.read_text(encoding="utf-8"))
267:     except (AssertionError, ValidationError) as ex:
268:         raise FeatNotFoundError(
269:             f"feature folder {id_!r} exists at {path}, but its content could not be parsed as a valid "
270:             f"feature document ({type(ex).__name__}: {ex})."
271:         ) from ex
272: 
273:     if doc.frontmatter.id != id_:
274:         raise FeatNotFoundError(
275:             f"feature folder {id_!r} exists at {path}, but its frontmatter id ({doc.frontmatter.id!r}) "
276:             f"does not match the containing folder's own name ({id_!r}) -- the folder was likely "
277:             f"renamed or copied without updating its frontmatter."
278:         )
279: 
280:     result = path
281:     return result

(End of file - total 281 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/__init__.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/__init__.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """MCP tool wrappers for risks (mirrors ``tsk/tools/``'s own shape).
19: 
20: ``parse_rsk`` reads a raw filepath, parses, and validates it into a
21: structured document model. ``get_rsk_example`` returns a complete, valid
22: sample risk document as raw markdown; ``get_rsk_template`` returns a
23: document with every field present but populated with short placeholder
24: ("blind text") content instead -- both read a packaged, build-guaranteed
25: data file rather than anything on the caller's filesystem. ``get_rsk``
26: reads, parses, and returns a full risk document by id -- the sole id-based
27: read path for RSK (there never was a ``specmgr://rsk/{id}`` resource to
28: begin with). ``list_rsk`` (Task 3.14) returns one page of
29: id/title/status/ref summaries of every risk, plus the initial/residual 5x5
30: zone levels, the TARA strategy word, the first ``## Scope`` entry, and the
31: residual-risk coordinates (``RskSummary``), so that ``max_results``/
32: ``offset`` paging parameters can be accepted (feat-13-list-paging, ADR
33: ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_rsk`` assigns a fresh id,
34: builds the frontmatter itself, and writes a new document (body markdown
35: only, no frontmatter) under the risk base directory (``rsk.tools._paths``/
36: ``_io``). Whole-body and line-range updates of an existing document go
37: through the generic ``update`` tool in ``general.tools`` (``type="rsk"``),
38: preserving every frontmatter field except ``updated``. Status changes of an
39: existing document go through the generic ``set_status`` tool in
40: ``general.tools`` (``type="rsk"``), also bumping ``updated``, leaving the
41: body untouched. ``delete_rsk`` is a registered stub -- always raises
42: ``NotImplementedError``, reserving the name for a future real
43: implementation. ``validate_rsk`` is a disk-free, id-free dry run against a
44: submitted ``content`` string, independent of the other tools. Import this
45: package to register all risk tools at once::
46: 
47:     from biz.dfch.specmgr.rsk import tools  # noqa: F401 (side-effects only)
48: """
49: 
50: from .create_rsk import create_rsk
51: from .delete_rsk import delete_rsk
52: from .get_rsk import get_rsk
53: from .get_rsk_example import get_rsk_example
54: from .get_rsk_template import get_rsk_template
55: from .list_rsk import list_rsk
56: from .parse_rsk import parse_rsk
57: from .validate_rsk import validate_rsk
58: 
59: __all__ = [
60:     "create_rsk",
61:     "delete_rsk",
62:     "get_rsk",
63:     "get_rsk_example",
64:     "get_rsk_template",
65:     "list_rsk",
66:     "parse_rsk",
67:     "validate_rsk",
68: ]

(End of file - total 68 lines)
</content>
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 22.6s)

_Thinking:_

Okay, I've got a solid understanding of the codebase now. Next things to check:

1. The ADRs that mandate the delete stubs (the "decisions and documents" that need updating)
2. The docstring in `server.py` (the authoritative list of tools)
3. Existing tests for the generic tools (to understand the test patterns)
4. Check the conventions in `.specmgr/conventions.md`
5. Check existing feature plans to follow the structure of the feature README

Let's search for references to the delete stubs in the ADRs and documentation.

Now let me find the ADRs/documents that mandate delete stubs, and examine the test patterns for generic tools.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rln \"delete_\" /home/user/src/biz.dfch.SpecMgr/docs/adr/ /home/user/src/biz.dfch.SpecMgr/docs/ /home/user/src/biz.dfch.SpecMgr/.specmgr/ 2>/dev/null | grep -v __pycache__ | sort"
}
```

**Output:**

```
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.dec.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.dec.tools.delete_dec.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.dec.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.feat.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.feat.tools.delete_feat.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.feat.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.gol.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.gol.tools.delete_gol.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.gol.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.prb.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.prb.tools.delete_prb.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.prb.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.qa.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.qa.tools.delete_qa.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.qa.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.req.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.req.tools.delete_req.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.req.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.rsk.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.rsk.tools.delete_rsk.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.rsk.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.server.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.sop.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.sop.tools.delete_sop.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.sop.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.tsk.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.tsk.tools.delete_tsk.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.tsk.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.uc.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.uc.tools.delete_uc.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.uc.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.vcr.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.vcr.tools.delete_vcr.md
/home/user/src/biz.dfch.SpecMgr/docs/api/biz.dfch.specmgr.vcr.tools.md
/home/user/src/biz.dfch.SpecMgr/docs/api/README.md
/home/user/src/biz.dfch.SpecMgr/docs/GENERATED.md
/home/user/src/biz.dfch.SpecMgr/docs/MCP.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/session-ses_ff52-feat-10-task-list.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/session-ses_ff52-feat-7-task-list.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-12-qa-artifact/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-12-qa-artifact/session-ses_feab-feat-12-qa-artifact.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-14-qa-v2-adjacent-qa/session-ses_fd23-feat-14-00.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/session-ses_fcc0-feat-15-01.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/session-ses_fccf-feat-15-00.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-16-problem-statement/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-16-problem-statement/session-ses_fc85-feat-16-01.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-16-problem-statement/session-ses_fc87-feat-16-00.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/session-ses_fc59-feat-18-01-implementation.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/session-ses_fc5c-feat-18-00.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-21-decision/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-21-decision/session-ses_fc01-feat-21-01-implementation.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-21-decision/session-ses_fc08-feat-21-00-design.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-22-consolidate-mutation-tools/session-ses_fbc5-feat-22-02-merge.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-22-consolidate-mutation-tools/session-ses_fbfe-feat-22-01-implementation.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-22-consolidate-mutation-tools/session-ses_fc05-feat-22.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/session-ses_fae2-feat-30-03-impl.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/session-ses_fae3-feat-30-02-design.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/session-ses_fae5-feat-30-01-desgin.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/session-ses_fb36-feat-30-00-desgin.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/session-ses_fac1-feat-31-02-impl.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/session-ses_fad1-feat-31-01-impl.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/session-ses_fad9-feat-31-01-design.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/session-ses_fadb-feat-31-00-design.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-33-vcr/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-33-vcr/session-ses_fa86-feat-33-03-pr.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-33-vcr/session-ses_fa96-feat-33-02-impl.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-33-vcr/session-ses_fa99-feat-33-01-design.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-33-vcr/session-ses_fa9f-feat-33-00-design.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/history.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-6-requirement-artifact/README.md
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/session-ses_fa86-feat-7-00-release-script.md

```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rln \"delete_\\|NotImplementedError\\|delete tool\\|delete stub\\|deletion\" /home/user/src/biz.dfch.SpecMgr/tests/ 2>/dev/null | sort | head -40"
}
```

**Output:**

```
/home/user/src/biz.dfch.SpecMgr/tests/adr/tools/__pycache__/test_option_delete.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/adr/tools/test_option_delete.py
/home/user/src/biz.dfch.SpecMgr/tests/dec/tools/__pycache__/test_delete_dec.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/dec/tools/__pycache__/test_integration.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/dec/tools/test_delete_dec.py
/home/user/src/biz.dfch.SpecMgr/tests/dec/tools/test_integration.py
/home/user/src/biz.dfch.SpecMgr/tests/feat/tools/__pycache__/test_delete_feat.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/feat/tools/__pycache__/test_integration.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/feat/tools/test_delete_feat.py
/home/user/src/biz.dfch.SpecMgr/tests/feat/tools/test_integration.py
/home/user/src/biz.dfch.SpecMgr/tests/general/tools/test_update.py
/home/user/src/biz.dfch.SpecMgr/tests/gol/tools/__pycache__/test_delete_gol.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/gol/tools/__pycache__/test_integration.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/gol/tools/test_delete_gol.py
/home/user/src/biz.dfch.SpecMgr/tests/gol/tools/test_integration.py
/home/user/src/biz.dfch.SpecMgr/tests/models/adr/v1/__pycache__/test_mutations.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/models/adr/v1/test_mutations.py
/home/user/src/biz.dfch.SpecMgr/tests/prb/tools/__pycache__/test_delete_prb.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/prb/tools/__pycache__/test_integration.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/prb/tools/test_delete_prb.py
/home/user/src/biz.dfch.SpecMgr/tests/prb/tools/test_integration.py
/home/user/src/biz.dfch.SpecMgr/tests/qa/tools/__pycache__/test_delete_qa.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/qa/tools/test_delete_qa.py
/home/user/src/biz.dfch.SpecMgr/tests/req/tools/__pycache__/test_delete_req.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/req/tools/test_delete_req.py
/home/user/src/biz.dfch.SpecMgr/tests/rsk/tools/__pycache__/test_delete_rsk.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/rsk/tools/test_delete_rsk.py
/home/user/src/biz.dfch.SpecMgr/tests/sop/tools/__pycache__/test_delete_sop.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/sop/tools/__pycache__/test_integration.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/sop/tools/test_delete_sop.py
/home/user/src/biz.dfch.SpecMgr/tests/sop/tools/test_integration.py
/home/user/src/biz.dfch.SpecMgr/tests/tsk/tools/__pycache__/test_delete_tsk.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/tsk/tools/test_delete_tsk.py
/home/user/src/biz.dfch.SpecMgr/tests/uc/tools/__pycache__/test_delete_uc.cpython-313.pyc
/home/user/src/biz.dfch.SpecMgr/tests/uc/tools/test_delete_uc.py
/home/user/src/biz.dfch.SpecMgr/tests/vcr/tools/test_delete_vcr.py
/home/user/src/biz.dfch.SpecMgr/tests/vcr/tools/test_integration.py

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 23.7s)

_Thinking:_

Now I have a grasp of the overall picture. What needs to be checked next is:

1. The ADR that decided on the delete stub — probably the feat-22 ADR, or the "dispatch only" ADR (36905d5b-8057-4294-8665-c7eed5534db0). Let me look for the relevant ADR in docs/adr/.
2. The test patterns for the generic `set_status` tool (tests/general/tools/test_set_status.py?)
3. The feature README structure (the feat-33-vcr or feat-21-decision plan as the newest one)

Let me check the ADR directory, and the tests/general/tools directory.

**Tool: bash**

**Input:**

```json
{
  "command": "ls /home/user/src/biz.dfch.SpecMgr/docs/adr/ && echo \"---TESTS GENERAL---\" && ls /home/user/src/biz.dfch.SpecMgr/tests/general/tools/ && echo \"---CONVENTIONS---\" && ls /home/user/src/biz.dfch.SpecMgr/.specmgr/"
}
```

**Output:**

```
23a14195-339c-48af-99d2-97c9964041ae-use-iso-8601-for-all-dates-and-times.md
3159caf2-4beb-43f2-9f5d-8f46be0211af-adopt-icontract-as-the-design-by-contract-library-for-specmg.md
33c5ab08-ff58-4c73-8c32-23abaf3838e3-filesystem-is-the-sole-source-of-truth-no-in-memory-id-to-do.md
36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md
3bf0326f-065a-424c-a2b9-87e5d5bcfa99-extract-mcp-singleton-into-its-own-module-to-break-domain-se.md
4c6119c9-532f-4629-8977-108e78304f48-parse-validate-render-pipeline-library-choices-no-ast-preser.md
71fd95d7-07f2-466f-81aa-d29b7e3ef34c-generic-update-section-key-value-with-deletion-sentinel-and.md
737858a9-7796-4f01-ae35-5afc1c707818-use-pre-commit-hooks-for-local-quality-gates.md
7531106b-074b-4bd8-a83a-e433d01676e2-expose-listing-and-by-id-reads-as-mcp-resources-in-addition.md
832cd6c1-ef8a-4bfc-990e-a610823f61ae-generic-heading-mapped-markdown-to-pydantic-parsing-with-dec.md
898bfcd0-85f9-462f-93a8-747bda4166c8-author-and-edit-adrs-only-through-mcp-structured-tools-never.md
8cf940c5-3100-485c-a12d-14b59b631712-id-filename-addressing-scheme-server-generated-uuid-id-slug.md
9c687bb1-8ee7-41c8-84ec-07606356bc73-enforce-doc-generation-lint-and-tests-locally-via-pre-commit.md
9d3800cf-b3b4-4d46-8b68-3573d932b1c8-detect-unreferenced-code-with-vulture-not-snakefood-enforced.md
bbf412a7-965e-4435-8669-c338407d73b7-frontmatter-extension-fields-id-version-with-whole-object-fu.md
bc5e18ad-6bbf-4265-bae4-3e34984a2d29-generic-base-frontmatter-model-for-markdown-document-types-m.md
c73e4f9d-81f3-495d-bd3a-f660ab992ed3-base-the-adr-template-on-madr-4-0-0.md
cb5a2d5f-7020-4c6e-b28d-a38d17b23243-use-conventional-commits-for-commit-messages.md
d54abe50-a2c5-44f8-8bfe-11ea634b6f87-pros-and-cons-of-the-options-as-a-derived-container-with-a-d.md
ddd038f0-ae16-4f4b-beef-df06f7ed226f-prompt-surface-narrated-guidance-plus-step-gated-test-varian.md
ddfb1109-422d-4507-8dbc-dc5e4bec9614-expose-id-based-req-document-reads-as-a-tool-get-req-not-a-r.md
e11421d3-cc1d-487b-af32-ee4093422712-use-architecture-decision-records-adrs-to-document-design-de.md
e369ee2e-3353-4f92-991c-6367d76d832e-organize-development-artifacts-in-specmgr-with-feature.md
ec9f5262-9912-49d0-903f-fcfb54f28c13-expose-domain-list-as-paged-mcp-tools-list-domain-not-resour.md
ece4554b-725c-4f76-bc04-5d2b760363d2-organize-the-codebase-by-document-type-domain-domain-first-h.md
README.md
---TESTS GENERAL---
__init__.py
__pycache__
test__doc_paths.py
test_mdformat.py
test__packaged_data.py
test_paging.py
test_set_status.py
test_update.py
test_webfetch.py
---CONVENTIONS---
conventions.md
feat
_template

```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rln \"delete\" /home/user/src/biz.dfch.SpecMgr/docs/adr/*.md | sort"
}
```

**Output:**

```
/home/user/src/biz.dfch.SpecMgr/docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md
/home/user/src/biz.dfch.SpecMgr/docs/adr/71fd95d7-07f2-466f-81aa-d29b7e3ef34c-generic-update-section-key-value-with-deletion-sentinel-and.md
/home/user/src/biz.dfch.SpecMgr/docs/adr/898bfcd0-85f9-462f-93a8-747bda4166c8-author-and-edit-adrs-only-through-mcp-structured-tools-never.md
/home/user/src/biz.dfch.SpecMgr/docs/adr/9d3800cf-b3b4-4d46-8b68-3573d932b1c8-detect-unreferenced-code-with-vulture-not-snakefood-enforced.md
/home/user/src/biz.dfch.SpecMgr/docs/adr/d54abe50-a2c5-44f8-8bfe-11ea634b6f87-pros-and-cons-of-the-options-as-a-derived-container-with-a-d.md

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 26.2s)

_Thinking:_

Let me look at ADR 36905d5b (the consolidation of update and set_status) — this is the precedent for the generic tool, and it probably mentions the delete stub. Let me check the important sections, and also look at ADR 898bfcd0 (which states that ADRs are edited only via MCP tools) — this is important, because this feature needs to update ADRs, and per that ADR, ADRs are only edited via MCP tools (update_section / option tools), not by hand.

Let me also check the following:

1. The test patterns in test_set_status.py
2. The structure of a recent feature's README (feat-33-vcr) — to model the new feature's plan on it
3. conventions.md

First, let me read the 36905d5b ADR (which is the key precedent).

Let me read the key ADR (generic-tool consolidation precedent) and check how it treats deletion.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n -i \"delete\" /home/user/src/biz.dfch.SpecMgr/docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md"
}
```

**Output:**

```
30:Option 1: two generic, type-dispatched tools — `update(id, type, content, begin, end)` in `general/tools/update.py` for the seven whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`), and `set_status(id, type, status, superseded_by)` in `general/tools/set_status.py` for all eight domains including `adr`. The explicit `type` parameter keeps id resolution single-domain (no directory scan, no cross-domain UUID ambiguity), matches the domain vocabulary the calling client already has, and reduces the tool surface from 15 near-duplicate entries to 2. Each domain's semantics are preserved 1:1 by a private adapter that is a verbatim port of the deleted tool body, so the filesystem-is-source-of-truth and validate-before-write invariants are untouched.
49:- Preserves all per-domain semantics: each adapter is a verbatim port of the deleted tool body (same lock, same `load_by_id`, same frontmatter carry-over and `updated` bump, same write path, same domain not-found error), and the filesystem-is-source-of-truth and validate-before-write invariants are untouched.

```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/tests/general/tools/test_set_status.py",
  "limit": 150
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/tests/general/tools/test_set_status.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Tests for the generic ``set_status`` ``@mcp.tool()`` wrapper (feat-22-consolidate-mutation-tools, Phase 4).
19: 
20: Parameterized over all twelve document types (ACC-004); seeds a real,
21: persisted document per type -- the eleven whole-body domains via the
22: domain's own ``create_<d>`` tool in a temp ``SPECMGR_DOCS_DIR`` (mirroring
23: the fixture strategy of ``tests/general/tools/test_update.py``), the ADR
24: by rendering a minimal valid model into a temp ``SPECMGR_ADR_DIR`` -- and
25: covers: status changed + ``updated`` bumped (microsecond timestamp) + body
26: untouched (eleven domains: raw body byte-identical; ADR: re-render round-
27: trip equal apart from status); each domain's closed-vocabulary
28: enforcement (positive value from the domain's own ``_ALLOWED_STATUSES``;
29: negative value valid in one domain but invalid in the tested one -- each a
30: ``pydantic.ValidationError`` with the file left byte-identical on disk);
31: the ADR-only ``superseded_by`` composition (``"superseded by X"`` in the
32: file) and the guard that rejects it for every non-``adr`` type *before*
33: any file access; and the per-domain not-found errors for an unknown id.
34: 
35: The per-type case data ties each ``valid_status``/``invalid_status`` pair
36: to the domain's own closed set (the authoritative source of truth in
37: ``models/<v>/frontmatter.py`` -- imported as a private name here on
38: purpose) -- the case-data test asserts the membership relations rather
39: than trusting the pair literals.
40: """
41: 
42: from __future__ import annotations
43: 
44: import re
45: import tempfile
46: import textwrap
47: import unittest
48: from dataclasses import dataclass
49: from pathlib import Path
50: from typing import Any, Callable
51: from unittest import mock
52: 
53: import frontmatter
54: from pydantic import ValidationError
55: 
56: from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR, AdrNotFoundError
57: from biz.dfch.specmgr.dec.models.v1.frontmatter import _ALLOWED_STATUSES as _DEC_ALLOWED_STATUSES
58: from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError
59: from biz.dfch.specmgr.dec.tools.create_dec import create_dec
60: from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
61: from biz.dfch.specmgr.general.tools._splice import body_text
62: from biz.dfch.specmgr.general.tools.set_status import set_status
63: from biz.dfch.specmgr.gol.models.v1.frontmatter import _ALLOWED_STATUSES as _GOL_ALLOWED_STATUSES
64: from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError
65: from biz.dfch.specmgr.gol.tools.create_gol import create_gol
66: from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter, parse_adr, render_adr
67: from biz.dfch.specmgr.models.adr.v1.frontmatter import _FIXED_STATUSES as _ADR_ALLOWED_STATUSES
68: from biz.dfch.specmgr.prb.models.v1.frontmatter import _ALLOWED_STATUSES as _PRB_ALLOWED_STATUSES
69: from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError
70: from biz.dfch.specmgr.prb.tools.create_prb import create_prb
71: from biz.dfch.specmgr.qa.models.v2.frontmatter import _ALLOWED_STATUSES as _QA_ALLOWED_STATUSES
72: from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError
73: from biz.dfch.specmgr.qa.tools.create_qa import create_qa
74: from biz.dfch.specmgr.req.models.v1.frontmatter import _ALLOWED_STATUSES as _REQ_ALLOWED_STATUSES
75: from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError
76: from biz.dfch.specmgr.req.tools.create_req import create_req
77: from biz.dfch.specmgr.rsk.models.v1.frontmatter import _ALLOWED_STATUSES as _RSK_ALLOWED_STATUSES
78: from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError
79: from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
80: from biz.dfch.specmgr.sop.models.v1.frontmatter import _ALLOWED_STATUSES as _SOP_ALLOWED_STATUSES
81: from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError
82: from biz.dfch.specmgr.sop.tools.create_sop import create_sop
83: from biz.dfch.specmgr.tsk.models.v1.frontmatter import _ALLOWED_STATUSES as _TSK_ALLOWED_STATUSES
84: from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError
85: from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
86: from biz.dfch.specmgr.uc.models.v2.frontmatter import _ALLOWED_STATUSES as _UC_ALLOWED_STATUSES
87: from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError
88: from biz.dfch.specmgr.uc.tools.create_uc import create_uc
89: from biz.dfch.specmgr.vcr.models.v1.frontmatter import _ALLOWED_STATUSES as _VCR_ALLOWED_STATUSES
90: from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError
91: from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr
92: 
93: #: ISO-8601 microsecond timestamp shape (the ``updated`` bump precision).
94: _MICROSECOND_TIMESTAMP = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}"
95: 
96: _REQ_MINIMAL_BODY = textwrap.dedent(
97:     """\
98:     # Maximum Engine Temperature
99: 
100:     WHILE the engine is running, THE temperature must be a maximum of 80 °C.
101: 
102:     ## Description
103: 
104:     If the engine becomes too hot, the lifetime of the system decreases.
105: 
106:     ## Characteristics
107: 
108:     1. Safety
109:     1. Reliability
110: 
111:     ## Level
112: 
113:     MUST
114: 
115:     ## Source
116: 
117:     The International Safety Board Association (TISBA)
118:     """
119: )
120: 
121: _UC_MINIMAL_BODY = textwrap.dedent(
122:     """\
123:     # Buy Goods
124: 
125:     ## Characteristic Information
126: 
127:     ### Goal in Context
128: 
129:     Buyer issues request directly to our company.
130: 
131:     ### Scope
132: 
133:     Company (the system being designed as a black box)
134: 
135:     ### Level
136: 
137:     Summary
138: 
139:     ### Preconditions
140: 
141:     - We know Buyer
142: 
143:     ### Success End Condition
144: 
145:     - Buyer has goods
146: 
147:     ### Primary Actor
148: 
149:     Buyer.
150: 

(Showing lines 1-150 of 629. Use offset=151 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 51.3s)

_Thinking:_

Now I understand the test pattern. Let me confirm:

1. The ADR for "Author/edit ADRs only through MCP structured tools" (898bfcd0) — this is important because the feature needs to update the ADR.
2. Recent feature plans (e.g., feat-33-vcr/README.md) to model the plan structure on.
3. conventions.md for coding conventions.

Also, I need to check `server.py`'s docstring to understand how tools are listed, and see how MCP.md is generated.

Key design questions that the feature plan needs to answer:

1. **Which domains should the generic `delete` cover?** The issue says "every domain (except ADR?)" — the delete stub exists in 11 whole-body domains (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr). ADR has no delete_adr stub. The issue asks "except ADR?" — so a decision is needed: should the generic delete also cover ADR? Let me check: ADR is under `models/adr` and has a `write_adr` round-trip. For consistency, the generic delete might cover all 12 domains including ADR, or just the 11. This is a design decision that should be flagged.

2. **Delete semantics**: hard delete (remove file from disk) or soft delete (status)? The issue clearly says "find the artifact to be deleted" and "lock when finding and deleting the file" — so it's a hard delete from disk. For feat (folder-per-document), deletion means removing the entire folder `<base>/<id>/` (README.md and probably history.md too!). This is an important nuance: feat-36's own folder... wait, but feat's id is `feat-NNN-slug`, not a UUID. The issue says the generic delete uses "type + uuid". But feat's id is not a UUID! This is an important design consideration that must be flagged. The feat adapter will end up taking a `feat-NNN-slug` id. The issue's "uuid" wording is loose, and the actual contract is "the domain's id".

3. **Path injection safety**:

   - `type` is a `Literal[...]` — closed vocabulary, so no injection via type (this is the same as set_status).
   - `id`/uuid — must be validated as str. The real injection risk is in `id`: if the id is used to build a path (especially feat's shortcut `base_dir / id / README.md`), a malicious id like `../something` could escape the base directory. Also in flat domains, `find_*_path` scans files, so a malicious id just doesn't match (safe), but the `id_` assertion `id_.strip()` is only an assert. We need to validate that id doesn't contain path separators or `..`. The issue explicitly says: "no one should be able to 'inject' relative paths via either type or uuid."
   - So we need input validation: type is a closed Literal (already safe), and id must be a str that doesn't contain `/`, `\`, or `..`, and for UUID domains should match a UUID pattern. For feat it should match the `feat-NNN-slug` pattern.

4. **Lock**: reuse each domain's existing `<d>_lock(id_)`.

5. **Exception handling**: "handle all exceptions gracefully. e.g., pass them to the caller with a meaningful error message." So wrap the operation and convert unexpected exceptions into meaningful errors. But the domain's not-found error should probably propagate as-is (same as set_status). Need to think about what "gracefully" means — probably: catch OSError etc. during deletion and re-raise with a meaningful message, or return an error. MCP tools usually raise, and the MCP SDK converts that to an error response. Let me think — the issue says "pass to the caller with a meaningful error message." So catching and re-raising with context, or converting to a specific error, is probably right.

Now, let me read the ADR that restricts ADR editing and the recent feature plan to check conventions. Let me also check server.py's docstring and how MCP.md is generated.

Let me do this efficiently. What to read:

- ADR 898bfcd0 (edit ADRs only through MCP)
- feat-33-vcr/README.md (recent feature plan structure)
- conventions.md
- server.py's docstring (the top part)

Actually, let me be strategic. The key deliverable is a PLAN (feature README) + setting up the worktree/branch. Let me gather enough info to write a solid plan. Let me read a few more important things in parallel.

Let me examine the ADR-authoring constraint, a recent feature plan for structure, and coding conventions.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/docs/adr/898bfcd0-85f9-462f-93a8-747bda4166c8-author-and-edit-adrs-only-through-mcp-structured-tools-never.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/docs/adr/898bfcd0-85f9-462f-93a8-747bda4166c8-author-and-edit-adrs-only-through-mcp-structured-tools-never.md</path>
<type>file</type>
<content>
1: ---
2: status: accepted
3: decision-makers: dfch
4: id: 898bfcd0-85f9-462f-93a8-747bda4166c8
5: version: 1.0.0
6: ---
7: 
8: # Author and edit ADRs only through MCP structured tools, never raw markdown
9: 
10: ## Context and Problem Statement
11: 
12: ADRs must be created and edited by an LLM through an MCP server. The LLM could approach this in two ways: (1) directly manipulating raw markdown files and trusting the result will be valid, or (2) calling structured MCP tools that enforce the schema and handle all parsing/validation/rendering internally. Raw markdown editing is error-prone (missing frontmatter, malformed YAML, inconsistent heading structure) and difficult to validate without round-trip parsing.
13: 
14: ## Decision Drivers
15: 
16: Reliability and correctness of generated ADRs; auditability of changes through structured tool calls; centralized schema validation to catch errors early; preventing malformed documents from being written to disk.
17: 
18: ## Considered Options
19: 
20: LLM writes raw markdown files directly vs. LLM calls structured MCP tools (create_adr, update_section, option_create, etc.) that enforce schema and handle all file I/O.
21: 
22: ## Decision Outcome
23: 
24: Expose only MCP tools (create_adr, update_frontmatter, update_section, set_status, option_list/create/read/update/delete, validate_adr). The LLM must use these tools; direct markdown editing is not available. Each tool re-reads the current on-disk state, applies the mutation through in-memory Pydantic models (ensuring schema compliance), validates the result, and writes back the full file deterministically. This ensures every edit round-trips through validation.
25: 
26: ### Consequences
27: 
28: All ADR edits go through a single, auditable code path. Schema violations are caught immediately by Pydantic, before writing. The LLM cannot accidentally create malformed frontmatter or missing required sections. Trade-off: the LLM must learn the tool names and parameters rather than directly manipulating prose.
29: 
30: ## More Information
31: 
32: See MCP tool definitions in `biz.dfch.specmgr.adr.tools`: create_adr, update_frontmatter, update_section, set_status, option_create, option_update, option_read, option_delete, option_list, get_adr, validate_adr.

(End of file - total 32 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-33-vcr/README.md"
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-33-vcr/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-31 07:25:24.241609
3: id: feat-33-vcr
4: status: done
5: type: feat
6: updated: 2026-08-31 16:26:00
7: version: 1.2.0
8: ---
9: 
10: # Feature: Add artifact type "Verification Case Record" (VCR)
11: 
12: ## Plan
13: 
14: ### Overview
15: 
16: New document-type domain, `vcr` ("Verification Case Record"), that captures
17: how a single requirement or use case is verified: a coverage assessment plus
18: a list of acceptance criteria, each with its own DTAIS verification method.
19: Fills a gap identified during `feat-32-sysrs` (System Specification)
20: planning -- see that feature's README, Design Notes, "Domain-to-source
21: mapping" table and "Not yet decided" list: no existing specmgr domain
22: models ISO/IEC/IEEE 29148's / MITRE SE Guide's "Verification / Test and
23: Evaluation" concept. Tracked by GitHub issue #33. Follows the domain-first
24: hierarchy (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and lands on the
25: "simple surface" from day one (generic `update`/`set_status` dispatch, per
26: ADR 36905d5b-8057-4294-8665-c7eed5534db0 -- no per-domain mutation tools,
27: including no per-AC create/read/update/delete tools).
28: 
29: Domain key: `vcr`.
30: 
31: ### Requirements
32: 
33: - REQ-001 (decided): `## Verifies` references **exactly one** REQ or UC --
34:   modeled as a `Verifies(MarkdownSection2WithComment)` with a single
35:   mandatory `value: MarkdownParagraph` line ("`REQ|UC <uuid>: <title>`",
36:   `field_validator`-regex-checked) plus a **mandatory** `notes: MarkdownParagraph` paraphrase (in fixed declaration order, mirroring
37:   RSK's `Assessment.probability`/`.impact` two-mandatory-fields idiom) and
38:   an optional leading HTML `comment`. **Not** a bullet list -- no
39:   cardinality `model_validator` is needed, since a single-value field is
40:   structurally incapable of holding more than one reference; see the
41:   "single-value-field over list-of-one" decision in Design Notes and
42:   Decisions Made below (this supersedes the original
43:   `MarkdownListItemWithNotes` design). Resolves the previously-open "id is
44:   a real UUID, not a human code" gap shared with `sysrs`'s own REQ-003.
45: - REQ-002 (decided): `## Coverage` is a closed vocabulary paragraph --
46:   `full` / `partial` / `none` -- mirroring `rsk`'s `## Strategy` pattern
47:   (`MarkdownParagraph` + `field_validator` regex).
48: - REQ-003 (decided): `## Acceptance Criteria` holds >= 1 repeating
49:   `### AC-NNN (Method): <criterion text>` sub-sections (3-digit
50:   zero-padded number, e.g. `AC-001`), DEC-Option-style (numbered H3, no
51:   per-item mutation tools). `Method` is parsed from the heading itself via
52:   regex (RSK `Probability`/`Impact` idiom) and is a closed **DTAIS**
53:   vocabulary: Demonstration, Test, Analysis, Inspection, Special.
54:   Each AC may optionally carry a `#### Test Steps` numbered procedure
55:   list. A `model_validator` rejects duplicate `AC-NNN` numbers.
56: - REQ-004 (decided): Frontmatter `status` is a closed, hyphen-free
57:   four-value lifecycle -- `draft` / `progress` / `complete` / `approved` --
58:   grounded in INCOSE's Guide for Writing Requirements, Attribute A26
59:   ("Need or Requirement Verification Status": "not started, in work,
60:   complete, and approved"; see
61:   `.specmgr/feat/feat-32-sysrs/incose-guide-writing-requirements-2019.md:1225`),
62:   reworded to this repo's hyphen-free style. No separate pass/fail/waived
63:   outcome field -- `## Coverage` is the only outcome signal.
64: - REQ-005 (not started): Everything else a from-scratch domain needs,
65:   patterned on `sop`'s precedent (`.specmgr/feat/feat-30-sop/README.md`):
66:   `vcr/models/v1/` schema + parser, 8 standard tools (`create_vcr`,
67:   `parse_vcr`, `list_vcr`, `get_vcr(raw=False)`, `get_vcr_example`,
68:   `get_vcr_template`, `delete_vcr` stub, `validate_vcr`), 3 resources
69:   (`schema`/`example`/`template`, no `/{id}`, no `/list`), prompts
70:   (`create_vcr`/`update_vcr`), generic `update`/`set_status` dispatch
71:   entries, packaged data, cross-cutting registration
72:   (`server.py`/`AGENTS.md`/`README.md`/CI/pre-commit).
73: - REQ-006 (decided): A cross-cutting `specmgr://dtais` resource explains
74:   the DTAIS verification-method vocabulary (what each of the 5 methods
75:   means and when/how to apply it), mirroring `sop`'s planned
76:   `specmgr://rasci` resource (`.specmgr/feat/feat-30-sop/README.md`
77:   REQ-011) and `rsk`'s existing `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix`
78:   resources: a thin `general/resources/dtais.py` returning
79:   `read_packaged_text("general", "dtais")` verbatim, backed by
80:   `general/data/general_dtais.md`. Flat top-level URI (like
81:   `specmgr://iso25010`/the planned `specmgr://rasci`), not
82:   `specmgr://vcr/dtais`, since the vocabulary is domain-knowledge that
83:   other domains (e.g. `sysrs`) may want to reference too, not owned by
84:   `vcr`'s own schema. See the persisted sketch in Design Notes.
85: 
86: ### Acceptance Criteria
87: 
88: - [x] ACC-001: Verifies REQ-001 -- `Verifies` (`vcr/models/v1/body.py`) is
89:   implemented exactly per the persisted class sketch (mandatory `value`
90:   regex-checked against `_VERIFIES_PATTERN`, mandatory `notes`, optional
91:   `comment`) and unit-tested end to end, including full-document
92:   round-trips, in `tests/vcr/models/v1/test_body.py`/`test_parser.py`.
93: - [x] ACC-002: Verifies REQ-002 -- `Coverage`'s closed
94:   `full`/`partial`/`none` vocabulary is implemented and unit-tested in
95:   `tests/vcr/models/v1/test_body.py`.
96: - [x] ACC-003: Verifies REQ-003 -- the `### AC-NNN (Method): ...` heading
97:   regex, closed DTAIS vocabulary (all 5 words), and the duplicate-`AC-NNN`-
98:   number `model_validator` are implemented in
99:   `vcr/models/v1/body.py`/`document.py` and unit-tested in
100:   `tests/vcr/models/v1/test_body.py`.
101: - [x] ACC-004: Verifies REQ-004 -- `VcrFrontmatter`'s closed
102:   `draft`/`progress`/`complete`/`approved` status vocabulary is
103:   implemented in `vcr/models/v1/frontmatter.py` and unit-tested in
104:   `tests/vcr/models/v1/test_frontmatter.py`.
105: - [x] ACC-005: Verifies REQ-005 -- the full domain now exists end to end:
106:   `vcr/models/v1/`, 8 tools (`vcr/tools/`), 3 resources (`vcr/resources/`),
107:   2 prompts (`vcr/prompts/`), generic `update`/`set_status` dispatch
108:   (`type="vcr"` in `general/tools/`), packaged data (`vcr/data/`), and
109:   cross-cutting registration (`server.py`, `AGENTS.md`, `README.md`,
110:   `.pre-commit-config.yaml`), all covered by `tests/vcr/` (models, tools,
111:   resources, prompts) plus the new `vcr` cases in
112:   `tests/general/tools/test_update.py`/`test_set_status.py`; the full
113:   suite passes (2452 tests, `OK`).
114: - [x] ACC-006: Verifies REQ-006 -- `specmgr://dtais` exists
115:   (`general/resources/dtais.py`), is registered in
116:   `general/resources/__init__.py` and `server.py`'s docstring, is
117:   documented in `docs/MCP.md` (confirmed in the generated output), and its
118:   content (`general/data/general_dtais.md`) matches the persisted Design
119:   Notes sketch, with `tests/general/resources/test_dtais.py` confirming
120:   every documented method word round-trips through
121:   `AcceptanceCriterion.from_text`.
122: 
123: ### Scope
124: 
125: #### Included
126: 
127: - Schema design and empirical validation for `## Verifies`, `## Coverage`,
128:   `## Acceptance Criteria` (incl. DTAIS method + optional `#### Test Steps`), `## More Information`, `## Updates`.
129: - Full domain build: models, parser, 8 tools, 3 resources, prompts,
130:   generic dispatch registration, cross-cutting registration.
131: - The cross-cutting `specmgr://dtais` resource (REQ-006), even though it
132:   lives in `general/`, not `vcr/`, since it exists to support this
133:   feature's `## Acceptance Criteria` method vocabulary.
134: 
135: #### Explicitly Out Of Scope
136: 
137: - Per-AC mutation tools (`ac_create`/`ac_read`/`ac_update`/`ac_delete`) --
138:   deliberately deferred/rejected in favor of the "simple surface" default;
139:   may be revisited later if agents need to target one AC without
140:   resending the whole document.
141: - A separate pass/fail/waived outcome field -- `## Coverage`
142:   (full/partial/none) is the only outcome signal for now.
143: - Any change to `sysrs`'s own schema (this feature is a sibling domain
144:   `sysrs` will cross-reference once both exist, not a section inside
145:   `sysrs` itself).
146: 
147: ### Dependencies
148: 
149: #### Depends On
150: 
151: - ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy).
152: - ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic `update`/`set_status`
153:   dispatch -- new domains use it from day one).
154: - ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based reads).
155: - ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 (paged `list_<d>` tool, not a
156:   resource).
157: - `.specmgr/feat/feat-30-sop/README.md` as the most recent
158:   from-scratch-domain precedent to copy tooling/registration shape from,
159:   including its planned (not yet implemented) `specmgr://rasci`
160:   cross-cutting resource design (REQ-011, Task 3.4/3.5/3.8), the direct
161:   precedent for `specmgr://dtais` (REQ-006).
162: - `rsk`'s existing `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix`
163:   resources, the closest *implemented* precedent for a raw-markdown
164:   domain-knowledge resource (`read_packaged_text` passthrough, no
165:   Pydantic parsing).
166: - `req`/`uc` domains, for the real (UUID) ids `## Verifies`
167:   cross-references.
168: 
169: #### Blocks
170: 
171: - `sysrs`'s own "Verification / Test and Evaluation" open design question
172:   (`.specmgr/feat/feat-32-sysrs/README.md`, "Not yet decided") -- once
173:   `vcr` exists, `sysrs` can cross-reference it instead of inventing a
174:   `## Verification` section of its own.
175: 
176: ### Design Notes
177: 
178: Full design was worked out interactively in a planning session conducted
179: on the `feat-32-sysrs` branch/worktree (before this feature got its own
180: branch); see that session's transcript for the complete rationale,
181: including:
182: 
183: - Why the "REQ-9687"-style ids seen elsewhere in the codebase
184:   (`req`/`gol`/`dec`'s `## Related Artifacts`) are illustrative only, not
185:   the real (UUID) id format -- and why `## Verifies` therefore needs an
186:   explicit `REQ`/`UC` literal type tag alongside the real id, rather than
187:   relying on an id-prefix regex.
188: - Why `## Verifies` ended up a single-value field, not a
189:   cardinality-1-constrained list: an explore-agent survey of every
190:   "exactly one X" relationship in the codebase found **zero** precedent
191:   for a list constrained to `len == 1` via `model_validator` anywhere,
192:   and equally zero precedent for baking a foreign id/title into a section's
193:   own heading (RSK's `### Probability {1..5}`/DEC's `### Option N: title`
194:   idiom is only ever used for repeatable *sibling* elements, never to
195:   collapse a whole section into its H2). The actual precedent for a
196:   true 1:1 relationship is a single non-list `value: MarkdownParagraph`
197:   field directly under the H2 -- SOP's `Accountable` (RASCI "exactly one
198:   owner"), RSK's `Strategy`/`Owner`, REQ/GOL's `Source` -- so `## Verifies`
199:   follows that shape instead, with `notes` made mandatory (unlike
200:   `MarkdownListItemWithNotes.notes`, which is optional) since a paraphrase
201:   is always expected. See the class sketch below.
202: - Why DTAIS's 5 methods (Demonstration, Test, Analysis, Inspection,
203:   Special) were chosen over the 4-method set (Inspection, Analysis,
204:   Demonstration, Test) found in the primary sources reviewed for `sysrs`
205:   (INCOSE Guide for Writing Requirements, MITRE SE Guide) -- a deliberate
206:   user choice to add a 5th method. Originally named "Certification"
207:   (hence the initial "DTAIC" acronym); renamed to "Special" (yielding
208:   "DTAIS") since it reads as broader than formal certification-body
209:   sign-off alone -- see Decisions Made below.
210: - Why frontmatter `status` uses INCOSE's A26 attribute's
211:   workflow-progress values (reworded hyphen-free:
212:   `draft`/`progress`/`complete`/`approved`) rather than an invented
213:   pass/fail/waived lifecycle.
214: - Why the acceptance-criteria list needed its own numbered-H3 sub-section
215:   per entry (DEC-`Option`-style) rather than a flat bullet list: each
216:   entry has structurally distinct fields (method, optional test steps),
217:   which a flat `MarkdownListItem` cannot carry.
218: - Why `specmgr://dtais` is a cross-cutting `general/` resource, not a
219:   `vcr/`-scoped one: it documents a vocabulary (the 5 DTAIS methods) that
220:   is conceptually independent of `vcr`'s own schema -- the same reasoning
221:   `sop`'s still-unimplemented `specmgr://rasci` design used for RASCI
222:   (`.specmgr/feat/feat-30-sop/README.md` REQ-011) -- and the raw-markdown
223:   passthrough shape (no Pydantic parsing) mirrors `rsk`'s already-shipped
224:   `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix` rather than
225:   `specmgr://iso25010`'s structured-parse approach, since the audience is
226:   an LLM agent reading guidance prose, not code consuming structured
227:   data.
228: - **Clean-example convention** (discovered while finalizing `example.md`
229:   as the sole draft): a survey of every already-implemented domain's
230:   shipped `<domain>_example.md` vs. `<domain>_template.md` found that
231:   `dec`/`uc`/`req` ship fully comment-free examples (instructional
232:   comments like "mandatory", "enforced via regex", closed-vocabulary
233:   hints live only in the template, or as plain descriptive prose in the
234:   body, never as an HTML comment in the finished example); `rsk`/`prb`
235:   *replace* a template's generic instructional comment with a realistic
236:   filled-in annotation (e.g. RSK's H1 comment naming the real risk
237:   entry) rather than leaving instructional text in place; and `feat`/`qa`
238:   comments are permanent structural anchors or first-class schema fields
239:   (e.g. `## Updates`' "newest first" note), not authoring guidance, so
240:   they appear unchanged in both example and template. `gol`/`tsk` show
241:   this isn't universally enforced (they leak leftover instructional text
242:   into their examples) -- an anti-pattern this feature avoids. `vcr`'s
243:   `example.md` now follows the `dec`/`uc`/`req`/`rsk`/`prb` pattern:
244:   every instructional comment was removed (they belong in the
245:   not-yet-drafted `template.md` instead), `## Updates`' anchor comment
246:   was kept as-is, and `## Verifies`' optional `comment` field is now
247:   exercised with one realistic filled annotation instead of staying
248:   empty.
249: 
250: **Candidate `Verifies` class sketch** (for `vcr/models/v1/body.py`, Phase
251: 1 -- not yet implemented; persisted here so a future implementer can start
252: from this instead of re-deriving it):
253: 
254: ```python
255: import re
256: 
257: from pydantic import Field, field_validator
258: 
259: from biz.dfch.specmgr.models.md import MarkdownParagraph, MarkdownSection2WithComment
260: 
261: _VERIFIES_PATTERN = r"^(REQ|UC) [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}: .+$"
262: 
263: 
264: class Verifies(MarkdownSection2WithComment):
265:     """`## Verifies` -- exactly one REQ or UC cross-reference. Mandatory.
266: 
267:     Modeled as a single non-list value field (SOP's `Accountable` / RSK's
268:     `Strategy`&`Owner` / REQ&GOL's `Source` precedent), not a bullet list
269:     -- a single-value field is structurally incapable of holding more than
270:     one reference, so no cardinality `model_validator` is needed. `value`
271:     and `notes` are two mandatory fields in fixed declaration order,
272:     mirroring RSK's `Assessment.probability`/`.impact` two-mandatory-
273:     fields-in-sequence idiom (just `MarkdownParagraph` instead of
274:     `Probability`/`Impact`).
275: 
276:     Parameters
277:     ----------
278:     comment:
279:         Optional explanatory HTML comment (`<!-- ... -->`). Inherited from
280:         `MarkdownSection2WithComment`.
281:     value:
282:         Single-line `"REQ|UC <uuid>: <title>"`. Mandatory.
283:         `field_validator`-regex-checked against `_VERIFIES_PATTERN`
284:         (standard 8-4-4-4-12 hex UUID shape -- no UUID-format precedent
285:         existed elsewhere in the codebase to reuse, so this introduces
286:         one).
287:     notes:
288:         One-paragraph paraphrase of why this REQ/UC is verified here.
289:         Mandatory (unlike `MarkdownListItemWithNotes.notes`, which is
290:         optional).
291:     """
292: 
293:     value: MarkdownParagraph = Field(description='Single-line value: "REQ|UC <uuid>: <title>".')
294:     notes: MarkdownParagraph = Field(description="Mandatory one-paragraph paraphrase.")
295: 
296:     @field_validator("value")
297:     @classmethod
298:     def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
299:         """Enforce `_VERIFIES_PATTERN` against `value.text` (mirrors `req.Level`/`rsk.Strategy`)."""
300:         if not re.fullmatch(_VERIFIES_PATTERN, value.text):
301:             raise ValueError(f"value must match pattern {_VERIFIES_PATTERN!r}, got {value.text!r}")
302:         return value
303: ```
304: 
305: **Candidate `specmgr://dtais` resource sketch** (for `general/resources/dtais.py` +
306: `general/data/general_dtais.md`, Phase 3 -- not yet implemented; persisted
307: here so a future implementer can start from this instead of re-deriving
308: it. Mirrors `rsk/resources/tara.py` + `rsk/data/rsk_tara.md` exactly,
309: just cross-cutting instead of `rsk`-scoped):
310: 
311: ```python
312: """Resource: specmgr://dtais -- the DTAIS verification-method vocabulary."""
313: 
314: from __future__ import annotations
315: 
316: from ..tools._packaged_data import read_packaged_text
317: from ...server import mcp
318: 
319: 
320: @mcp.resource(
321:     "specmgr://dtais",
322:     name="dtais",
323:     title="DTAIS Verification Method Vocabulary",
324:     description=(
325:         "What DTAIS is (Demonstration, Test, Analysis, Inspection, Special), the five valid "
326:         "`### AC-NNN (Method): ...` method words, and when and how to apply each, as raw "
327:         "markdown domain-knowledge guidance."
328:     ),
329:     mime_type="text/markdown",
330: )
331: def dtais() -> str:
332:     """Return the packaged DTAIS guidance's full markdown text, verbatim."""
333:     return read_packaged_text("general", "dtais")
334: ```
335: 
336: Registered in `general/resources/__init__.py` alongside `iso25010`/`version`
337: (and, once built, `rasci`):
338: 
339: ```python
340: from . import dtais, iso25010, version  # noqa: F401
341: 
342: __all__ = [
343:     "dtais",
344:     "iso25010",
345:     "version",
346: ]
347: ```
348: 
349: Draft content outline for `general/data/general_dtais.md` (mirroring
350: `rsk_tara.md`'s shape -- closed-vocabulary list, then a "when to apply
351: each" section per method):
352: 
353: ```markdown
354: # DTAIS Verification Methods
355: 
356: The five valid `### AC-NNN (Method): ...` method words used by `vcr`'s
357: `## Acceptance Criteria` (and any other domain that needs to describe how
358: a criterion is verified):
359: 
360: - `Demonstration` -- observing the system in operation, without
361:   instrumented measurement, to confirm a qualitative or operational
362:   characteristic.
363: - `Test` -- exercising the system under controlled, instrumented
364:   conditions and comparing measured results against a quantitative
365:   threshold.
366: - `Analysis` -- using calculation, modeling, or simulation (not direct
367:   observation of the built system) to show a requirement is met.
368: - `Inspection` -- visual or procedural examination of the system,
369:   design artifacts, or source code, without operating the system.
370: - `Special` -- any other verification approach not covered by the four
371:   methods above, e.g. a formal third-party certification/compliance
372:   sign-off, a supplier's certificate of conformance, or another
373:   contractually-mandated special process.
374: 
375: ## When to apply each method
376: 
377: ...(guidance per method, mirroring `rsk_tara.md`'s "## When to apply each
378: strategy" section -- to be filled in during Phase 3, informed by
379: INCOSE's Guide for Writing Requirements / MITRE SE Guide's own
380: Demonstration/Test/Analysis/Inspection definitions).
381: 
382: ## Relationship to `## Coverage`
383: 
384: ... (how an AC's method interacts with the overall `full`/`partial`/`none`
385: coverage signal -- see `vcr`'s REQ-002).
386: ```
387: 
388: **Candidate H1/body outline** (not yet empirically validated against
389: `models/md` -- Phase 0 task):
390: 
391: ```markdown
392: # Feature: <free text, unconstrained like RSK/GOL/DEC/SOP>
393: 
394: ## Verifies
395: 
396: <!-- Optional context comment. -->
397: 
398: REQ <uuid>: <title>
399: 
400: <one-line paraphrase>
401: 
402: ## Coverage
403: 
404: full
405: 
406: ## Acceptance Criteria
407: 
408: ### AC-001 (Test): <criterion text>
409: 
410: #### Test Steps
411: 
412: 1. ...
413: 2. ...
414: 
415: ### AC-002 (Analysis): <criterion text>
416: 
417: ## More Information
418: 
419: ...
420: 
421: ## Updates
422: 
423: <!-- Newest entry first -->
424: 
425: ### <timestamp> — Created
426: 
427: ...
428: ```
429: 
430: (Note: `### {timestamp} — {title}`, one level shallower than `feat`'s own
431: `## Progress` → `### Updates` → `#### {timestamp} — {title}`, since `vcr`
432: has no Plan/Progress split -- same reasoning `sysrs` used for its own
433: `## Updates` section.)
434: 
435: ### Related Decisions
436: 
437: - No dedicated ADR yet -- design decisions recorded above and in this
438:   feature's own Decisions Made log below, per the "scoped entirely to
439:   this feature's implementation details" rule in AGENTS.md.
440: 
441: ### Task List
442: 
443: #### Phase 0: Empirical schema validation
444: 
445: - [x] Task 0.1: Draft `example.md`/`template.md` bodies exercising every
446:   section and validate against the `models/md` engine (mirroring `sop`'s/
447:   `sysrs`'s discipline) before writing any Pydantic model code.
448:   - [x] `example.md` finalized as the **sole** draft (earlier
449:     `example.v2.md`/`example.v3.md` iterations merged into it and
450:     deleted): real frontmatter, single-value-field `## Verifies` (see
451:     Design Notes' `Verifies` class sketch), DTAIS/`Special` terminology,
452:     and every instructional/enforcement comment removed per the
453:     clean-example convention discovered in `dec`/`uc`/`req`'s shipped
454:     `*_example.md` files (see Design Notes) -- the only comment kept is
455:     `## Updates`' permanent "newest first" anchor, plus one new filled
456:     annotation exercising `Verifies`' optional `comment` field. Still not
457:     yet validated against `models/md`, since no `vcr` model code exists
458:     yet; see Task 1.1-1.3.
459:   - [x] `template.md` drafted (blind-text placeholder, mirroring
460:     `dec`/`rsk`/`prb`/`req`/`uc`'s shipped `*_template.md` shape): exercises
461:     the same section shape as `example.md` (frontmatter, `## Verifies`
462:     with optional `comment` + mandatory `value` + mandatory `notes`,
463:     `## Coverage`, `## Acceptance Criteria` with two `### AC-NNN (Method):
464:     ...` entries -- one with `#### Test Steps`, one without --,
465:     `## More Information`, `## Updates`), with placeholder ("blind text")
466:     content and a real-looking placeholder UUID
467:     (`deaddead-face-face-face-deaddeadface` for the frontmatter `id`,
468:     `c0ffeec0-ffee-ffee-ffee-c0ffeec0ffee` for the `## Verifies`
469:     cross-reference). Restores the instructional guidance stripped from
470:     `example.md` per the clean-example convention, but only as an actual
471:     HTML comment where `example.md` itself already shows one is
472:     structurally valid (`## Verifies`' single leading-comment slot, and
473:     `## Updates`' permanent anchor) -- `## Coverage`, `## Acceptance
474:     Criteria`, and `#### Test Steps` carry no comment in the already-
475:     finalized `example.md` either (mirroring their precedent classes'
476:     lack of a `WithComment` variant: `rsk.Strategy`, `dec.ProsAndCons`,
477:     `dec.Option`, none of which support a leading comment), so adding one
478:     there would silently commit `template.md` to a schema shape Phase 1
479:     has not decided and `example.md` already contradicts. Their guidance
480:     (Coverage's closed vocabulary; Method's closed DTAIS set; the `>= 1`/
481:     unique-number rule; Test Steps' optionality) is instead folded into
482:     the free-form AC body prose as a trailing sentence, mirroring
483:     `prb_template.md`/`uc_template.md`'s established precedent of
484:     appending "Mandatory."/"Optional." notes directly into blind-text
485:     paragraph/list content rather than a comment; `## Coverage` itself
486:     (an exact-match `full`/`partial`/`none` value with no other content
487:     allowed, `re.fullmatch`-enforced) carries no note at all, matching
488:     `rsk_template.md`'s identical bare-value `## Strategy` precedent.
489:     `## More Information` uses the exact `dec_template.md`/
490:     `feat_template.md` boilerplate sentence instead of a comment, for the
491:     same reason. Still not yet validated against `models/md`, since no
492:     `vcr` model code exists yet; see Task 1.1-1.3.
493: - [x] Task 0.2: Confirm the `### AC-NNN (Method): ...` heading regex and
494:   duplicate-number `model_validator` behave as expected on hand-written
495:   fixtures. Done via a throwaway `/tmp` scratch script (not committed, not
496:   a permanent test file), modeled on `dec`'s
497:   `_OPTION_HEADING_PATTERN`/`_validate_option_numbers_unique` precedent;
498:   see the new Updates entry below for the exact pattern, fixtures, and
499:   outcomes (all passed after fixing one bug in the first draft pattern --
500:   missing literal escaped parentheses around the method group).
501: 
502: #### Phase 1: Models and parser
503: 
504: - [x] Task 1.1: `vcr/models/v1/frontmatter.py` (`VcrFrontmatter`, closed
505:   `status` vocabulary).
506: - [x] Task 1.2: `vcr/models/v1/body.py` (`Verifies`, `Coverage`,
507:   `AcceptanceCriterion`/`AcceptanceCriteria`, `MoreInformation`, reused
508:   `Updates`).
509: - [x] Task 1.3: `vcr/models/v1/document.py`, `parser.py`, `summary.py`,
510:   `_util.py`, `__init__.py`.
511: - [x] Task 1.4: Unit tests for every model class and the parser.
512: 
513: #### Phase 2: Tools
514: 
515: - [x] Task 2.1: `create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr` (with
516:   `raw` param), `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub,
517:   `validate_vcr`.
518: - [x] Task 2.2: Generic `update`/`set_status` dispatch entries
519:   (`type="vcr"`) in `general/tools/`.
520: 
521: #### Phase 3: Resources and prompts
522: 
523: - [x] Task 3.1: `specmgr://vcr/schema`, `.../example`, `.../template`
524:   resources.
525: - [x] Task 3.2: `create_vcr`/`update_vcr` prompts.
526: - [x] Task 3.3: `general/data/general_dtais.md` content (fill in the
527:   draft outline persisted in Design Notes), `general/resources/dtais.py`
528:   (`specmgr://dtais`), registered in `general/resources/__init__.py`;
529:   unit tests.
530: 
531: #### Phase 4: Cross-cutting registration
532: 
533: - [x] Task 4.1: `server.py` import line.
534: - [x] Task 4.2: `AGENTS.md` Status section bullet (mirroring the
535:   `sop`/`feat` bullets).
536: - [x] Task 4.3: `README.md`, CI/pre-commit updates as needed.
537: - [x] Task 4.4: `specmgr docs`/`specmgr adr-toc` regeneration, full test
538:   suite, ruff/vulture gates.
539: 
540: ## Progress
541: 
542: ### Current Status
543: 
544: **As of 2026-08-31 (post-merge, latest)**: Merged current `dev` into this
545: branch (PR #34 / `feat-30-sop`, which added the `sop` domain and the
546: cross-cutting `specmgr://rasci` resource, plus chore `03260fe`). Every
547: conflict was additive (`sop` and `vcr` register into the same generic
548: dispatch points) and was resolved by combining both sides; a missing
549: `vcr` packaged-schema CI step was added for parity with `sop`. All
550: generated artifacts were regenerated from the merged source and verified
551: drift-free; full gate green (2704 tests `OK`). The branch is now PR-ready
552: against `dev`. See the newest Updates entry below for the per-file
553: resolution log.
554: 
555: **As of 2026-08-31 (pre-merge)**: Feature complete end to end. Phase 4
556: (Cross-cutting registration) wired `vcr/__init__.py` (now imports
557: `prompts`/`resources`/`tools`, mirroring `dec/__init__.py` exactly),
558: added `vcr` to `server.py`'s bottom import line and its full module
559: docstring (resources, the "no `{id}`/no `list`" paragraph, tools,
560: prompts, and the closing domain-enumeration paragraph -- all
561: domain-count language bumped from nine/ten to ten/eleven where it now
562: includes `vcr`), added a new `vcr/` bullet to `AGENTS.md`'s Status
563: section (positioned after `feat/`, before `general/`, mirroring `dec/`'s
564: shape) plus every other domain-enumeration spot in that file (`general/`'s
565: own resource list gains `specmgr://dtais`; the "still missing"
566: `validate_*`/`delete_*` lists gain `validate_vcr`/`delete_vcr`; the
567: tools/resources/prompts registration summary and the MCP-server-import
568: summary both gain `vcr`), added "Verification Case Record (VCR)" to root
569: `README.md`'s artifact list (alphabetically last, after "Use Case (UC)"),
570: added a `specmgr-schema-vcr-package` pre-commit hook (mirroring
571: `specmgr-schema-feat-package`) and inserted `vcr/models/v1` into every one
572: of the 10 existing `files:` regexes (the shared `specmgr-schema` hook plus
573: 9 per-package hooks) and the `specmgr-schema` hook's own description, and
574: added a `CHANGELOG.md` `[Unreleased]` entry ("Twelfth domain feature").
575: Regenerated `docs/GENERATED.md`, `docs/api/`, `docs/MCP.md`,
576: `docs/adr/README.md` (no change -- confirmed empty diff, as expected since
577: this feature never touches `docs/adr/`), every `docs/*_schema.json`, and
578: the packaged `vcr/data/vcr_schema.json` copy -- each regeneration command
579: was run a second time afterward and confirmed stable (`unchanged`/
580: identical output, no further drift). Manually confirmed in the generated
581: `docs/MCP.md` that all 8 VCR tools, all 3 VCR resources, both VCR prompts,
582: and the standalone `specmgr://dtais` resource appear with correct
583: descriptions. Quality gate green: `ruff format --check` (1386 files
584: already formatted), `ruff check` (all checks passed), `vulture` (no
585: output, no new whitelist entries needed), and the full `unittest` suite
586: (2452 tests, `OK`, unchanged from Phase 3 -- Phase 4 added no new test
587: files, only cross-cutting registration/docs). All ACC-001..006 confirmed
588: and checked off. This feature is now fully implemented end to end,
589: matching every other already-shipped domain's registration shape.
590: 
591: **As of 2026-08-31 (earlier)**: Phase 3 (Resources and prompts) complete.
592: `vcr/resources/` (`vcr_schema`/`vcr_example`/`vcr_template`, mirroring
593: `dec/resources/` file-for-file) and `vcr/prompts/` (`create_vcr`/
594: `update_vcr`, mirroring `dec/prompts/` file-for-file, plus their packaged
595: `vcr_create_instructions.md`/`vcr_update_instructions.md`) now exist.
596: `commands/schema.py` gained `generate_vcr_schema`/a `"vcr"` `_GENERATORS`
597: entry, and both `docs/vcr_schema.json` and the packaged
598: `vcr/data/vcr_schema.json` copy are generated and drift-free. The
599: cross-cutting `specmgr://dtais` resource (REQ-006) now exists:
600: `general/data/general_dtais.md` (the five DTAIS method words, a "When to
601: apply each method" section, and a "Relationship to `## Coverage`"
602: section illustrating the `partial`-coverage/pending-`Special`-
603: certification scenario from `example.md`), `general/resources/dtais.py`,
604: registered in `general/resources/__init__.py`. 52 new unit tests
605: (`tests/vcr/resources/`, `tests/vcr/prompts/`,
606: `tests/general/resources/test_dtais.py`, bringing the full suite from
607: 2400 to 2452). Neither `server.py` nor `vcr/__init__.py` was touched --
608: `vcr/__init__.py` deliberately still does not import
609: `tools`/`resources`/`prompts` (that domain-registration wiring is Phase
610: 4's job).
611: 
612: **As of 2026-08-31 (earlier)**: Phase 2 (Tools) complete. `vcr/tools/` now exists in
613: full, mirroring `dec/tools/` file-for-file: `_paths.py`/`_lock.py`/`_io.py`/
614: `_write.py` plumbing, and the 8 standard tools (`create_vcr`, `parse_vcr`,
615: `get_vcr` with `raw`, `get_vcr_example`, `get_vcr_template`, `list_vcr`,
616: `delete_vcr` stub, `validate_vcr`). Packaged data
617: (`vcr/data/vcr_example.md`/`vcr_template.md`, copied byte-for-byte from
618: this feature's finalized planning drafts) backs `get_vcr_example`/
619: `get_vcr_template`, declared in `pyproject.toml`'s
620: `[tool.setuptools.package-data]`. The generic `update`/`set_status` tools
621: in `general/tools/` now dispatch `type="vcr"` to `_update_vcr`/
622: `_set_status_vcr`, ported verbatim from `_update_dec`/`_set_status_dec`.
623: 64 new unit tests (`tests/vcr/tools/`, bringing the full suite from 2336 to
624: 2400) plus new `vcr` cases in
625: `tests/general/tools/test_update.py`/`test_set_status.py` cover the full
626: create->get->list->update->set_status->validate->delete lifecycle. Neither
627: `server.py` nor `vcr/__init__.py` was touched -- `vcr/__init__.py`
628: deliberately still does not import `tools`/`resources`/`prompts` (that
629: domain-registration wiring, plus `vcr/resources`/`vcr/prompts` themselves,
630: is Phase 3/4's job). One noted, non-blocking fragility: running
631: `tests/vcr/tools/` in isolation (before Phase 4 wires `vcr/__init__.py`'s
632: own `tools` import) can hit a circular-import `ImportError` in
633: `test__io.py`/similar files that import `vcr.models.v1` directly, since
634: `general.tools.update`/`set_status` now import `vcr.tools._io` etc. at
635: module load time and `vcr.tools`'s own `__init__.py` eagerly imports
636: `list_vcr` (which needs `VcrSummary`) -- resolved automatically once Phase
637: 4 makes `vcr/__init__.py` bootstrap `tools` first (mirroring every other
638: domain's own `__init__.py`); the full repo-wide test suite (the specified
639: quality gate) is unaffected and passes cleanly (2400 tests, `OK`).
640: 
641: **As of 2026-08-31 (earlier)**: Phase 1 (Models and parser) complete. `vcr/models/v1/`
642: now exists in full: `frontmatter.py` (`VcrFrontmatter`, closed
643: draft/progress/complete/approved status set), `body.py` (`Verifies`,
644: `Coverage`, `TestSteps`, `AcceptanceCriterion`/`AcceptanceCriteria`,
645: `MoreInformation`, `UpdateEntry`/`Updates`, and the top-level `Vcr` H1
646: container with its duplicate-AC-number `model_validator`), plus
647: `document.py`/`parser.py`/`summary.py`/`_util.py`/`__init__.py` mirroring
648: `dec/models/v1`'s shape exactly. 103 new unit tests (`tests/vcr/models/v1/`)
649: cover every heading alias, `Verifies`'/`Coverage`'s regex-enforced values,
650: the `AC-NNN (Method): ...` heading regex and computed `number`/`method`
651: fields, `TestSteps` presence/absence, mandatory/optional-section behavior,
652: misordering, the duplicate-AC-number after-validator, and full-document
653: round-trips through `parse_vcr`. REQ-001..004 (and their corresponding
654: ACC-001..004 schema-level acceptance criteria) are now implemented and
655: unit-tested end to end; ACC checkboxes themselves are left for sign-off
656: per this feature's own discipline. No `vcr` tool/resource/prompt code
657: exists yet, and `vcr/__init__.py` deliberately stays empty (no
658: `tools`/`resources`/`prompts` import) -- that domain-registration wiring
659: is Phase 2/3/4's job.
660: 
661: ### Blockers
662: 
663: - None currently.
664: 
665: ### Updates
666: 
667: <!-- Newest entry first -- prepend new entries directly below this comment. -->
668: 
669: #### 2026-08-31T16:26:00.000000 — Merged current `dev` (incl. PR #34 / SOP) into `feat-33-vcr`; resolved all conflicts additively; branch PR-ready
670: 
671: `origin/dev` had advanced past this branch's merge base (`4c7d976`) by PR
672: #34 ("feat(30): Add artifact type \"Standard Operating Procedure\" (SOP) —
673: complete", `ec3d644`) -- the new `sop` domain plus the cross-cutting
674: `specmgr://rasci` resource -- and by chore `03260fe` (a feat-7 README
675: backlog note; no file overlap). `git merge origin/dev` conflicted in 14
676: files; every conflict was additive (both `sop` and `vcr` register into the
677: same generic dispatch points) and was resolved by combining both sides:
678: 
679: - `general/tools/update.py`: eleven whole-body domains
680:   (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`),
681:   both `_update_sop` and `_update_vcr` adapters, 11-way return union,
682:   11-value `type` enum; the `update` docstring was re-normalized to the
683:   base indentation the `sop` side had re-indented.
684: - `general/tools/set_status.py`: twelve domains incl. `adr`, both
685:   adapters, 12-way union, 12-value enum; same docstring normalization.
686: - `server.py`: module docstring gains both domains' resource lines,
687:   "no `{id}`/no `list`" sentences, tools/prompt paragraphs, and the count
688:   bumps (eleven whole-body / twelve incl. `adr`); the bottom import line
689:   is now `adr, dec, feat, general, gol, prb, qa, req, rsk, sop, tsk, uc,
690:   vcr`.
691: - `general/resources/__init__.py`: imports/`__all__`/docstring carry
692:   `dtais`, `iso25010`, `rasci`, and `version`.
693: - `commands/schema.py`: both `generate_sop_schema` and
694:   `generate_vcr_schema` plus both `_GENERATORS` entries (the registry
695:   itself auto-merged).
696: - `.pre-commit-config.yaml`: all 11 `files:` regexes carry
697:   `sop/models/v1` and `vcr/models/v1`; both `specmgr-schema-sop-package`
698:   and `specmgr-schema-vcr-package` hooks present (12 schema hooks total).
699: - `tests/general/tools/test_update.py` / `test_set_status.py`: both
700:   per-domain cases and fixtures (after the `dec` case, `sop` then
701:   `vcr`); `update`'s registration assertion now expects the 11-value
702:   enum; docstring counts updated to eleven/twelve -- the `sop` side had
703:   left `test_set_status`'s docstring stale at nine/eight, fixed as part
704:   of the union; `test_update`'s field-error note now names
705:   `dec`/`sop`/`vcr` (duplicated `### Option`/`### Step`/`### AC-NNN`
706:   numbers).
707: - `AGENTS.md`: both `sop/` and `vcr/` Status bullets; `general/`
708:   paragraph unioned (eleven whole-body domains, twelve incl. `adr`,
709:   resources `version`/`iso25010`/`dtais`/`rasci`, eleven `get_<d>`
710:   tools); the "still missing" `validate_*`/`delete_*` lists, the
711:   registration summary, and the MCP-server import list all gain both.
712: - `README.md` / `pyproject.toml`: auto-merged cleanly (SOP line after
713:   RSK, VCR line after UC; both `package-data` entries).
714: - `.github/workflows/ci.yml`: an audit against the pre-commit hooks
715:   found all 11 packaged schema copies covered by hooks but only 10 by
716:   CI steps (`vcr` missing -- this branch had added the pre-commit hook
717:   but no CI step, unlike the `sop` PR). Added the
718:   `src/biz/dfch/specmgr/vcr/data/vcr_schema.json` packaged-copy drift
719:   step (after the `feat` step, before `docs/coverage.svg`) and added
720:   `vcr` to the all-types comment.
721: - Generated artifacts (`docs/GENERATED.md`, `docs/api/**`,
722:   `docs/MCP.md`, `docs/*_schema.json`, packaged schema copies,
723:   `docs/adr/README.md`): conflict markers were dropped in favor of a
724:   full regeneration from the merged source -- `specmgr docs`,
725:   `specmgr mcp-docs`, `specmgr schema` (all 11 types `unchanged`),
726:   `specmgr schema --type {sop,vcr} --output-dir src/.../{sop,vcr}/data`
727:   (both `unchanged`), `specmgr adr-toc` -- then re-run as a fixed-point
728:   check with zero drift.
729: 
730: Quality gate after the merge: `ruff format --check` (1481 files),
731: `ruff check` (all passed), `vulture` (clean, no new whitelist entries
732: needed), full `unittest` suite (2704 tests, `OK`), `coverage run` +
733: `specmgr coverage-badge` (99%, `docs/coverage.svg` byte-unchanged),
734: advisory `pylint` (8.87/10, no new messages from the merge).
735: 
736: #### 2026-08-31T15:30:00.000000 — Phase 4 complete: cross-cutting registration; feature fully implemented end to end
737: 
738: Implemented Task 4.0 (the implicit prerequisite): wired `vcr/__init__.py`
739: to `from . import prompts, resources, tools`, mirroring `dec/__init__.py`
740: file-for-file (module docstring adapted to VCR's actual schema/tools/
741: resources/prompts, including the `specmgr://dtais` cross-reference). This
742: resolves the non-blocking circular-import fragility noted in the Phase
743: 2/3 Updates entries (`tests/vcr/tools/`/`tests/vcr/resources/`/
744: `tests/vcr/prompts/` now import cleanly in isolation too, not just as
745: part of the full suite).
746: 
747: Implemented Task 4.1: added `vcr` to `server.py`'s bottom import line
748: (alphabetical position, after `uc`) and updated its module docstring in
749: full -- three new `specmgr://vcr/schema`/`.../example`/`.../template`
750: resource lines (after `feat`'s, before `iso25010`), a new
751: `specmgr://dtais` resource line (between `feat/template` and
752: `iso25010`), a new VCR sentence in the "no `{id}`/no `list`" paragraph, a
753: new "Verification case record tools (`vcr/tools/`)" paragraph (before
754: "General tools"), a new "Verification case record prompts
755: (`vcr/prompts/`)" paragraph (before "General prompts"), the `general`
756: tools paragraph's domain-count language bumped (`update`: nine -> ten
757: whole-body domains, list gains `vcr`; `set_status`: "all ten domains" ->
758: "all eleven domains", list gains `vcr` right before `adr`), and the
759: closing "Modules are grouped domain-first" paragraph's three
760: domain-enumeration spots (the domain list, the import-list sentence, and
761: the tools/resources/prompts registration sentence) all gain `vcr`. Re-read
762: the entire docstring end to end afterward to confirm every VCR mention is
763: internally consistent with what Phases 1-3 actually built.
764: 
765: Implemented Task 4.2: added a new `vcr/` bullet to `AGENTS.md`'s Status
766: section, positioned after `feat/` and before `general/` (mirroring
767: `dec/`'s bullet shape/depth), describing VCR's actual schema (`##
768: Verifies` single-value cross-reference, `## Coverage` closed vocabulary,
769: `## Acceptance Criteria` DTAIS-classified `### AC-NNN` entries), its 8
770: tools, 3 resources, 2 prompts, generic `update`/`set_status` dispatch, and
771: the cross-cutting `specmgr://dtais` resource. Also updated every other
772: domain-enumeration spot in the same file: the `general/` bullet's own
773: resource list (`specmgr://version`, `specmgr://iso25010` -> gains
774: `specmgr://dtais` with a one-line description), the `general/tools/`
775: `update` sub-bullet's domain count/list (nine -> ten, gains `vcr`), the
776: `set_status` sub-bullet's domain count (ten -> eleven), the "The nine
777: `get_<d>` tools" sentence (-> "The ten `get_<d>` tools"), the "Still
778: genuinely missing" bullets (`validate_vcr` added to the `validate_*` list,
779: `delete_vcr` added to the `delete_*` list), the "each register `tools`,
780: `resources`, and `prompts`" summary bullet (gains `vcr`), and the MCP
781: server section's "imports every domain package" sentence (gains `vcr`).
782: Did not touch the "Models location" paragraph (VCR has no exception to
783: document) or any unrelated `.specmgr/feat/` references.
784: 
785: Implemented Task 4.3: added "Verification Case Record (VCR)" to root
786: `README.md`'s artifact list (alphabetically last, after "Use Case (UC)"),
787: following the same precedent `feat-31-feature`'s own Phase 5 used to add
788: "Feature (FEAT)" to that same list -- confirmed the "Environment
789: Variables" section itself needed no change (it is already fully generic,
790: `SPECMGR_DOCS_DIR`-based, with no per-domain enumeration). Updated
791: `.pre-commit-config.yaml`: inserted `vcr/models/v1` into all 10 existing
792: occurrences of the shared `files:` regex (the `specmgr-schema` hook plus
793: the 9 per-package `specmgr-schema-<domain>-package` hooks), right after
794: `uc/models/v2` and before the always-last `models/md`, added a new
795: `specmgr-schema-vcr-package` hook block (appended after
796: `specmgr-schema-feat-package`, VCR-ified: `vcr/data/vcr_schema.json`,
797: `specmgr://vcr/schema`, `docs/vcr_schema.json`, `--type vcr
798: --output-dir src/biz/dfch/specmgr/vcr/data`) with the same updated regex,
799: and updated the `specmgr-schema` hook's own description text to list
800: `vcr` last. Added a `CHANGELOG.md` `[Unreleased]` `### Added` entry
801: ("Twelfth domain feature (VCR/Verification Case Record tooling)"),
802: mirroring the FEAT entry's structure/depth (models, tools, resources +
803: prompts, the cross-cutting `specmgr://dtais` resource, cross-cutting
804: registration, test coverage).
805: 
806: Implemented Task 4.4: ran `specmgr docs`, `specmgr mcp-docs`,
807: `specmgr adr-toc`, `specmgr schema`, and
808: `specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data`,
809: each exactly twice -- the first run wrote real changes (`docs/GENERATED.md`,
810: `docs/api/README.md`, `docs/api/biz.dfch.specmgr.server.md`,
811: `docs/api/biz.dfch.specmgr.vcr.md`, `docs/MCP.md`, `docs/adr/README.md`
812: regenerated with no diff, every `docs/*_schema.json` and the packaged
813: `vcr/data/vcr_schema.json` copy reported "unchanged"), the second run
814: confirmed byte-identical output (`md5sum` comparison before/after for the
815: docs-generation commands; "unchanged"/no-diff for every schema and the
816: adr-toc command) -- no residual drift from this phase's own edits.
817: Manually read the generated `docs/MCP.md` and confirmed all 8 VCR tools
818: (`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr`, `get_vcr_example`,
819: `get_vcr_template`, `delete_vcr`, `validate_vcr`), all 3 VCR resources
820: (`specmgr://vcr/schema`/`.../example`/`.../template`), both VCR prompts
821: (`create_vcr`, `update_vcr`), and the standalone `specmgr://dtais`
822: resource appear with sensible, accurate descriptions. Quality gate green:
823: `ruff format --check` (1386 files already formatted), `ruff check` (all
824: checks passed), `vulture src/ whitelist.py --min-confidence 60` (no
825: output, no new whitelist entries needed), and the full `unittest` suite
826: (2452 tests, `OK` -- unchanged from Phase 3's count, since Phase 4 added
827: no new test files, only cross-cutting registration/docs). Updated the
828: Task List's Phase 4 checkboxes, walked every ACC-001..006 item and marked
829: all six `[x]` with a concrete justification citing the specific test
830: file/resource/tool proving each, and updated Current Status to reflect
831: the feature is now fully implemented end to end. Bumped this README's own
832: frontmatter `status` from `planning` to `done` and `version` from `1.0.0`
833: to `1.1.0`.
834: 
835: #### 2026-08-31T14:00:00.000000 — Phase 3 complete: `vcr/resources/`, `vcr/prompts/`, and the cross-cutting `specmgr://dtais` resource implemented
836: 
837: Implemented Task 3.1 (`vcr/resources/`): `vcr_schema.py`/`vcr_example.py`/
838: `vcr_template.py`, mirroring `dec/resources/`'s three files exactly
839: (rename `Dec`/`dec` -> `Vcr`/`vcr`, same URIs
840: `specmgr://vcr/schema`/`.../example`/`.../template`, same
841: `read_packaged_text` plumbing), plus `vcr/resources/__init__.py`. The
842: schema resource needed generator plumbing first: added
843: `generate_vcr_schema()` to `commands/schema.py` (mirroring
844: `generate_dec_schema` exactly) and a `"vcr"` entry to `_GENERATORS`
845: (alphabetically last, after `"uc"`), then ran
846: `specmgr schema --type vcr` (writes `docs/vcr_schema.json`) and
847: `specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data`
848: (writes the packaged copy `vcr/data/vcr_schema.json`) -- both exited 1
849: on first generation (new file) and 0 (unchanged) on every subsequent run,
850: confirmed once more at the very end of the phase.
851: 
852: Implemented Task 3.2 (`vcr/prompts/`): `create_vcr.py`/`update_vcr.py`,
853: mirroring `dec/prompts/create_dec.py`/`update_dec.py` exactly (same
854: `string.Template`/`$topic`/`$id`/`$instructions` substitution shape,
855: `raw=True` for `update_vcr`'s line-range line numbers, narration-only
856: contract -- never calls `TodoWrite`/`question`/`list_vcr`/`create_vcr`/
857: `get_vcr`/`update`/`set_status` itself), plus `vcr/prompts/__init__.py`.
858: Their packaged instructions
859: (`vcr/data/vcr_create_instructions.md`/`vcr_update_instructions.md`)
860: adapt `dec`'s exact structure/tone to VCR's own schema (`## Verifies` ->
861: `## Coverage` -> `## Acceptance Criteria` -> `## More Information` ->
862: `## Updates` section recap, the closed DTAIS method vocabulary spelled
863: out verbatim, VCR's own four-value `draft`/`progress`/`complete`/
864: `approved` status set instead of DEC's six-value set, and references to
865: the new `specmgr://dtais` resource for method-word guidance) -- including
866: DEC's own step-0 "check `list_vcr` for a near-duplicate first" convention
867: and the same tool-call-sequence ending in `create_vcr(content)`/optional
868: `validate_vcr(content, full=False)`.
869: 
870: Implemented Task 3.3 (the cross-cutting `specmgr://dtais` resource,
871: REQ-006): `general/data/general_dtais.md` filled in every placeholder
872: from the Design Notes' persisted draft outline -- a closed-vocabulary
873: bullet list of the five DTAIS words (verbatim, in the same order as
874: `vcr.models.v1.body`'s `_AC_HEADING_PATTERN` method group, confirmed by a
875: new test), a "## When to apply each method" section with concrete
876: per-method guidance (informed by well-established V&V domain knowledge:
877: `Demonstration` for observable behavior without a quantitative
878: threshold, `Test` for a quantitative/measured threshold, `Analysis` for
879: calculation/modeling/simulation or pre-existence-of-system verification,
880: `Inspection` for artifact/source examination without operating the
881: system, and this feature's own addition `Special` for external
882: certification/compliance/supplier-conformance sign-off), and a
883: "## Relationship to `## Coverage`" section explaining that `## Coverage`
884: is a roll-up of every acceptance criterion's verification status (not an
885: independent field), concretely illustrated with `example.md`'s own
886: AC-004-pending-`Special`-certification `partial`-coverage scenario.
887: `general/resources/dtais.py` copies the plan's persisted sketch verbatim
888: (only the `..tools`/`...server` relative-import order was corrected to
889: match this codebase's actual isort convention, confirmed against
890: `general/resources/iso25010.py`'s own ordering), and
891: `general/resources/__init__.py` now imports/exports `dtais` alongside
892: `iso25010`/`version` (alphabetical).
893: 
894: Added 52 new unit tests across `tests/vcr/resources/`
895: (`test_vcr_schema.py`/`test_vcr_example.py`/`test_vcr_template.py`,
896: mirroring `tests/dec/resources/`'s three files), `tests/vcr/prompts/`
897: (`test_create_vcr.py`/`test_update_vcr.py`, mirroring
898: `tests/dec/prompts/`'s two files), and
899: `tests/general/resources/test_dtais.py` (mirroring
900: `tests/rsk/resources/test_tara.py`'s structure: a regex asserting the
901: five documented method-word bullets exactly match the model's closed
902: DTAIS set in order, a per-word round-trip through
903: `AcceptanceCriterion.from_text` confirming every documented word is
904: genuinely accepted end to end, and a rejected-word case using
905: `"Certification"` -- VCR's own retired 5th-method name -- which raises
906: `AssertionError` (an `AcceptanceCriterion` alias mismatch, not
907: `pydantic.ValidationError`, unlike RSK's `Strategy`-based rejected-word
908: test) since `AcceptanceCriterion` is a regex-`@alias`-matched heading
909: class, not a `field_validator`-checked value). Quality gate green: `ruff
910: format --check`, `ruff check`, `vulture` (no new whitelist entries
911: needed), and the full `unittest` suite (2452 tests, `OK`, up from 2400)
912: all pass. Did not touch `server.py`, `AGENTS.md`, top-level `README.md`,
913: or `.pre-commit-config.yaml` -- all reserved for Phase 4; `vcr/__init__.py`
914: also stays untouched (still no `tools`/`resources`/`prompts` import), so
915: the same non-blocking circular-import fragility noted in the Phase 2
916: Updates entry (isolated `vcr.models.v1` imports before `general` has
917: fully loaded) still applies identically to the new `vcr/resources`/
918: `vcr/prompts` modules in isolation -- unaffected in the full repo-wide
919: suite, which is the specified quality gate.
920: 
921: #### 2026-08-31T12:30:00.000000 — Phase 2 complete: `vcr/tools/` implemented, generic `update`/`set_status` dispatch wired for `type="vcr"`
922: 
923: Implemented the full `vcr/tools/` package, mirroring `dec/tools/` file-for-
924: file: `_paths.py` (`VCR_TYPE_NAME`, `VcrNotFoundError`, `vcr_base_dir`/
925: `ensure_vcr_base_dir`/`iter_vcr_paths`/`find_vcr_path`, built on the shared
926: `general.tools._doc_paths` helpers, not a new dependency), `_lock.py`
927: (`vcr_lock`), `_io.py` (`read_vcr`/`load_by_id`), `_write.py`
928: (`write_vcr_file`), and the 8 standard `@mcp.tool()` wrappers: `create_vcr`
929: (fresh `uuid.uuid4()` id, `type="vcr"`, `status="draft"` always on create,
930: filename `vcr-{id}-{slug}.md`), `parse_vcr`, `get_vcr` (with `raw: bool =
931: False`), `get_vcr_example`/`get_vcr_template` (reading new packaged data),
932: `list_vcr` (paged from day one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13),
933: `delete_vcr` (stub, always `NotImplementedError`), and `validate_vcr`
934: (disk-free/id-free dry run, `full: bool = False`). Copied the
935: already-finalized `example.md`/`template.md` planning drafts byte-for-byte
936: into `vcr/data/vcr_example.md`/`vcr_template.md`
937: (confirmed via `diff`: zero output) and declared the new
938: `"biz.dfch.specmgr.vcr"` package-data entry in `pyproject.toml`, inserted
939: after `"biz.dfch.specmgr.uc"` and before `"biz.dfch.specmgr.general"`,
940: matching every other domain's two-pattern (`data/*.md`, `data/*.json`)
941: shape even though no `vcr_schema.json` exists yet (Phase 3's job). Added
942: `vcr` as a tenth entry to the generic `update` tool's `_ADAPTERS` (new
943: `_update_vcr`, ported verbatim from `_update_dec`, appended last after
944: `feat`) and as an eleventh entry to `set_status`'s `_ADAPTERS` (new
945: `_set_status_vcr`, ported verbatim from `_set_status_dec` including the
946: `assert superseded_by is None` guard, inserted right after `feat` and
947: before the always-last `adr`), updating both tools' `Literal[...]`
948: parameter types, module/tool docstrings, and domain-count language
949: ("nine"/"ten" -> "ten"/"eleven" as appropriate) throughout. Added 64 new
950: unit tests under `tests/vcr/tools/` (mirroring `tests/dec/tools/`'s 13

(Output capped at 50 KB. Showing lines 1-950. Use offset=951 to continue.)
</content>
````

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 41.5s)

_Thinking:_

I've got a really solid understanding of the feature plan structure now. This is a very detailed plan with phases, tasks, design notes, decisions, etc.

Next, let me check the following:

1. The `update.py` generic tool, to see how it handles the dispatch table (I already saw the pattern in set_status).
2. The conventions in `.specmgr/conventions.md`.
3. The docstring of `server.py` (I've already confirmed it mentions delete).
4. Confirm whether ADR deletion is included — the issue says "(except ADR?)", and ADR has no `delete_adr` stub. Let me check: does ADR have a delete? No, there's no `delete_adr` in `adr/tools/`. So the 11 delete stubs are: delete_req, delete_uc, delete_tsk, delete_qa, delete_prb, delete_gol, delete_rsk, delete_dec, delete_sop, delete_feat, delete_vcr. 11 in total.

Now, a key design question: should the generic `delete` cover all 12 domains (including ADR), or just the 11 whole-body domains? The issue says "every domain (except ADR?) has a delete\_<domain> tool" — meaning ADR currently doesn't have a delete stub. And the generic delete "like set_status" — set_status covers all 12 including ADR. So there's an open question of whether delete should cover ADR too. I'll flag this as a decision point.

Let me look at conventions.md and check the delete stub tests to understand what gets deleted. Also let me confirm that no delete_adr exists, and understand the ADR deletion situation (ADR uses write_adr rendering).

Things to read:

- conventions.md
- one delete stub test (test_delete_rsk.py)
- the docstring section of server.py that enumerates the tools

Let me run these in parallel.

Let me review the coding conventions, a delete-stub test, and the `server.py` docstring's tool enumeration.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/conventions.md"
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/conventions.md</path>
<type>file</type>
<content>
1: # Specification: SpecMgr Coding Conventions
2: 
3: This document defines the general coding requirements and conventions used throughout the SpecMgr project.
4: 
5: ## Python Version and Types
6: 
7: **Requirement:** Use Python 3.11+ and modern Python type notation.
8: 
9: - Python version: 3.11 and later
10: - Prefer built-in types over typing module aliases:
11:   - Use `str` instead of `Str`
12:   - Use `list` instead of `List`
13:   - Use `dict` instead of `Dict`
14:   - Use `bool` instead of `Bool`
15:   - Use `tuple` instead of `Tuple`
16:   - Use `set` instead of `Set`
17:   - Use `bytes` instead of `Bytes`
18:   - Use `int`, `float`, etc. directly over `Integer`, `Float`, etc.
19: 
20: **Example:**
21: ```python
22: # ✓ Modern Python (3.11+)
23: def process_items(items: list[str], filter_enabled: bool = True) -> str | None:
24:     if filter_enabled:
25:         result = [item.upper() for item in items]
26:     else:
27:         result = items.copy()
28:     return result
29: ```
30: 
31: ## Assert Statements
32: 
33: **Rule 1:** Always use `assert` to validate all input parameters in public methods and functions.
34: 
35: **Rule 2:** Use assert statements for input parameter validation, preconditions, and program invariants only.
36: 
37: **Rule 3:** Do not use assert for user-controlled flow control; use it only for program invariants and input validation.
38: 
39: **Example:**
40: ```python
41: def calculate_discount(value: str, price: float, discount_rate: float) -> float:
42: 
43:     assert isinstance(value, str), type(value)
44:     assert value.strip()
45:     assert isinstance(price, float), type(price)
46:     assert 0 <= price, price
47: 
48:     discount_rate = 0.05
49: 
50:     result = price * (1 - discount_rate)
51: 
52:     return result
53: ```
54: 
55: **Best Practices:**
56: - Define numeric and string constants for thresholds, minimums, maximums, and standard states
57: - Place constants at module level with clear documentation
58: - Use constants in assert statements to make conditions self-documenting and maintainable
59: 
60: ## Variable Naming Convention
61: 
62: **Requirement:** When a function or method returns a value, use the variable name "result" in the function body.
63: 
64: - Use `result: Type = value` pattern for return values
65: - Only use different variable names for special cases where the name is more descriptive
66: - Follow this convention consistently for all return value assignments
67: 
68: **Example:**
69: 
70: ```python
71: def get_status() -> str:
72:     result = "active"
73:     return result
74: 
75: 
76: def calculate_total(items: list[str]) -> int:
77:     result = 0
78:     for item in items:
79:         result += len(item)
80:     return result
81: ```
82: 
83: ## Comparison Constants
84: 
85: **Requirement:** Use named constants for values used in comparisons (lvalue-side constants).
86: 
87: - When comparing variables against string literals or values used as a standard for comparison, define those values as constants
88: - This improves readability and makes it easier to update the comparison value later
89: - Apply this pattern to all equality checks (`==`, `!=`, `is`, `is not`), inequality checks (`<`, `>`, `<=`, `>=`), and membership checks (`in`, `not in`)
90: 
91: **Example:**
92: ```python
93: # ✓ Use constant for comparison value
94: VALID_STATUS = "active"
95: user_status = "inactive"
96: if user_status == VALID_STATUS:
97:     print("Status is valid")
98: 
99: # ✓ Use constant for threshold comparison
100: MAX_RETRY_ATTEMPTS = 3
101: attempt = 5
102: if attempt >= MAX_RETRY_ATTEMPTS:
103:     raise RuntimeError("Max attempts exceeded")
104: 
105: # ✓ Use constant for membership checks
106: ALLOWED_FILE_EXT = {".md", ".txt", ".py"}
107: filename = "document.md"
108: if filename.endswith(tuple(ALLOWED_FILE_EXT)):
109:     print("File type is allowed")
110: 
111: # ✗ Avoid inline string values in comparisons
112: # if user_status == "active":  # Hard to maintain
113: #     print("Status is valid")
114: ```
115: 
116: **Best Practices:**
117: - Place constants at the top of the module or in a dedicated configuration section
118: - Use `ALL_CAPS` naming convention for constants to distinguish them from variables
119: - Group related constants together for easy maintenance
120: - Document the purpose and allowed values of each constant
121: 
122: **Example Module-Level Constants:**
123: ```python
124: # Constants for string comparisons
125: DEFAULT_ENCODING = "utf-8"
126: INDENTATION = "    "
127: 
128: # Constants for numeric comparisons
129: MIN_USER_ID = 1
130: MAX_BATCH_SIZE = 1000
131: 
132: # Constants for status checks
133: STATUS_ACTIVE = "active"
134: STATUS_INACTIVE = "inactive"
135: STATUS_PENDING = "pending"
136: ```
137: 
138: ## Type Hints
139: 
140: **Requirement:** Always use type hints for all function signatures, parameters, and variables.
141: 
142: - Type hints are mandatory for:
143:   - Function and method parameters
144:   - Return types
145:   - Variables that are assigned specific types in functions/methods
146:   - Variables outside functions when they are not inferred from context
147: 
148: **Example:**
149: ```python
150: def load_config(filename: str) -> dict[str, str]:
151:     content: str = ""
152: 
153:     with open(filename, "r", encoding="utf-8") as f:
154:         content = f.read()
155: 
156:     result: dict[str, str] = {}
157:     for line in content.split("\n"):
158:         if ":" in line:
159:             key, value = line.split(":", 1)
160:             result[key.strip()] = value.strip()
161: 
162:     return result
163: ```
164: 
165: ## Documentation Requirements
166: 
167: **Requirement:** Include docstrings for classes, their attributes, and method/function parameters/returns.
168: 
169: - Classes: Document purpose and behavior in class docstrings
170: - Attributes: Document class attributes using inline comments
171: - Functions/methods: Document parameters and return types
172: - Maintain formal, concise documentation; avoid obvious statements
173: 
174: **Example:**
175: ```python
176: class DataProcessor:
177:     """Process and validate data entries.
178: 
179:     Attributes:
180:         max_items: Maximum number of items allowed per batch.
181:     """
182: 
183:     max_items: int = 100
184: 
185:     def __init__(self, max_items: int) -> None:
186:         """Initialize the processor.
187: 
188:         Args:
189:             max_items: Maximum batch size.
190:         """
191:         self.max_items = max_items
192: 
193:     def process(self, items: list[str]) -> str:
194:         """Process a batch of items.
195: 
196:         Args:
197:             items: List of items to process.
198: 
199:         Returns:
200:             Summary string of processed items.
201:         """
202:         assert len(items) > 0
203:         result = f"Processed {len(items)} items"
204:         return result
205: ```
206: 
207: ## Additional Best Practices
208: 
209: ### Import Organization
210: 
211: ```python
212: # Standard library imports
213: import os
214: from pathlib import Path
215: 
216: # Third-party imports
217: from pydantic import BaseModel
218: 
219: # Local imports
220: from biz.dfch.specmgr.models import Adr
221: ```
222: 
223: ### Docstring Style
224: 
225: ```python
226: def process_data(data: list[str]) -> str:
227:     """
228:     Process a list of strings and return a summary.
229: 
230:     Args:
231:         data: The list of strings to process.
232: 
233:     Returns:
234:         A summary string of the processed data.
235: 
236:     Example:
237:         >>> process_data(["hello", "world"])
238:         "Processed 2 items"
239:     """
240:     assert len(data) > 0, "Data list cannot be empty"
241:     result = "Processed items"
242:     return result
243: ```
244: 
245: ### Error Handling
246: 
247: ```python
248: from pathlib import Path
249: 
250: 
251: def load_file(path: str) -> str:
252:     """Load content from a file.
253: 
254:     Args:
255:         path: Path to the file to load.
256: 
257:     Returns:
258:         File content as a string.
259: 
260:     Raises:
261:         FileNotFoundError: If the file doesn't exist.
262:         UnicodeDecodeError: If the file cannot be decoded.
263:     """
264:     file_path = Path(path)
265:     result = file_path.read_text(encoding="utf-8")
266:     return result
267: ```
268: 
269: ### Test Framework
270: 
271: **Requirement:** Use `unittest` for all test cases and follow a consistent structure.
272: 
273: -[ ] All tests must use the `unittest` framework, not `pytest`
274: -[ ] Tests must be in the `tests/` directory and have the same hierarchy as the source structure
275: -[ ] Test file names start with `test_`
276: -[ ] Test classes inherit from `unittest.TestCase`
277: -[ ] Test class names start with `Test`
278: -[ ] Test methods start with `test_`
279: -[ ] Use descriptive names that show what the test does and under what conditions
280: -[ ] Do not use docstrings for test methods
281: -[ ] Tests have one *subject under test*. The subject variable name is `sut`. 
282: -[ ] Tests have a clear *arrange*-*act*-*assert* (AAA) structure
283: -[ ] Place shared test fixtures in `fixtures` directory
284: -[ ] Avoid complex setup/teardown; prefer simple, isolated tests
285: -[ ] Use `setUp()` and `tearDown()` methods for test initialization and cleanup
286: -[ ] Mock external dependencies using `unittest.mock`
287: 
288: **Examples**:
289: 
290: ```python
291: . <project-root>
292: + src
293:     + project
294:       + domainA
295:         + moduleA1
296:           : class Calculator
297: + tests
298:     + project
299:       + domainA
300:         + moduleA1
301:           - Test_Calculator.py
302:             : test_divide_by_zero_fails
303:             : test_divide_by_int_returns_float
304:             : test_add_int_and_float_succeeds
305: ```
306: 
307: ```python
308: # test_Calculator.py
309: class TestCalculator(unittest.TestCase):
310:     def test_add_int_float_succeeds() -> None:
311:         expected = 42.0
312:         addend: int = 5
313:         summand: float = 37.0
314: 
315:         sut = Calculator()
316: 
317:         result = sut.add(addend, summand)
318: 
319:         self.assertEqual(result, expected)
320: 
321:     def test_divide_by_zero_fails() -> None: ...
322: ```
323: 
324: 
325: ## TODO
326: 
327: * Use "uv", do not use "pip"
328: * Use "setuptools", do not use "hatchling"
329: 
330: ## Rationale
331: 
332: These conventions were chosen to:
333: 
334: 1. **Simplicity:** Modern Python types are more intuitive than typing aliases
335: 2. **Clarity:** Assert statements provide clear preconditions and invariants
336: 3. **Consistency:** `result` variable name makes return values obvious
337: 4. **Type Safety:** Mandatory type hints ensure code is self-documenting and catch type errors early
338: 5. **Readability:** Followed conventions make the codebase easier to understand and maintain
339: 
340: ## Changelog
341: 
342: - **2026-08-06:** Initial version created
343: - **2026-08-06:** Added Python 3.11+ type requirements
344: - **2026-08-06:** Added assert statement requirement
345: - **2026-08-06:** Added variable naming convention requirement
346: - **2026-08-06:** Added mandatory type hints requirement
347: - **2026-08-06:** Added documentation requirements with reference to AGENTS.md
348: - **2026-08-06:** Added test framework conventions
349: - **2026-08-06:** Added test file organization guidelines
350: - **2026-08-06:** Added test method naming conventions
351: - **2026-08-06:** Added test data and fixtures guidelines

(End of file - total 351 lines)
</content>
````

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/tests/rsk/tools/test_delete_rsk.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/tests/rsk/tools/test_delete_rsk.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Tests for the ``delete_rsk`` ``@mcp.tool()`` stub wrapper (Task 3.6)."""
19: 
20: from __future__ import annotations
21: 
22: import unittest
23: 
24: from biz.dfch.specmgr.rsk.tools.delete_rsk import delete_rsk
25: 
26: 
27: class TestDeleteRsk(unittest.TestCase):
28:     """Tests for the delete_rsk stub tool."""
29: 
30:     def test_raises_not_implemented_error(self) -> None:
31:         """delete_rsk must always raise NotImplementedError, regardless of id."""
32:         with self.assertRaises(NotImplementedError):
33:             delete_rsk("some-id")
34: 
35:     def test_raises_not_implemented_error_for_unknown_id(self) -> None:
36:         """delete_rsk must never look up or validate the id -- it always raises."""
37:         with self.assertRaises(NotImplementedError):
38:             delete_rsk("does-not-exist-and-never-checked")
39: 
40: 
41: if __name__ == "__main__":
42:     unittest.main()

(End of file - total 42 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"delete\\|General tools\\|set_status\\|mdformat\\|webfetch\" /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py | head -40"
}
```

**Output:**

```
153:``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
157:``get_uc_template``, ``create_uc``, ``delete_uc``
162:``get_req_template``, ``create_req``, ``delete_req``
167:``get_tsk_template``, ``create_tsk``, ``delete_tsk``
172:``get_qa_template``, ``create_qa``, ``delete_qa``
177:``delete_prb`` (stub, not yet implemented), ``validate_prb``.
181: ``delete_gol`` (stub, not yet implemented), ``validate_gol``.
185: ``get_rsk_template``, ``create_rsk``, ``delete_rsk``
190:    ``get_dec_template``, ``create_dec``, ``delete_dec``
195:    ``get_sop_template``, ``create_sop``, ``delete_sop``
197:    per-domain ``update_sop``/``set_status_sop`` tools at all -- whole-body and line-range
199:    and status changes through the generic ``set_status`` tool (``type="sop"``), per ADR
208:  ``get_feat_template``, ``create_feat``, ``delete_feat``
211:  ``general/tools/_doc_paths.py``) and has no ``update_feat``/``set_status_feat`` tools of
212:  its own -- it dispatches through the generic ``update``/``set_status`` tools below from
217:  ``create_vcr``, ``delete_vcr`` (stub, not yet implemented), ``validate_vcr``.
218:  General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
224:result is validated as a whole document before anything is written); ``set_status`` --
231:``webfetch`` -- fetch a URL over HTTP GET with a
272:``update``/``set_status`` tools with ``type="sop"`` (both whole-body and line-range
274:``set_status_sop`` tools (ADR 36905d5b-8057-4294-8665-c7eed5534db0).
296:resources, the ``mdformat`` tool, or the ``compact_history`` prompt) stay under the top-level

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 53.8s)

_Thinking:_

With this, I've been able to grasp the comprehensive overall picture. Let me confirm a few more things:

1. How `update.py` structures its dispatch table (already confirmed the pattern via set_status).
2. Whether the existing tests for `set_status` include injection/path-safety tests (to check the precedent for the "no path injection" requirement).
3. How the worktree setup for existing features looks (feat-33-vcr) — I've already confirmed the worktree list.

Let me also understand the following:

- The issue states "We must also update the corresponding decisions and documents that require domains to provide the 'old' delete tool." So I need to find ADRs and documents that reference delete stubs or require domains to provide delete tools. What I found:
  - ADR 36905d5b (consolidation of update/set_status) — mentions the generic tools but I need to check whether it mandates delete stubs.
  - AGENTS.md — has a list of "delete\_\* are stubs" under "still truly missing."
  - The server.py docstring mentions the delete stubs.

Let me check where the requirement that "domains should provide a delete\_<domain> tool" is documented. This is probably in the "simple surface"/domain conventions. Let me search for the canonical description of the "8 standard tools" that includes the delete stub.

Actually, let me look for the ADR or document that defines the standard domain tool surface (the 8 tools including the delete stub). The feat-33 README says "8 standard tools (... delete_vcr stub ...)". This "8 standard tools" convention must be defined somewhere. Let me search.

Let me also confirm that ADR deletion isn't included (no delete_adr exists) — confirmed. adr/tools has no delete_adr.py.

Let me do a few more targeted searches, then confirm the worktree/branch setup approach, then ask the user clarifying questions about the key design decisions, and write the plan.

Things to check:

1. Where the "8 standard tools" / delete stub convention is defined (ADR or docs).
2. Path-safety/injection tests for the generic tools (precedent).
3. The exact list of delete stubs and their tests (11 domains + tests).

Let me search for the canonical "standard tools" definition.

Let me find where the "standard domain tool surface" (including delete stubs) is canonically defined, and check for any path-safety test precedent.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rn \"delete_<\\|delete stub\\|delete_\\* \\|standard tools\\|eight standard\\|8 standard\\|NotImplementedError\" /home/user/src/biz.dfch.SpecMgr/docs/adr/*.md | head -30"
}
```

**Output:**

```
(no output)
```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rln \"path\\|injection\\|\\.\\.\\|traversal\\|escape\\|separator\" /home/user/src/biz.dfch.SpecMgr/tests/general/tools/test_set_status.py /home/user/src/biz.dfch.SpecMgr/tests/general/tools/test_update.py; echo \"---search for existing path-safety guards in src---\"; grep -rn \"separators\\|is_absolute\\|resolve()\\|\\\\.\\\\.\\\\|\\\\\"..\\\\\"\\\\|traversal\\|escape\" /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/*.py /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/_paths.py | head -30"
}
```

**Output:**

```
/home/user/src/biz.dfch.SpecMgr/tests/general/tools/test_set_status.py
/home/user/src/biz.dfch.SpecMgr/tests/general/tools/test_update.py
---search for existing path-safety guards in src---
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/mdformat.py:29:from ...models.md._markdown import format_markdown_document
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/mdformat.py:30:from ...server import mcp
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_packaged_data.py:20:shape so a future artifact domain (UC, goal, acc, ...) never needs its own
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_paging.py:41:from ..models.paged_result import PagedResult
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:78:from ...adr.tools._io import load_by_id as load_adr_by_id
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:79:from ...adr.tools._io import write_adr
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:80:from ...adr.tools._lock import adr_lock
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:81:from ...adr.tools._paths import adr_base_dir
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:82:from ...dec.models.v1 import DecDocument, DecFrontmatter
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:83:from ...dec.tools._io import load_by_id as load_dec_by_id
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:84:from ...dec.tools._lock import dec_lock
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:85:from ...dec.tools._paths import dec_base_dir
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:86:from ...dec.tools._write import write_dec_file
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:87:from ...feat.models.v1 import FeatDocument, FeatFrontmatter
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:88:from ...feat.tools._io import load_by_id as load_feat_by_id
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:89:from ...feat.tools._lock import feat_lock
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:90:from ...feat.tools._paths import feat_base_dir
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:91:from ...feat.tools._write import write_feat_file
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:92:from ...gol.models.v1 import GolDocument, GolFrontmatter
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:93:from ...gol.tools._io import load_by_id as load_gol_by_id
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:94:from ...gol.tools._lock import gol_lock
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:95:from ...gol.tools._paths import gol_base_dir
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:96:from ...gol.tools._write import write_gol_file
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:97:from ...models.adr import Adr
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:98:from ...models.adr.v1 import mutations
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:99:from ...prb.models.v1 import PrbDocument, PrbFrontmatter
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:100:from ...prb.tools._io import load_by_id as load_prb_by_id
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:101:from ...prb.tools._lock import prb_lock
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:102:from ...prb.tools._paths import prb_base_dir
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/set_status.py:103:from ...prb.tools._write import write_prb_file

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 42.4s)

_Thinking:_

Interesting — there's no existing path-injection/traversal guard anywhere in the codebase. This confirms that the "no path injection" requirement is new and needs to be designed.

Also, the "8 standard tools" convention isn't written in any ADR — it's a convention that's been established across multiple features. Let me check the feat-31-feature and feat-30-sop READMEs to see how they document this, and more importantly, find where the delete stub requirement is canonically stated. The issue says "update the relevant decisions and documents that require domains to provide the 'old' delete tool."

Let me search for the exact phrase about delete stubs in ADRs and feature docs. Let me check ADR 36905d5b more thoroughly, and also look at the feat-31 and feat-30 READMEs.

Actually, I already have a good enough grasp. Let me check a few specific things:

1. Does ADR 36905d5b explicitly require a delete tool? Let me read the full text.
2. The feat-31-feature README (the one about feat's special path handling) — relevant since feat's id isn't a UUID.

Let me read the full text of ADR 36905d5b, and grep the feature READMEs for mentions of the delete convention.

No existing path-injection guards exist — confirming this is new design work. Let me read the consolidation ADR fully and check how feature plans document the delete-stub convention.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md</path>
<type>file</type>
<content>
1: ---
2: status: accepted
3: date: '2026-08-27'
4: decision-makers: OpenCode agent + user decision
5: id: 36905d5b-8057-4294-8665-c7eed5534db0
6: version: 1.0.0
7: ---
8: 
9: # Consolidate whole-body update and status-change tools into generic type-dispatched tools
10: 
11: ## Context and Problem Statement
12: 
13: The specmgr MCP server currently exposes 15 near-duplicate mutation tools for what are two conceptual operations: seven per-domain whole-body updates (`update_req`, `update_uc`, `update_tsk`, `update_qa`, `update_prb`, `update_gol`, `update_rsk`), seven per-domain status changes (`set_status_req`, `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`, `set_status_gol`, `set_status_rsk`), and ADR's own `set_status`. Each tool shares the same shape — id resolution in one domain directory, validation, frontmatter carry-over, `updated` bump, write — and differs only in domain vocabulary. LLM/agent clients see 15 entries in the MCP tool list for 2 conceptual operations, and every future document domain (e.g. the planned `ac`) would add more of the same duplicates, growing the surface linearly with the number of domains.
14: 
15: ## Decision Drivers
16: 
17: - A simpler tool surface: the two conceptual operations should be exposed as two tools, not fifteen near-duplicates.
18: - Id resolution must not require an all-domains directory scan on the write path, and must not introduce per-domain v4-UUID-collision ambiguity — uuid-only id resolution was considered and rejected (per-domain v4 UUIDs are not guaranteed unique across domains).
19: - The calling client already knows the domain it is operating on (the same vocabulary as the frontmatter `type` field), so passing it explicitly costs the client nothing.
20: - Preserve the existing invariants: the filesystem is the sole source of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3) and validation happens before any write (nothing is written on validation failure).
21: 
22: ## Considered Options
23: 
24: - Option 1: two generic tools in `general/tools/` with an explicit `type` parameter — `update(id, type, content, begin, end)` covering the seven whole-body domains and `set_status(id, type, status, superseded_by)` covering all eight domains including `adr` — each dispatching to a private, verbatim-ported per-domain adapter. Chosen.
25: - Option 2: generic tools that resolve the id by uuid alone, scanning every domain directory to locate the matching document.
26: - Option 3: keep the 15 per-domain tools unchanged.
27: 
28: ## Decision Outcome
29: 
30: Option 1: two generic, type-dispatched tools — `update(id, type, content, begin, end)` in `general/tools/update.py` for the seven whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`), and `set_status(id, type, status, superseded_by)` in `general/tools/set_status.py` for all eight domains including `adr`. The explicit `type` parameter keeps id resolution single-domain (no directory scan, no cross-domain UUID ambiguity), matches the domain vocabulary the calling client already has, and reduces the tool surface from 15 near-duplicate entries to 2. Each domain's semantics are preserved 1:1 by a private adapter that is a verbatim port of the deleted tool body, so the filesystem-is-source-of-truth and validate-before-write invariants are untouched.
31: 
32: ### Consequences
33: 
34: - Bad (breaking): the 14 per-domain tools are removed outright, and ADR `set_status`'s signature gains a required `type` parameter — existing ADR callers must now pass `type="adr"`. The package is 0.x and the MCP tool list is the only client contract; the breaking change is recorded in `CHANGELOG.md`.
35: - ADR is excluded from `update` — its section-level MADR contract (`update_frontmatter`/`update_section`/`option_*`, ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) has no whole-body replace by design — but is included in `set_status` with the `superseded_by` special case: `superseded_by` composes the status as `"superseded by {superseded_by}"`, and `superseded_by` given with any `type` other than `"adr"` raises `ValueError` before any file access.
36: - The `update` line-range contract: optional 1-based, inclusive body-line coordinates `begin`/`end`, with `N+1` as the EOF sentinel (`begin = end = N+1` appends at end of body; `end = N+1` extends the range through the last line). The spliced result is validated as a whole document before anything is written (splice-then-validate-whole), and the YAML frontmatter is never addressable (coordinates are body-relative by construction).
37: - Line numbers for range updates are served by a new `get_<d>(raw=True)` parameter returning the frontmatter-stripped body text verbatim — tool-first per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (agents invoke tools more reliably than parameterized resources); re-introducing `specmgr://<d>/{id}` resources was considered and rejected.
38: - Good: future domains (e.g. `ac`) add one dispatch entry per generic tool (plus a `raw` getter parameter), not new tools.
39: 
40: ## Pros and Cons of the Options
41: 
42: ### Option 1: Generic tools with an explicit type parameter
43: 
44: #### Pros
45: 
46: - Minimal tool surface: two tools for the two conceptual operations (the feature ends at 71 tools / 25 resources / 19 prompts, from 84/25/19: −15 +2), instead of 15 near-duplicate entries in the MCP tool list.
47: - The calling client already knows the domain — it is the same vocabulary as the frontmatter `type` field — so the explicit parameter costs the client nothing, and id resolution stays single-domain: no all-directories scan on the write path, no per-domain v4-UUID-collision ambiguity.
48: - Every future domain (e.g. the planned `ac`) adds one dispatch entry per generic tool, keeping the surface flat as domains grow.
49: - Preserves all per-domain semantics: each adapter is a verbatim port of the deleted tool body (same lock, same `load_by_id`, same frontmatter carry-over and `updated` bump, same write path, same domain not-found error), and the filesystem-is-source-of-truth and validate-before-write invariants are untouched.
50: 
51: #### Cons
52: 
53: - Breaking change for 0.x clients: the 14 per-domain tools disappear, and ADR `set_status`'s signature gains a required `type` (existing ADR callers must now pass `type="adr"`).
54: - ADR needs special-casing in `set_status` (the `superseded_by` composition) and is excluded from `update` by design (its MADR section-level contract has no whole-body replace).
55: 
56: ### Option 2: uuid-only id resolution scanning all domain directories
57: 
58: #### Pros
59: 
60: - Shortest client call: no `type` parameter; any document in any domain is addressable by id alone.
61: 
62: #### Cons
63: 
64: - Full-directory scan on every write: all domain directories must be traversed and every file parsed to locate the matching id, and the cost grows with each added domain on the write path.
65: - Per-domain v4 UUIDs are not guaranteed unique across domains, so a collision between two domains makes the id ambiguous — the server would have to pick one arbitrarily or raise a new class of errors.
66: - Loses the explicit domain vocabulary clients already use everywhere else (the frontmatter `type` field) and obscures which domain's semantics (status vocabulary, lock, write path) are actually being applied.
67: 
68: ### Option 3: Keep the per-domain tools
69: 
70: #### Pros
71: 
72: - No breaking change; existing clients keep working unchanged.
73: - No dispatch-table machinery; each tool remains a simple single-domain wrapper.
74: 
75: #### Cons
76: 
77: - The MCP tool list carries 15 near-duplicate entries for 2 conceptual operations, inflating every client's tool context.
78: - Every future domain adds more near-duplicate tools (a `update_<d>` / `set_status_<d>` pair per domain), growing the surface linearly with the number of domains.
79: - LLM clients must pick among the duplicates for each operation, which risks mis-selection and makes the surface harder to document, test, and keep consistent.
80: 
81: ## More Information
82: 
83: - Feature plan and progress: `.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`.
84: - Related ADRs: ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-based document reads are tools, not resources), 71fd95d7-07f2-466f-81aa-d29b7e3ef34c (the ADR `update_section` contract that `update` deliberately does not extend to ADR), 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of truth), ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy — the generic tools live in the cross-cutting `general/` package).

(End of file - total 84 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rn \"delete\" /home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md /home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md /home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md | grep -iv \"session\\|delete_adr\\|option_delete\" | head -30"
}
```

**Output:**

```
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:104:  `get_feat_example`, `get_feat_template`, `delete_feat` (stub),
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:152:  registered, and callable; a create→get→list→delete(stub)→validate
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:219:- Real implementation of `delete_feat` — a stub raising
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:220:  `NotImplementedError`, matching every other domain's `delete_*` stub.
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:657:  `get_feat_example`/`get_feat_template`, `delete_feat` (stub,
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:680:  `test_delete_feat.py`/`test_get_feat_example.py`/
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:783:  `delete_*`/`validate_*` enumeration lists, the domain-register-all-three
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:785:  (server.py)" all gained `feat`/`delete_feat`/`validate_feat`. Root
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:972:`get_feat_example`, `get_feat_template`, `delete_feat` stub, `validate_feat`)
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:978:update(line-range)→set_status→get→list→validate→delete(stub) round-trip and
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:1143:  unaffected by this change) is preserved, not deleted.
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:1276:  `delete_*` lists and the register-all-three sentence; the "MCP server
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:1323:    test_full_lifecycle_roundtrip` (create→get→list→...→delete-stub→
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:1494:    the packaged files themselves are Phase 3's job), `delete_feat` (stub),
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:1510:  `test_validate_feat.py`, `test_delete_feat.py`,
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:1514:  list→validate→delete(stub) round-trip and a 20-thread concurrent-`create_feat` collision test (ACC-002/ACC-003/ACC-004).
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:1678:  artifacts — flagged as safe to remove, not yet deleted (awaiting
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:1909:  `delete_feat` stub/`validate_feat` + `type="feat"` in the generic
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:50:  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13), `get_sop(id, raw=False)`, `get_sop_example`, `get_sop_template`, `delete_sop` (stub),
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:122:  `sop-{id}-{slug}.md`; `delete_sop` raises `NotImplementedError`;
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:201:- Real implementation of `delete_sop` — a stub raising
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:202:  `NotImplementedError`, matching every other domain's `delete_*` stub.
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:376:`delete_sop(id)` stub (`NotImplementedError`, `structured_output=False`);
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:455:  enumeration and to the `delete_*` stub list; explicit note that `sop`
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:571:  `delete_sop` stub `structured_output=False`) — depends on: Task 2.1 —
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:677:  `delete_*` stub list; note on `sop`'s dispatch-only tool surface;
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:718:`set_status(type="sop")`→`validate_sop`→`delete_sop`) and ACC-007
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:818:`delete_sop` (stub, `structured_output=False`), `validate_sop`) plus the
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:904:  `get_sop_example`, `get_sop_template`, `create_sop`, `delete_sop` stub,
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-30-sop/README.md:944:  `validate_*` list, `delete_*` stub list, "each register" enumeration,

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 134.8s)

_Thinking:_

With this, I've got a very complete overall picture. The delete-stub convention is documented in each feature's README, and the "8 standard tools" surface is an established convention. The ADR that most needs updating is 36905d5b (the ADR on generic tool consolidation). In practice, this ADR is about `update`/`set_status` and does not mandate deletion. The requirement that "domains must provide a delete tool" is a cross-cutting convention documented in AGENTS.md and in the README of each feature.

Let me check AGENTS.md — in the "still genuinely missing" section it's written as follows:

- "`delete_req`/`delete_uc`/... are stubs, not yet implemented."

And in each domain's bullet list, `delete_<d>` stubs are enumerated.

So "the relevant decisions and documents that require domains to provide the 'old' delete tool" are:

1. **AGENTS.md** — the Status section bullet points for each domain enumerate the `delete_<d>` stubs; the "still genuinely missing" bullet states that the delete stubs are not implemented; the description of `general/` describes the two generic tools (`update`, `set_status`) — the new `delete` needs to be added there.
2. **The docstring of server.py** — the authoritative tool list that mentions `delete_*` stubs for each domain; `delete` needs to be added to the generic tools paragraph.
3. **ADR 36905d5b** — the ADR on generic tool consolidation. This is the decision-level document. A new ADR should be created (following ADR conventions), or 36905d5b should be updated, to record that generic `delete` supersedes per-domain delete tools. Actually, the issue says "update the relevant decisions and documents." Given the ADR convention (ADR 898bfcd0: ADRs are only created/edited via MCP tools), a new ADR should be created via the `create_adr` tool and 36905d5b should be recorded as partially superseded, or the new ADR should reference it. But this is design-time, and since we're only planning, we just need to note it.
4. **The README of each feature** — but these are historical progress records and should not be rewritten. The issue says "documents that require domains to provide the 'old' delete tool" — the forward-looking conventions are in AGENTS.md and ADRs.

Actually, let me reconsider. The important "decisions" are ADRs. Let me check if there's an ADR that mandates the 8-tool surface including delete. From the grep results, the ADRs mentioning delete are:

- 36905d5b (generic update/set_status — delete is not mandated)
- 71fd95d7 (ADR's update_section with a deletion sentinel — this is about ADR options/sections, not about document deletion)
- 898bfcd0 (ADRs only via MCP)
- 9d3800cf (vulture)
- d54abe50 (pros and cons derived containers)

In other words, there is no ADR that specifically mandates per-domain delete tools. The convention lives in AGENTS.md and the per-feature READMEs. Therefore, "updating the relevant decisions" primarily means the following:

- Creating a new ADR that records the decision on the generic `delete` tool (this is the "decision").
- Updating AGENTS.md (Status bullets, the "still missing" delete stub list, the general/ description).
- Updating the docstring of server.py (the authoritative tool list).
- Possibly updating ADR 36905d5b to reference the new delete ADR, or noting it as a follow-up.

Now, the user has clearly stated: "I want to create and design a new feature, but I don't want to implement it yet." And "I want to put this feature in a separate git worktree branch. There is already a sibling directory for it. The branch and feature name is 'feat-36-delete'."

So the deliverables for this planning task are:

1. A feature plan (README.md) at `.specmgr/feat/feat-36-delete/README.md` inside the new worktree.
2. Setting up a git worktree at `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` with branch `feat-36-delete`.

However — we are currently in PLAN MODE (read-only). We cannot create the worktree or write files right now. The user said "I want to create and design a new feature, but I don't want to implement it yet... please make a plan."

Therefore, my job right now is to make a plan. The plan includes the worktree setup steps (which will be executed in the implementation phase), and the design of the feature itself.

Wait, let me re-read: "I want to create and design a new feature, but I don't want to implement it yet. Please look at what we want to do. How can this be done, and make a plan."

So the user is asking for a plan for the feature (design + how to do it). The feature itself is about implementing the generic delete tool. But the user does not want to implement it yet — they want to create/design it. In other words, "creating and designing a feature" means producing a feature plan (README.md) and setting up the worktree/branch. The "implementation" (writing the actual delete tool code) is not yet desired.

This matches the repository's conventions: a feature is a `.specmgr/feat/feat-NNN-slug/README.md` that includes a plan (requirements, acceptance criteria, design notes, task list) and progress. So the deliverable of this task is:

1. Set up the worktree + branch `feat-36-delete`.
2. Create `.specmgr/feat/feat-36-delete/README.md` with a comprehensive design plan (following the template and the conventions of recent features).
3. Do not implement the delete tool code.

So my plan (as a plan-mode agent) should describe what to do in these steps, and importantly, should present the feature design itself so the user can review/approve it before we write the README.

Now, there are several important design decisions I should surface to the user as questions, since they involve trade-offs:

**Decision 1: Which domains should the generic `delete` cover?**

- Option A: Only the 11 whole-body domains that currently have `delete_<d>` stubs (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr) — mirroring the existing stubs exactly, and ADR is not included (ADR has no delete stub, and per ADR 36905d5b/71fd95d7 ADR is treated specially).
- Option B: All 12 domains including ADR (mirroring `set_status` which covers ADR).
  The issue says "all domains (except ADR?)" — the question mark suggests the author is unsure. I lean toward Option A (11 domains, excluding ADR). Reasons: (a) no `delete_adr` stub exists, (b) ADR has special handling (render round-trip, and it's under `models/adr` not the domain package, and it's the "most complete" domain). But it could also be argued for Option B for full consistency with set_status. This is worth asking the user about.

Actually, let me reconsider. The `update` tool excludes ADR (by design, ADR has no whole-body replacement). The `set_status` tool includes ADR. So there is precedent for both. For delete, since ADR never had a delete stub to begin with, and ADR deletion is a heavier operation (it is an architecture record, and deleting it would break cross-references in other ADRs' "superseded by"), I think excluding ADR is safer and matches the "replace the existing delete\_<domain> stubs" framing. But I should ask the user.

**Decision 2: Delete semantics — hard delete or soft delete?**
The issue clearly describes hard delete: "create the corresponding path and find the artifact to delete," "have a lock in place when finding and deleting the file." So it's a hard delete (file removal from disk). But I should confirm: for `feat` (one folder per document), deleting means `shutil.rmtree` on the entire `<base>/<id>/` folder (which may contain README.md and history.md). This is a significant nuance. Confirm hard delete + folder removal for feat.

**Decision 3: Path injection safety.**
The issue explicitly requires: "no one should be able to 'inject' a relative path via either type or uuid."

- `type` is `Literal[...]` (closed set) → inherently safe, same as set_status.
- `id`/uuid needs validation. Two sub-approaches:
  - (a) For the 10 UUID domains: validate id against a strict UUID regex (canonical 8-4-4-4-12 hex). This rejects `../`, `/`, backslashes, etc.
  - (b) For `feat`: validate id against the `feat-NNN-slug` folder pattern, and additionally ensure it does not contain path separators.
  - Also, as defense in depth: after resolving the path, assert that the resolved path is within the base directory (`path.resolve().is_relative_to(base_dir.resolve())`).
    This is a new primitive (no precedent). It should be centralized — e.g., a shared helper in `general/tools/` (like `_doc_paths.py`) that validates id and confirms containment. I'll propose a new module `general/tools/_id_safety.py` or an extension of `_doc_paths.py` with a function like `resolve_within_base(base_dir, candidate)` + an id validator.

Actually, the existing `find_*_path` functions in the flat domains scan files, so a malicious id will simply not match (it's safe, but it wastes time parsing every file, and the error message will be "not found" rather than "invalid id"). But `feat`'s shortcut directly does `base_dir / id_ / README.md`, so a malicious id like `../../etc` could escape. So feat is the most dangerous. For consistency and explicit safety (per the issue), add an id validation layer to all domains, not just feat.

**Decision 4: Exception handling / "gracefully handle all exceptions... pass them to the caller with meaningful error messages."**
Interpretation: the delete operation should catch low-level errors (OSError, FileNotFoundError, permission errors, parse errors) and re-raise/return with meaningful messages. But the domain not-found errors should propagate (same as set_status). I need to decide: raise a typed exception (e.g., the domain's `XNotFoundError`, or a new `DeleteError`), or return an error string. Given the MCP tool convention in this codebase (tools raise typed exceptions and the SDK surfaces them), and the "meaningful error messages" requirement, I propose: keep propagating the domain's `XNotFoundError` for not-found, and wrap unexpected I/O errors in a new, meaningful exception (or a clear `OSError`-with-message). This is a design detail that can be spelled out in the plan.

**Decision 5: What should `delete` return?**
Options: return `None` (void), return a confirmation string, or return the path that was deleted. The existing delete stubs are `NoReturn` (always raise). For the real tool, I'd propose returning a short confirmation (e.g., the resolved path as a string, or a small summary). This is a minor design point.

**Decision 6: Locking.**
Reuse each domain's existing `<d>_lock(id_)` (the same lock set_status uses). This satisfies "have a lock in place when finding and deleting the file." Good — no new lock needed.

Now, about the worktree: the user says "there is already a sibling directory for it." That is `/home/user/src/biz.dfch.SpecMgr.worktrees/`. Existing worktrees: feat-32-sysrs, feat-33-vcr. So I'll create `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` with branch `feat-36-delete` based on `dev` (the current branch and default).

Let me confirm the base branch. The current branch is `dev`. Recent features (feat-33-vcr) branched from dev. So feat-36-delete should also branch from `dev`.

Let me double-check: are there any uncommitted changes or considerations? The working tree is clean. Good.

Now, one more thing: the feature README needs frontmatter. Let me look at the template `.specmgr/_template/v1/README.md` to follow the exact format.

Let me read the template and also check the git log for the most recent commit to base the branch on.

Also, let me verify the exact count of delete stubs, and confirm there is no delete_adr. 11 stubs: delete_req, delete_uc, delete_tsk, delete_qa, delete_prb, delete_gol, delete_rsk, delete_dec, delete_sop, delete_feat, delete_vcr. Let me quickly confirm the list and that each has a test file.

Let me read the template, get the git log, and enumerate the delete stubs.

Let me review the feature template, the current branch state, and confirm the exact set of delete stubs.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/_template/v1/README.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/_template/v1/README.md</path>
<type>file</type>
<content>
1: ---
2: id: feat-NNN-slug
3: version: 1.0.0
4: status: planning
5: created: YYYY-MM-DD
6: updated: YYYY-MM-DD
7: ---
8: 
9: # Feature: [Feature Title]
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Brief description of what this feature does and why it matters.
16: 
17: ### Requirements
18: 
19: - REQ-001: [Functional requirement]
20: - REQ-002: [Non-functional requirement]
21: - REQ-003: [Constraint or dependency]
22: 
23: ### Acceptance Criteria
24: 
25: - [ ] ACC-001: Verifies REQ-001 — [testable condition]
26: - [ ] ACC-002: Verifies REQ-002 — [testable condition]
27: - [ ] ACC-003: Verifies REQ-003 — [testable condition]
28: 
29: ### Scope
30: 
31: What is included in this feature:
32: - Item 1
33: - Item 2
34: 
35: What is explicitly out of scope:
36: - Item A
37: - Item B
38: 
39: ### Dependencies
40: 
41: - Depends on: [other feat-NNN-slug, ADR id, or external]
42: - Blocks: [other feat-NNN-slug]
43: 
44: ### Design Notes
45: 
46: Any architectural decisions, patterns, or design rationale relevant to this feature.
47: 
48: ### Related ADRs
49: 
50: - [ADR id]: [Title]
51: - [ADR id]: [Title]
52: 
53: ### Task List
54: 
55: Single, canonical breakdown of work phases and tasks. Status lives on the
56: task itself — there is no separate "planned" vs. "executed" list to keep in
57: sync; a task's line *is* its current status. Update it in place as work
58: progresses (edit, don't duplicate).
59: 
60: #### Phase 1: [Phase name]
61: - [x] Task 1.1: [description] — depends on: none — status: done (2026-08-01)
62: - [ ] Task 1.2: [description] — depends on: Task 1.1 — status: in-progress, ETA 2026-08-10
63: - [ ] Task 1.3: [description] — depends on: Task 1.2 — status: blocked (see Blockers)
64: 
65: #### Phase 2: [Phase name]
66: - [ ] Task 2.1: [description] — depends on: Task 1.3 — status: not-started
67: - [ ] Task 2.2: [description] — depends on: Task 2.1 — status: not-started
68: 
69: **Note:** If a task's scope changes mid-flight, edit its description in place;
70: rely on git history (`git log -p` on this file) to recover what was
71: originally planned, rather than keeping a second copy of the task around.
72: 
73: ## Progress
74: 
75: ### Current Status
76: 
77: **As of [YYYY-MM-DD]**: [Brief status summary]
78: 
79: ### Blockers
80: 
81: - [ ] Blocker 1 — [description, impact, mitigation]
82: - [ ] Blocker 2 — [description, impact, mitigation]
83: 
84: (Remove this section if no blockers.)
85: 
86: ### Recent Updates
87: 
88: If this section grows too long, move older entries to `history.md` in this
89: same folder and leave a pointer here, e.g.:
90: `See history.md for updates before YYYY-MM-DD.`
91: 
92: #### Update [YYYY-MM-DDTHH:mm:ssz] (newest)
93: - Completed: [what was done]
94: - Next: [what comes next]
95: - Notes: [any relevant context]
96: 
97: #### Update [YYYY-MM-DDTHH:mm:ssz] (oldest)
98: - Completed: [what was done]
99: - Next: [what comes next]
100: - Notes: [any relevant context]
101: 
102: ### Decisions Made
103: 
104: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
105: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
106: 
107: ### Related PRs / Commits
108: 
109: - [PR #NNN](link): [description]
110: - [Commit hash](link): [description]

(End of file - total 110 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "git -C /home/user/src/biz.dfch.SpecMgr log --oneline -8 && echo \"---delete stub files---\" && ls /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/*/tools/delete_*.py && echo \"---confirm no delete_adr---\" && ls /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/ | grep -i delete || echo \"no delete in adr/tools\""
}
```

**Output:**

```
44d649c docs(feat-33-vcr): add session transcript "merge pr"
9ef52b9 feat(33): Add artifact type "Verification Case Record" (VCR) — complete (#35)
69b6c42 docs(feat-7): add session transcript for "release script"
bb2fd21 docs(sop): use headBranch-filtered gh run list in step 2 manual fallback
6e614d3 feat(release): add /release OpenCode command; document SOP-based flow in README/AGENTS.md
3c2b8e9 feat(release): add staged release automation script (SOP 98537416)
79b3951 docs(sop): add 'Perform a release of biz.dfch.SpecMgr' SOP (draft)
1a0daf3 chore(feat-7): extend Task 0.29 with issue #27 sibling trigger
---delete stub files---
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/dec/tools/delete_dec.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/delete_feat.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/delete_gol.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/delete_prb.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/delete_qa.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/delete_req.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/delete_rsk.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/tools/delete_sop.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/tools/delete_tsk.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/tools/delete_uc.py
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/vcr/tools/delete_vcr.py
---confirm no delete_adr---
option_delete.py

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 194.8s)

_Thinking:_

Confirmed:

- 11 delete stubs: dec, feat, gol, prb, qa, req, rsk, sop, tsk, uc, vcr.
- No delete_adr (only option_delete, which is for ADR options, not documents).
- Current HEAD is 44d649c on `dev`.
- The template is clear.

Now I have everything I need to build the plan. Let me think through the design decisions and surface the important ones to the user as clarifying questions. The plan mode instructions say to "ask the user clarifying questions when you're weighing trade-offs, or ask for their opinion."

Main open design questions:

1. **ADR inclusion**: Should the generic `delete` cover ADR (12 domains, matching `set_status`), or just the 11 whole-body domains (matching the existing stubs and `update`)? The issue says "except ADR?" with a question mark.
2. **Delete semantics**: Confirm hard delete (remove file from disk) vs. soft delete. The issue strongly implies hard delete. And for `feat` (folder per document), does deleting remove the entire folder (including history.md)?
3. **Return value**: What should `delete` return — None, a confirmation string, the deleted path?
4. **Path-safety approach**: I have a clear design (Literal type + strict id validation + containment check). Not really a question, more of a design choice I'll present. But I can confirm the level of strictness (UUID regex vs. just "no separators").

Actually, let me rethink the scope of what the user is asking for right now. What they're asking for is:

- "See what we want to do" ✓ (I've read the issue)
- "How it can be done, and make a plan" → create the feature plan/design
- "Put the feature on a separate git worktree branch. There's already a sibling directory for that. The branch and feature name is 'feat-36-delete'."

So the plan has two parts:
A. **Worktree/branch setup** (execution steps): Create branch `feat-36-delete` from `dev`, create worktree at `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete`.
B. **Feature design** (the actual content of the README to be created in the worktree): A comprehensive plan for the generic delete tool.

In plan mode I don't do the execution. I present the plan. But I should ask clarifying questions on the real trade-offs before finalizing the feature design. Let me ask the important ones.

Let me be efficient and only ask the most impactful questions. I'll ask:

1. ADR inclusion (11 vs. 12 domains).
2. Delete semantics (hard delete confirmed? and feat folder removal).
3. Return value shape.

Actually, the issue is pretty clear about hard delete. But the feat folder nuance and ADR question are real. Let me ask a focused set. I'll present my recommendations.

Also to reconsider: should the new generic `delete` be added to `general/tools/` (like update/set_status)? Yes, clearly — the issue says "a generic tool delete (like set_status)." So it goes in `general/tools/delete.py`.

One more thing: the issue says "remove all other existing delete\_<domain> tools." So the 11 stubs get removed (files + registrations + docstring mentions + tests). And their tests (test_delete\_<d>.py) get removed/replaced. This is a breaking change (the MCP tool surface changes). The 0.x precedent in ADR 36905d5b already accepts breaking changes to the tool surface. Good.

Also "update the relevant decisions and documents that require domains to provide the 'old' delete tools, and note that from now on all domains must implement adapters in the new generic delete tool." This means:

- Update AGENTS.md (each domain's bullet lists the delete stub; the "still missing" list; the general/ description).
- Update server.py's docstring (the authoritative tool list).
- Create a new ADR recording this decision (or update 36905d5b). Given ADR 898bfcd0 (ADRs only via MCP tools), the new ADR should be created via the `create_adr` tool. This is part of implementation, but I'll note it in the plan.

OK, let me think about whether to ask questions now or present a full plan. The plan mode reminder says to build a well-formed plan and to ask clarifying questions when weighing trade-offs. Since there are real trade-offs (ADR inclusion, return shape, feat folder), let me ask a concise set of questions first, then present the full plan. Actually — I could also present the plan with my recommendations embedded, flag the open decisions, and ask the user to confirm. But the guidance says to ask before making big assumptions. ADR inclusion is the biggest assumption. Let me ask a few targeted questions.

Use the question tool for the important design decisions. Keep it to the really impactful ones:

Q1: ADR inclusion — 11 vs. 12 domains.
Q2: Delete semantics for feat — remove the entire folder, or just README.md?
Q3: Return value shape.

Actually, let me rethink Q2. For feat, deleting just the README.md and leaving an empty folder would be weird; the natural hard delete is to remove the folder. But I should confirm, since the folder might contain history.md or session transcripts that the user may want to keep. That's a real trade-off. Let me ask.

Also reconsider: is the delete id parameter name `id` (matching set_status/update)? Yes, for consistency. The issue says "type + uuid," but the codebase uses `id`. I'll use `id`.

OK, let me ask the questions. I'll bundle the important ones.

Wait, let me rethink whether I should ask all of these or just present recommendations. The user is clearly a technical person running this repo (dfch). They wrote the issue. Let me ask the 3 most impactful questions with my recommended options at the top. That respects "ask the user for their opinion when weighing trade-offs."

Let me frame them:

1. **ADR scope**: Should the generic `delete` include ADR?

   - Recommended: No — cover only the 11 whole-body domains (matching the existing `delete_<d>` stubs and the `update` precedent; ADR has never had a delete stub, is treated specially, and its deletion would break "superseded by" cross-references).
   - Alternative: Yes — cover all 12 including ADR (full parity with `set_status`).

2. **feat folder deletion**: `feat` is folder per document (`<base>/<id>/README.md`, plus optional `history.md` and session transcripts). On `delete(type="feat", id=...)`, what to remove?

   - Recommended: The entire `<base>/<id>/` folder (rmtree) — full hard delete, folder becomes empty.
   - Alternative: Just the `README.md` file, leaving the folder and other files.

3. **Return value**: What should `delete` return on success?

   - Recommended: The deleted file's path as a string (useful confirmation, low cost).
   - Alternative: None / void.
   - Alternative: A small confirmation message.

Let me ask these three. Then I'll finalize the plan.

Actually, I realized I should double-check one more thing before asking: does the codebase have any existing "id validation" or UUID regex I can reference for the safety design? I saw that VCR has `_VERIFIES_PATTERN` with a UUID shape. Let me not over-engineer; I'll present the safety design in the plan.

OK, let me ask the questions now.

I now have a thorough understanding. Let me confirm a few genuine design trade-offs before finalizing the plan.

Here's what I've established from the issue and codebase:

- **Issue #36**: Add a generic `delete(type, id)` tool in `general/tools/` (like `set_status`), then remove the 11 existing `delete_<domain>` stubs (`req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr`), update the decisions/docs that require per-domain delete tools, and add path-injection safety + locking + graceful error handling.
- **Precedents**: `set_status.py`/`update.py` show the exact type-dispatch pattern (12/11-way `Literal` + per-domain private adapters + shared dispatch table). Each domain already has `<d>_lock(id)`, `<d>_base_dir()`, and `load_by_id()`. **No path-injection guard exists anywhere today** — that's net-new.
- **Worktree**: sibling dir `/home/user/src/biz.dfch.SpecMgr.worktrees/` exists (holds `feat-32-sysrs`, `feat-33-vcr`); current branch is `dev` at `44d649c`.

A few decisions have real trade-offs I want your call on:

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "header": "ADR scope",
      "question": "Should the new generic `delete` tool also cover ADR (making it 12 domains, like `set_status`), or only the 11 whole-body domains that currently have `delete_<d>` stubs (like `update`)? Note: ADR has never had a delete stub, is treated specially (render round-trip, lives in shared `models/adr/`), and deleting an ADR could break other ADRs' \"superseded by X\" cross-references.",
      "multiple": false,
      "options": [
        {
          "label": "11 whole-body domains only (Recommended)",
          "description": "Mirrors the existing delete_<d> stubs and the `update` precedent. ADR is deliberately excluded. Lower risk, matches the issue's 'except ADR?' framing."
        },
        {
          "label": "All 12 incl. ADR",
          "description": "Full parity with `set_status`. ADR deletion added via its own adapter (adr_lock + load_by_id + file unlink). Broader but riskier (cross-reference breakage)."
        }
      ]
    },
    {
      "header": "feat folder delete",
      "question": "`feat` is folder-per-document: `<base>/<id>/README.md` plus an optional `history.md` and session transcripts in the same folder. When `delete(type=\"feat\", id=...)` runs, what should be removed?",
      "multiple": false,
      "options": [
        {
          "label": "Entire <id>/ folder (rmtree) (Recommended)",
          "description": "True hard delete; the folder is removed completely (README.md, history.md, any session files). Cleanest, but destroys non-README content too."
        },
        {
          "label": "Only README.md",
          "description": "Unlink just the document file, leaving the folder and any history.md/session transcripts in place. More conservative."
        }
      ]
    },
    {
      "header": "delete return value",
      "question": "What should the generic `delete` tool return on success? (The old stubs were `NoReturn`/always-raised, so there's no existing shape to mirror.)",
      "multiple": false,
      "options": [
        {
          "label": "Deleted file path as str (Recommended)",
          "description": "Returns the absolute path of the removed file as a confirmation string. Useful and cheap."
        },
        {
          "label": "None (void)",
          "description": "Return nothing; success is implied by no exception. Simplest, matches a `NoReturn`-style mental model."
        },
        {
          "label": "Confirmation message",
          "description": "Return a human-readable sentence like \"Deleted <type> <id> at <path>\"."
        }
      ]
    }
  ]
}
```

**Output:**

```
User has answered your questions: "Should the new generic `delete` tool also cover ADR (making it 12 domains, like `set_status`), or only the 11 whole-body domains that currently have `delete_<d>` stubs (like `update`)? Note: ADR has never had a delete stub, is treated specially (render round-trip, lives in shared `models/adr/`), and deleting an ADR could break other ADRs' "superseded by X" cross-references."="11 whole-body domains only (Recommended)", "`feat` is folder-per-document: `<base>/<id>/README.md` plus an optional `history.md` and session transcripts in the same folder. When `delete(type="feat", id=...)` runs, what should be removed?"="Entire <id>/ folder (rmtree) (Recommended)", "What should the generic `delete` tool return on success? (The old stubs were `NoReturn`/always-raised, so there's no existing shape to mirror.)"="Deleted file path as str (Recommended)". You can now continue with the user's answers in mind.
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 53.0s)

_Thinking:_

The user has confirmed all three recommended options:

1. Only 11 whole-body domains (excluding ADR)
2. feat: delete the entire `<id>/` folder (rmtree)
3. Return the deleted file's path as a str

With this, I have everything I need to finalize the plan. To make sure the plan is accurate, let me also quickly verify a few implementation details:

1. How the dispatch table and adapters look in `update.py` (I've already seen the pattern from set_status).
2. What the per-domain `load_by_id` returns — a `(path, doc)` tuple. Good, this is what we need for deletion (the path).
3. For feat, `load_by_id`/`find_feat_path_by_id` resolves `<base>/<id>/README.md`. For rmtree, we need the parent folder `<base>/<id>/`. So the feat adapter will either call `find_feat_path_by_id` and then take `.parent`, or use `feat_base_dir() / id`.

Let me verify the exact function names for feat's `_io.py` and `_paths.py`, and also confirm that all domains have `load_by_id`. Also, let me look at the top of `update.py` to see how the dispatch table is defined, and how the `Literal` type is set up.

Actually, I've seen set_status.py in full, and update.py follows the same pattern. I have enough information. But since the feat adapter needs it, let me specifically check the function signatures of feat's `_io.py` and `_paths.py` to make sure the plan is accurate.

Also, to make the plan accurate, let me verify the exact list of the 11 domains that have both `_lock` and `load_by_id`:

- req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr

All of them have `_lock.py` and `_io.py` (load_by_id). Let me verify that feat's load_by_id exists and what it returns.

Let me quickly read feat's \_io.py, and also look at update.py's dispatch table to mirror it accurately.

All three recommendations confirmed. Let me verify the `feat` adapter specifics and the `update.py` dispatch pattern to make the plan precise.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/_io.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/tools/_io.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Thin file read helpers over ``parse_feat`` (Task 2.2).
19: 
20: Read-only, mirroring ``dec.tools._io``'s own shape and rationale: there is
21: no ``write_feat``/``render_feat`` counterpart here, since ``create_feat``
22: and the generic ``update`` tool in ``general.tools`` (``type="feat"``)
23: persist the caller's own already-validated body markdown byte-for-byte
24: rather than rendering it back out from a parsed model -- see
25: ``feat.tools._write.write_feat_file``.
26: 
27: No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
28: separate from any ``@mcp.tool()``-decorated function so they stay
29: independently testable.
30: """
31: 
32: from __future__ import annotations
33: 
34: from pathlib import Path
35: 
36: from ..models.v1 import FeatDocument, parse_feat
37: from ._paths import find_feat_path_by_id
38: 
39: __all__ = ["load_by_id", "read_feat"]
40: 
41: 
42: def read_feat(path: Path) -> FeatDocument:
43:     """Read and parse the feature document at ``path``.
44: 
45:     Parameters
46:     ----------
47:     path:
48:         The filesystem path to the feature's ``README.md`` file.
49: 
50:     Returns
51:     -------
52:     FeatDocument
53:         The parsed, validated document.
54:     """
55:     assert isinstance(path, Path), type(path)
56: 
57:     result = parse_feat(path.read_text(encoding="utf-8"))
58:     return result
59: 
60: 
61: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, FeatDocument]:
62:     """Resolve ``id_`` under ``base_dir`` and read the matching feature document.
63: 
64:     Parameters
65:     ----------
66:     base_dir:
67:         The feature base directory (typically :func:`._paths.feat_base_dir`'s
68:         return value).
69:     id_:
70:         The id to look up.
71: 
72:     Returns
73:     -------
74:     tuple[Path, FeatDocument]
75:         The resolved ``README.md`` path and the parsed document -- callers
76:         that mutate the document need the path to write it back afterward.
77: 
78:     Raises
79:     ------
80:     FeatNotFoundError
81:         If no folder matches (propagated from :func:`._paths.find_feat_path_by_id`).
82:     """
83:     assert isinstance(base_dir, Path), type(base_dir)
84:     assert isinstance(id_, str), type(id_)
85:     assert id_.strip()
86: 
87:     path = find_feat_path_by_id(base_dir, id_)
88:     result = (path, read_feat(path))
89:     return result

(End of file - total 89 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '480,540p' /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/update.py"
}
```

**Output:**

```
            fm_data["updated"] = now
            new_frontmatter = FeatFrontmatter(**fm_data)
            new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
            write_feat_file(path, new_frontmatter, spliced)
        return new_doc

    body = Feature.from_text(format_text(content))

    base_dir = feat_base_dir()
    with feat_lock(id_):
        path, existing = load_feat_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = FeatFrontmatter(**fm_data)
        new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
        write_feat_file(path, new_frontmatter, content)
    return new_doc


def _update_sop(id_: str, content: str, begin: int | None, end: int | None) -> SopDocument:
    """Replace the body of the SOP identified by ``id_`` (whole-body or line-range mode).

    Verbatim-shape port of :func:`_update_dec` (same ``sop_lock``,
    ``load_by_id``, frontmatter carry-over with only ``updated`` bumped,
    ``write_sop_file``, ``SopNotFoundError``; ``sop`` is the first domain
    built dispatch-only from day one per ADR 36905d5b, so there was never a
    per-domain ``update_sop`` tool to port -- this adapter was written
    directly in this shape), plus the REQ-002 range branch
    (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = sop_base_dir()
        with sop_lock(id_):
            path, existing = load_sop_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Sop.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = SopFrontmatter(**fm_data)
            new_doc = SopDocument(frontmatter=new_frontmatter, body=body)
            write_sop_file(path, new_frontmatter, spliced)
        return new_doc

    body = Sop.from_text(format_text(content))

    base_dir = sop_base_dir()
    with sop_lock(id_):
        path, existing = load_sop_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = SopFrontmatter(**fm_data)
        new_doc = SopDocument(frontmatter=new_frontmatter, body=body)
        write_sop_file(path, new_frontmatter, content)
    return new_doc



```

**Tool: bash**

**Input:**

```json
{
  "command": "for d in req uc tsk qa prb gol rsk dec sop feat vcr; do printf \"%s: \" \"$d\"; grep -h \"def load_by_id\" /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/$d/tools/_io.py | sed 's/^ *//'; done"
}
```

**Output:**

```
req: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, ReqDocument]:
uc: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, UcDocument]:
tsk: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, TskDocument]:
qa: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, QaDocument]:
prb: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, PrbDocument]:
gol: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, GolDocument]:
rsk: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, RskDocument]:
dec: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, DecDocument]:
sop: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, SopDocument]:
feat: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, FeatDocument]:
vcr: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, VcrDocument]:

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 302.8s)

_Thinking:_

Everything confirmed. All 11 domains have `load_by_id(base_dir, id_) -> tuple[Path, XDocument]` and a `<d>_lock(id_)` context manager. For feat, `load_by_id` returns the path to README.md. The parent folder is `path.parent`.

Now I have all the information I need. Let me finalize the plan.

Key design:

**New file: `general/tools/delete.py`**

- `@mcp.tool(name="delete", title=..., description=...)`
- Signature: `def delete(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk","dec","sop","feat","vcr"]) -> str`
- Returns the deleted file path as str.
- 11 private adapters `_delete_<d>(id_: str) -> str`.
- 11-way dispatch table `_ADAPTERS: dict[str, Callable[[str], str]]`.

**Per-domain adapter shape (flat-file domains: req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr):**

```python
def _delete_req(id_: str) -> str:
    _validate_id(id_)  # path-safety
    base_dir = req_base_dir()
    with req_lock(id_):
        path, _existing = load_req_by_id(base_dir, id_)
        _assert_within_base(base_dir, path)  # containment check
        path.unlink()
    return str(path)
```

Wait, there's a subtle point: `load_by_id` returns `(path, doc)`. For deletion we only need the path. But calling `load_by_id` also parses the document (a validation that the document is well-formed). That's fine — it guarantees we only delete a valid document of that type with that id. Actually, for deletion we might not want to require the document to parse (a corrupted file should also be deletable). Hmm. But the existing `find_*_path` functions skip files that fail to parse. So `load_by_id` on a corrupted document raises NotFoundError. That's acceptable and consistent with the rest of the codebase (the filesystem is the source of truth, but lookup requires parseability). Actually, thinking about it — if a file is corrupted, the user can't delete it via the tool. But that's an edge case. For consistency and simplicity, I'll go with using `load_by_id` (resolving the path via the domain's own finder, which gives us a not-found error). We could also use only `find_<d>_path` (path only, no parse). But even `find_feat_path_by_id` parses feat. In the flat domains, `find_<d>_path` doesn't parse — it scans and parses each file to compare ids. So the two are equivalent. Use `load_by_id` for consistency with set_status/update (since they use it), and note that the doc is discarded (we only need the path). Actually, we could call `find_<d>_path(base_dir, id_)` directly to avoid the full document parse — but `find_*_path` is a private function in each domain's `_paths.py` (it's in `__all__` though). Hmm, let me check: rsk's `_paths.__all__` includes `find_rsk_path`. So it's semi-public. But set_status/update use `load_by_id` from `_io`. For maximum consistency and to keep the plan simple, I'll go with `load_by_id` and discard the document. The cost of parsing is negligible.

Actually, there's a cleaner argument: `load_by_id` gives us both the path and a guarantee that the document is a valid domain document. For deletion, I think using `load_by_id` is fine and most consistent. Let me go with that and mention the alternative.

**feat adapter (folder per document):**

```python
def _delete_feat(id_: str) -> str:
    _validate_id(id_)  # feat-specific: must match feat-NNN-slug, no separators
    base_dir = feat_base_dir()
    with feat_lock(id_):
        path, _existing = load_feat_by_id(base_dir, id_)  # <base>/<id>/README.md
        folder = path.parent
        _assert_within_base(base_dir, folder)
        shutil.rmtree(folder)
    return str(folder)  # or str(path)?
```

The user said to return "the path of the deleted file as str." For feat, the deleted "file" is the folder. Return the folder path (the rmtree target) — or the README path? I'll go with returning the folder path since that's what was deleted. Actually, for consistency with "the path of the deleted file," in flat domains we return the file path, and for feat we return the folder path. That's the natural "thing that was deleted." Document it that way.

**Path-safety (the new primitive):**
The issue requires that neither type nor uuid can inject a relative path.

- `type`: `Literal[...]` → closed set → safe (no injection possible). This is a structural guarantee.
- `id`: needs validation. Add a small shared module, e.g. `general/tools/_id_safety.py` (or extend `_doc_paths.py`):
  - `_validate_id(id_: str, type: str)`:
    - assert isinstance str, non-empty.
    - reject if it contains a path separator (`/`, `\`) or `..`.
    - For the 10 UUID domains: require a match against a strict canonical UUID regex `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` (case-insensitive) — this alone blocks all traversal characters.
    - For feat: require a match against `^feat-\d+-[a-z0-9-]+$` (folder pattern) — blocks traversal.
  - Containment check (defense in depth): after path resolution, assert `resolved.resolve().is_relative_to(base_dir.resolve())`.
- Raise a clear `ValueError` (or a new `InvalidIdError`) with a meaningful message when the id fails validation. The issue says "make sure the input is str" and "no one can inject relative paths."

Actually, a subtle point: in the flat domains, even an invalid id won't cause traversal. Because `find_<d>_path` scans files and compares parsed ids — it never does `base_dir / id`. So the only place where a path is constructed from id is feat's shortcut (`base_dir / id_ / README.md`) and mdformat (but that takes a full path, not id). So the strict injection risk is feat. But the issue explicitly asks for a guarantee across the board, and defense in depth is good. So I'll add id validation for all 11 (UUID domains get UUID regex, feat gets folder pattern), plus a containment assertion. This directly and explicitly addresses the issue.

Let me think about where to put validation. Two options:

- (a) In each adapter (repetitive).
- (b) In a shared helper called from the public `delete()` before dispatch (single place, cleanest).

Since the public `delete()` has both `type` and `id`, we can validate there: `_validate_id_for_type(type, id)` — one call, then dispatch to the adapter. That's cleanest and centralizes the safety invariant. The adapter then does the containment assertion as defense in depth. Let me go with (b): public `delete()` validates id against type before dispatching.

But wait — should validation be inside the lock, or before it? Before the lock is fine (validation doesn't touch the filesystem). Validate before acquiring the lock.

**Error handling ("handle all exceptions gracefully... meaningful error messages"):**

- Not-found: propagate the domain's own `XNotFoundError` (consistent with set_status/update, already meaningful).
- Validation failure: raise `ValueError` with a clear message (invalid id / path injection attempt).
- I/O errors during unlink/rmtree (OSError, PermissionError, FileNotFoundError race): wrap in a meaningful error. The issue says "pass them to the caller with meaningful error messages." So catch `OSError` from the deletion operation and re-raise as a new exception with context (e.g. `DeleteError` / or a descriptive message). Let me introduce a small wrapper: try the deletion, on `OSError` raise a `RuntimeError`/custom `XDeleteError` with a message like `f"failed to delete {path}: {exc}"`. Actually, to keep it simple and meaningful, either re-raise `OSError` with a clearer message, or define a single `DeleteError(OSError)` in the shared module. Let me propose a `DeleteError` (subclass of `OSError` or `RuntimeError`) in the shared safety module, and have each adapter wrap unexpected I/O failures with it. Not-found keeps the domain-specific type.

Hmm, but the MCP tool's error contract: what does the SDK do with raised exceptions? In this codebase, tools raise typed exceptions (ValidationError, XNotFoundError, ValueError) and the MCP SDK converts them into error results. So raising a meaningful exception is the established "graceful" pattern. Let me follow that.

Let me not over-engineer the exception design in the plan. I'll specify:

- Invalid id / injection → `ValueError` (clear message), raised before any filesystem access.
- Not found → the domain's `XNotFoundError` (unchanged).
- I/O failure during deletion → catch and re-raise as a new `DeleteError` (defined in the shared module) with a message including the path and the underlying error. `DeleteError` subclasses `OSError` so callers can catch the I/O family.

**Locking:** Reuse each domain's existing `<d>_lock(id_)`. Wrap the entire find+delete sequence inside it. Satisfies the issue.

**Removal of the 11 stubs:**

- Delete the files: `src/.../<d>/tools/delete_<d>.py` (11 files).
- Remove from each `<d>/tools/__init__.py`: `from .delete_<d> import delete_<d>` and the `__all__` entry and the docstring mention.
- Delete the tests: `tests/<d>/tools/test_delete_<d>.py` (11 files).
- Update `server.py` docstring: remove the `delete_<d>` stub mentions, add the generic `delete` to the general-tools paragraph.
- Update `AGENTS.md`: each domain bullet (remove the delete\_<d> stub mention, note the generic delete), the "still missing" section (remove the bullet "delete\_\* are stubs"), the general/ bullet (add `delete` to the generic tools), the MCP-server import note.
- Update `docs/` via `specmgr docs` + `specmgr mcp-docs` regeneration (auto-generated, not by hand).
- ADR: create a new ADR via `create_adr` recording the decision. Note that from now on domains implement adapters in the generic `delete` (not per-domain delete tools). Possibly update ADR 36905d5b's "More Information" to reference it, or leave 36905d5b alone and have the new ADR be the decision record. The issue says "update the relevant decisions and documents" — the "decisions" = ADRs. Since this is a new cross-domain decision, the right move per convention is a new ADR. Write the new ADR, and if needed mark 36905d5b as partially superseded... actually 36905d5b is about update/set_status, not delete. So a new standalone ADR is cleaner. Let me specify: create a new ADR "Replace domain-specific delete with generic type-dispatched delete tool."

Wait — there's a subtlety about ADR creation. ADR 898bfcd0 says ADRs are authored/edited only via MCP tools (create_adr etc.). And ADRs live in `docs/adr/`. So during implementation, the new ADR should be created via the `specmgr_create_adr` MCP tool (which writes to the ADR base dir) and `specmgr adr-toc` to regenerate the TOC. Let me note that. But the ADR base dir — where does create_adr write? The tool says "write the new document to the ADR base directory," configurable via SPECMGR_ADR_DIR, defaulting to docs/adr. Good.

Actually, let me reconsider whether creating an ADR is in scope for this feature, or whether the feature README's "Decisions Made" is sufficient. AGENTS.md says: "If a decision is at the architecture/structure level, affects more than one feature or the whole repository, or reverses/supersedes a previous ADR, it belongs in a full ADR (docs/adr/). If it's scoped entirely to that feature's implementation details, it belongs in that feature's own 'Decisions Made' log. When in doubt, write the ADR."

This decision (generic delete tool, removing per-domain delete tools, the "from now on all domains implement adapters in the generic delete" convention) is at the architecture level, affects all domains and future domains, and establishes a new convention. So it deserves a full ADR. Let me include ADR creation in the plan.

**CHANGELOG.md:** Add an entry under [Unreleased] for the breaking change (removal of 11 tools, addition of 1 generic tool). Precedent from ADR 36905d5b ("record the breaking change in CHANGELOG.md").

**Tests (new):**

- `tests/general/tools/test_delete.py`:
  - Parameterized over all 11 types. Seed a real document per type (via the domain's `create_<d>` in a temporary SPECMGR_DOCS_DIR / SPECMGR_FEAT_DIR / SPECMGR_ADR_DIR), then:
    - delete succeeds, returns the path, file (or folder for feat) is gone, and subsequent `get_<d>`/`load_by_id` raises XNotFoundError.
    - Invalid id (path injection attempts: `../x`, `a/b`, `\`, `..`, a non-UUID string for a UUID domain, a non-feat-pattern for feat) → ValueError before any filesystem access, file unchanged.
    - Unknown id → the domain's XNotFoundError.
    - Containment check: simulate/mock that the resolved path is outside the base → DeleteError (or the ValueError from validation). Actually, since validation blocks it, containment is defense in depth. Test via a crafted scenario or a unit test of the containment helper.
    - I/O failure: mock `Path.unlink`/`shutil.rmtree` to raise OSError → DeleteError with a meaningful message, file unchanged (or partial).
    - Locking: verify the adapter acquires the domain lock (e.g. mock `<d>_lock` and assert it's called, or a concurrency test).
  - Unit tests for the shared id-safety helper (`tests/general/tools/test__id_safety.py` or similar): the UUID regex, the feat pattern, the separator/`..` rejection, the containment check.
- Remove the 11 `test_delete_<d>.py` stub tests.

**Worktree setup (execution steps for Phase 0 of the feature, or pre-implementation):**

- `git worktree add /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete -b feat-36-delete dev` (branch feat-36-delete from dev).
- Inside the worktree, `uv sync --all-extras --frozen` to set up the venv.
- Create `.specmgr/feat/feat-36-delete/README.md` (the plan itself) in the worktree.

Wait — the user said "I want to create and design a new feature, but not implement it yet" and "make a plan." So the immediate deliverable is: worktree + branch + feature README (design/plan). Implementation (delete.py, removing stubs, tests, ADR, docs) comes later (a separate phase, not now).

So the plan I present should have two layers:

- **Layer 1 (this task, now):** Set up the worktree/branch, author the feature plan README (`.specmgr/feat/feat-36-delete/README.md`) containing the full design. Do not write any implementation code.
- **Layer 2 (future, not now):** The actual implementation phases (as recorded in the README's task list).

Let me structure the final answer as the plan. Since we're in plan mode, I present the plan and don't execute. I'll give the user a comprehensive plan covering:

1. Worktree/branch setup.
2. Feature README content (design): overview, requirements, acceptance criteria, scope, dependencies, design notes (including the concrete adapter shape, the path-safety module, the locking, the error handling), the new ADR, task list (phases).

Let me also decide on the name of the new shared module. Options: `_id_safety.py`, `_path_safety.py`, extend `_doc_paths.py`. Since the safety concern is about resolving ids to safe paths, and `_doc_paths.py` is the existing "doc-type-agnostic path" module, I think a new small module `general/tools/_path_safety.py` is cleanest (keeps `_doc_paths.py` focused). But the id validation (UUID regex vs. feat pattern) is type-specific. Hmm. Let me think:

- Containment check (`is_relative_to`) → generic, belongs in a shared module.
- Id format validation → differs per type (UUID vs. feat slug).

I'll propose: a new `general/tools/_path_safety.py` with:

- `validate_id_for_type(type_: str, id_: str) -> None` — dispatches on type to a UUID regex (10 domains) or the feat folder pattern (feat); raises ValueError with a meaningful message on failure. (This encodes "make sure the input is str" + "no relative-path injection.")
- `assert_within(base_dir: Path, candidate: Path) -> None` — containment check (defense in depth); raises a `PathTraversalError`/ValueError.
- `class DeleteError(OSError)` — for wrapping I/O failures.

Actually, `validate_id_for_type` needs to know which types are UUID and which is feat. That's a small mapping. Fine.

But wait: is `validate_id_for_type` too opinionated / does it belong in `general`? The generic `delete` tool is in `general`, and the validation is part of its safety contract, so yes, `general/tools/_path_safety.py` is the right home.

Alternatively, simpler: do the validation inline in `delete.py` (since only `delete` uses it). But a separate module is more testable and matches the codebase's `_doc_paths.py`/`_splice.py`/`_paging.py` private-helper convention. Let me go with a separate `_path_safety.py`.

Hmm, but let me reconsider the UUID validation. Currently, are the ids for the 10 domains required to be UUIDs? Let me check — in create\_<d>, the id is `uuid.uuid4()`. And `find_<d>_path` compares against `frontmatter.id`. The id in frontmatter is a UUID string. So yes, for the 10 domains the id is a canonical UUID. For feat, it's `feat-NNN-slug`. So validation via regex is accurate and doesn't reject any legitimate id.

But one concern: does the codebase currently accept uppercase UUIDs or non-canonical forms? `uuid.uuid4().str` is lowercase. Frontmatter id — let me not overthink. I'll propose a case-insensitive canonical 8-4-4-4-12 hex UUID regex for the 10 domains, and `^feat-\d+-[a-z0-9]+(?:-[a-z0-9]+)*$` for feat. Actually, feat's folder pattern per `FEAT_FOLDER_PATTERN` is `^feat-(\d+)-`. Let me propose `^feat-\d+-.+$` plus an explicit no-separator/no-`..` check. To be safe and simple: for feat, require it matches `^feat-[0-9]+-[a-z0-9-]+$` (lowercase alphanumerics and hyphens). That blocks `/`, `\`, `..` (well, `..` is dots, not in `[a-z0-9-]`, so blocked). Good.

Actually, the cleanest universal guard that directly answers the issue's "no one can inject a relative path via either type or uuid":

1. `type` is a Literal (closed set) → no injection via type.
2. `id` must not contain `/`, `\`, or `..` (universal traversal guard), AND
3. `id` must match the domain's expected format (UUID regex for 10, feat pattern for feat), AND
4. Defense in depth: the resolved path must be `is_relative_to` the base dir.

Layers 2+3 are belt-and-suspenders. Let me specify all of them.

Now, let me write the plan. This is going to be a substantial plan document. Since we're in plan mode, I'll present it as my response (not write a file). But the user will probably want the README created in the worktree during implementation. Let me present the plan clearly, structured as:

A. What we're doing (recap of issue #36 + confirmed decisions).
B. Worktree/branch setup (the "put it on a separate worktree" part).
C. Feature design (the content of `.specmgr/feat/feat-36-delete/README.md`):

- Overview
- Requirements (REQ-xxx)
- Acceptance criteria (ACC-xxx)
- Scope (in / out)
- Dependencies
- Design notes (concrete: delete.py shape, adapters, \_path_safety.py, locking, error handling, return value)
- Related ADRs (new ADR to create)
- Task list (phases)
  D. What's explicitly not doing now (no implementation code).
  E. Next steps / what I'll execute on approval.

Let me keep it comprehensive but concise. I'll present the design at a level where the implementer (future me) can execute without re-deriving.

Let me draft the requirements:

- REQ-001: A new generic `delete(id, type)` MCP tool in `general/tools/delete.py`, dispatched over the 11 whole-body domains (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr). Excludes ADR (confirmed). On success, returns the deleted path as str.
- REQ-002: Removal of the 11 existing `delete_<d>` stub tools (files, `__init__` registrations, `__all__`, docstring mentions, stub tests).
- REQ-003: Path-safety — `type` is a closed Literal (no injection). `id` is validated (str, no `/`/`\`/`..`, domain-format regex: canonical UUID for the 10, `feat-NNN-slug` for feat). Containment assertion (resolved path `is_relative_to` base) as defense in depth. Violations raise ValueError before any filesystem access.
- REQ-004: Locking — each adapter wraps the find+delete in the domain's existing `<d>_lock(id)`.
- REQ-005: Graceful error handling — not-found → domain's `XNotFoundError`. Invalid id → ValueError (clear message). I/O failure during deletion → wrapped as `DeleteError` with a meaningful message (path + underlying error).
- REQ-006: feat deletes the entire `<base>/<id>/` folder (shutil.rmtree). The other 10 delete a single file (Path.unlink).
- REQ-007: Documentation/decision updates — a new ADR recording the generic-delete decision + the "from now on all domains implement adapters in the generic delete" convention. AGENTS.md updates (domain bullets, the "still missing" delete-stub list, the general/ bullet). server.py docstring (authoritative tool list). CHANGELOG [Unreleased] breaking-change entry. Regenerate docs/ (specmgr docs, mcp-docs, adr-toc).
- REQ-008: Tests — a new `tests/general/tools/test_delete.py` (parameterized over 11 types: success + return path + gone + subsequent not-found; injection attempts → ValueError before fs access; unknown id → XNotFoundError; I/O failure → DeleteError; lock acquisition) and unit tests for the `_path_safety` helpers. Remove the 11 stub tests.

Acceptance criteria map to these.

Design notes: the concrete shape. Let me write out the `delete.py` sketch and the `_path_safety.py` sketch.

Task list phases:

- Phase 0: Worktree/branch setup + authoring the feature README (this is partly what we're doing now, but the README authoring is a task). Actually, since the user asked to "create and design but not implement," Phase 0 = set up worktree + write the README. Then stop.
- Phase 1: `_path_safety.py` (validation + containment + DeleteError) + unit tests.
- Phase 2: `delete.py` (the 11 adapters + dispatch + tool) + `tests/general/tools/test_delete.py`.
- Phase 3: Removal of the 11 stubs (files + `__init__` + docstrings + stub tests).
- Phase 4: Docs/decisions (new ADR via create_adr, AGENTS.md, server.py docstring, CHANGELOG, doc regeneration: specmgr docs / mcp-docs / adr-toc).
- Phase 5: Quality gate (ruff format/check, vulture, full unittest, pylint advisory) + ACC sign-off + README progress updates.

That's a clean breakdown.

Now, one more consideration: since we're in plan mode and the user wants a worktree, I need to clearly indicate that the worktree creation is an action to be performed on approval (it's a system change, not allowed right now).

Let me also double-check: the feature README should go inside the worktree (on the new branch), not the main checkout. Yes — `.specmgr/feat/feat-36-delete/README.md` inside the worktree's checkout. That's the convention (each feature has its own branch/worktree).

Let me verify the worktree directory path convention: existing are `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-32-sysrs` and `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr`. So the new one is `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete`.

Now let me write the final plan. Make it well-structured and executable. Keep in mind the 4-line guideline is for normal responses, but this is an explicit request for a plan, and the plan mode system reminder asks for a comprehensive plan. So a longer, structured response is appropriate here. Still, keep it tight and avoid verbosity.

Let me present it.

I have everything I need. Here is the plan.

______________________________________________________________________

# Plan — feat-36-delete: generic `delete` tool (issue #36)

## Confirmed decisions (your answers)

- **Scope:** 11 whole-body domains only — `req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr`. **ADR excluded** (matches `update` precedent; no `delete_adr` stub exists; avoids breaking "superseded by X" cross-refs).
- **feat:** hard-delete the **entire `<base>/<id>/` folder** (`shutil.rmtree`), not just `README.md`.
- **Return:** the **deleted path as `str`** (file for the 10 flat domains, folder for feat).

## Part A — Worktree / branch setup (executed on approval)

Sibling dir already exists: `/home/user/src/biz.dfch.SpecMgr.worktrees/` (holds `feat-32-sysrs`, `feat-33-vcr`).

```
git -C /home/user/src/biz.dfch.SpecMgr worktree add \
    /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete \
    -b feat-36-delete dev
cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete
uv sync --all-extras --frozen
```

Base is `dev` (current, clean, at `44d649c`). The feature README lives **inside this worktree** at `.specmgr/feat/feat-36-delete/README.md`.

## Part B — The feature (design only now; no implementation code)

Author `.specmgr/feat/feat-36-delete/README.md` from the repo's `_template/v1/README.md`, with the following design. This is the deliverable of *this* task.

### Overview

Add one generic, type-dispatched `delete(id, type)` MCP tool in `general/tools/delete.py` (exact analog of `set_status.py`/`update.py`), retire the 11 unimplemented `delete_<domain>` stubs, and record the new convention (every future domain implements a `delete` **adapter**, never a per-domain delete tool) in a new ADR + AGENTS.md/server.py/CHANGELOG. Net-new safety: id validation + path-containment guard + per-domain lock + graceful error wrapping.

### Requirements

- **REQ-001** — New `@mcp.tool(name="delete")` in `general/tools/delete.py`: signature `def delete(id: str, type: Literal[11 domains]) -> str`; 11 private adapters `_delete_<d>(id_) -> str`; shared `_ADAPTERS` dispatch table (mirrors `set_status._ADAPTERS`). Returns the deleted path as `str`.
- **REQ-002** — Remove all 11 `delete_<d>` stubs: the 11 files, their `from .delete_<d> import …` + `__all__` entries + docstring mentions in each `<d>/tools/__init__.py`, and the 11 `tests/<d>/tools/test_delete_<d>.py` stub tests.
- **REQ-003** — **Path-injection safety** (issue's explicit requirement; no such guard exists today):
  - `type` is a closed `Literal` → structurally safe.
  - New `general/tools/_path_safety.py`: `validate_id_for_type(type_, id_)` → `id` must be a non-empty `str`, must contain **no** `/`, `\`, or `..`, and must match the domain format (canonical 8‑4‑4‑4‑12 hex UUID for the 10 UUID domains; `^feat-[0-9]+-[a-z0-9-]+$` for feat). Violation → `ValueError` with a clear message, raised **before any filesystem access**.
  - Defense-in-depth `assert_within(base_dir, candidate)`: resolved path must be `is_relative_to(base_dir)`.
- **REQ-004** — **Locking:** each adapter wraps find+delete in the domain's existing `<d>_lock(id_)` (same lock `set_status`/`update` use).
- **REQ-005** — **Graceful errors:** not-found → the domain's own `XNotFoundError` (unchanged); invalid id → `ValueError`; I/O failure during `unlink`/`rmtree` (`OSError`/`PermissionError`) → caught and re-raised as new `DeleteError(OSError)` carrying the path + underlying message.
- **REQ-006** — Delete mechanics: 10 flat domains `Path.unlink()` the file; feat `shutil.rmtree(path.parent)` the folder.
- **REQ-007** — Docs/decisions: new ADR (via `specmgr_create_adr` + `specmgr adr-toc`); update `AGENTS.md` (per-domain bullets, the "still missing" `delete_*` stubs bullet, the `general/` bullet gains `delete`); update `server.py` docstring (authoritative tool list); `CHANGELOG.md` `[Unreleased]` breaking-change entry; regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`).
- **REQ-008** — Tests: new `tests/general/tools/test_delete.py` (parameterized over 11 types) + unit tests for `_path_safety` helpers.

### Design sketch (persisted in README Design Notes)

```python
# general/tools/delete.py (shape; per-domain adapters are 1:1 like set_status)
def _delete_req(id_: str) -> str:
    base_dir = req_base_dir()
    with req_lock(id_):
        path, _doc = load_req_by_id(base_dir, id_)   # resolves + domain-not-found
        assert_within(base_dir, path)                 # defense-in-depth
        try:
            path.unlink()
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex
    return str(path)

@ mcp.tool(name="delete", title="Delete document", description=…)
def delete(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk","dec","sop","feat","vcr"]) -> str:
    validate_id_for_type(type, id)        # REQ-003, before any fs access
    return _ADAPTERS[type](id)
```

feat adapter is identical but `shutil.rmtree(path.parent)` and returns `str(path.parent)`.

### Task list (phases; only Phase 0 runs now)

- **Phase 0 (this task):** create worktree/branch; author the feature README (plan + design, status `planning`). **Stop — no source code.**
- Phase 1: `_path_safety.py` + its unit tests.
- Phase 2: `delete.py` (adapters + dispatch + tool) + `tests/general/tools/test_delete.py`.
- Phase 3: retire the 11 stubs (files, `__init__`, docstrings, stub tests).
- Phase 4: ADR + AGENTS.md + server.py docstring + CHANGELOG + `docs/` regeneration.
- Phase 5: quality gate (ruff format/check, vulture, full unittest, advisory pylint), ACC sign-off, README progress update.

### Out of scope

- Any change to ADR deletion (ADR has no delete and stays that way).
- Soft-delete/archival semantics (issue specifies hard delete).
- Re-introducing `specmgr://<d>/{id}` resources or per-domain delete tools.

______________________________________________________________________

**Two things to confirm before I execute:**

1. This task = **Part A + Part B Phase 0 only** (worktree/branch + the README). Implementation (Phases 1–5) happens later on your go-ahead. Correct?
2. New ADR title: **"Replace domain-specific delete tools with a generic type-dispatched delete tool"** — OK, or do you want it phrased differently?

On your confirmation I'll create the worktree/branch and write `.specmgr/feat/feat-36-delete/README.md`.

______________________________________________________________________

## User

make sure that the path and file validation logic that shall prevent injections is reusable and can later be used by the get and update tolls as well (f we decide to do so)

Do not commit anything in "dev". As soon as you are in build mode you create the git worktree branch and write the plan

answers to your questions:

-- 1: implementation will require a different agent (Phase-Orchestrator). You are the designer. So you do not implement.
-- 2: ok

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-2 · 210.4s)

_Thinking:_

The user provided important refinements:

1. **The path and file validation logic must be reusable** — it should be designed so that, if we decide to do so later, the `get` and `update` tools can use it too. So it shouldn't be a `delete`-specific module like `_path_safety.py`, but a reusable, generic safety module. Let me rethink the naming and design. It should be a general-purpose "ID → safe path resolution" helper that takes `type` + `id` and returns a validated, contained path (or raises). That way `get_<d>`/`update`/`set_status`/`delete` can all call it later.

2. **Don't commit anything to "dev".** All work goes into a worktree branch `feat-36-delete`. I'm still in plan mode now (read-only), so I won't actually create the worktree yet — the user said "as soon as you enter build mode, create the git worktree branch and write the plan." So the plan should include, as the first build-mode step, worktree creation. I should not commit to dev. Good — I was already planning to branch from dev without touching dev's working tree. `git worktree add -b feat-36-delete dev` creates a new branch and doesn't modify dev. Good.

3. **I am the designer, not the implementer.** Implementation will be done by a separate agent (phase-orchestrator). So my job right now (in plan mode) is to produce a well-formed design/plan. The README I write in build mode should be a *design document* that the phase-orchestrator/phase-implementer can execute from. I should write the feature README (that's the "write the plan" part), but I should not implement the source code.

Wait — let me re-read: "as soon as you enter build mode, create the git worktree branch and write the plan." So in build mode I: (a) create the worktree branch, (b) write the plan (the feature README). I do not implement. This is consistent with "you are the designer. So you do not implement."

So the deliverable in build mode is: worktree + `.specmgr/feat/feat-36-delete/README.md` (comprehensive design). And that README must be executable by the phase-orchestrator.

Now, let me refine the design based on the reusability requirement. This is an important change. Let me rethink.

**Reusable validation design:**

Currently, each domain resolves id → path via `find_<d>_path(base_dir, id_)` (flat domains scan and parse; feat is a shortcut). The `set_status`/`update` adapters call `load_by_id`, which calls `find_<d>_path`. None of them validate the id for injection — they rely on the scan (flat) being safe, or the feat shortcut (which is the risky one).

For reusability, I want a single module, e.g. `general/tools/_path_safety.py` (or better, `general/tools/_safe_paths.py`), that provides:

1. **ID format validation** — but this is type-dependent (UUID vs feat slug). To make it reusable across get/update/delete, the function should take `type` and `id` and validate. But `get_<d>` tools are per-domain and don't take a `type` parameter. Hmm. So a reusable function should be composable at two levels:

   - A generic, type-agnostic level: `reject_path_separators(id_)` / `assert_no_traversal(id_)` — works for any domain, checks no `/`, `\`, `..`. This is the universal guard.
   - A type-specific format level: `assert_uuid(id_)` (for the 10 UUID domains), `assert_feat_id(id_)` (for feat).

   Then a convenience function `validate_id(type_, id_)` that combines the universal guard + the type-specific format. The generic `delete` tool calls `validate_id(type, id)`. Later, if we want, `get_<d>` can call `assert_no_traversal(id_)` + `assert_uuid(id_)`, and `update`/`set_status` can call `validate_id(type, id)`.

2. **Containment check** — `assert_within(base_dir, candidate)` — type-agnostic, reusable anywhere we resolve a path.

3. **`DeleteError`** — wait, if it's reusable, the error should probably be generic too. But `DeleteError` is specific to delete. Let me separate: the safety module provides validation + containment (reusable) and raises generic errors (e.g. `ValueError` for bad ids, or a dedicated `PathTraversalError`). The `DeleteError` (I/O wrap) is delete-specific and can live in `delete.py` or the safety module. Actually, to keep the safety module focused and reusable, I'll put:

   - `assert_no_traversal(id_) -> None` (raises `ValueError`)
   - `assert_uuid(id_) -> None` (raises `ValueError`)
   - `assert_feat_id(id_) -> None` (raises `ValueError`)
   - `validate_id(type_, id_) -> None` (dispatches to the above; raises `ValueError`)
   - `assert_within(base_dir, candidate) -> None` (raises a new `PathOutsideBaseError` or `ValueError`)

   And keep `DeleteError` in `delete.py` (delete-specific I/O wrap), or in the safety module as a generic `DeleteError`. Actually, the I/O wrap is only needed for delete (get/update read, they don't delete; though update writes and could also hit I/O errors). Hmm. To keep scope tight, I'll put the id validation + containment (the injection-prevention part, which is what the user explicitly wants reusable) in the shared module, and keep delete's I/O error wrap in `delete.py`. That matches the user's ask: "the path and file validation logic that should prevent injection is reusable."

   So the reusable part = **id validation + path containment**. That's exactly the injection prevention.

Let me rethink the module name and location. `general/tools/` is where cross-domain tool helpers live (`_doc_paths.py`, `_splice.py`, `_paging.py`, `_packaged_data.py`). A new `general/tools/_path_safety.py` fits perfectly and is importable from any domain or tool.

Actually, let me reconsider whether it belongs in `_doc_paths.py` (the existing "path" module). The user wants it reusable for get/update/delete. `_doc_paths.py` is already the shared path module. But adding injection validation there might bloat it. A dedicated `_path_safety.py` is cleaner and has a single responsibility (safety/injection prevention). I'll propose a new `general/tools/_path_safety.py`. I'll note that it's deliberately separated from `_doc_paths.py` (which is about base-dir resolution and id→path lookup) — `_path_safety.py` is about *validating* inputs and *confining* resolved paths.

Let me refine REQ-003 to reflect reusability, and update the design sketch and task list. Also, I'll make it explicit in the README that `get_<d>` and `update`/`set_status` are *not* changed in this feature (only `delete` uses the new safety module), but the module is designed so they can adopt it later without rework. That's the "if we decide to do so later" part.

Let me also reconsider: should `validate_id` be called in the public `delete()` before dispatch (as I had), or in each adapter? For reusability and a single enforcement point, the public `delete()` should call `validate_id(type, id)` once, before dispatch. That's clean. And the adapters do the containment check after path resolution (defense in depth). Both are in the shared module. Good.

Now, one more reconsideration: the user says "the path and file validation logic." "File validation" — does this mean validating the file that exists (e.g. it parses as the right type)? Or validating the file path? I think "path and file validation logic that should prevent injection" = logic that validates the id (input) and the resolved file path (output) to prevent path injection/traversal. So:

- ID validation (input) → `validate_id` / `assert_no_traversal` / format check.
- File/path validation (resolved) → `assert_within` (containment), and possibly also verifying that the resolved path is a file (not a directory) for the 10 flat domains, or that the parent is a folder for feat. I'll add a small `assert_regular_file(path)` for the 10 flat domains, and let feat assert that `path.parent` is a directory. This makes "file validation" concrete and reusable (get/update can also assert the resolved path is a regular file before reading).

Good, that's a nice refinement. Let me add:

- `assert_regular_file(path) -> None` (raises if it doesn't exist or is not a file) — reusable for get/update reads and delete unlinks.
- For feat, the folder check is domain-specific, so I'll keep it in the feat adapter (or add `assert_within` for the folder).

Let me finalize the `_path_safety.py` API:

```
assert_no_traversal(id_: str) -> None          # universal: no '/', '\', '..', non-empty str
assert_uuid(id_: str) -> None                   # canonical UUID shape (10 domains)
assert_feat_id(id_: str) -> None                # feat-NNN-slug shape
validate_id(type_: str, id_: str) -> None       # dispatch: assert_no_traversal + type format
assert_within(base_dir: Path, candidate: Path) -> None   # containment (defense in depth)
assert_regular_file(path: Path) -> None         # exists + is a file
```

All raise `ValueError` with meaningful messages (or a dedicated exception). I'll use `ValueError` for id/format issues (input validation, consistent with the codebase using `assert` + `ValueError`), and maybe a small `PathSafetyError(ValueError)` for the containment/file checks. Actually, to keep it simple and consistent with the codebase (which raises `ValueError` and domain `LookupError`s), I'll do:

- id/format problems → `ValueError`
- containment problem → `ValueError` (shouldn't happen if id validation works, but defense in depth)
- file check problem → the delete adapter treats a missing file as the domain's not-found (via `load_by_id`), so `assert_regular_file` is mostly redundant with `load_by_id`. I'll keep `assert_regular_file` as an optional extra guard.

Hmm, I'm overcomplicating. Let me keep the reusable module focused on **injection prevention**, which is the user's explicit ask:

- `assert_no_traversal(id_)`
- `assert_uuid(id_)` / `assert_feat_id(id_)`
- `validate_id(type_, id_)` (convenience dispatcher)
- `assert_within(base_dir, candidate)` (containment)

And I'll mention `assert_regular_file` as an optional addition. The delete-specific I/O wrap (`DeleteError`) stays in `delete.py`.

Let me update the plan accordingly. I'll present the refined design. Since the user has answered my questions and given refinements, I think I should present the updated plan (focusing on the reusability change) and confirm, or since they said "as soon as you enter build mode... write the plan" — they want me to proceed to write the plan in build mode. But I'm still in plan mode now. The user's message is a refinement of the plan, plus instructions for build mode.

Re-reading the flow: the user is still giving me plan-mode input (refinements). The system reminder confirms plan mode is active and read-only. So I should incorporate the refinements and present the updated plan. The user said "as soon as you enter build mode, create the git worktree branch and write the plan" — that's an instruction for when I'm no longer in plan mode. Right now I should finalize the plan (incorporating the reusability requirement) and confirm it's ready.

I don't think I need to ask more questions — the user has been clear. I'll present the updated design (especially the reusable `_path_safety.py`), confirm the build-mode steps, and indicate readiness. I'll keep it concise since it's a delta from the previous plan.

Let me write out the refined plan section. I'll present the full updated design (not just the diff) so it's a complete, self-contained plan, but I'll keep it tight.

Actually, the user asked me to make sure the validation logic is reusable. That's the main change. Let me present the updated plan clearly, with emphasis on the reusable safety module, and confirm the build-mode actions. I'll restate the key points concisely rather than repeating the entire previous plan verbatim, but I'll make the safety module design concrete and complete.

Let me draft the response.

Key updates:

1. Rename/reframe REQ-003: the injection-prevention logic lives in a **reusable** module `general/tools/_path_safety.py`, designed so `get_<d>`/`update`/`set_status` can adopt it later without rework. This feature wires it only into `delete`.
2. Concrete API of `_path_safety.py`.
3. Make explicit that `get`/`update`/`set_status` are **not** modified in this feature (only `delete` uses it), but the module is built to be reusable.
4. Build-mode actions: create worktree (branch from dev, don't touch dev), write README. Don't commit to dev. Don't implement.
5. I'm the designer; the phase-orchestrator implements from the README.

Let me also reconsider the module name. `_path_safety.py` is good. Or `_safe_id.py`. Since it covers both id validation and path containment, I'll go with `_path_safety.py`. Actually, "path and file validation" — maybe `_path_validation.py`. I'll use `_path_safety.py` and note it's about injection/safety. Either is fine; I'll go with `_path_safety.py`.

Let me write the response. Keep it well-structured and reasonably concise.

One more thing: the user emphasized "don't commit anything to 'dev'." `git worktree add -b feat-36-delete dev` — the `-b` creates a new branch starting from dev's commit, but doesn't modify dev. All subsequent commits go to feat-36-delete in the worktree. So dev is untouched. Good. I'll state this explicitly.

Also, in build mode I write the README. Writing the README is a file creation in the worktree (not dev). That's allowed in build mode. And it's not an "implementation" of the feature code — it's the design document. Good. The user explicitly asked me to "write the plan" in build mode. So writing the README is expected.

Let me finalize.

Understood. Two refinements incorporated: (1) the injection-prevention logic becomes a **reusable** module, not delete-specific, so `get`/`update` can adopt it later without rework; (2) I'm the designer — I only set up the worktree and author the plan, the Phase-Orchestrator implements, and nothing is ever committed to `dev`.

Here is the updated, final plan.

______________________________________________________________________

# feat-36-delete — design (revised)

## Build-mode actions (when I exit plan mode)

```
git -C /home/user/src/biz.dfch.SpecMgr worktree add \
    /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete \
    -b feat-36-delete dev        # new branch from dev's HEAD; dev itself untouched
uv sync --all-extras --frozen    # inside the new worktree
```

Then author **only** `.specmgr/feat/feat-36-delete/README.md` (this design). No `src/` code, no commits to `dev`. All later work commits to `feat-36-delete` in the worktree. The README is written to be **executable by the Phase-Orchestrator / phase-implementer** (concrete shapes, file lists, task phases).

## The reusable safety module (the key change)

New file **`general/tools/_path_safety.py`** — cross-domain, single-responsibility "injection prevention" helper, sibling to the existing `_doc_paths.py`/`_splice.py`/`_paging.py`. Deliberately **separate** from `_doc_paths.py` (which resolves base-dirs and does id→path lookup); `_path_safety.py` only *validates inputs* and *confines resolved paths*.

Proposed API (all raise `ValueError` with a meaningful message):

```
assert_no_traversal(id_: str) -> None          # universal: non-empty str, no '/', '\', or '..'
assert_uuid(id_: str) -> None                   # canonical 8-4-4-4-12 hex (the 10 UUID domains)
assert_feat_id(id_: str) -> None                # ^feat-[0-9]+-[a-z0-9-]+$  (feat)
validate_id(type_: str, id_: str) -> None       # convenience: assert_no_traversal + type format
assert_within(base_dir: Path, candidate: Path) -> None   # containment: candidate is_relative_to base_dir
```

- **Reusability contract:** `delete` calls `validate_id(type, id)` once (before any fs access) + `assert_within` (after resolution). The same five functions are directly callable later by `get_<d>` (`assert_no_traversal` + `assert_uuid`/`assert_feat_id` + `assert_within`) and by `update`/`set_status` (`validate_id` + `assert_within`) **with zero rework** — but this feature does **not** modify `get`/`update`/`set_status`; it only builds and wires the module into `delete`.
- The delete-specific I/O wrapper (`DeleteError`) stays in `delete.py`, not in the reusable module.

## Requirements (final)

- **REQ-001** — `general/tools/delete.py`: `@mcp.tool(name="delete")`, `def delete(id: str, type: Literal[11]) -> str`; 11 private adapters `_delete_<d>`; `_ADAPTERS` dispatch table (mirrors `set_status`). Returns deleted path as `str`.
- **REQ-002** — Retire the 11 `delete_<d>` stubs (files + `__init__` imports/`__all__`/docstrings + 11 stub test files).
- **REQ-003** — Reusable `general/tools/_path_safety.py` (API above) + unit tests. Wired into `delete` only; designed for later `get`/`update` adoption.
- **REQ-004** — Locking: each adapter wraps find+delete in the domain's existing `<d>_lock(id_)`.
- **REQ-005** — Errors: not-found → domain `XNotFoundError`; invalid id / containment breach → `ValueError`; I/O failure during `unlink`/`rmtree` → `DeleteError` (path + cause).
- **REQ-006** — Mechanics: 10 flat domains `Path.unlink()`; feat `shutil.rmtree(path.parent)`.
- **REQ-007** — ADR (**"Replace domain-specific delete tools with a generic type-dispatched delete tool"**, via `create_adr` + `adr-toc`); `AGENTS.md` (per-domain bullets, the "still missing" `delete_*` bullet, `general/` bullet gains `delete`); `server.py` docstring; `CHANGELOG.md [Unreleased]` (breaking); regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`).
- **REQ-008** — Tests: `tests/general/tools/test_delete.py` (11 types: success+return+gone+subsequent-not-found; injection attempts → `ValueError` pre-fs; unknown id → `XNotFoundError`; I/O failure → `DeleteError`; lock taken) + `tests/general/tools/test__path_safety.py`.

## Design sketch (persisted in README)

```python
# general/tools/delete.py
def _delete_req(id_: str) -> str:
    base_dir = req_base_dir()
    with req_lock(id_):
        path, _doc = load_req_by_id(base_dir, id_)   # resolves + domain not-found
        assert_within(base_dir, path)                # defense-in-depth (REQ-003)
        try:
            path.unlink()
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex
    return str(path)

@mcp.tool(name="delete", title="Delete document", description=…)
def delete(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk","dec","sop","feat","vcr"]) -> str:
    validate_id(type, id)          # REQ-003, before any filesystem access
    return _ADAPTERS[type](id)
```

feat adapter: identical, but `shutil.rmtree(path.parent)` and `return str(path.parent)`.

## Task phases (for the Phase-Orchestrator; none executed by me)

- **Phase 0 (me, build mode):** worktree/branch + author README. Stop.
- **Phase 1:** `_path_safety.py` + `test__path_safety.py`.
- **Phase 2:** `delete.py` + `test_delete.py`.
- **Phase 3:** retire the 11 stubs.
- **Phase 4:** ADR + AGENTS.md + server.py docstring + CHANGELOG + `docs/` regen.
- **Phase 5:** quality gate (ruff format/check, vulture, full unittest, advisory pylint), ACC sign-off, README progress update.

## Out of scope

ADR deletion; soft-delete/archival; modifying `get`/`update`/`set_status` (module is ready for them, but they're untouched); re-adding per-domain delete tools or `specmgr://<d>/{id}` resources.

______________________________________________________________________

Ready to execute on your go: I'll create the `feat-36-delete` worktree (branch from `dev`, `dev` untouched) and write `.specmgr/feat/feat-36-delete/README.md` with this design. Confirm and I'll proceed.

______________________________________________________________________

## User

go

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 45.4s)

_Thinking:_

The user has said "go". I'm now in build mode. What I need to do is:

1. Create a git worktree branch `feat-36-delete` from `dev` at `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete`.
2. Write the plan to `.specmgr/feat/feat-36-delete/README.md` inside that worktree.
3. Don't commit anything to dev. Don't implement the feature code.

First I'll set up the todo list, then create the worktree.

Let's start by creating the worktree.

First, check the current state and create the worktree. The command is as follows:

```
git -C /home/user/src/biz.dfch.SpecMgr worktree add /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete -b feat-36-delete dev
```

This creates a new branch `feat-36-delete` from `dev` and checks it out into the worktree. It doesn't touch `dev` itself.

After that, I'll write the README inside the worktree.

Alright, let's proceed. First I'll create the todo list.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Create git worktree + branch feat-36-delete from dev (dev untouched)",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Author .specmgr/feat/feat-36-delete/README.md design plan in the worktree",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Verify worktree/branch state and that dev is untouched",
      "status": "pending",
      "priority": "medium"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Create git worktree + branch feat-36-delete from dev (dev untouched)",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Author .specmgr/feat/feat-36-delete/README.md design plan in the worktree",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Verify worktree/branch state and that dev is untouched",
    "status": "pending",
    "priority": "medium"
  }
]
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 38.5s)

_Thinking:_

Let's create the worktree. First, I'll check the existing worktree directory structure.

Creating the worktree and branch from `dev` (this does not modify `dev`).

**Tool: bash**

**Input:**

```json
{
  "command": "git -C /home/user/src/biz.dfch.SpecMgr worktree add /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete -b feat-36-delete dev 2>&1"
}
```

**Output:**

```
Preparing worktree (new branch 'feat-36-delete')
HEAD is now at 6d6bf2f chore(release): bump version to v0.15.0

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 46.7s)

_Thinking:_

Interesting — HEAD is now at 6d6bf2f "chore(release): bump version to v0.15.0". This is different from the 44d649c I saw earlier. Wait, did the dev branch move forward? Let me check. Earlier `git log --oneline -8` showed `44d649c` at the top. Now it's showing `6d6bf2f`. Let me verify the current state of dev and the worktree.

Actually, wait — the worktree was created from `dev`, and HEAD is now at 6d6bf2f. But earlier, the main checkout was on dev at 44d649c. Did dev get updated? Let me check. It's possible dev was fast-forwarded, or a commit was made. Let me look at the current git state.

Actually, this is important. Let me verify.

**Tool: bash**

**Input:**

```json
{
  "command": "echo \"=== worktree state ===\" && git -C /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete status -sb && echo \"=== worktree HEAD ===\" && git -C /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete log --oneline -3 && echo \"=== dev branch (main checkout) ===\" && git -C /home/user/src/biz.dfch.SpecMgr log --oneline -3 dev && echo \"=== worktree list ===\" && git -C /home/user/src/biz.dfch.SpecMgr worktree list"
}
```

**Output:**

```
=== worktree state ===
## feat-36-delete
=== worktree HEAD ===
6d6bf2f chore(release): bump version to v0.15.0
44d649c docs(feat-33-vcr): add session transcript "merge pr"
9ef52b9 feat(33): Add artifact type "Verification Case Record" (VCR) — complete (#35)
=== dev branch (main checkout) ===
6d6bf2f chore(release): bump version to v0.15.0
44d649c docs(feat-33-vcr): add session transcript "merge pr"
9ef52b9 feat(33): Add artifact type "Verification Case Record" (VCR) — complete (#35)
=== worktree list ===
/home/user/src/biz.dfch.SpecMgr                           6d6bf2f [dev]
/home/user/src/biz.dfch.SpecMgr.worktrees/feat-32-sysrs   4a4fc62 [feat-32-sysrs]
/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr     5ab4d20 [feat-33-vcr]
/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete  6d6bf2f [feat-36-delete]

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 75.1s)

_Thinking:_

The dev branch had advanced to `6d6bf2f` (a release commit that was pulled in after my earlier investigation). The worktree is correctly on `feat-36-delete` which branches from the tip of dev (`6d6bf2f`). The main checkout remains on `dev`, untouched (same commit, no changes). Good.

The worktree is clean and on the new branch. Next, let's write the feature README inside the worktree.

First, let me check the worktree's `.specmgr/feat/` directory and confirm that the feat-36-delete folder doesn't already exist.

Actually, since this is a fresh worktree branched from dev, the `.specmgr/feat/` directory contains the existing feature folders. I need to create `.specmgr/feat/feat-36-delete/README.md`.

Let me confirm the directory exists and take a look at the template again (I already have it). I'll create the folder and write the README.

Now, let me write a comprehensive design README. This should be something that a Phase-Orchestrator can execute. Let me follow the structure of the template and recent features (like feat-33-vcr).

Structure:

- Frontmatter: id, version, status, created, updated
- `# Feature: ...`
- `## Plan`
  - `### Overview`
  - `### Requirements`
  - `### Acceptance Criteria`
  - `### Scope` (what's included / what's explicitly out of scope)
  - `### Dependencies` (what it depends on / what it blocks)
  - `### Design Notes` (concrete design: reusable \_path_safety.py, shape of delete.py, adapters, locking, error handling)
  - `### Related ADRs` (new ADR to be created)
  - `### Task List` (phases)
- `## Progress`
  - `### Current Status`
  - `### Blockers`
  - `### Updates`
  - `### Decisions Made`
  - `### Related PRs / Commits`

Let me get the current date and time for the frontmatter. Today's date is Monday, August 31, 2026. Let me get the exact timestamp.

Let me check the exact date/time to use. I'll use `date` to get it. Actually, for the created/updated in the frontmatter, recent features use `YYYY-MM-DD` in the template, but feat-33-vcr was using full ISO timestamps in created and `updated` in a different format. Let me look at the convention.

From the template:

```
created: YYYY-MM-DD
updated: YYYY-MM-DD
```

But feat-33-vcr's frontmatter:

```
created: 2026-08-31 07:25:24.241609
updated: 2026-08-31 16:26:00
```

Hmm, there's variation. AGENTS.md says `created`/`updated` (`YYYY-MM-DD`, and `updated` gets bumped on every substantive edit). But actual features use timestamps. The feat domain's schema (FeatFrontmatter) — let me check what it requires. Actually, the README in `.specmgr/feat/` is a feat document that gets parsed by `feat/models/v1`. Let me check the format of the created/updated fields in the feat frontmatter model to make sure I write something that will parse.

Wait — but this README is a *feature plan* document under `.specmgr/feat/`. Does it need to be parseable by the feat model? Let me check. AGENTS.md says feat formalizes the `.specmgr/feat/<id>/README.md` convention into a schema-backed domain. So yes, `.specmgr/feat/feat-36-delete/README.md` should conform to the feat schema. Let me check the feat frontmatter model to get the format of the fields right.

Let me look at the feat model's frontmatter and body to make sure the README will parse. Actually, the safest approach is: closely mirror the structure of an existing, working feature README (like feat-33-vcr) that is known to parse. Let me check feat's frontmatter model.

Let me read the feat frontmatter model and the body model to understand the required structure.

Worktree is correct: `feat-36-delete` branches from `dev` tip (`6d6bf2f`), main checkout still on `dev` untouched. Now let me confirm the feat schema so the README I author will parse cleanly.

**Tool: bash**

**Input:**

```json
{
  "command": "date -u +\"%Y-%m-%dT%H:%M:%SZ\"; echo \"=== feat frontmatter ===\"; sed -n '1,140p' /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/models/v1/frontmatter.py"
}
```

**Output:**

```
2026-08-31T15:37:40Z
=== feat frontmatter ===
# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Feature (FEAT) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `rsk/models/v1/frontmatter.py::RskFrontmatter`:
a subtype of `MarkdownFrontmatter` that restricts `type` to a fixed
``Literal["feat"]`` and narrows the free-form ``status`` to a closed,
hyphen-free four-value lifecycle set, *and* redeclares the default away from
the base's ``"draft"`` (a `feat` document starts life ``"planning"``, not
``"draft"`` -- ``"draft"`` is not part of `feat`'s own closed set) -- see
`.specmgr/feat/feat-31-feature/README.md` Design Notes ("Frontmatter").

`created`/`updated` are inherited unchanged from `MarkdownFrontmatter` as
plain, unvalidated ``str | None`` -- the base model performs no format
validation on either field for any domain (the specific microsecond
timestamp convention every domain, including `feat`, uses is a
tool-layer/`_write.py` concern, not a model-layer one).
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md._util import default_if_blank

#: Fixed, closed set of accepted ``status`` values for features -- a
#: deliberately hyphen-free four-value lifecycle (``"progress"``, not
#: ``"in-progress"``), per explicit user direction:
#: ``planning`` (design/requirements still being written), ``progress``
#: (implementation under way), ``review`` (implementation done, pending
#: verification), or ``done`` (shipped).
_ALLOWED_STATUSES = frozenset(
    {
        "planning",
        "progress",
        "review",
        "done",
    }
)

#: Default ``status`` value when the key is absent or blank -- the starting
#: state of a feature's lifecycle. The base `MarkdownFrontmatter`'s own
#: default is ``"draft"``, which is not part of `feat`'s own set.
DEFAULT_FEAT_STATUS = "planning"


class FeatFrontmatter(MarkdownFrontmatter):
    """Feature (FEAT) frontmatter: `MarkdownFrontmatter` narrowed for the ``feat`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"feat"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["feat"] = "feat"``, so a document
        omitting ``type`` entirely still parses as a feature document.
    status:
        One of ``"planning"``, ``"progress"``, ``"review"``, ``"done"``.
        Narrows the base's free-form ``str`` field to this closed four-value
        set; absent/blank defaults to ``"planning"``
        (``_default_blank_status_to_planning`` below, which runs before the
        base's inherited ``_default_blank_status_to_draft``).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["feat"] = "feat"  # type: ignore
    status: str = DEFAULT_FEAT_STATUS

    @field_validator("status", mode="before")
    @classmethod
    def _default_blank_status_to_planning(cls, value: object) -> object:
        """Map an absent/blank ``status`` to ``"planning"`` (not the base's ``"draft"``).

        Runs before the base's inherited ``_default_blank_status_to_draft``
        (Pydantic applies child-class ``mode="before"`` validators first), so
        by the time the base's validator sees the value it is already
        ``"planning"`` and passes it through unchanged.
        """
        return default_if_blank(value, DEFAULT_FEAT_STATUS)

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 62.3s)

_Thinking:_

Frontmatter requires the following: `id`, `type` (default is feat), `status` (one of planning/progress/review/done), `version`, `created`, `updated`. In feat-33-vcr's frontmatter, `type: feat` and `version: 1.2.0` were used, and `created`/`updated` were written as full timestamps. Since created/updated are just simple strings with no validation, any format will work, but to be consistent with the actual feat documents, I'll use the full microsecond-precision timestamp format.

Next, let's check the feat body model and confirm that the required headings (like "Feature: ...", etc.) are correct. To understand the required structure, let's take a look at the feat body model.

Let me check the feat body schema for required headings so the README parses.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -nE \"class |Alias|alias|H1|Heading|^_.*=|required|mandatory\" /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/models/v1/body.py | head -60"
}
```

**Output:**

```
18:"""Feature (FEAT) body models: whole-section fields under a single H1.
24:the top-level H1 container, holding exactly two children, `Plan` and
29:Field declaration order on every composite class below enforces markdown
57:    AliasType,
65:    alias,
70:class Overview(MarkdownSection3):
80:_REQUIREMENT_ITEM_PATTERN = re.compile(r"^REQ-\d{3}: (?P<description>.+)$")
83:class RequirementItem(MarkdownListItem):
86:    A leaf `MarkdownListItem` subclass (no checkbox marker, unlike `TaskItem`):
115:class Requirements(MarkdownSection3):
146:_ACCEPTANCE_CRITERION_ITEM_PATTERN = re.compile(r"^ACC-\d{3}: (?P<description>.+)$")
149:class AcceptanceCriterionItem(TaskItem):
181:class AcceptanceCriteria(MarkdownSection3):
210:class Included(MarkdownSection4):
214:class ExplicitlyOutOfScope(MarkdownSection4):
219:class Scope(MarkdownSection3):
220:    """`### Scope` -- container for the two mandatory Included/Explicitly Out Of Scope leaves. No own text.
236:class DependsOn(MarkdownSection4):
241:class Blocks(MarkdownSection4):
246:class Dependencies(MarkdownSection3):
264:class DesignNotes(MarkdownSection3):
268:class RelatedDecisions(MarkdownSection3):
276:_PHASE_HEADING_PATTERN = re.compile(r"^Phase (?P<number>\d+): (?P<title>.+)$")
279:@alias(value=r"^Phase \d+: .+$", type=AliasType.REGEX)
280:class Phase(MarkdownSection4):
316:                `Phase`'s declared `@alias` (unreachable via the engine:
317:                `match_alias` already enforced it at parse time).
335:                `Phase`'s declared `@alias` (unreachable via the engine:
336:                `match_alias` already enforced it at parse time).
354:class TaskList(MarkdownSection3):
371:class Plan(MarkdownSection2):
406:class CurrentStatus(MarkdownSection3):
410:class Blockers(MarkdownSection3):
418:_ENTRY_HEADING_PATTERN = re.compile(
422:#: The `@alias` REGEX value shared verbatim by `UpdateEntry` and
425:_ENTRY_HEADING_ALIAS = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$"
428:@alias(value=_ENTRY_HEADING_ALIAS, type=AliasType.REGEX)
429:class UpdateEntry(MarkdownSection4):
465:                class's declared `@alias` (unreachable via the engine:
466:                `match_alias` already enforced it at parse time).
483:                class's declared `@alias` (unreachable via the engine:
484:                `match_alias` already enforced it at parse time).
492:class Updates(MarkdownSection3WithComment):
534:@alias(value=_ENTRY_HEADING_ALIAS, type=AliasType.REGEX)
535:class DecisionEntry(MarkdownSection4):
538:    Identical shape to `UpdateEntry` (same alias regex, same `timestamp`/
540:    a distinct class since it belongs to a semantically distinct section.
569:                class's declared `@alias` (unreachable via the engine:
570:                `match_alias` already enforced it at parse time).
587:                class's declared `@alias` (unreachable via the engine:
588:                `match_alias` already enforced it at parse time).
596:class DecisionsMade(MarkdownSection3WithComment):
640:@alias(value="Related PRs / Commits", type=AliasType.LITERAL)
641:class RelatedPrsCommits(MarkdownSection3):
649:class MoreInformation(MarkdownSection3):
653:class Progress(MarkdownSection2):
684:@alias(value="^Feature: .+$", type=AliasType.REGEX)
685:class Feature(MarkdownSection1):
686:    """The `feat` body: a single H1 section (`# Feature: {title}`) with the fields below.

```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/data/feat_template.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/data/feat_template.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-30
3: id: feat-0-template
4: status: planning
5: type: feat
6: updated: 2026-08-30
7: version: 1.0.0
8: ---
9: 
10: # Feature: Level 1 Heading is the Title of the Feature
11: 
12: ## Plan
13: 
14: ### Overview
15: 
16: A short description of what this feature is and why it exists.
17: 
18: ### Requirements
19: 
20: - REQ-001: A short, verifiable description of one specific requirement this feature must satisfy.
21: 
22: ### Acceptance Criteria
23: 
24: - [ ] ACC-001: A short, verifiable description of how you know this requirement has been met.
25: 
26: ### Scope
27: 
28: #### Included
29: 
30: - A bullet list of what this feature covers.
31: 
32: #### Explicitly Out Of Scope
33: 
34: - A bullet list of what this feature deliberately does not cover.
35: 
36: ### Dependencies
37: 
38: #### Depends On
39: 
40: - A bullet list of things this feature needs first. Optional.
41: 
42: #### Blocks
43: 
44: - A bullet list of things that cannot start until this feature ships. Optional.
45: 
46: ### Design Notes
47: 
48: Free-form design rationale, schema sketches, etc. Optional.
49: 
50: ### Related Decisions
51: 
52: - A bullet list of related ADR or DEC ids, each with a short description. Optional.
53: 
54: ### Task List
55: 
56: #### Phase 1: Placeholder Phase
57: 
58: - [ ] Task 1.1: A short description of one task in this phase.
59: 
60: ## Progress
61: 
62: ### Current Status
63: 
64: **As of 2026-08-30**: A short, free-form narrative of where things stand.
65: 
66: ### Blockers
67: 
68: - A short description of an open blocker. Optional.
69: 
70: ### Updates
71: 
72: <!-- Newest entry first -- prepend new entries directly below this comment. -->
73: 
74: #### 2026-08-30 00:00:00.000Z — Created
75: 
76: A short lead paragraph describing this update.
77: 
78: ### Decisions Made
79: 
80: <!-- Newest entry first -- prepend new entries directly below this comment. -->
81: 
82: #### 2026-08-30 00:00:00.000Z — Placeholder decision
83: 
84: A short lead paragraph describing the decision and its rationale.
85: 
86: ### Related PRs / Commits
87: 
88: - A bullet list of related pull requests or commits. Optional.
89: 
90: ### More Information
91: 
92: This optional section can contain additional information. There is no defined format for this section.

(End of file - total 92 lines)
</content>

<system-reminder>
Instructions from: /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/AGENTS.md
# AGENTS.md

Quick reference for OpenCode agents working on **biz.dfch.SpecMgr** — an artifact manager for system specifications.

## Status: domain packages implemented (the per-domain bullets below are the live enumeration)

Each package below follows the domain-first layout from ADR
ece4554b-725c-4f76-bc04-5d2b760363d2 ("Organize the codebase by
document-type domain: domain-first hierarchy for tools/prompts/resources,
shared versioned models") — one bullet per implemented package, document
type or cross-cutting:

- **`adr/`** (Architecture Decision Records) — the original, most complete
  domain. `adr/tools/` has 11 `@mcp.tool()` wrappers (`get_adr`, `list_adr`,
  `create_adr`, `update_frontmatter`, `update_section`,
  `option_list`/`option_create`/`option_read`/`option_update`/
  `option_delete`, `validate_adr`); ADR status changes go through the
  generic `set_status` tool in `general/tools/` (called with
  `type="adr"`, ADR-only `superseded_by`); `adr/resources/` exposes
  `specmgr://adr/{id}` only — no `specmgr://adr/list` (listing is the
  `list_adr` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13);
  `adr/prompts/` has
  narrated `create_adr`/`update_adr` prompts plus step-gated
  `create_adr_test`/`update_adr_test` A/B variants (see
  `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §11). Its Pydantic
  schema uniquely lives under the shared top-level `models/adr/` (not
  `adr/models/`) — see the "models location" note below.
- **`req/`** (Requirements) — `req/tools/` (`create_req`, `parse_req`,
  `list_req`, `delete_req` stub, `validate_req`); whole-body and line-range
  updates go through the generic `update` tool in `general/tools/`
  (`type="req"`), status changes through the generic `set_status` tool
  (`type="req"`); `req/resources/` (`specmgr://req/schema`,
  `specmgr://req/example`, `specmgr://req/template`; no `specmgr://req/{id}`
  — id-based reads are `get_req`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://req/list` —
  listing is the `list_req` tool, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13); `req/prompts/`
  (`create_req`/`update_req`). Its schema lives at `req/models/v1/`, inside
  the domain package itself, not under top-level `models/`.
- **`uc/`** (Use Cases) — same tools/resources/prompts shape as `req/` but
  for use cases (`create_uc`, `parse_uc`,
  `list_uc`, `get_uc`, `get_uc_example`, `get_uc_template`, `delete_uc` stub,
  `validate_uc`); whole-body and line-range updates go through the generic
  `update` tool in `general/tools/` (`type="uc"`), status changes through
  the generic `set_status` tool (`type="uc"`), and the `get_uc` tool takes
  `raw: bool = False` — `raw=True` returns the frontmatter-stripped body
  text as-is (the text `update`'s `begin`/`end` index into); no
  `specmgr://uc/{id}` resource for the same reason as
  REQ, and no `specmgr://uc/list` resource either — listing is the
  `list_uc` tool (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). Schema at
  `uc/models/v1/` (legacy) and `uc/models/v2/` (current),
  inside the domain package, not `models/uc/`.
- **`tsk/`** (Task Lists) — same shape again (`create_tsk`,
  `parse_tsk`, `list_tsk`, `get_tsk`, `get_tsk_example`,
  `get_tsk_template`, `delete_tsk` stub, `validate_tsk`); whole-body and
  line-range updates go through the generic `update` tool in
  `general/tools/` (`type="tsk"`), status changes through the generic
  `set_status` tool (`type="tsk"`), and the `get_tsk` tool takes
  `raw: bool = False` — `raw=True` returns the frontmatter-stripped body
  text as-is (the text `update`'s `begin`/`end` index into); plus a distinct
  `implement_task` prompt (reads a task list via `get_tsk`, builds a
  `TodoWrite` list from its items, and uses the `question` tool to resolve
  ambiguity). Its resources are the usual `specmgr://tsk/schema`/
  `specmgr://tsk/example`/`specmgr://tsk/template` only — no
  `specmgr://tsk/{id}` and no `specmgr://tsk/list` resource (listing is
  the `list_tsk` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). Schema
  at `tsk/models/v1/`, inside the domain package.
- **`qa/`** (Question and Answer) — same tools/resources/prompts shape as
  `req/`/`tsk/` but for requirements-elicitation Q&A interviews (`create_qa`,
  `parse_qa`, `list_qa`, `get_qa`, `get_qa_example`,
  `get_qa_template`, `delete_qa` stub, `validate_qa`); whole-body and
  line-range updates go through the generic `update` tool in
  `general/tools/` (`type="qa"`), status changes through the generic
  `set_status` tool (`type="qa"`), and the `get_qa` tool takes
  `raw: bool = False` — `raw=True` returns the frontmatter-stripped body
  text as-is (the text `update`'s `begin`/`end` index into); `qa/resources/`
  (`specmgr://qa/schema`, `specmgr://qa/example`,
  `specmgr://qa/template`; no `specmgr://qa/{id}` — id-based reads are
  `get_qa`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://qa/list` — listing is the `list_qa` tool, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13); `qa/prompts/`
  (`create_qa`/`update_qa`, plus `refine`). Schema at `qa/models/v2/`,
  inside the domain package, not `models/qa/` — QA is a single-schema
  (v2-only) domain: every question/answer category holds zero or more
  adjacent, un-headed pairs (`<!-- optional comment -->` + `> {question}`
  block quote + free-form answer prose) directly inside a category section,
  no heading of its own per pair, plus a `## Elicitation Context` section
  (structurally identical to, but not one of, the 9 ISO/IEC 25010:2023
  characteristic sections) between `## General` and
  `## Functional Suitability`. An earlier `qa/models/v1/` schema (one
  `### {heading}` H3 per question/answer pair) existed alongside v2 during
  feat-14 and was removed entirely once every QA MCP tool/resource/prompt
  was repointed at v2 (feat-14 Phase 8) — there is no version-gate or
  dual-schema read support: a document shaped for the removed v1 schema
  fails v2 parsing with a structural
  `AssertionError`/`pydantic.ValidationError`, not a migration-specific
  error.
- **`prb/`** (Problem Statement) — same tools/resources/prompts shape as
  `req/`/`tsk`/`qa` but for Six-Sigma-style problem statements
  (`create_prb`, `parse_prb`, `list_prb`,
  `get_prb`, `get_prb_example`, `get_prb_template`, `delete_prb` stub,
  `validate_prb`); whole-body and line-range updates go through the generic
  `update` tool in `general/tools/` (`type="prb"`), status changes through
  the generic `set_status` tool (`type="prb"`), and the `get_prb` tool
  takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped
  body text as-is (the text `update`'s `begin`/`end` index into);
  `prb/resources/` (`specmgr://prb/schema`,
  `specmgr://prb/example`, `specmgr://prb/template`; no
  `specmgr://prb/{id}` — id-based reads are `get_prb`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://prb/list` — listing
  is the `list_prb` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13);
   `prb/prompts/` (`create_prb`/`update_prb`, narrated `TodoWrite` +
   `question`-tool-driven 5W2H interview flows). Schema at
   `prb/models/v1/`, inside the domain package, not top-level
   `models/`.
- **`gol/`** (Goal) — same tools/resources/prompts shape as
  `req/`/`prb/` but for high-level business goals (the strategic
  "what the organization wants to achieve" level that sits above
  individual requirements) (`create_gol`,
  `parse_gol`, `list_gol`, `get_gol`,
  `get_gol_example`, `get_gol_template`, `delete_gol` stub,
  `validate_gol`); whole-body and line-range updates go through the generic
  `update` tool in `general/tools/` (`type="gol"`), status changes through
  the generic `set_status` tool (`type="gol"`), and the `get_gol` tool
  takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped
  body text as-is (the text `update`'s `begin`/`end` index into);
  `gol/resources/` (`specmgr://gol/schema`,
  `specmgr://gol/example`, `specmgr://gol/template`; no
  `specmgr://gol/{id}` — id-based reads are `get_gol`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://gol/list` —
  `list_gol` ships as a paged tool from day one, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13); `gol/prompts/`
  (`create_gol`/`update_gol`, narrated `TodoWrite` +
  `question`-tool-driven interview flows; `create_gol` first checks
   `list_gol` for a near-duplicate goal). Its schema lives at
   `gol/models/v1/`, inside the domain package, not top-level
   `models/`. The body mirrors REQ minus the `## Characteristics`
  and `## Level` sections (see `.specmgr/feat/feat-18-goal/README.md`).
- **`rsk/`** (Risk) — same tools/resources/prompts shape as
  `req/`/`prb/` but for risk-register entries (the scenario decomposed
  into `## Cause`/`## Trigger`/`## Consequence`, a 5x5 probability/impact
  assessment BEFORE mitigation (`## Initial Assessment`) and the same 5x5
  AFTER mitigation (`## Residual Assessment`) with the value in the H3
  heading itself (`### Probability {1..5}` / `### Impact {1..5}`, regex
  `@alias`-constrained, derived zone `level` always computed from the
  product), and a TARA response strategy `## Strategy` (closed 4-value set
  `transfer`/`accept`/`reduce`/`avoid`))
  (`parse_rsk`, `get_rsk`, `list_rsk`, `get_rsk_example`,
  `get_rsk_template`, `create_rsk`,
  `delete_rsk` stub, `validate_rsk`); whole-body and line-range updates
  go through the generic `update` tool in `general/tools/`
  (`type="rsk"`), status changes through the generic `set_status` tool
  (`type="rsk"`), and the `get_rsk` tool takes `raw: bool = False` —
  `raw=True` returns the frontmatter-stripped body text as-is (the text
  `update`'s `begin`/`end` index into); `rsk/resources/`
  (`specmgr://rsk/schema`, `specmgr://rsk/example`,
  `specmgr://rsk/template`, plus two static domain-knowledge resources
  `specmgr://rsk/tara` — what TARA is and when/how to apply each of the
  four words — and `specmgr://rsk/risk-matrix` — the 5x5 scale anchors,
  zone table, and product thresholds; no `specmgr://rsk/{id}` — id-based
  reads are `get_rsk`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://rsk/list` — `list_rsk` ships as a paged tool from day one,
  ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, and its `RskSummary` lines
  carry the residual-risk coordinates so a register-wide risk-matrix view
  can be built from the listing alone); `rsk/prompts/`
   (`create_risk`/`update_risk` — the issue's literal wording, not the
   `rsk`-prefixed convention the tools/resources use). Its schema lives at
   `rsk/models/v1/`, inside the domain package, not top-level
   `models/`.
- **`dec/`** (Decision) — same tools/resources/prompts shape as
  `req/`/`prb/` but for decisions in general (not architecture-only)
  (`parse_dec`, `get_dec`, `list_dec`, `get_dec_example`,
  `get_dec_template`, `create_dec`, `delete_dec` stub,
  `validate_dec`); whole-body and line-range updates go through the
  generic `update` tool in `general/tools/` (`type="dec"`), status
  changes through the generic `set_status` tool (`type="dec"`), and
  the `get_dec` tool takes `raw: bool = False` — `raw=True` returns
  the frontmatter-stripped body text as-is (the text `update`'s
  `begin`/`end` index into); `dec/resources/`
  (`specmgr://dec/schema`, `specmgr://dec/example`,
  `specmgr://dec/template`; no `specmgr://dec/{id}` — id-based reads
  are `get_dec`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://dec/list` — `list_dec` ships as a paged tool from day
  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13); `dec/prompts/`
  (`create_dec`/`update_dec`, narrated `TodoWrite` +
  `question`-tool-driven interview flows; `create_dec` first checks
  `list_dec` for a near-duplicate decision). Its schema lives at
  `dec/models/v1/`, inside the domain package, not top-level
  `models/`. A DEC keeps the ADR's general structure (MADR-style
  headings, `Options` collection) but is built on the generic
  `models/md` parser with the GOL/RSK/QA simple surface — no
  fine-grained mutation tools, no renderer: writes persist the
  caller's raw validated body byte-for-byte.
- **`sop/`** (Standard Operating Procedure) — same tools/resources/prompts
  shape as `dec/` but for structured, step-by-step operational documents
  with a RASCI-style responsibility assignment and a closed
  approval/effectivity lifecycle (`create_sop`, `parse_sop`, `list_sop`,
  `get_sop`, `get_sop_example`, `get_sop_template`, `delete_sop` stub,
  `validate_sop`); `sop` is the **first domain built dispatch-only from day
  one** (ADR 36905d5b-8057-4294-8665-c7eed5534db0) — it has NO per-domain
  `update_sop`/`set_status_sop` tools at all, so whole-body and line-range
  updates go through the generic `update` tool in `general/tools/`
  (`type="sop"`) and status changes through the generic `set_status` tool
  (`type="sop"`), and the `get_sop` tool takes `raw: bool = False` —
  `raw=True` returns the frontmatter-stripped body text as-is (the text
  `update`'s `begin`/`end` index into); `sop/resources/`
  (`specmgr://sop/schema`, `specmgr://sop/example`,
  `specmgr://sop/template`; no `specmgr://sop/{id}` — id-based reads
  are `get_sop`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://sop/list` — `list_sop` ships as a paged tool from day
  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13); `sop/prompts/`
  (`create_sop`/`update_sop`, narrated `TodoWrite` +
  `question`-tool-driven interview flows; `create_sop` first checks
  `list_sop` for a near-duplicate SOP; both prompts include an explicit
  `specmgr://rasci` read-first step before `## Roles and Responsibilities`,
  and `update_sop` names the GENERIC `update`/`set_status` tools with
  `type="sop"`). Its schema lives at `sop/models/v1/`, inside the domain
  package, not top-level `models/`. An SOP is built on the generic
  `models/md` parser with the GOL/RSK/QA/DEC simple surface — no
  fine-grained mutation tools, no renderer: writes persist the
  caller's raw validated body byte-for-byte. `sop` relies on the
  cross-cutting `specmgr://rasci` resource (REQ-011, see `general/`
  below) for the generic RASCI role definitions used by its
  `## Roles and Responsibilities` section, not a domain-local one.
- **`feat/`** (Feature) — formalizes the ad hoc `.specmgr/feat/<id>/
  README.md` convention (ADR e369ee2e-3353-4f92-991c-6367d76d832e) into a
  real, schema-backed domain, and is the one domain in this codebase whose
  own addressing genuinely deviates from every other domain's precedent
  (ADR 8cf940c5-3100-485c-a12d-14b59b631712): `id` is a chosen
  `feat-NNN-slug` — the containing folder's own name, not a
  server-generated UUID — and documents live one-per-folder as
  `<base>/<id>/README.md` (a fixed filename), not flat files directly
  under the base directory. This bespoke, folder-per-document addressing
  is hand-rolled in `feat/tools/_paths.py` (ADR-style, like `adr/tools/
  _paths.py`), **not** built on the shared flat-file
  `general/tools/_doc_paths.py` every other whole-body domain uses;
  `SPECMGR_FEAT_DIR` overrides the base directory (mandatory-in-spirit
  test-isolation env var, same as every other domain's own equivalent).
  All 8 tools (`create_feat`, `parse_feat`, `list_feat`, `get_feat`,
  `get_feat_example`, `get_feat_template`, `delete_feat` stub,
  `validate_feat`); whole-body and line-range updates go through the
  generic `update` tool in `general/tools/` (`type="feat"`), status
  changes through the generic `set_status` tool (`type="feat"`) — no
  `update_feat`/`set_status_feat` of its own — and the `get_feat` tool
  takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped
  body text as-is (the text `update`'s `begin`/`end` index into);
  `feat/resources/` (`specmgr://feat/schema`, `specmgr://feat/example`,
  `specmgr://feat/template`; no `specmgr://feat/{id}` — id-based reads
  are `get_feat`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://feat/list` — `list_feat` ships as a paged tool from day
  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13); `feat/prompts/`
  (`create_feat`/`update_feat`, narrated instruction flows; `create_feat`
  first checks `list_feat` for a near-duplicate feature). Its schema
  lives at `feat/models/v1/`, inside the domain package, not top-level
  `models/`. `FeatSummary` adds one extra field beyond every other
  domain's summary, `path: str` (the real filesystem path to the
  document's `README.md`) — a deliberate divergence, since direct
  hand/agent editing of `.specmgr/feat/<id>/README.md` remains the
  domain's own normal, sanctioned workflow even after its MCP tools
  exist, unlike every other domain's summary, whose `ref` field is
  deliberately *not* a path. See
  `.specmgr/feat/feat-31-feature/README.md` for the full design.
- **`vcr/`** (Verification Case Record) — same tools/resources/prompts
  shape as `req/`/`prb/`/`dec/` but for how a single REQ/UC is verified: a
  `## Verifies` single-value cross-reference (exactly one mandatory
  `REQ|UC <uuid>: <title>` line plus a mandatory `notes` paraphrase, not a
  bullet list — a single-value field is structurally incapable of holding
  more than one reference), a `## Coverage` closed-vocabulary outcome
  signal (`full`/`partial`/`none`, mirroring RSK's `## Strategy` idiom),
  and a `## Acceptance Criteria` collection of `### AC-NNN (Method): ...`
  entries (3-digit zero-padded number, DEC-`Option`-style numbered H3, no
  per-AC mutation tools; `Method` is a closed **DTAIS** vocabulary —
  Demonstration, Test, Analysis, Inspection, Special — parsed from the
  heading itself via regex, RSK `Probability`/`Impact`-style; each entry
  optionally carries a free-form `description` paragraph and/or a
  `#### Test Steps` numbered procedure; a `model_validator` rejects
  duplicate `AC-NNN` numbers), plus optional `## More Information`/
  `## Updates` (`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr`,
  `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub,
  `validate_vcr`); whole-body and line-range updates go through the
  generic `update` tool in `general/tools/` (`type="vcr"`), status
  changes through the generic `set_status` tool (`type="vcr"`), and the
  `get_vcr` tool takes `raw: bool = False` — `raw=True` returns the
  frontmatter-stripped body text as-is (the text `update`'s `begin`/`end`
  index into); `vcr/resources/` (`specmgr://vcr/schema`,
  `specmgr://vcr/example`, `specmgr://vcr/template`; no
  `specmgr://vcr/{id}` — id-based reads are `get_vcr`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://vcr/list` —
  `list_vcr` ships as a paged tool from day one, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13); `vcr/prompts/`
  (`create_vcr`/`update_vcr`). Its schema lives at `vcr/models/v1/`,
  inside the domain package, not top-level `models/`. The closed DTAIS
  method vocabulary its `## Acceptance Criteria` depends on is documented
  by the cross-cutting `specmgr://dtais` resource, which lives in
  `general/resources/`, not `vcr/resources/`, since it is domain-knowledge
  other document types may also want to reference (mirroring RSK's
  `specmgr://rsk/tara` shape). See `.specmgr/feat/feat-33-vcr/README.md`
  for the full design.
  - **`general/`** — cross-cutting, non-domain-specific package:
    `general/tools/` (`mdformat`, formats a markdown file in place while
    preserving YAML frontmatter blocks; `update`, the generic whole-body
    *and* line-range replace for the eleven whole-body domains — `type` is
    one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr, optional 1-based inclusive
    body-line
    `begin`/`end` with the `N+1` end-of-body sentinel, splice-then-
    validate-whole; `set_status`, the generic status change for all twelve
    domains incl. adr — `superseded_by` is ADR-only, composing
    `"superseded by X"`), `general/resources/`
   (`specmgr://version`, `specmgr://iso25010` — the ISO/IEC 25010:2023
   quality model, `specmgr://dtais` — the DTAIS verification-method
   vocabulary VCR's `## Acceptance Criteria` depends on, kept here rather
   than under `vcr/resources/` since it is domain-knowledge other document
   types may also want to reference, and `specmgr://rasci` — the generic
   RASCI responsibility-assignment framework, REQ-011; motivated by `sop`
   but not scoped to it), and `general/prompts/` (`compact_history` — rotates
     older `Recent Updates` entries out of any feature folder's `README.md`
     into a sibling `history.md`). The eleven `get_<d>` tools additionally
     take a `raw: bool = False` parameter — `raw=True` returns the
    frontmatter-stripped body text as-is (the text `update`'s `begin`/`end`
    index into).

**Models location — a real, intentional divergence, not an oversight**:
the rule is domain-first — every document type keeps its schema inside
its own domain package (`<domain>/models/vN/`); building a new document
type requires no edit to this paragraph. The single exception is ADR:
its schema (`AdrFrontmatter`, `AdrBody`, `AdrOption`, `Adr`, `parse_adr`,
`render_adr`) stays under the shared top-level `models/adr/` package
because it predates the domain-first refactor and has no dependency on
`mcp`/`tools`/`resources`/`prompts`. Top-level `models/` therefore holds
`adr/` (the exception) plus only shared cross-domain modules —
`iso25010.py`, `md/` (markdown-section building blocks), and
`version_info.py` — don't assume any other doc type's schema lives there.

`server.py`'s own module docstring is the single most authoritative,
currently-maintained list of every resource/tool/prompt this MCP server
registers — read it before consulting this file for specifics, and update
it whenever you add/remove/rename a resource, tool, or prompt.
`docs/MCP.md` is the auto-generated (via `specmgr mcp-docs`), user-facing
mirror of that same registration and must never be hand-edited.

Still genuinely missing / not yet done (don't assume otherwise):
- No `validate_adr` (or `validate_req`/`validate_uc`/`validate_tsk`/
  `validate_qa`/`validate_prb`/`validate_gol`/`validate_rsk`/
  `validate_dec`/`validate_sop`/`validate_feat`/`validate_vcr`) tool runs
  over the repo's
  own documents yet via pre-commit or CI. (ADR
  9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests
  locally via pre-commit hook, not just CI")
- `delete_req`/`delete_uc`/`delete_tsk`/`delete_qa`/`delete_prb`/
  `delete_gol`/`delete_rsk`/`delete_dec`/`delete_sop`/`delete_feat`/
  `delete_vcr` are stubs, not yet implemented.
- No `ac` (Acceptance Criteria) domain exists yet, despite `server.py`'s
  docstring already reserving a spot for it ("... and later `ac`") — the
  convention for adding it (or any future domain) is fixed by ADR
  36905d5b-8057-4294-8665-c7eed5534db0: one dispatch entry to each of the
  two generic tools in `general/tools/` (`update`'s `type`,
  `set_status`'s `type`) plus a `raw` parameter on the new `get_<d>` tool
  — not new `update_<d>`/`set_status_<d>` tools.
- `req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr` each register
  `tools`, `resources`, and `prompts`; `uc` registers `tools` and
  `resources` only — it has no `prompts` sub-package yet.

`.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §10 ("Next steps") tracks per-item done/not-done
status for the ADR feature specifically and should be kept in sync with
`src/` as this evolves; treat it as current-state tracking, not just a
historical design doc. Don't assume any domain package exists beyond the
per-domain bullets in the Status section above (each with its respective
`tools`/`prompts`/`resources` sub-packages, per the exceptions noted
there), or anything in `general/resources/` beyond `version`/`iso25010` —
check first.

## Project Shape

- **Type**: Python library + optional CLI + optional MCP server, in one repo
- **Namespace**: `biz.dfch.specmgr` in `src/biz/dfch/specmgr/` — `biz`/`biz/dfch`
  are implicit namespace packages (no `__init__.py` in those two dirs; only the
  leaf `specmgr/` has one)
- **Package manager**: `uv` (not pip) — lockfile is committed, use `--frozen`
- **Python**: `requires-python = ">=3.11"` (3.11–3.13 tested in CI); local dev
  defaults to 3.13 via `.python-version` — two separate settings, keep in
  sync intentionally, not by accident

## Development Artifacts (`.specmgr/`)

Per ADR e369ee2e-3353-4f92-991c-6367d76d832e ("Organize development
artifacts in `.specmgr` with feature-driven work units"), development
planning/progress artifacts live under `.specmgr/`, separate from published
documentation in `docs/`:

```

.specmgr/
├── \_template/
│ └── v1/
│ └── README.md # Versioned feature template (plan + progress)
└── feat/
└── feat-NNN-slug/ # One folder per GitHub issue
├── README.md # Feature plan + progress (mandatory)
└── history.md # Archived older "Recent Updates" entries (optional)

````

- **Naming convention**: `feat-NNN-slug`, where `NNN` is the GitHub issue
  number. Work started without an issue yet uses `feat-0-slug` (issue number
  `0`) until/unless an issue is later opened for it.
- **Single `README.md` per feature** combines the plan (requirements,
  acceptance criteria, scope, dependencies, design notes) and progress
  (current status, blockers, recent updates, decisions made) — there is no
  separate `progress.md`; status lives inline on each task line, edited in
  place rather than duplicated.
- **Template**: `.specmgr/_template/v1/README.md` is the versioned,
  reusable template (copy it when starting a new feature folder). It is
  hand-copied, not scaffolded by any tool — no automation exists for this
  yet, and none is currently planned.
- **Frontmatter**: every feature `README.md` starts with a minimal YAML
  frontmatter block — `id` (the `feat-NNN-slug` folder name itself, not a
  generated UUID), `version` (semver, starts at `1.0.0`), `status`
  (`planning` | `in-progress` | `review` | `done`), and `created`/`updated`
  (`YYYY-MM-DD`, `updated` bumped on every substantive edit). There is no
  separate `GitHub Issue` field/body-line: the issue number is the `NNN`
  infix already embedded in `id`/the folder name (`feat-NNN-slug`) — `0`
  means no issue yet — so it is never duplicated elsewhere in the file. See
  ADR e369ee2e-3353-4f92-991c-6367d76d832e's Option 1 for the full
  rationale.
- **`doc/` has been migrated** into this structure — development planning docs
   now live in `.specmgr/feat/` with their respective feature folders.
- **No CI/pre-commit enforcement** exists for `.specmgr/` content — unlike
  `docs/adr/`, there is no `validate_adr`-equivalent check and no `adr-toc`-
  equivalent generation step wired into hooks or CI for feature folders.
- **ADR vs. feature-level "Decisions Made" log**: a decision belongs in a
  full ADR (`docs/adr/`) if it's architecture/structure-level, affects more
  than one feature or the repo as a whole, or reverses/supersedes a previous
  ADR. It belongs in the feature's own "Decisions Made" log instead if it's
  scoped entirely to that feature's implementation details. When in doubt,
  write the ADR.
- Existing feature folders: `.specmgr/feat/feat-9-doc-in-specmgr/`
   (development artifacts migration), `.specmgr/feat/feat-4-use-cases/` (use-case
   modeling and examples), `.specmgr/feat/feat-5-md-model-parser/` (markdown
   parsing infrastructure).

## Developer Commands

```bash
uv sync --all-extras                                                   # install deps
uv run --frozen pre-commit install                                     # one-time: enable pre-commit hooks
uv run --frozen ruff format --check && uv run --frozen ruff check      # lint (enforced)
uv run --frozen pylint $(git ls-files '*.py')                          # lint (advisory only; CI runs it with `|| true`)
uv run --frozen vulture src/ whitelist.py --min-confidence 60          # dead-code check (enforced)
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"  # tests
scripts/release.sh help                                            # staged release automation (SOP 98537416; README "Make a Release")
uv run --frozen specmgr docs                                           # regenerate docs/api/ + docs/GENERATED.md
uv run --frozen specmgr adr-toc                                        # regenerate docs/adr/README.md (ADR table of contents)
uv run --frozen specmgr unused-code                                    # report unused code in src/ (same check as the vulture hook)
uv run --frozen specmgr unused-code --test                             # report symbols only referenced from tests/, never src/
uv run --frozen specmgr version                                        # run the CLI
````

### Using a different Python version

The project defaults to Python 3.13 (see `.python-version`). To use a different version (e.g., 3.12), add `--python X.Y` to **both** `uv sync` and `uv run` commands, and include `--all-extras` on the `uv run` call:

```bash
uv sync --all-extras --frozen --python 3.12
uv run --frozen --all-extras --python 3.12 specmgr docs
```

Without `--all-extras` on `uv run`, only base dependencies are installed, causing `ModuleNotFoundError` for CLI/MCP extras like `typer`.

`pylint` only sees files tracked by git (`git ls-files`) — new files must be
`git add`ed before it will lint them, both locally and in CI.

`pre-commit install` is one-time per clone (see `.pre-commit-config.yaml`):
runs `ruff format`/`ruff check`, the full `unittest` suite (scoped to
`src/**/*.py`/`tests/**/*.py` changes), a local `specmgr docs` hook (scoped to
`src/**/*.py` changes), and a local `specmgr adr-toc` hook (scoped to
`docs/adr/**/*.md` changes) before every commit, so a broken test or drift in
`docs/api/`/`docs/GENERATED.md`/`docs/adr/README.md` gets caught locally instead
of failing later in CI. (ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests locally via pre-commit hook, not just CI")

## Extras split (base library has no CLI/MCP deps)

`dependencies` in `pyproject.toml` is only `pydantic` + `python-dotenv`, so the
library is usable standalone. `typer`/`rich` live in the `cli` extra, `mcp` in
the `mcp` extra. **Never** import `cli.py` or `server.py` from
`src/biz/dfch/specmgr/__init__.py` — that would force those extras onto every
consumer of the base library.

## CLI (`cli.py`)

- Typer app, entry point `specmgr` (`pyproject.toml` `[project.scripts]`);
  `python -m biz.dfch.specmgr` (`__main__.py`) runs the same Typer `app()`.
- **Gotcha**: with only one `@app.command()` registered, Typer collapses to a
  single top-level command and drops subcommand dispatch (`specmgr version`
  would fail with "unexpected extra argument"). An explicit `@app.callback()`
  (see `_callback` in `cli.py`) forces Typer to keep treating it as a command
  group — keep that callback even after a second command is added, don't
  assume it becomes dead code to remove.

## MCP server (`server.py`)

- Builds the `MCPServer` instance (`mcp` object) and a no-op `_lifespan`,
  then imports every domain package (`adr`, `dec`, `feat`, `general`,
  `gol`, `prb`, `qa`, `req`, `rsk`, `sop`, `tsk`, `uc`, `vcr`) as its last line purely
  for the side effect of
  running their `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` decorators.
  When adding a new domain, add its import to that same last line —
  forgetting it means the new tools/resources/prompts silently never
  register.
- **`specmgr mcp`** (`commands/mcp.py`) *does* start the server —
  `mcp_server.run(transport="stdio")` by default, or
  `mcp_server.run(transport="sse", host=..., port=...)` via
  `--transport sse`/`-t sse`. `python -m biz.dfch.specmgr mcp` and
  `uvx --from "biz-dfch-specmgr[mcp]" specmgr mcp` both work identically
  (see `README.md`'s "Add to OpenCode" section) — don't assume the server
  has no working entry point.

## CI / Release

- Branches: `dev` (default, feature work) → `main` (stable) → tag.
- `.github/workflows/ci.yml`: ruff + pylint (`|| true`) + vulture + unittest
  run on matrix 3.11/3.12/3.13 via `uv sync --frozen --all-extras`, but
  `specmgr docs` and `specmgr adr-toc` drift checks run **only on Python
  3.13** (pinned, since different Python versions generate different
  docstring formatting in the API docs, and we want consistent ADR TOC
  generation).
- `.github/workflows/publish.yml` exists and has shipped `v0.1.0`, `v0.2.0`,
  `v0.2.1` to PyPI/the MCP Registry, triggered on `v*` tags.
- Version bumps: update `version` in `pyproject.toml` (single source) and
  move `CHANGELOG.md`'s `[Unreleased]` into a dated section, same commit.

## Coding Standards

See `.specmgr/conventions.md` for detailed coding requirements and conventions:

- Python version and type notation

- Assert statement guidelines

- Variable naming (use `result` for return values)

- Comparison constants

- Mandatory type hints

- Documentation requirements for classes, attributes, and functions

- Formatter/linter: `ruff` (enforced, not black), line length 120.

- `pylint` is advisory fallback only (see pylint caveat above).

## Generated Documentation

See [`docs/GENERATED.md`](docs/GENERATED.md), auto-generated by `specmgr docs` (implemented-domain list, per-module docstrings, and test-file count).
This pointer is permanent and hand-written — it is never regex-spliced or
otherwise auto-edited; only `docs/GENERATED.md` itself is regenerated.

</system-reminder>
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 111.3s)

_Thinking:_

I've confirmed the feat schema and template. Now I have a clear picture of the structure the README should follow. Important details:

- Frontmatter: `created`, `id`, `status`, `type`, `updated`, `version`.
- H1: `# Feature: {title}`
- `## Plan` containing `### Overview`, `### Requirements`, `### Acceptance Criteria`, `### Scope` (with `#### Included`, `#### Explicitly Out Of Scope`), `### Dependencies` (with `#### Depends On`, `#### Blocks`), `### Design Notes`, `### Related Decisions`, `### Task List` (with `#### Phase N: {title}` and task items).
- `## Progress` containing `### Current Status`, `### Blockers`, `### Updates` (with `<!-- Newest entry first ... -->` comment and `#### {timestamp} — {title}` entries), `### Decisions Made` (with comment and entries), `### Related PRs / Commits`, `### More Information`.

Important format details from the body model:

- Requirements: `- REQ-NNN: {description}` — the pattern is `^REQ-\d{3}: (?P<description>.+)$`. Note: it's `MarkdownListItem` (no checkbox).
- Acceptance Criteria: `- [ ] ACC-NNN: {description}` — `TaskItem` (with checkbox), pattern is `^ACC-\d{3}: (?P<description>.+)$`.
- Task list: phases are `#### Phase N: {title}`, tasks are `- [ ] Task N.M: {description}`.
- Updates/Decisions entries: `#### {timestamp} — {title}`, where the timestamp pattern is `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$`. So the format is `YYYY-MM-DD HH:MM:SS.mmmZ` or with offset, followed by `—` (em dash), and then the title. Note: it's an em dash (—), not a hyphen.

Wait, the feat-33-vcr README used `#### 2026-08-31T16:26:00.000000 — Merged current...` (with a T and 6-digit microseconds). But the alias regex is `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$`, which requires a space separator (not T), milliseconds (\\d{3}), and Z or offset. Hmm, this is contradictory. Let me re-check.

Actually, wait. feat-33-vcr's frontmatter is `updated: 2026-08-31 16:26:00` and the update entries are `#### 2026-08-31T16:26:00.000000 — ...`. If the regex requires `YYYY-MM-DD HH:MM:SS.mmmZ`, then `2026-08-31T16:26:00.000000` shouldn't match. But feat-33-vcr is a `done` and presumably parsed feature...

Let me reconsider. Maybe the `_ENTRY_HEADING_ALIAS` regex I saw isn't what's actually being enforced, or maybe there's a different version. Let me carefully re-read the body model's UpdateEntry/DecisionEntry aliases. What I saw was:

```
418:_ENTRY_HEADING_PATTERN = re.compile(
422:#: The `@alias` REGEX value shared verbatim by `UpdateEntry` and
425:_ENTRY_HEADING_ALIAS = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$"
```

Hmm, wait, that's the alias. But the feat-33-vcr entries use `T` separators and 6-digit microseconds. This is contradictory. Maybe... I misread. Let me actually re-read that section of body.py and look at the exact regex. Actually, the grep output might have been showing something slightly different. Let me read the actual lines 410–440 of body.py.

Actually, this is important. Because I need to write the README so it can be parsed. But wait — do I actually need it to be parseable? AGENTS.md says "CI/pre-commit enforcement doesn't yet exist for .specmgr/ content — there's no validate_adr-equivalent check for feature folders." So feature READMEs aren't validated in CI or pre-commit. However, the `feat` domain parses them, and the `compact_history` prompt and `get_feat` operate on them. Also, `list_feat` scans `.specmgr/feat/` (SPECMGR_FEAT_DIR). So this README will be parsed by the feat tools. To be safe and consistent, it should be in a parseable format.

But actually — here's a subtle point. This feature folder `feat-36-delete` will be inside the worktree. In production, the feat base directory is `.specmgr/feat/`. When running in the worktree, `list_feat`/`get_feat` with `SPECMGR_FEAT_DIR` pointing at the worktree's `.specmgr/feat` would pick it up. So it should be in a valid format.

Let me read the exact UpdateEntry alias to get the timestamp format right. Let me read lines 405–540 of body.py.

Actually, let me reconsider whether I'm overthinking this. The safest approach: mimic the exact format of existing parseable feature READMEs (like feat-33-vcr or feat-31-feature) as closely as possible. feat-33-vcr is `status: done` and is an actual feature document that the feat domain parses (it's under `.specmgr/feat/` and gets listed by `list_feat`). So if I match its format exactly, mine should parse too.

Let me look at the timestamp format feat-33-vcr uses in its Updates and Decisions Made entries, and in its frontmatter. From what I read earlier:

- Frontmatter: `created: 2026-08-31 07:25:24.241609`, `updated: 2026-08-31 16:26:00`
- Updates entries: `#### 2026-08-31T16:26:00.000000 — Merged current ...`

But the template (feat_template.md) uses:

- Frontmatter: `created: 2026-08-30`, `updated: 2026-08-30`
- Updates: `#### 2026-08-30 00:00:00.000Z — Created`
- Decisions: `#### 2026-08-30 00:00:00.000Z — Placeholder decision`

So the template uses the space-separated `YYYY-MM-DD HH:MM:SS.mmmZ` format that matches the regex `_ENTRY_HEADING_ALIAS`. The feat-33-vcr uses `T`-separated 6-digit microseconds, which shouldn't match that regex...

This is a genuine contradiction. Let me resolve it by actually reading the body.py regex. Perhaps the alias is more lenient than I think, or perhaps the `UpdateEntry`'s `@alias` regex is different from `_ENTRY_HEADING_ALIAS` (which might be used for `DecisionEntry`). Let me read the actual file.

Let me carefully read body.py lines 405–540.

The feat schema has strict heading/timestamp formats. Let me read the exact `UpdateEntry`/`DecisionEntry` alias regexes and phase/task patterns so the README I write parses cleanly.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/models/v1/body.py",
  "offset": 405,
  "limit": 140
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/models/v1/body.py</path>
<type>file</type>
<content>
405: 
406: class CurrentStatus(MarkdownSection3):
407:     """`### Current Status` -- free-form narrative of where things stand. Mandatory."""
408: 
409: 
410: class Blockers(MarkdownSection3):
411:     """`### Blockers` -- free-form list of open blockers. Optional."""
412: 
413: 
414: #: Matches a `{timestamp} — {title}` heading line, capturing the ISO8601
415: #: timestamp (named group `timestamp`) and the title (named group `title`).
416: #: Shared verbatim between `UpdateEntry` and `DecisionEntry` (identical
417: #: shape, see both classes' docstrings).
418: _ENTRY_HEADING_PATTERN = re.compile(
419:     r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})) — (?P<title>.+)$"
420: )
421: 
422: #: The `@alias` REGEX value shared verbatim by `UpdateEntry` and
423: #: `DecisionEntry` -- ISO8601 date + space + time + milliseconds + explicit
424: #: UTC offset (`+02:00`, `-05:00`) or `Z` for UTC.
425: _ENTRY_HEADING_ALIAS = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$"
426: 
427: 
428: @alias(value=_ENTRY_HEADING_ALIAS, type=AliasType.REGEX)
429: class UpdateEntry(MarkdownSection4):
430:     """`#### {timestamp} — {title}` under `### Updates` -- one update entry.
431: 
432:     The timestamp format is deliberately not the same format as frontmatter
433:     `created`/`updated` (a `datetime.isoformat(timespec="microseconds")`
434:     value, e.g. `2026-08-30T14:23:01.123456`) -- this format is scoped to
435:     `### Updates`/`### Decisions Made` entry headings only, hand/LLM-authored
436:     body content, not tool-generated frontmatter.
437: 
438:     Parameters
439:     ----------
440:     content:
441:         The lead paragraph right after the H4 heading -- this entry's own
442:         update text. Mandatory.
443:     timestamp:
444:         Computed. The entry's ISO8601 timestamp, verbatim from the heading.
445:         Never stored separately -- derived from the retained heading text.
446:     title:
447:         Computed. The entry's title (the heading text after `" — "`). Never
448:         stored separately -- derived from the retained heading text.
449:     """
450: 
451:     content: MarkdownParagraph = Field(
452:         description="The lead paragraph directly under the H4 heading -- this entry's own update text. Mandatory."
453:     )
454: 
455:     @computed_field  # type: ignore
456:     @property
457:     def timestamp(self) -> str:
458:         """The entry's ISO8601 timestamp carried by this heading, verbatim.
459: 
460:         Returns:
461:             The timestamp string parsed from the retained heading text.
462: 
463:         Raises:
464:             AssertionError: the retained heading text does not match this
465:                 class's declared `@alias` (unreachable via the engine:
466:                 `match_alias` already enforced it at parse time).
467:         """
468:         match = _ENTRY_HEADING_PATTERN.fullmatch(self.text)
469:         assert match, f"{type(self).__name__}: expected heading '{{timestamp}} — {{title}}', got {self.text!r}"
470:         result: str = match.group("timestamp")
471:         return result
472: 
473:     @computed_field  # type: ignore
474:     @property
475:     def title(self) -> str:
476:         """The entry's title carried by this heading (the heading text after `" — "`).
477: 
478:         Returns:
479:             The title parsed from the retained heading text.
480: 
481:         Raises:
482:             AssertionError: the retained heading text does not match this
483:                 class's declared `@alias` (unreachable via the engine:
484:                 `match_alias` already enforced it at parse time).
485:         """
486:         match = _ENTRY_HEADING_PATTERN.fullmatch(self.text)
487:         assert match, f"{type(self).__name__}: expected heading '{{timestamp}} — {{title}}', got {self.text!r}"
488:         result: str = match.group("title")
489:         return result
490: 
491: 
492: class Updates(MarkdownSection3WithComment):
493:     """`### Updates` -- a dynamic, newest-first list of ISO8601-timestamped `#### ` update entries. Mandatory.
494:     At least one entry. May be preceded by an explanatory HTML comment (e.g. an ordering hint).
495: 
496:     Parameters
497:     ----------
498:     comment:
499:         Optional explanatory HTML comment (`<!-- ... -->`), e.g.
500:         `<!-- Newest entry first -- prepend new entries directly below
501:         this comment. -->`. Inherited from `MarkdownSection3WithComment`.
502:     updates:
503:         The `#### {timestamp} — {title}` entries, in document order,
504:         newest-first (enforced, see `_validate_newest_first`). At least
505:         one entry.
506:     """
507: 
508:     updates: list[UpdateEntry] = Field(
509:         min_length=1,
510:         description="Dynamic collection of `#### {timestamp} — {title}` entries, in document order, "
511:         "newest-first. Must contain at least one entry.",
512:     )
513: 
514:     @model_validator(mode="after")
515:     def _validate_newest_first(self) -> Updates:
516:         """Reject entries that are not in newest-first order.
517: 
518:         Consecutive entries' parsed `datetime.fromisoformat(entry.timestamp)`
519:         values must be non-increasing (each entry's timestamp `<=` the
520:         previous entry's) -- extending the existing eager-computed-field-
521:         validation pattern (`tsk.models.v1.body.Task._validate_items_eagerly`)
522:         to a genuine cross-item ordering guarantee. Raises on the first
523:         out-of-order pair.
524:         """
525:         for earlier, later in zip(self.updates, self.updates[1:]):
526:             earlier_ts = datetime.fromisoformat(earlier.timestamp)
527:             later_ts = datetime.fromisoformat(later.timestamp)
528:             assert earlier_ts >= later_ts, (
529:                 f"Updates: entries must be newest-first; {earlier.timestamp!r} precedes {later.timestamp!r}"
530:             )
531:         return self
532: 
533: 
534: @alias(value=_ENTRY_HEADING_ALIAS, type=AliasType.REGEX)
535: class DecisionEntry(MarkdownSection4):
536:     """`#### {timestamp} — {title}` under `### Decisions Made` -- one decision entry.
537: 
538:     Identical shape to `UpdateEntry` (same alias regex, same `timestamp`/
539:     `title` computed-field extraction, same `content: MarkdownParagraph`) --
540:     a distinct class since it belongs to a semantically distinct section.
541: 
542:     Parameters
543:     ----------
544:     content:

(Showing lines 405-544 of 697. Use offset=545 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 91.3s)

_Thinking:_

Now I know the exact format. The UpdateEntry/DecisionEntry headings must match the following:
`^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$`

So: `YYYY-MM-DD HH:MM:SS.mmm` (3-digit milliseconds) + (`Z` or `+HH:MM`/`-HH:MM`) + `—` (space, em dash, space) + title.

But feat-33-vcr uses `#### 2026-08-31T16:26:00.000000 — ...` (T separator, 6-digit microseconds). This doesn't match the alias regex! So how did feat-33-vcr get parsed?

Wait. Let me reconsider. Maybe feat-33-vcr's README doesn't actually get parsed by the feat domain. Or maybe it gets skipped. Actually, AGENTS.md says there's no CI/pre-commit enforcement for `.specmgr/` contents. But `list_feat` and `get_feat` do parse it. If feat-33-vcr doesn't match, then `list_feat` should skip it (parse failures are silently skipped in `find_*_path`'s scan… no wait, that's for id lookup. `list_feat` iterates paths and parses each one).

Hmm, actually let me reconsider. Maybe the `Updates` section is optional and… no, `updates: list[UpdateEntry] = Field(min_length=1)` — it's required, at least one.

Wait, maybe I'm misreading feat-33-vcr's entries. Let me look again. What I saw earlier at line 669 was: `#### 2026-08-31T16:26:00.000000 — Merged current ...`. This is T separator + 6-digit microseconds. This doesn't match the alias.

But… hmm. This is a real contradiction. Let me actually test whether feat-33-vcr can be parsed. Actually, I shouldn't spend too much time on this. Key insight: **I must write the README so that it actually matches the alias regex**, i.e., use the space-separated `YYYY-MM-DD HH:MM:SS.mmmZ` format. That's the format the schema enforces, and the format the template uses. The fact that feat-33-vcr deviates from it is either (a) it can't actually be parsed and is silently skipped, or (b) I'm misreading it.

To make sure of the correct format, let me verify by parsing the template and checking whether feat-33-vcr can be parsed. Actually, the cleanest thing is: write my README in the template's format (which by construction matches the regex), and verify by parsing with `specmgr` or a quick Python script using `parse_feat`.

Let me reconsider: I want the README to be parseable so that `list_feat`/`get_feat`/`compact_history` all work on it. So I'll use the exact format the alias regex requires. Let me validate with a quick parse test after writing.

Actually, let me first verify that the template itself can be parsed (it should, since it's a packaged data file used by `get_feat_template` and validated). And check the Requirements/TaskList/Phase/Scope formats. Let me re-read the relevant parts of body.py (lines 55–405) to get the exact patterns for Requirements, AcceptanceCriteria, Scope, Dependencies, TaskList, Phase, and the H1.

What I know so far:

- H1: `^Feature: .+$` (Feature class, MarkdownSection1)
- Requirements: `^REQ-\d{3}: (?P<description>.+)$` (RequirementItem, MarkdownListItem — no checkbox)
- AcceptanceCriteria: `^ACC-\d{3}: (?P<description>.+)$` (AcceptanceCriterionItem, TaskItem — with checkbox `- [ ]`)
- TaskList phases: `^Phase \d+: .+$` (Phase, MarkdownSection4, `#### Phase N: title`)
- Tasks: need to check the TaskItem pattern. Let me check.
- Scope: `### Scope` with `#### Included` and `#### Explicitly Out Of Scope` (both required, MarkdownSection4)
- Dependencies: `### Dependencies` with `#### Depends On` and `#### Blocks` (optional)
- DesignNotes: `### Design Notes` (optional, free-form)
- RelatedDecisions: `### Related Decisions` (optional)

Let me read lines 55–405 to get the TaskItem pattern and confirm which sections are required vs. optional, and their order. The order matters, because "field declaration order in every composite class enforces the Markdown ordering."

Let me read that.

The entry-heading format is strict: `YYYY-MM-DD HH:MM:SS.mmmZ — title` (space separator, 3-digit millis, em dash). Let me read the rest of the body model (requirements/tasks/phases/section order) to nail every format before writing.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/models/v1/body.py",
  "limit": 350,
  "offset": 55
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/models/v1/body.py</path>
<type>file</type>
<content>
55: 
56: from ....models.md import (
57:     AliasType,
58:     MarkdownListItem,
59:     MarkdownParagraph,
60:     MarkdownSection1,
61:     MarkdownSection2,
62:     MarkdownSection3,
63:     MarkdownSection3WithComment,
64:     MarkdownSection4,
65:     alias,
66: )
67: from ....tsk.models.v1.task_item import TaskItem
68: 
69: 
70: class Overview(MarkdownSection3):
71:     """`### Overview` -- free-form prose describing what this feature is and
72:     why it exists. Mandatory."""
73: 
74: 
75: #: Matches a `REQ-NNN: {description}` list item's `.text`, capturing the
76: #: description (named group `description`). Mirrors `dec`'s
77: #: `_OPTION_HEADING_PATTERN`/`tsk`'s `TaskItem._MARKER_PATTERN` -- the value
78: #: is carried by the item's own text and extracted at access time, never
79: #: stored.
80: _REQUIREMENT_ITEM_PATTERN = re.compile(r"^REQ-\d{3}: (?P<description>.+)$")
81: 
82: 
83: class RequirementItem(MarkdownListItem):
84:     """`- REQ-NNN: {text}` -- one bullet-list requirement entry under `### Requirements`.
85: 
86:     A leaf `MarkdownListItem` subclass (no checkbox marker, unlike `TaskItem`):
87:     the requirement number and its description both live in the item's own
88:     text (e.g. `"REQ-001: The widget must render within 200ms."`), recovered
89:     by the `@computed_field` below.
90: 
91:     Parameters
92:     ----------
93:     description:
94:         Computed. This item's own text with the `REQ-NNN: ` prefix stripped.
95:         Raises `AssertionError` if `.text` does not match `REQ-\\d{3}: .+`.
96:     """
97: 
98:     @computed_field  # type: ignore
99:     @property
100:     def description(self) -> str:
101:         """This item's own description, with the `REQ-NNN: ` prefix stripped.
102: 
103:         Returns:
104:             The description text following the `REQ-NNN: ` prefix.
105: 
106:         Raises:
107:             AssertionError: `.text` does not match `^REQ-\\d{3}: .+$`.
108:         """
109:         match = _REQUIREMENT_ITEM_PATTERN.fullmatch(self.text)
110:         assert match, f"RequirementItem: expected 'REQ-NNN: <description>', got {self.text!r}"
111:         result: str = match.group("description")
112:         return result
113: 
114: 
115: class Requirements(MarkdownSection3):
116:     """`### Requirements` -- bullet list of `REQ-NNN: {text}` entries. Mandatory. At least one item.
117: 
118:     Parameters
119:     ----------
120:     items:
121:         The `REQ-NNN: {text}` entries, in document order. At least one item.
122:     """
123: 
124:     items: list[RequirementItem] = Field(
125:         min_length=1,
126:         description="Bullet list of `REQ-NNN: {text}` entries, in document order. Must contain at least one item.",
127:     )
128: 
129:     @model_validator(mode="after")
130:     def _validate_items_eagerly(self) -> Requirements:
131:         """Force every item's `.description` computed field to evaluate eagerly, not lazily.
132: 
133:         Mirrors `tsk.models.v1.body.Task._validate_items_eagerly`: without
134:         this, a malformed item (e.g. `"- Not a requirement"`) would parse
135:         silently and only raise, if ever, whenever something later happens
136:         to read `.description`.
137:         """
138:         for item in self.items:
139:             _ = item.description
140:         return self
141: 
142: 
143: #: Matches an `ACC-NNN: {description}` `TaskItem.description` value (already
144: #: stripped of its `- [ ]`/`- [x]` marker), capturing the description (named
145: #: group `description`).
146: _ACCEPTANCE_CRITERION_ITEM_PATTERN = re.compile(r"^ACC-\d{3}: (?P<description>.+)$")
147: 
148: 
149: class AcceptanceCriterionItem(TaskItem):
150:     """`- [ ] ACC-NNN: {text}` -- one checklist acceptance-criterion entry under `### Acceptance Criteria`.
151: 
152:     Reuses `tsk.TaskItem`'s `checked`/`description`-from-checkbox split
153:     as-is, adding one more computed field re-matching the `ACC-NNN: ` prefix
154:     against the inherited `description`.
155: 
156:     Parameters
157:     ----------
158:     criterion_description:
159:         Computed. `.description` (already checkbox-stripped) with the
160:         `ACC-NNN: ` prefix further stripped. Raises `AssertionError` if
161:         `.description` does not match `ACC-\\d{3}: .+`.
162:     """
163: 
164:     @computed_field  # type: ignore
165:     @property
166:     def criterion_description(self) -> str:
167:         """This item's own description, with the `ACC-NNN: ` prefix further stripped.
168: 
169:         Returns:
170:             The description text following the `ACC-NNN: ` prefix.
171: 
172:         Raises:
173:             AssertionError: `.description` does not match `^ACC-\\d{3}: .+$`.
174:         """
175:         match = _ACCEPTANCE_CRITERION_ITEM_PATTERN.fullmatch(self.description)
176:         assert match, f"AcceptanceCriterionItem: expected 'ACC-NNN: <description>', got {self.description!r}"
177:         result: str = match.group("description")
178:         return result
179: 
180: 
181: class AcceptanceCriteria(MarkdownSection3):
182:     """`### Acceptance Criteria` -- checklist of `- [ ]/[x] ACC-NNN: {text}` entries. Mandatory. At least one item.
183: 
184:     Parameters
185:     ----------
186:     items:
187:         The `ACC-NNN: {text}` checklist entries, in document order. At
188:         least one item.
189:     """
190: 
191:     items: list[AcceptanceCriterionItem] = Field(
192:         min_length=1,
193:         description="Checklist of `- [ ]/[x] ACC-NNN: {text}` entries, in document order. "
194:         "Must contain at least one item.",
195:     )
196: 
197:     @model_validator(mode="after")
198:     def _validate_items_eagerly(self) -> AcceptanceCriteria:
199:         """Force every item's `.checked`/`.criterion_description` computed fields to evaluate eagerly.
200: 
201:         Mirrors `tsk.models.v1.body.Task._validate_items_eagerly` and
202:         `Requirements._validate_items_eagerly` above.
203:         """
204:         for item in self.items:
205:             _ = item.checked
206:             _ = item.criterion_description
207:         return self
208: 
209: 
210: class Included(MarkdownSection4):
211:     """`#### Included` under `### Scope` -- free-form bullet list of what this feature covers. Mandatory."""
212: 
213: 
214: class ExplicitlyOutOfScope(MarkdownSection4):
215:     """`#### Explicitly Out Of Scope` under `### Scope` -- free-form bullet list of what this feature
216:     deliberately does not cover. Mandatory."""
217: 
218: 
219: class Scope(MarkdownSection3):
220:     """`### Scope` -- container for the two mandatory Included/Explicitly Out Of Scope leaves. No own text.
221: 
222:     Parameters
223:     ----------
224:     included:
225:         `#### Included`. Mandatory.
226:     explicitly_out_of_scope:
227:         `#### Explicitly Out Of Scope`. Mandatory.
228:     """
229: 
230:     included: Included = Field(description="`#### Included` section. Mandatory.")
231:     explicitly_out_of_scope: ExplicitlyOutOfScope = Field(
232:         description="`#### Explicitly Out Of Scope` section. Mandatory."
233:     )
234: 
235: 
236: class DependsOn(MarkdownSection4):
237:     """`#### Depends On` under `### Dependencies` -- free-form list of things this feature needs first.
238:     Optional."""
239: 
240: 
241: class Blocks(MarkdownSection4):
242:     """`#### Blocks` under `### Dependencies` -- free-form list of things that cannot start until this
243:     feature ships. Optional."""
244: 
245: 
246: class Dependencies(MarkdownSection3):
247:     """`### Dependencies` -- container for the two independently optional Depends On/Blocks leaves. No own text.
248: 
249:     Optional as a whole; a feature may have no dependencies and block
250:     nothing else.
251: 
252:     Parameters
253:     ----------
254:     depends_on:
255:         `#### Depends On`. Optional.
256:     blocks:
257:         `#### Blocks`. Optional.
258:     """
259: 
260:     depends_on: DependsOn | None = Field(default=None, description="`#### Depends On` section. Optional.")
261:     blocks: Blocks | None = Field(default=None, description="`#### Blocks` section. Optional.")
262: 
263: 
264: class DesignNotes(MarkdownSection3):
265:     """`### Design Notes` -- free-form design rationale, schema sketches, etc. Optional."""
266: 
267: 
268: class RelatedDecisions(MarkdownSection3):
269:     """`### Related Decisions` -- free-form cross-reference list; entries may reference either an ADR id or a
270:     `dec` id (or any other decision record). Optional."""
271: 
272: 
273: #: Matches a `Phase N: {title}` heading line, capturing the phase number
274: #: (named group `number`) and its title (named group `title`). Mirrors
275: #: `dec`'s `_OPTION_HEADING_PATTERN`.
276: _PHASE_HEADING_PATTERN = re.compile(r"^Phase (?P<number>\d+): (?P<title>.+)$")
277: 
278: 
279: @alias(value=r"^Phase \d+: .+$", type=AliasType.REGEX)
280: class Phase(MarkdownSection4):
281:     """`#### Phase N: {title}` under `### Task List` -- one phase's own flat checklist.
282: 
283:     Unpadded phase numbers (matching this very plan's own "Phase 0".."Phase
284:     5" headings). Per-item metadata (`depends on:`/`status:`/`ETA`) stays
285:     unparsed free text inside each item's own description.
286: 
287:     Parameters
288:     ----------
289:     items:
290:         The flat `- [ ] .../- [x] ...` checklist for this phase, reusing
291:         `tsk.models.v1.task_item.TaskItem` as-is. At least one item.
292:     number:
293:         Computed. The phase's number (e.g. `1` for `#### Phase 1: X`).
294:         Never stored separately -- derived from the retained heading text.
295:     title:
296:         Computed. The phase's title (the heading text after `": "`). Never
297:         stored separately -- derived from the retained heading text.
298:     """
299: 
300:     items: list[TaskItem] = Field(
301:         min_length=1,
302:         description="The flat `- [ ] .../- [x] ...` checklist for this phase, in document order. "
303:         "Must contain at least one item.",
304:     )
305: 
306:     @computed_field  # type: ignore
307:     @property
308:     def number(self) -> int:
309:         """The phase's number carried by this heading (e.g. `1` for `#### Phase 1: X`).
310: 
311:         Returns:
312:             The integer number parsed from the retained heading text.
313: 
314:         Raises:
315:             AssertionError: the retained heading text does not match
316:                 `Phase`'s declared `@alias` (unreachable via the engine:
317:                 `match_alias` already enforced it at parse time).
318:         """
319:         match = _PHASE_HEADING_PATTERN.fullmatch(self.text)
320:         assert match, f"Phase: expected heading 'Phase N: <title>', got {self.text!r}"
321:         result: int = int(match.group("number"))
322:         return result
323: 
324:     @computed_field  # type: ignore
325:     @property
326:     def title(self) -> str:
327:         """The phase's title carried by this heading (e.g. `X` for `#### Phase 1: X`).
328: 
329:         Returns:
330:             The title parsed from the retained heading text (the heading
331:             text after `": "`, colons inside the title included).
332: 
333:         Raises:
334:             AssertionError: the retained heading text does not match
335:                 `Phase`'s declared `@alias` (unreachable via the engine:
336:                 `match_alias` already enforced it at parse time).
337:         """
338:         match = _PHASE_HEADING_PATTERN.fullmatch(self.text)
339:         assert match, f"Phase: expected heading 'Phase N: <title>', got {self.text!r}"
340:         result: str = match.group("title")
341:         return result
342: 
343:     @model_validator(mode="after")
344:     def _validate_items_eagerly(self) -> Phase:
345:         """Force every item's `.checked` computed field to evaluate eagerly, not lazily.
346: 
347:         Mirrors `tsk.models.v1.body.Task._validate_items_eagerly`.
348:         """
349:         for item in self.items:
350:             _ = item.checked
351:         return self
352: 
353: 
354: class TaskList(MarkdownSection3):
355:     """`### Task List` -- container for the `#### Phase N: ...` entries. No own text. Mandatory. At least
356:     one phase.
357: 
358:     Parameters
359:     ----------
360:     phases:
361:         The `#### Phase N: {title}` entries, in document order. At least
362:         one phase.
363:     """
364: 
365:     phases: list[Phase] = Field(
366:         min_length=1,
367:         description="The `#### Phase N: {title}` entries, in document order. Must contain at least one phase.",
368:     )
369: 
370: 
371: class Plan(MarkdownSection2):
372:     """`## Plan` -- container for the feature's plan-side sections. No own text. Mandatory.
373: 
374:     Parameters
375:     ----------
376:     overview:
377:         `### Overview`. Mandatory.
378:     requirements:
379:         `### Requirements`. Mandatory.
380:     acceptance_criteria:
381:         `### Acceptance Criteria`. Mandatory.
382:     scope:
383:         `### Scope`. Mandatory.
384:     dependencies:
385:         `### Dependencies`. Optional.
386:     design_notes:
387:         `### Design Notes`. Optional.
388:     related_decisions:
389:         `### Related Decisions`. Optional.
390:     task_list:
391:         `### Task List`. Mandatory.
392:     """
393: 
394:     overview: Overview = Field(description="`### Overview` section. Mandatory.")
395:     requirements: Requirements = Field(description="`### Requirements` section. Mandatory.")
396:     acceptance_criteria: AcceptanceCriteria = Field(description="`### Acceptance Criteria` section. Mandatory.")
397:     scope: Scope = Field(description="`### Scope` section. Mandatory.")
398:     dependencies: Dependencies | None = Field(default=None, description="`### Dependencies` section. Optional.")
399:     design_notes: DesignNotes | None = Field(default=None, description="`### Design Notes` section. Optional.")
400:     related_decisions: RelatedDecisions | None = Field(
401:         default=None, description="`### Related Decisions` section. Optional."
402:     )
403:     task_list: TaskList = Field(description="`### Task List` section. Mandatory.")
404: 

(Showing lines 55-404 of 697. Use offset=405 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 53.8s)

_Thinking:_

Now I have all the details of the schema. Let me also check the order of the `Progress` section and the `Feature` H1 container (lines 640–697), and confirm the mandatory/optional fields of `Progress` and the field order of the H1.

From the grep earlier:

- 640: `@alias(value="Related PRs / Commits", ...)` RelatedPrsCommits
- 649: MoreInformation
- 653: class Progress(MarkdownSection2)
- 684: `@alias(value="^Feature: .+$", ...)` class Feature(MarkdownSection1)

Let me read lines 653–697 to get the field order and mandatory/optional of Progress.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/models/v1/body.py",
  "limit": 70,
  "offset": 628
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/src/biz/dfch/specmgr/feat/models/v1/body.py</path>
<type>file</type>
<content>
628:         Mirrors `Updates._validate_newest_first` exactly -- see its
629:         docstring for the full rationale.
630:         """
631:         for earlier, later in zip(self.decisions, self.decisions[1:]):
632:             earlier_ts = datetime.fromisoformat(earlier.timestamp)
633:             later_ts = datetime.fromisoformat(later.timestamp)
634:             assert earlier_ts >= later_ts, (
635:                 f"DecisionsMade: entries must be newest-first; {earlier.timestamp!r} precedes {later.timestamp!r}"
636:             )
637:         return self
638: 
639: 
640: @alias(value="Related PRs / Commits", type=AliasType.LITERAL)
641: class RelatedPrsCommits(MarkdownSection3):
642:     """`### Related PRs / Commits` -- free-form list of related pull requests/commits. Optional.
643: 
644:     The slash/mixed-case wording breaks the plain `SPACE_SEPARATED`
645:     convention, so the heading is pinned `LITERAL`.
646:     """
647: 
648: 
649: class MoreInformation(MarkdownSection3):
650:     """`### More Information` -- free-form optional supplementary text, no fixed format. Optional."""
651: 
652: 
653: class Progress(MarkdownSection2):
654:     """`## Progress` -- container for the feature's progress-side sections. No own text. Mandatory.
655: 
656:     Parameters
657:     ----------
658:     current_status:
659:         `### Current Status`. Mandatory.
660:     blockers:
661:         `### Blockers`. Optional.
662:     updates:
663:         `### Updates`. Mandatory.
664:     decisions_made:
665:         `### Decisions Made`. Optional.
666:     related_prs_commits:
667:         `### Related PRs / Commits`. Optional.
668:     more_information:
669:         `### More Information`. Optional.
670:     """
671: 
672:     current_status: CurrentStatus = Field(description="`### Current Status` section. Mandatory.")
673:     blockers: Blockers | None = Field(default=None, description="`### Blockers` section. Optional.")
674:     updates: Updates = Field(description="`### Updates` section. Mandatory.")
675:     decisions_made: DecisionsMade | None = Field(default=None, description="`### Decisions Made` section. Optional.")
676:     related_prs_commits: RelatedPrsCommits | None = Field(
677:         default=None, description="`### Related PRs / Commits` section. Optional."
678:     )
679:     more_information: MoreInformation | None = Field(
680:         default=None, description="`### More Information` section. Optional."
681:     )
682: 
683: 
684: @alias(value="^Feature: .+$", type=AliasType.REGEX)
685: class Feature(MarkdownSection1):
686:     """The `feat` body: a single H1 section (`# Feature: {title}`) with the fields below.
687: 
688:     Parameters
689:     ----------
690:     plan:
691:         `## Plan`. Mandatory.
692:     progress:
693:         `## Progress`. Mandatory.
694:     """
695: 
696:     plan: Plan = Field(description="`## Plan` section. Mandatory.")
697:     progress: Progress = Field(description="`## Progress` section. Mandatory.")

(End of file - total 697 lines)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 212.7s)

_Thinking:_

Now I have a complete grasp of the entire feat schema. Let me write the README following the exact format:

**Frontmatter:**

```yaml
---
created: 2026-08-31 15:37:40.000000   (actually free-form string; use a timestamp)
id: feat-36-delete
status: planning
type: feat
updated: 2026-08-31 15:37:40.000000
version: 1.0.0
---
```

Wait, feat-33-vcr used `created: 2026-08-31 07:25:24.241609` (space-separated isoformat microseconds). The template used `created: 2026-08-30` (date only). Both are free-form strings. I'll go with the full timestamp to match the convention of actual features. For created/updated I'll use `2026-08-31 15:37:40` — hmm, let me be consistent. I'll go with a format close to `datetime.now().isoformat(timespec="microseconds")`. I'll use `2026-08-31 15:37:40.000000`. Actually, frontmatter created/updated is a free-form string, so anything works. I'll use the microsecond isoformat style like feat-33-vcr.

Wait, but there's a subtle point: the frontmatter `id` must match the folder name (`feat-36-delete`). Yes. And `type: feat`. And `version: 1.0.0`. And `status: planning`.

**Body structure (in exact field order):**

```
# Feature: <title>

## Plan

### Overview
<free-form>

### Requirements
- REQ-001: ...
- REQ-002: ...
...

### Acceptance Criteria
- [ ] ACC-001: ...
- [ ] ACC-002: ...
...

### Scope

#### Included
- ...

#### Explicitly Out Of Scope
- ...

### Dependencies

#### Depends On
- ...

#### Blocks
- ...

### Design Notes
<free-form, may include code blocks>

### Related Decisions
- ...

### Task List

#### Phase 0: ...
- [ ] Task 0.1: ...

#### Phase 1: ...
- [ ] Task 1.1: ...
...

## Progress

### Current Status
**As of ...**: ...

### Blockers
- None currently.   (optional section; can omit, or list none)

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-31 15:37:40.000Z — Created
<lead paragraph>

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-31 15:37:40.000Z — <decision title>
<lead paragraph>

### Related PRs / Commits
- ...

### More Information
<optional>
```

Key format constraints I have to respect:

01. H1: `# Feature: <title>` — title is anything.

02. Requirements items: `- REQ-NNN: <desc>` — NNN is exactly 3 digits. No checkbox.

03. ACC items: `- [ ] ACC-NNN: <desc>` — 3 digits, unchecked checkbox (since we're in planning).

04. Scope: `#### Included` and `#### Explicitly Out Of Scope` are both mandatory. Free-form bullet lists.

05. Dependencies: `#### Depends On` / `#### Blocks` — optional; I'll include both.

06. Phase headings: `#### Phase N: <title>` — N is an un-padded number.

07. Task items: `- [ ] Task N.M: <desc>` — these are TaskItems (checkbox). TaskItem pattern — let me check. tsk's TaskItem: `_MARKER_PATTERN`. A task item is `- [ ] <desc>` or `- [x] <desc>`, and desc is free-form. So `Task 0.1: ...` is just free-form desc after the checkbox. Good. But note: TaskItem's desc — is there a pattern constraint? In tsk, TaskItem splits checked/description from the checkbox. The description is free-form. So `Task 0.1: do X — depends on: none — status: not-started` is fine as free text. Good.

    Wait, I need to double-check that TaskItem doesn't require a specific format. Let me recall: `tsk.models.v1.task_item.TaskItem` has `checked: bool` and `description: str` computed fields from `- [ ]`/`- [x]`. The description is everything after the marker, free-form. Good.

08. Update/decision entry headings: `#### YYYY-MM-DD HH:MM:SS.mmmZ — <title>` (space-separated, 3-digit millis, Z or ±HH:MM offset, em dash). Must be newest-first.

09. `### Updates` is mandatory and must have one or more entries. `### Decisions Made` is optional.

10. Section order is enforced: Plan must contain overview, requirements, acceptance_criteria, scope, [dependencies], [design_notes], [related_decisions], task_list in that order. Progress must contain current_status, [blockers], updates, [decisions_made], [related_prs_commits], [more_information].

Now, one concern: the `### Blockers` section. It's optional. The template has it with "- A short description of an open blocker. Optional." I could include `### Blockers` with a "None currently." bullet, or omit it. Since it's optional and I don't want to fabricate a blocker, I'll include it with a clear "None." Actually the feat-33 README has `### Blockers` with "- None currently." I'll do the same. But wait — is Blockers' content a free-form MarkdownSection3? Yes, `class Blockers(MarkdownSection3)` — free-form. So a bullet is fine.

Actually, let me reconsider: to minimize parse risk, I could also omit the optional Blockers section. But including "None currently." matches the convention. I'll include it.

Next, let me think about the content. This is the design document. Let me write comprehensive, precise content that the Phase-Orchestrator can execute.

Let me draft the requirements (REQ-001..008), acceptance criteria (ACC-001..008), scope, dependencies, design notes (with concrete code sketches), related decisions (new ADR), task list (phases 0-5), and progress.

Let me be careful with the timestamp format for Updates/Decisions entries. Use `2026-08-31 15:37:40.000Z`. That matches the alias: `\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|...)`. `15:37:40.000Z` — yes: date `2026-08-31`, space, time `15:37:40`, `.000` (3 digits), `Z`.

Now let me write the README. I'll make the Design Notes section detailed with:

- Reusable `_path_safety.py` API (the key change).
- Shape of `delete.py` with adapter sketch.
- Per-domain adapter table.
- Locking, error handling, return value.
- feat special case (rmtree).
- Injection safety explanation.
- ADR content outline.
- Documentation update list (AGENTS.md, server.py, CHANGELOG).
- Test plan.

Let me also reconsider the module naming for the reusable safety. The user said "the path and file validation logic that should prevent injection is reusable, and can be used later by get and update tools too." So the module should be generic. Name it `general/tools/_path_safety.py`. Functions:

- `assert_no_traversal(id_: str) -> None`
- `assert_uuid(id_: str) -> None`
- `assert_feat_id(id_: str) -> None`
- `validate_id(type_: str, id_: str) -> None`
- `assert_within(base_dir: Path, candidate: Path) -> None`

That's clean and reusable. get/update can call `assert_no_traversal` + the format assert + `assert_within` later.

Now let me write it. I'll create the directory and write the file.

Actually, let me reconsider the frontmatter created/updated format once more. To be safe and consistent with feat-33-vcr (an actual done feature), I'll use:

```
created: 2026-08-31 15:37:40.000000
updated: 2026-08-31 15:37:40.000000
```

These are free-form strings so any format parses. Good.

Now, one more important consideration: the H1 title. `# Feature: Replace per-domain delete stubs with a generic type-dispatched delete tool`. Good.

Let me write the full README now.

Let me think about what ACC items map to REQ items:

- ACC-001 verifies REQ-001 (the generic delete tool exists, dispatched over 11 domains, returns path as str)
- ACC-002 verifies REQ-002 (the 11 stubs removed)
- ACC-003 verifies REQ-003 (reusable \_path_safety module + wired into delete; unit tested)
- ACC-004 verifies REQ-004 (locking — each adapter acquires the domain lock)
- ACC-005 verifies REQ-005 (error handling — not-found → XNotFoundError, invalid id → ValueError, I/O → DeleteError)
- ACC-006 verifies REQ-006 (mechanics — 10 unlink, feat rmtree)
- ACC-007 verifies REQ-007 (ADR + AGENTS.md + server.py + CHANGELOG + docs regen)
- ACC-008 verifies REQ-008 (tests — test_delete.py over 11 types + test\_\_path_safety.py; stub tests removed)

Good.

Next, the task list phases:

- Phase 0: Worktree and feature plan (this is mostly done — the README authoring). Actually Phase 0 is "design and plan authoring" which is what I'm doing now. Mark Task 0.1 (worktree + branch) as done, Task 0.2 (README authoring) as done/in-progress. But wait — the user said "you are the designer. So you do not implement." And the Phase-Orchestrator does the implementation. Is Phase 0 (worktree + README) done by me (designer), or by the orchestrator?

Re-reading: "1: implementation will need a separate agent (Phase-Orchestrator). You are the designer. So you do not implement." And "as soon as you enter build mode, create the git worktree branch and write the plan."

So: I (designer, in build mode) create the worktree branch and write the plan (README). That's Phase 0. Then Phase-Orchestrator (separate agent) does Phase 1-5 (implementation). So in the task list, Phase 0 tasks are what I do now (mark done once complete), and Phase 1-5 are for the orchestrator (mark not-started).

But there's a subtlety: should Phase 0 in the README be marked done? The worktree is created and I'm writing the README. So Task 0.1 (worktree) = done, Task 0.2 (README authoring) = done (once I finish writing). I'll mark them done with dates. Actually, since I'm writing this now, I'll mark Task 0.1 done and Task 0.2 done (this README is the deliverable). And I'll note in Current Status that Phase 0 is complete, ready for Phase-Orchestrator.

Hmm, but let me reconsider — maybe Phase 0 should be presented as a "setup" that's complete. I'll structure it as:

- Phase 0: Worktree, branch, and design plan (done — by designer)
  - Task 0.1: Create worktree + branch feat-36-delete from dev — done
  - Task 0.2: Author this feature README (design) — done
- Phase 1: Reusable path-safety module (orchestrator)
  - Task 1.1: general/tools/\_path_safety.py
  - Task 1.2: tests/general/tools/test\_\_path_safety.py
- Phase 2: The generic delete tool (orchestrator)
  - Task 2.1: general/tools/delete.py (11 adapters + dispatch + tool)
  - Task 2.2: tests/general/tools/test_delete.py
- Phase 3: Retire the 11 stubs (orchestrator)
  - Task 3.1: Delete the 11 delete\_<d>.py files
  - Task 3.2: Update the 11 <d>/tools/__init__.py (imports/__all__/docstrings)
  - Task 3.3: Delete the 11 test_delete\_<d>.py stub tests
- Phase 4: Decisions and docs (orchestrator)
  - Task 4.1: New ADR (create_adr + adr-toc)
  - Task 4.2: AGENTS.md updates
  - Task 4.3: server.py docstring updates
  - Task 4.4: CHANGELOG [Unreleased]
  - Task 4.5: docs regeneration (specmgr docs, mcp-docs)
- Phase 5: Quality gate and sign-off (orchestrator)
  - Task 5.1: ruff format/check, vulture, full unittest, pylint
  - Task 5.2: ACC sign-off + README progress update

Good. Now let me write it all out.

Let me be careful: in Phase 3, I said "delete the 11 test_delete\_<d>.py". Let me verify that all 11 domains have test_delete\_<d>.py. From the earlier grep, the ones with test files were: dec, feat, gol, prb, qa, req, rsk, sop, tsk, uc, vcr. That's 11. Good. (qa had test_delete_qa.py, and I saw test_integration.py too.) Let me confirm the full list of stub test files.

Actually, from the earlier grep output, the test files are:

- tests/dec/tools/test_delete_dec.py
- tests/feat/tools/test_delete_feat.py
- tests/gol/tools/test_delete_gol.py
- tests/prb/tools/test_delete_prb.py
- tests/qa/tools/test_delete_qa.py
- tests/req/tools/test_delete_req.py
- tests/rsk/tools/test_delete_rsk.py
- tests/sop/tools/test_delete_sop.py
- tests/tsk/tools/test_delete_tsk.py
- tests/uc/tools/test_delete_uc.py
- tests/vcr/tools/test_delete_vcr.py

11 total. Good.

Now, one more: do I need to worry about whether the README I write can be parsed by the feat model? Let me validate after writing using the feat parser. I can write a quick Python check. But I need the venv. Let me run `uv sync` in the worktree first (that was in the plan). Actually, for validating the README, I need `parse_feat`. Let me run `uv sync --all-extras --frozen` in the worktree, then run a quick parse check.

Wait — `uv sync` creates a `.venv` in the worktree. That's fine. But it might take time and network. Let me do it since I need it for validation. Actually, I can validate the README parsing without a full sync if the main checkout already has a venv with the package installed. The main checkout `/home/user/src/biz.dfch.SpecMgr` should have a `.venv` (since it's the dev environment). I can use the main venv's python to import `biz.dfch.specmgr.feat.models.v1.parse_feat` and parse the README in the worktree. Since it's the same code (dev and feat-36-delete are the same commit 6d6bf2f), that will work.

Let me check if the main checkout has a .venv.

Actually, simpler: use `uv run` in the main checkout, or just use the python in the main .venv. Let me first check for .venv.

Let me proceed:

1. Create the directory `.specmgr/feat/feat-36-delete/` in the worktree.
2. Write the README.
3. Validate parsing using the main checkout's venv (or the worktree's).

Let me check the main venv and create the directory.

Actually, I'll write the file first, then validate. Let me create the directory and write.

Let me get the current timestamp precisely for the frontmatter and update entries. It was `2026-08-31T15:37:40Z`. I'll use `2026-08-31 15:37:40.000000` for frontmatter created/updated, and `2026-08-31 15:37:40.000Z` for update/decision entry headings.

Now let me write the README. It's going to be long. Let me structure it carefully.

I need to be careful about the em dash in update entry headings: `—` (space, U+2014 em dash, space). Let me use that.

Also, the HTML comment in Updates/Decisions: `<!-- Newest entry first -- prepend new entries directly below this comment. -->`. I'll include it.

Now let me write it.

One more reconsideration on REQ-003 wording for reusability: "a reusable `general/tools/_path_safety.py` ... wired only into `delete` in this feature; designed so that `get_<d>`/`update`/`set_status` can adopt it later without rework."

And in Design Notes, I'll spell out the reusability contract.

Now let me write the file.

Schema is fully mapped. Now I'll create the feature folder and author the design README in the worktree.

**Tool: bash**

**Input:**

```json
{
  "command": "mkdir -p /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete && echo \"dir created\" && ls -d /home/user/src/biz.dfch.SpecMgr/.venv 2>/dev/null && echo \"main venv exists\" || echo \"no main venv\""
}
```

**Output:**

```
dir created
/home/user/src/biz.dfch.SpecMgr/.venv
main venv exists

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 427.2s)

_Thinking:_

The main venv exists at /home/user/src/biz.dfch.SpecMgr/.venv. We can use that Python to verify parsing of the README (same commit). Alright, let's write the README.

Okay, now let's create the complete README content.

The main checkout has a `.venv` I can reuse to validate the README parses (same commit). Now writing the design README.

**Tool: write**

**Input:**

````json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md",
  "content": "---\ncreated: 2026-08-31 15:37:40.000000\nid: feat-36-delete\nstatus: planning\ntype: feat\nupdated: 2026-08-31 15:37:40.000000\nversion: 1.0.0\n---\n\n# Feature: Replace per-domain delete stubs with a generic type-dispatched delete tool\n\n## Plan\n\n### Overview\n\nEvery document domain except ADR currently ships an unimplemented `delete_<domain>`\nMCP tool (a registered stub that always raises `NotImplementedError`). This feature\nreplaces those eleven near-duplicate stubs with a single generic, type-dispatched\n`delete(id, type)` tool in `general/tools/delete.py` — the exact analog of the\nexisting generic `update` and `set_status` tools (ADR\n36905d5b-8057-4294-8665-c7eed5534db0). The new tool dispatches on an explicit\n`type` parameter (one of the eleven whole-body domains `req`/`uc`/`tsk`/`qa`/`prb`/\n`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`; **ADR is deliberately excluded**) to a private\nper-domain adapter that resolves the document, takes the domain's own lock, and hard-\ndeletes it from disk, returning the deleted path as a `str`.\n\nThe feature's second, load-bearing contribution is a **new, reusable path-safety\nmodule** (`general/tools/_path_safety.py`) that prevents path-injection through the\n`type` or `id` inputs and confines resolved paths to their base directory. No such\nguard exists anywhere in the codebase today. It is wired into `delete` in this\nfeature, but is designed so the `get_<d>`, `update`, and `set_status` tools can adopt\nit later with zero rework (they are **not** modified here). The convention \"every\ndomain implements a `delete` adapter in the generic tool, never a per-domain\n`delete_<d>` tool\" is recorded in a new ADR and propagated to `AGENTS.md`, the\n`server.py` docstring, and `CHANGELOG.md`.\n\nTracked by GitHub issue #36. Branch/worktree: `feat-36-delete`.\n\n### Requirements\n\n- REQ-001: Add a generic `@mcp.tool(name=\"delete\")` in `general/tools/delete.py` with signature `def delete(id: str, type: Literal[\"req\",\"uc\",\"tsk\",\"qa\",\"prb\",\"gol\",\"rsk\",\"dec\",\"sop\",\"feat\",\"vcr\"]) -> str`; eleven private adapters `_delete_<d>(id_) -> str`; a shared `_ADAPTERS: dict[str, Callable[[str], str]]` dispatch table — mirroring `set_status.py`'s structure. On success it returns the deleted path as a `str` (the file path for the ten flat domains, the folder path for `feat`).\n- REQ-002: Remove all eleven existing `delete_<domain>` stub tools: the eleven `src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` files, their `from .delete_<d> import delete_<d>` / `__all__` / module-docstring references in each `<d>/tools/__init__.py`, and the eleven `tests/<d>/tools/test_delete_<d>.py` stub test files.\n- REQ-003: Add a **reusable** path-safety module `general/tools/_path_safety.py` providing `assert_no_traversal(id_)`, `assert_uuid(id_)`, `assert_feat_id(id_)`, `validate_id(type_, id_)`, and `assert_within(base_dir, candidate)` (all raising `ValueError` with a meaningful message). It must prevent path-injection via `type` or `id`, and it must be callable unchanged by the `get_<d>`, `update`, and `set_status` tools in the future. This feature wires it into `delete` only; it does not modify `get`/`update`/`set_status`.\n- REQ-004: Locking — each adapter wraps its resolve-then-delete sequence in the domain's existing `<d>_lock(id_)` context manager (the same lock `update`/`set_status` already use), so a concurrent same-id mutation cannot interleave with the delete.\n- REQ-005: Graceful error handling — a missing document raises the domain's own `XNotFoundError` (unchanged); an invalid `id` (non-str, traversal character, or wrong format for the type) raises `ValueError` before any filesystem access; an I/O failure during the actual `unlink`/`rmtree` (`OSError`/`PermissionError`/race) is caught and re-raised as a new `DeleteError` (defined in `delete.py`, subclassing `OSError`) carrying the path and the underlying cause.\n- REQ-006: Delete mechanics — the ten flat-file domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`vcr`) remove the single `*.md` file via `Path.unlink()`; `feat` (folder-per-document, ADR 8cf940c5) removes the entire `<base>/<id>/` folder via `shutil.rmtree(folder)`, deleting `README.md`, any `history.md`, and any session transcripts in that folder.\n- REQ-007: Record and propagate the decision — create a new ADR titled \"Replace domain-specific delete tools with a generic type-dispatched delete tool\" (via the `create_adr` MCP tool, then `specmgr adr-toc`); update `AGENTS.md` (each of the eleven per-domain Status bullets drops the `delete_<d> stub` mention and the \"Still genuinely missing\" `delete_*` stubs bullet is removed/rewritten; the `general/` bullet gains the `delete` tool and a note that all domains now implement a `delete` adapter there); update `server.py`'s module docstring (the authoritative tool list — remove the eleven `delete_<d>` stub mentions, add `delete` to the General tools paragraph); add a `CHANGELOG.md` `[Unreleased]` breaking-change entry; regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`).\n- REQ-008: Tests — add `tests/general/tools/test_delete.py` (parameterized over all eleven types: seed a real persisted document per type, then assert delete succeeds, returns the right path, the file/folder is gone, and a subsequent `get_<d>`/`load_by_id` raises the domain `XNotFoundError`; assert every path-injection attempt raises `ValueError` before any filesystem access; assert an unknown id raises the domain `XNotFoundError`; assert an I/O failure raises `DeleteError`; assert the domain lock is acquired) and `tests/general/tools/test__path_safety.py` (unit tests for every `_path_safety` function, including the UUID and feat-format regexes, the traversal-character rejections, and the containment check).\n\n### Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — `general/tools/delete.py` exists and registers `@mcp.tool(name=\"delete\")` with the eleven-value `type` Literal; it dispatches through an `_ADAPTERS` table to eleven private `_delete_<d>` adapters; a live call `delete(id, type)` on a seeded document removes it and returns the deleted path as a `str`; `docs/MCP.md` (regenerated) lists exactly one `delete` tool and no `delete_<d>` tools.\n- [ ] ACC-002: Verifies REQ-002 — the eleven `delete_<d>.py` source files, their `__init__.py` imports/`__all__`/docstring references, and the eleven `test_delete_<d>.py` files are all gone (`git status`/`grep -r \"delete_<d>\"` over `src/` and `tests/` returns nothing for a per-domain delete tool); `import biz.dfch.specmgr.<d>.tools` succeeds for every domain.\n- [ ] ACC-003: Verifies REQ-003 — `general/tools/_path_safety.py` exposes `assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, and `assert_within`; `tests/general/tools/test__path_safety.py` passes; the functions are pure (no filesystem side effects) and importable by `get_<d>`/`update`/`set_status` without modification (i.e. no delete-specific coupling).\n- [ ] ACC-004: Verifies REQ-004 — each of the eleven adapters acquires its domain's `<d>_lock(id_)` around the resolve-then-delete sequence (verified by a test that mocks/spies the lock, or a concurrency test showing a same-id `update` and `delete` do not interleave).\n- [ ] ACC-005: Verifies REQ-005 — for a seeded document, `delete` with an unknown id raises that domain's `XNotFoundError`; with an injected id (`../x`, `a/b`, `a\\b`, `..`, a non-UUID string for a UUID type, a non-`feat-NNN-slug` for `feat`) it raises `ValueError` and leaves the filesystem untouched; with a mocked `unlink`/`rmtree` that raises `OSError` it raises `DeleteError` whose message names the path.\n- [ ] ACC-006: Verifies REQ-006 — for the ten flat domains the `*.md` file is removed and its directory is left intact; for `feat` the whole `<base>/<id>/` folder (including a seeded `history.md`) is removed.\n- [ ] ACC-007: Verifies REQ-007 — a new accepted ADR exists in `docs/adr/` (listed in the regenerated `docs/adr/README.md`); `AGENTS.md`, `server.py`'s docstring, and `CHANGELOG.md` are updated per REQ-007; `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` all run clean (no drift) after the edits.\n- [ ] ACC-008: Verifies REQ-008 — `tests/general/tools/test_delete.py` and `tests/general/tools/test__path_safety.py` exist and pass; the full `unittest` suite is green; `ruff format --check`, `ruff check`, and `vulture` are clean.\n\n### Scope\n\n#### Included\n\n- The generic `delete` MCP tool (`general/tools/delete.py`) with eleven type-dispatched adapters and an `_ADAPTERS` table.\n- The reusable path-safety module (`general/tools/_path_safety.py`) and its unit tests.\n- Removal of the eleven `delete_<d>` stub tools (source, registration, docstrings, stub tests).\n- Per-domain locking and graceful error handling (`ValueError` for bad ids, `XNotFoundError` for missing docs, `DeleteError` for I/O failures).\n- The `feat` folder-per-document hard delete (`shutil.rmtree`).\n- Decision/documentation propagation: new ADR, `AGENTS.md`, `server.py` docstring, `CHANGELOG.md`, and `docs/` regeneration.\n- New test files `tests/general/tools/test_delete.py` and `tests/general/tools/test__path_safety.py`.\n\n#### Explicitly Out Of Scope\n\n- Any change to ADR deletion — ADR has no `delete_adr` today and gets none; the generic `delete` covers only the eleven whole-body domains.\n- Modifying the `get_<d>`, `update`, or `set_status` tools to call the new `_path_safety` module — the module is built to be reusable by them, but they are left untouched here (adoption is a future, separate decision).\n- Soft-delete, archival, or status-based \"deleted\" semantics — the issue specifies a hard delete from disk.\n- Re-introducing any per-domain `delete_<d>` tool, or any `specmgr://<d>/{id}` resource.\n- A `delete` prompt (no `create_<d>`/`update_<d>`-style narrated prompt is added for deletion).\n\n### Dependencies\n\n#### Depends On\n\n- ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic type-dispatched `update`/`set_status` tools — the structural precedent this feature copies for `delete`, including the `Literal` `type` parameter, the private-adapter-per-domain pattern, and the `_ADAPTERS` dispatch table).\n- ADR 8cf940c5-3100-485c-a12d-14b59b631712 (`feat`'s folder-per-document, `feat-NNN-slug` addressing — the reason `feat`'s adapter and id format differ from the ten UUID domains).\n- Each domain's existing `<d>/tools/_lock.py` (`<d>_lock`), `<d>/tools/_io.py` (`load_by_id`), and `<d>/tools/_paths.py` (`<d>_base_dir`, `XNotFoundError`) — the adapters reuse all of these rather than introducing new plumbing.\n- ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of truth) and ADR 898bfcd0-85f9-462f-93a8-747bda4166c8 (author/edit ADRs only through MCP structured tools — governs how the new ADR for this decision is created).\n\n#### Blocks\n\n- Nothing. This feature is self-contained; it removes a long-standing \"still missing\" item from `AGENTS.md` and is a prerequisite for any future domain that would otherwise be expected to ship its own `delete_<d>` stub (the new convention is that they instead add one adapter to the generic `delete` tool).\n\n### Design Notes\n\nThis design is the complete, implementer-ready specification. The Phase-Orchestrator\nshould execute the Task List below against these notes; every file, function, and\nbehavior is pinned here so no design work remains at implementation time.\n\n#### 1. The reusable path-safety module (`general/tools/_path_safety.py`)\n\nThis is the feature's most important new artifact and the one the user explicitly\nrequired to be reusable by `get`/`update` later. It is a private, cross-domain helper\nin the same package and in the same style as the existing `general/tools/_doc_paths.py`,\n`_splice.py`, and `_paging.py`. It has **no** `mcp`/file-write dependency and performs\n**no filesystem mutation** — it only inspects strings and `Path` objects — so it is\ntrivially safe to import from any read tool as well.\n\nPublic API (every function raises `ValueError` with a message that names the offending\nvalue; every function starts with the codebase-standard `assert isinstance(...)` /\n`assert value.strip()` input guards per `.specmgr/conventions.md`):\n\n```python\n__all__ = [\n    \"assert_feat_id\",\n    \"assert_no_traversal\",\n    \"assert_uuid\",\n    \"assert_within\",\n    \"validate_id\",\n]\n\n#: The ten whole-body domains whose `id` is a server-generated v4 UUID.\n_UUID_TYPES = frozenset({\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\", \"dec\", \"sop\", \"vcr\"})\n\n#: Canonical 8-4-4-4-12 lowercase-hex UUID shape (the form `uuid.uuid4().str` produces,\n#: which is what every `create_<d>` tool writes into the frontmatter `id`).\n_UUID_PATTERN = re.compile(r\"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$\")\n\n#: The `feat` folder-name shape (ADR 8cf940c5): `feat-NNN-slug`, lowercase alnum + hyphen.\n_FEAT_ID_PATTERN = re.compile(r\"^feat-[0-9]+-[a-z0-9-]+$\")\n\n\ndef assert_no_traversal(id_: str) -> None:\n    \"\"\"Reject any id that could contribute a relative path.\n\n    Universal guard, independent of domain: the value must be a non-empty `str`\n    and must contain no `/`, no `\\\\`, and no `..`. This alone makes it impossible\n    for the id to escape its base directory when joined into a path.\n    \"\"\"\n\n\ndef assert_uuid(id_: str) -> None:\n    \"\"\"Reject any id that is not a canonical lowercase-hex v4-shaped UUID.\n\n    Enforced for the ten `_UUID_TYPES` domains. (Subsumes `assert_no_traversal`\n    for well-formed input, but both are applied so the error message is precise.)\n    \"\"\"\n\n\ndef assert_feat_id(id_: str) -> None:\n    \"\"\"Reject any id that is not a well-formed `feat-NNN-slug` folder name.\"\"\"\n\n\ndef validate_id(type_: str, id_: str) -> None:\n    \"\"\"Convenience dispatcher: `assert_no_traversal` plus the type's format check.\n\n    `type_` in `_UUID_TYPES` -> `assert_uuid`; `type_ == \"feat\"` ->\n    `assert_feat_id`; any other `type_` -> `ValueError` (unknown type). This is the\n    single entry point the generic `delete` (and, later, `update`/`set_status`)\n    calls before any filesystem access.\n    \"\"\"\n\n\ndef assert_within(base_dir: Path, candidate: Path) -> None:\n    \"\"\"Defense-in-depth: `candidate.resolve()` must be `is_relative_to(base_dir.resolve())`.\n\n    Type-agnostic. Called by the adapters *after* id -> path resolution, so that even\n    if a future id-validation gap existed, a resolved path could never point outside\n    the domain's own base directory.\n    \"\"\"\n```\n\nReusability contract (why `get`/`update` can adopt this later with zero rework):\nthe five functions take only plain `str`/`Path`/`type` inputs, perform no I/O, and\nreturn `None` (raise on failure). A future `get_<d>` would call\n`assert_no_traversal(id)` + the domain's format assert + `assert_within(base_dir, path)`;\na future `update`/`set_status` would call `validate_id(type, id)` + `assert_within(...)`.\nNo delete-specific state, argument, or return value leaks into this module. `DeleteError`\n(RQ-005's I/O wrapper) deliberately lives in `delete.py`, **not** here, for the same\nreason — it is a delete-specific concern, not a reusable safety primitive.\n\n#### 2. The generic tool (`general/tools/delete.py`)\n\nStructure mirrors `general/tools/set_status.py` file-for-file: a long module docstring\n(explaining the dispatch, the safety, the error contract, and that ADR is excluded),\nthe per-domain private adapters, the `_ADAPTERS` table, and the single\n`@mcp.tool(name=\"delete\")`-decorated public function. Imports follow the same\nqualified, per-domain `from ...<d>.tools._lock import <d>_lock` / `from ...<d>.tools._io\nimport load_by_id as load_<d>_by_id` / `from ...<d>.tools._paths import <d>_base_dir`\npattern `set_status.py` uses.\n\nPublic function (parameter intentionally named `type`, matching `set_status`/`update`):\n\n```python\n#: The eleven whole-body domains the generic delete tool covers (ADR excluded).\n_DELETE_TYPES = (\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\", \"dec\", \"sop\", \"feat\", \"vcr\")\n\nclass DeleteError(OSError):\n    \"\"\"A delete failed at the filesystem layer (I/O error, permission, or race).\n\n    Carries the resolved path and the underlying `OSError` as `__cause__` so the\n    MCP host can surface a meaningful message to the caller (REQ-005).\n    \"\"\"\n\n@mcp.tool(\n    name=\"delete\",\n    title=\"Delete document\",\n    description=(\n        \"Permanently delete an existing document from disk across the eleven whole-body \"\n        \"domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr; \"\n        \"`adr` is not supported). Resolves the document by `id`, takes the domain lock, \"\n        \"and removes it: the single `*.md` file for the ten flat domains, or the entire \"\n        \"`<base>/<id>/` folder for `feat`. Returns the deleted path as a string. \"\n        \"An invalid `id` (path-injection attempt or wrong format) is a `ValueError` \"\n        \"raised before any file access; a missing document is the domain's own \"\n        \"`XNotFoundError`; an I/O failure is a `DeleteError`. This is the sole \"\n        \"delete entry point -- the former per-domain `delete_<d>` tools are removed.\"\n    ),\n)\ndef delete(\n    id: str,\n    type: Literal[\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\", \"dec\", \"sop\", \"feat\", \"vcr\"],\n) -> str:\n    \"\"\"...\"\"\"\n    # REQ-003: validate before any filesystem access (injection prevention).\n    validate_id(type, id)\n    result = _ADAPTERS[type](id)\n    return result\n```\n\n`_ADAPTERS` is `dict[str, Callable[[str], str]]` mapping each of the eleven `type`\nstrings to its `_delete_<d>` adapter.\n\n#### 3. The per-domain adapters\n\nTen of the eleven are byte-for-byte the same shape, differing only in the domain's\nlock / `load_by_id` / `base_dir` / `XNotFoundError` names. The canonical form (shown\nfor `req`):\n\n```python\ndef _delete_req(id_: str) -> str:\n    \"\"\"Hard-delete the requirement `id_` from disk (REQ-001/004/005/006).\"\"\"\n    base_dir = req_base_dir()\n    with req_lock(id_):                                  # REQ-004\n        path, _existing = load_req_by_id(base_dir, id_)  # resolves + ReqNotFoundError\n        assert_within(base_dir, path)                    # REQ-003 defense-in-depth\n        try:\n            path.unlink()                                # REQ-006\n        except OSError as ex:\n            raise DeleteError(f\"failed to delete {path}: {ex}\") from ex   # REQ-005\n    return str(path)                                     # REQ-001\n```\n\nNotes on the adapter contract:\n- `load_by_id` is used (not a raw `find_*_path`) for consistency with `set_status`/\n  `update`; the returned parsed document is discarded (`_existing`) — only the `path`\n  is needed. This also guarantees the target is a valid, parseable document of that\n  domain with that exact `id` before anything is removed.\n- The domain's own `XNotFoundError` (e.g. `ReqNotFoundError`) propagates unchanged\n  from `load_by_id` — the adapter does not catch it (REQ-005).\n- `validate_id` is **not** repeated inside each adapter; it is called once in the\n  public `delete` before dispatch. The `assert_within` **is** repeated per adapter\n  because it needs the resolved `path` (available only inside the lock).\n\nThe `feat` adapter diverges in exactly two ways (folder-per-document, ADR 8cf940c5):\nit removes the containing folder, not the `README.md` file, and it returns the folder\npath.\n\n```python\ndef _delete_feat(id_: str) -> str:\n    base_dir = feat_base_dir()\n    with feat_lock(id_):\n        path, _existing = load_feat_by_id(base_dir, id_)   # <base>/<id>/README.md\n        folder = path.parent\n        assert_within(base_dir, folder)\n        try:\n            shutil.rmtree(folder)                          # REQ-006: whole folder\n        except OSError as ex:\n            raise DeleteError(f\"failed to delete {folder}: {ex}\") from ex\n    return str(folder)\n```\n\n`delete.py` therefore imports `shutil` (the only new stdlib import) and, for `feat`,\nuses `path.parent` as the deletion target.\n\n#### 4. Locking (REQ-004)\n\nNo new lock is introduced. Each adapter re-uses the domain's existing\n`<d>/tools/_lock.py::<d>_lock(id_)` — the very lock the generic `update` and\n`set_status` adapters already take for the same id. Because `delete`'s\nresolve-then-delete runs under that same per-id lock, a concurrent `update`/\n`set_status`/`delete` targeting the same id is serialized, satisfying the issue's\n\"we have a lock in place when we find the file and delete it.\"\n\n#### 5. Path-injection threat model (REQ-003)\n\n- `type`: a closed `Literal` of eleven strings — structurally incapable of carrying\n  a path. No check needed beyond the `Literal` itself (and `validate_id` rejecting an\n  unknown type string at the Python level, for callers that bypass the schema).\n- `id`: the only free-form input. Two independent layers stop injection:\n  1. **Format validation** (`validate_id`, before any I/O): no `/`, `\\`, or `..`\n     (`assert_no_traversal`), plus a strict domain format (canonical UUID for the ten\n     UUID domains; `feat-NNN-slug` for `feat`). A value like `../../etc/passwd` fails\n     both the traversal and the format checks and is rejected with a `ValueError`\n     before the filesystem is touched.\n  2. **Containment** (`assert_within`, after resolution, inside the lock): the resolved\n     path must be `is_relative_to` the domain's base directory. This is defense-in-depth\n     against any future gap in layer 1 (e.g. a domain whose resolver builds a path from\n     the id, as `feat` does).\n- The ten flat domains' resolvers (`find_<d>_path`) scan and compare parsed ids rather\n  than joining the id into a path, so they are already injection-safe; the `feat`\n  resolver (`find_feat_path_by_id`) *does* join `base_dir / id / README.md`, which is\n  precisely why the two-layer guard matters and is why `assert_feat_id` +\n  `assert_within` are both applied for `feat`.\n\n#### 6. Error contract (REQ-005)\n\n| Condition | Raised | Where | Filesystem touched? |\n|---|---|---|---|\n| `id` has `/`, `\\`, `..`, or wrong format for `type` | `ValueError` | public `delete`, via `validate_id` | No (before dispatch) |\n| unknown `type` string (Python-level) | `ValueError` | `validate_id` | No |\n| no document with `id` in `type`'s domain | domain `XNotFoundError` | adapter, via `load_by_id` | No (read-only scan) |\n| resolved path escapes base dir | `ValueError` | adapter, via `assert_within` | No |\n| `unlink`/`rmtree` I/O failure | `DeleteError` (wraps `OSError`) | adapter | Partial at most |\n\n#### 7. The new ADR (REQ-007)\n\nCreated via the `create_adr` MCP tool (per ADR 898bfcd0, ADRs are authored only\nthrough structured tools), then `specmgr adr-toc`. Title: **\"Replace domain-specific\ndelete tools with a generic type-dispatched delete tool\"**. Suggested body:\n- *Context and Problem Statement*: eleven unimplemented `delete_<d>` stubs inflate the\n  tool surface; no delete path-safety exists; the issue (#36) asks for one generic,\n  safe, locked delete.\n- *Decision Drivers*: minimal tool surface; explicit `type` keeps id resolution\n  single-domain; injection safety; reuse of existing per-domain locks/resolvers;\n  filesystem-is-source-of-truth.\n- *Considered Options*: (1) generic `delete(id, type)` with per-domain adapters + a\n  reusable `_path_safety` module (chosen); (2) implement each `delete_<d>` stub\n  independently (rejected: eleven near-duplicates, no shared safety); (3) uuid-only\n  id resolution scanning all domains (rejected: cross-domain UUID ambiguity, full-dir\n  scan on the write path — same reasons ADR 36905d5b rejected it for `update`).\n- *Decision Outcome*: Option 1; ADR excluded (no `delete_adr` ever existed; deleting an\n  ADR risks breaking other ADRs' \"superseded by X\" references); convention — every\n  current and future domain implements a `delete` adapter in the generic tool, never a\n  per-domain `delete_<d>` tool.\n- *Consequences*: breaking (eleven tools removed, one added — the 0.x MCP tool list is\n  the only client contract, recorded in `CHANGELOG.md`); `get`/`update`/`set_status`\n  can now adopt `_path_safety` for their own injection protection in a future change.\n- *More Information*: this feature plan; related ADRs 36905d5b, 8cf940c5, 33c5ab08,\n  898bfcd0.\n\n#### 8. Documentation propagation (REQ-007)\n\n- `AGENTS.md`: in each of the eleven per-domain Status bullets, replace the\n  \"`delete_<d>` stub\" / \"`delete_<d>` (stub, not yet implemented)\" mention with a note\n  that deletion goes through the generic `delete` tool (`type=\"<d>\"`); delete the\n  \"Still genuinely missing\" bullet \"`delete_req`/…/`delete_vcr` are stubs, not yet\n  implemented\"; in the `general/` bullet, add `delete` to the `general/tools/` list and\n  add a sentence that all eleven whole-body domains implement a `delete` adapter there\n  (ADR-excluded). Keep the `ac` \"future domain\" convention note in sync (a future domain\n  adds a `delete` adapter too).\n- `server.py` module docstring: remove the eleven per-domain `delete_<d>` stub mentions\n  from the domain tool paragraphs; add `delete` to the \"General tools\n  (`general/tools/`)\" paragraph describing it (eleven whole-body domains, ADR excluded,\n  returns the deleted path, safety/lock/error contract in one line).\n- `CHANGELOG.md`: under `[Unreleased]`, a `### Changed`/`### Removed` entry: removed the\n  eleven `delete_<d>` stub tools; added the generic `delete` tool; added reusable\n  `general/tools/_path_safety.py`. Mark breaking (0.x).\n- Regenerate `docs/`: `specmgr docs` (API docs + `docs/GENERATED.md`), `specmgr\n  mcp-docs` (`docs/MCP.md`), `specmgr adr-toc` (`docs/adr/README.md`) — each run twice\n  to confirm a stable fixed point (no drift).\n\n#### 9. Test design (REQ-008)\n\n`tests/general/tools/test__path_safety.py` — pure unit tests, no filesystem:\n- `assert_no_traversal`: accepts a plain id; rejects `\"\"`, `\"../x\"`, `\"a/b\"`, `\"a\\b\"`,\n  `\"..\"`, `\"a/../b\"` (each a `ValueError`).\n- `assert_uuid`: accepts a canonical lowercase UUID; rejects uppercase, a 31-char\n  string, a string with `/`, and a `feat-1-x` string.\n- `assert_feat_id`: accepts `\"feat-36-delete\"`; rejects `\"feat-36\"` (no slug),\n  `\"feature-36-x\"`, `\"feat-36/../x\"`, and a UUID.\n- `validate_id`: for each of the ten UUID types a UUID passes and a `feat` id fails;\n  for `feat` a `feat` id passes and a UUID fails; an unknown `type_` raises.\n- `assert_within`: a child path of the base passes; a sibling/ancestor path raises.\n\n`tests/general/tools/test_delete.py` — parameterized over all eleven types (mirroring\n`test_set_status.py`'s fixture strategy: seed a real document per type via the domain's\nown `create_<d>` into a temp `SPECMGR_DOCS_DIR` / `SPECMGR_FEAT_DIR`):\n- success: record the returned `str`; assert the file (or `feat` folder) no longer\n  exists; assert a follow-up `get_<d>`/`load_by_id` raises the domain `XNotFoundError`.\n- `feat` specifically: seed a `history.md` in the folder; assert the whole folder (and\n  the `history.md`) is gone.\n- injection: for each type, call `delete` with `../x`, `a/b`, `a\\b`, `..`, and a\n  wrong-format id; assert `ValueError` and that the seeded document still exists.\n- unknown id: assert the domain `XNotFoundError`.\n- I/O failure: mock `Path.unlink` (or `shutil.rmtree` for `feat`) to raise `OSError`;\n  assert `DeleteError` is raised and its message contains the path.\n- locking: spy/mock the domain `<d>_lock` and assert it is entered for the delete.\n\nThe eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files are deleted (REQ-002);\nno replacement per-domain delete tests are added — coverage moves entirely to\n`tests/general/tools/test_delete.py`.\n\n### Related Decisions\n\n- New ADR (created in Phase 4, REQ-007): \"Replace domain-specific delete tools with a\n  generic type-dispatched delete tool\" — the architecture-level record of this feature's\n  decision and of the forward convention that every domain implements a `delete` adapter\n  in the generic tool.\n- ADR 36905d5b-8057-4294-8665-c7eed5534db0 — the `update`/`set_status` generic-tool\n  precedent this feature extends with `delete`.\n- ADR 8cf940c5-3100-485c-a12d-14b59b631712 — `feat`'s folder-per-document addressing,\n  which drives `feat`'s distinct adapter and id format.\n- ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 — filesystem is the sole source of truth\n  (delete removes the on-disk file; there is no separate deletion record).\n- ADR 898bfcd0-85f9-462f-93a8-747bda4166c8 — ADRs are authored/edited only through MCP\n  structured tools (governs Phase 4's `create_adr` step).\n\n### Task List\n\n#### Phase 0: Worktree, branch, and design plan (designer)\n\n- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from `dev` at\n  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) —\n  status: done (2026-08-31).\n- [x] Task 0.2: Author this feature README (the full design) — status: done (2026-08-31).\n\n#### Phase 1: Reusable path-safety module (Phase-Orchestrator)\n\n- [ ] Task 1.1: Add `general/tools/_path_safety.py` exactly per Design Notes §1\n  (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`,\n  `assert_within`; `ValueError` on failure; no I/O) — depends on: Task 0.2 —\n  status: not-started.\n- [ ] Task 1.2: Add `tests/general/tools/test__path_safety.py` per Design Notes §9 —\n  depends on: Task 1.1 — status: not-started.\n\n#### Phase 2: The generic delete tool (Phase-Orchestrator)\n\n- [ ] Task 2.1: Add `general/tools/delete.py` per Design Notes §2–§6 (`DeleteError`,\n  eleven `_delete_<d>` adapters, `_ADAPTERS`, `@mcp.tool(name=\"delete\")` public\n  function calling `validate_id` then dispatching) — depends on: Task 1.1 —\n  status: not-started.\n- [ ] Task 2.2: Add `tests/general/tools/test_delete.py` per Design Notes §9 —\n  depends on: Task 2.1 — status: not-started.\n\n#### Phase 3: Retire the eleven delete stubs (Phase-Orchestrator)\n\n- [ ] Task 3.1: Delete the eleven `src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` files —\n  depends on: Task 2.1 — status: not-started.\n- [ ] Task 3.2: In each of the eleven `<d>/tools/__init__.py`, remove the\n  `from .delete_<d> import delete_<d>` line, the `delete_<d>` `__all__` entry, and the\n  stub mention in the module docstring — depends on: Task 3.1 — status: not-started.\n- [ ] Task 3.3: Delete the eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files —\n  depends on: Task 3.2 — status: not-started.\n\n#### Phase 4: Decision and documentation propagation (Phase-Orchestrator)\n\n- [ ] Task 4.1: Create the new ADR via the `create_adr` MCP tool per Design Notes §7,\n  set it `accepted`, and run `specmgr adr-toc` — depends on: Task 3.3 —\n  status: not-started.\n- [ ] Task 4.2: Update `AGENTS.md` per Design Notes §8 — depends on: Task 3.3 —\n  status: not-started.\n- [ ] Task 4.3: Update `server.py`'s module docstring per Design Notes §8 — depends on:\n  Task 3.3 — status: not-started.\n- [ ] Task 4.4: Add the `CHANGELOG.md` `[Unreleased]` entry per Design Notes §8 —\n  depends on: Task 3.3 — status: not-started.\n- [ ] Task 4.5: Regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`, `specmgr\n  adr-toc`), each run twice to confirm no drift — depends on: Tasks 4.1–4.4 —\n  status: not-started.\n\n#### Phase 5: Quality gate and sign-off (Phase-Orchestrator)\n\n- [ ] Task 5.1: Run the full gate — `ruff format --check`, `ruff check`, `vulture\n  src/ whitelist.py --min-confidence 60`, the full `unittest` suite, and advisory\n  `pylint` — and fix any failures — depends on: Task 4.5 — status: not-started.\n- [ ] Task 5.2: Walk ACC-001..ACC-008, mark each `[x]` with a concrete justification\n  (test file / tool / doc proving it), update Current Status, and bump this README's\n  frontmatter `status`/`updated` — depends on: Task 5.1 — status: not-started.\n\n## Progress\n\n### Current Status\n\n**As of 2026-08-31**: Design complete (Phase 0). The `feat-36-delete` worktree/branch\nwas cut from `dev` and this README captures the full, implementer-ready design: the\ngeneric `delete` tool, the reusable `_path_safety` module, the eleven stub removals,\nthe locking/error contract, the new ADR, and the documentation propagation. No source\ncode has been written yet — implementation (Phases 1–5) is delegated to the\nPhase-Orchestrator. All three open design questions were resolved with the requester:\nADR is excluded (eleven whole-body domains only), `feat` deletes its whole folder, and\nthe tool returns the deleted path as a `str`.\n\n### Blockers\n\n- None currently.\n\n### Updates\n\n<!-- Newest entry first -- prepend new entries directly below this comment. -->\n\n#### 2026-08-31 15:37:40.000Z — Feature designed; worktree and plan authored (Phase 0 complete)\n\nCompleted the design for issue #36. Created the `feat-36-delete` git worktree/branch\nfrom `dev` (leaving `dev` untouched) and authored this README as the full,\nimplementer-ready plan. Key design decisions, confirmed with the requester: (1) the\ngeneric `delete` tool covers the eleven whole-body domains and excludes ADR; (2) `feat`\nhard-deletes its entire `<base>/<id>/` folder; (3) the tool returns the deleted path as\na `str`; and (4) the path/file injection-prevention logic lives in a new **reusable**\nmodule `general/tools/_path_safety.py` so the `get`/`update`/`set_status` tools can\nadopt it later with zero rework (they are not modified in this feature). No\nimplementation code has been written; Phases 1–5 are delegated to the Phase-Orchestrator.\n\n### Decisions Made\n\n<!-- Newest entry first -- prepend new entries directly below this comment. -->\n\n#### 2026-08-31 15:37:40.000Z — ADR excluded from the generic delete tool\n\nThe generic `delete` covers only the eleven whole-body domains (`req`/`uc`/`tsk`/`qa`/\n`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`), not ADR. Rationale: ADR has never had a\n`delete_adr` stub, it is treated specially (render round-trip, schema under shared\n`models/adr/`), and hard-deleting an ADR could break other ADRs' \"superseded by X\"\ncross-references. This mirrors the `update` tool's precedent of excluding ADR.\n\n#### 2026-08-31 15:37:40.000Z — Injection prevention is a reusable, non-I/O module\n\nThe path/file validation that prevents injection is implemented in\n`general/tools/_path_safety.py` as pure functions (string/`Path` inspection only, no\nfilesystem mutation), deliberately separate from the delete-specific `DeleteError` and\nfrom `_doc_paths.py`. This makes it directly reusable by the `get_<d>`, `update`, and\n`set_status` tools in a future change without rework, per the requester's requirement.\n`delete` is the only tool wired to it in this feature.\n\n#### 2026-08-31 15:37:40.000Z — `feat` deletes its whole folder; the tool returns the deleted path\n\nBecause `feat` is folder-per-document (ADR 8cf940c5), its adapter removes the entire\n`<base>/<id>/` folder via `shutil.rmtree` (including any `history.md`/session files),\nwhile the ten flat domains remove their single `*.md` file via `Path.unlink()`. The\npublic `delete` tool returns the deleted path as a `str` (file path for the flat\ndomains, folder path for `feat`).\n"
}
````

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 71.6s)

_Thinking:_

Okay, so I'll use the main checkout's venv to verify that the README is correctly parsed by the feat model (same commit). I'll write a simple verification script.

Actually, I can just run a Python one-liner that imports parse_feat and parses the file. I'll try using the main venv's python.

Now let me validate the README parses cleanly against the feat schema (using the main checkout's venv, same commit).

**Tool: bash**

**Input:**

```json
{
  "command": "/home/user/src/biz.dfch.SpecMgr/.venv/bin/python -c \"\nfrom biz.dfch.specmgr.feat.models.v1 import parse_feat\np = '/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md'\ndoc = parse_feat(open(p, encoding='utf-8').read())\nprint('PARSE OK')\nprint('id        =', doc.frontmatter.id)\nprint('type      =', doc.frontmatter.type)\nprint('status    =', doc.frontmatter.status)\nprint('version   =', doc.frontmatter.version)\nprint('H1        =', doc.body.plan and 'yes')\nprint('overview  =', bool(doc.body.plan.overview.text.strip()))\nprint('reqs      =', len(doc.body.plan.requirements.items))\nprint('accs      =', len(doc.body.plan.acceptance_criteria.items))\nprint('included  =', len(doc.body.plan.scope.included.text.strip().splitlines()))\nprint('oos       =', len(doc.body.plan.scope.explicitly_out_of_scope.text.strip().splitlines()))\nprint('dependsOn =', bool(doc.body.plan.dependencies and doc.body.plan.dependencies.depends_on))\nprint('blocks    =', bool(doc.body.plan.dependencies and doc.body.plan.dependencies.blocks))\nprint('design    =', bool(doc.body.plan.design_notes and doc.body.plan.design_notes.text.strip()))\nprint('related   =', bool(doc.body.plan.related_decisions and doc.body.plan.related_decisions.text.strip()))\nprint('phases    =', [(ph.number, ph.title, len(ph.items)) for ph in doc.body.plan.task_list.phases])\nprint('curStatus =', bool(doc.body.progress.current_status.text.strip()))\nprint('updates   =', [(u.timestamp, u.title) for u in doc.body.progress.updates.updates])\nprint('decisions =', [(d.timestamp, d.title) for d in doc.body.progress.decisions_made.decisions])\n\"\n"
}
```

**Output:**

```
Traceback (most recent call last):
  File "<string>", line 4, in <module>
    doc = parse_feat(open(p, encoding='utf-8').read())
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/models/v1/parser.py", line 86, in parse_feat
    body = Feature.from_text(format_text(post.content))
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_section.py", line 216, in from_text
    instance = super().from_text(body_text)
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_str.py", line 371, in from_text
    extent, instance_value = cls.process_field(field_name, field_type, remaining_text, optional=is_optional)
                             ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_str.py", line 195, in process_field
    instance = type_.from_text(field_text)
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_section.py", line 216, in from_text
    instance = super().from_text(body_text)
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_str.py", line 371, in from_text
    extent, instance_value = cls.process_field(field_name, field_type, remaining_text, optional=is_optional)
                             ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_str.py", line 195, in process_field
    instance = type_.from_text(field_text)
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_section.py", line 216, in from_text
    instance = super().from_text(body_text)
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_str.py", line 358, in from_text
    new_remaining_text, list_value = cls.process_list_field(
                                     ~~~~~~~~~~~~~~~~~~~~~~^
        field_name, item_type, remaining_text, optional=is_optional
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_str.py", line 268, in process_list_field
    items.append(item_type.from_text(item_text))
                 ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_section.py", line 216, in from_text
    instance = super().from_text(body_text)
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_str.py", line 384, in from_text
    instance = cls(**kwargs)  # type: ignore
  File "/home/user/src/biz.dfch.SpecMgr/.venv/lib/python3.13/site-packages/pydantic/main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
pydantic_core._pydantic_core.ValidationError: 1 validation error for Phase
  Assertion failed, TaskItem: expected a '- [ ]'/'- [x]' checkbox marker, got '[x] Task 0.1: Create the `feat-36-delete` git worktree/branch from `dev` at\n`/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) —\nstatus: done (2026-08-31).' [type=assertion_error, input_value={'items': [- [x] Task 0.1...s: done (2026-08-31).
]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/assertion_error

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 123.6s)

_Thinking:_

The parse failed because a task item spans multiple lines. The `TaskItem` parser expects each `- [ ]`/`- [x]` item to be on a single line (or at least, the first line to contain the checkbox marker). My Task 0.1 item is wrapped across multiple lines, and the parser is reading the continuation line as part of the item's text, but it seems the way list items are processed is — the problem is that my task item text contains newlines, and the item parser is getting confused.

Looking at the error: `TaskItem: expected a '- [ ]'/'- [x]' checkbox marker, got '[x] Task 0.1: Create the ... at\n`/home/user/...` (`dev` left untouched) —\nstatus: done (2026-08-31).'`

So the item text contains `\n` (newlines) — my task items are wrapped. The TaskItem parser expects each item to be a single-line checkbox. Continuation lines are being included in the item, and that's breaking the marker match.

Wait, let me think again. The issue is that the list-item parser is grabbing multi-line items. When a `- [x]` item is followed by indented or continuation text, those get folded into the item. But here my items aren't indented — they're just wrapped within the same bullet. Let me look: my task items are written like this:

```
- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from
  `/dev` at
  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) —
  status: done (2026-08-31).
```

Wait, no. Let me re-check what I actually wrote. I wrote:

```
- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from
  `dev` at
  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) —
  status: done (2026-08-31).
```

Hmm, actually in the file I wrote it like this:

```
- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from
  `dev` at `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left
  untouched) — status: done (2026-08-31).
```

The continuation lines are indented with 2 spaces. So the list-item parser treats the indented continuation as part of the same item, resulting in item text containing newlines. And TaskItem's marker matching fails, because... actually the error says it received `[x] Task 0.1: ...\n...\nstatus: done...`. So the item's `.text` includes the newlines.

Wait, but the real problem is: does `TaskItem.from_text` expect the entire item (including continuation lines) to start with a checkbox? Let me look at how tsk's TaskItem handles multi-line items. Actually, the issue might be that the markdown list parser is folding continuation lines into the item, and TaskItem's regex only matches the first line.

Let me look at how existing feature READMEs write their task items — are they single-line? Let me check the task items in feat-33-vcr's README. From what I read earlier, the task items were long and wrapped across multiple lines. For example:

```
- [x] Task 0.1: Draft `example.md`/`template.md` bodies exercising every
  section and validate against the `models/md` engine (mirroring `sop`'/
  `sysrs`'s discipline) before writing any Pydantic model code.
```

So feat-33-vcr has multi-line task items. And feat-33-vcr is a `done` feature that presumably parses (it's the one that shipped). So multi-line task items should be fine...

Wait, unless feat-33-vcr doesn't actually parse. Let me reconsider. Earlier I noticed that feat-33-vcr's update entries use the `T`-separated `2026-08-31T16:26:00.000000` format, which doesn't match the `_ENTRY_HEADING_ALIAS` regex. That suggests feat-33-vcr's README might not parse cleanly.

Hmm, that's concerning. Let me actually test whether feat-33-vcr's README parses. If it doesn't, then the feat domain is silently skipping it in list_feat, and the "canonical" parseable format is the template's format, not feat-33-vcr's.

But my specific error is about TaskItem multi-line items. Let me test: does the template's single-line task items parse? Of course they do. The question is whether multi-line task items parse.

Let me investigate TaskItem more carefully. Let me look at tsk's task_item.py and how process_list_field handles items.

Actually, the error is clear: `TaskItem: expected a '- [ ]'/'- [x]' checkbox marker, got '[x] Task 0.1: ...\n...\nstatus: done (2026-08-31).'`. So the item text being passed to TaskItem.from_text contains embedded newlines (the continuation lines). And TaskItem.from_text is trying to match the checkbox marker against the whole multi-line text and failing.

But wait — how does process_list_field split items? It should split on lines starting with `- `. Continuation lines (indented) get appended to the current item. So the item text = "[x] Task 0.1: Create...\\n`dev` at...\\nstatus: done...". Then TaskItem.from_text(item_text) receives this multi-line string.

Let me look at TaskItem.from_text and see whether it handles multi-line. Let me read tsk/models/v1/task_item.py.

Actually, I think the cleanest fix is: make each task item single-line (don't wrap). That's the safe, parseable format. But the existing READMEs (like feat-33-vcr) wrap them... Let me check whether those actually parse. Let me test feat-33-vcr's README with the parser.

Let me do both: read task_item.py and test-parsing feat-33-vcr.

The multi-line task items break the `TaskItem` parser. Let me check how `TaskItem` handles items and whether the existing feat-33-vcr README actually parses.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/task_item.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/task_item.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """`TaskItem` -- a single `- [ ] .../- [x] ...` checklist entry.
19: 
20: The project's shared markdown parser (`MarkdownIt("commonmark")`, see
21: `models/md/_markdown.py`) has no GFM task-list plugin enabled, so `- [ ] text`/
22: `- [x] text` is not a distinct AST node -- it parses as an ordinary bullet-list
23: item whose leading-paragraph text is the literal string `"[ ] text"`/
24: `"[x] text"` (see `MarkdownListItem.text`). `TaskItem` recovers the intended
25: `checked`/`description` split from that literal text via a regular expression.
26: """
27: 
28: from __future__ import annotations
29: 
30: import re
31: 
32: from pydantic import computed_field
33: 
34: from ....models.md import MarkdownListItem, MarkdownParagraph
35: 
36: #: Matches a literal `[ ]`/`[x]`/`[X]` checkbox marker at the start of a
37: #: `TaskItem`'s own leading-paragraph text (see `MarkdownListItem.text`),
38: #: capturing the marker character (group 1) and the remaining description
39: #: text (named group `description`). The marker check is case-insensitive
40: #: for the "checked" state (`[x]`/`[X]` both count), matching common GFM
41: #: task-list authoring conventions.
42: _MARKER_PATTERN = re.compile(r"^\[( |x|X)\]\s*(?P<description>.*)$")
43: 
44: 
45: class TaskItem(MarkdownListItem):
46:     """One `- [ ] .../- [x] ...` checklist entry of a `Task`'s flat item list.
47: 
48:     A leaf `MarkdownListItem` subclass (declares no nested `MarkdownStr`
49:     fields of its own, only the two computed properties below), so it parses/
50:     renders exactly like the base class -- `checked`/`description` are purely
51:     derived views over the inherited `.text`, computed lazily rather than
52:     stored, and therefore never interfere with `MarkdownStr`'s field-based
53:     `from_text`/`__str__` distribution (see `MarkdownStr._get_field_names`).
54: 
55:     Parameters
56:     ----------
57:     checked:
58:         Computed. `True` for a `[x]`/`[X]` marker, `False` for a `[ ]`
59:         marker. Raises `AssertionError` if `.text` does not start with a
60:         well-formed checkbox marker at all.
61:     description:
62:         Computed. The item's own text with the leading checkbox marker
63:         stripped, e.g. `"Do the thing"` for `"- [ ] Do the thing"`. Raises
64:         `AssertionError` under the same condition as `checked`.
65:     content:
66:         An optional list of paragraphs with details content of the task item.
67:     """
68: 
69:     @computed_field  # type: ignore
70:     @property
71:     def checked(self) -> bool:
72:         """Whether this item's checkbox marker is `[x]`/`[X]` (checked) rather than `[ ]` (unchecked).
73: 
74:         Returns:
75:             `True` for a `[x]`/`[X]` marker, `False` for a `[ ]` marker.
76: 
77:         Raises:
78:             AssertionError: `.text` does not start with a well-formed
79:                 checkbox marker (see `_MARKER_PATTERN`).
80:         """
81:         match = _MARKER_PATTERN.match(self.text)
82:         assert match, f"TaskItem: expected a '- [ ]'/'- [x]' checkbox marker, got {self.text!r}"
83:         return match.group(1).lower() == "x"
84: 
85:     @computed_field  # type: ignore
86:     @property
87:     def description(self) -> str:
88:         """This item's own text with the leading checkbox marker stripped.
89: 
90:         Returns:
91:             The description text following the checkbox marker, e.g.
92:             `"Do the thing"` for `"- [ ] Do the thing"`.
93: 
94:         Raises:
95:             AssertionError: `.text` does not start with a well-formed
96:                 checkbox marker (see `_MARKER_PATTERN`).
97:         """
98:         match = _MARKER_PATTERN.match(self.text)
99:         assert match, f"TaskItem: expected a '- [ ]'/'- [x]' checkbox marker, got {self.text!r}"
100:         return match.group("description").strip()
101: 
102:     content: list[MarkdownParagraph] | None = None

(End of file - total 102 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "/home/user/src/biz.dfch.SpecMgr/.venv/bin/python -c \"\nfrom biz.dfch.specmgr.feat.models.v1 import parse_feat\nfor p in ['/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-33-vcr/README.md','/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/feat/data/feat_template.md']:\n    try:\n        doc = parse_feat(open(p, encoding='utf-8').read())\n        print('PARSE OK :', p.split('/')[-3])\n    except Exception as e:\n        print('PARSE FAIL:', p.split('/')[-3], '->', type(e).__name__, str(e).splitlines()[0][:120])\n\""
}
```

**Output:**

```
PARSE FAIL: feat -> ValidationError 1 validation error for Requirements
PARSE OK : feat

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 143.6s)

_Thinking:_

Very informative:

1. The **template parses correctly** (`PARSE OK: feat` for feat_template.md).
2. **feat-33-vcr does not parse** (`PARSE FAIL: feat-33-vcr -> ValidationError ... for Requirements`). In other words, the shipped feat-33-vcr README is actually not parseable by the feat model! This backs up my suspicion — the feat domain is silently skipping it. So I shouldn't model after feat-33-vcr's format; I should model after the **template's** format, which actually parses.

Now, about TaskItem: the regex is `_MARKER_PATTERN = re.compile(r"^\[( |x|X)\]\s*(?P<description>.*)$")` — a single-line match against `.text`. `MarkdownListItem.text` — how is this computed? For multi-line items, `.text` will contain newlines, and `_MARKER_PATTERN` uses `^\[( |x|X)\]\s*(?P<description>.*)$`, but by default `.` doesn't match newlines and `$` matches at end of string (or before a trailing newline). In other words, multi-line `.text` fails the match.

Wait, but the template has a single-line task item, and that parses correctly. My README has multi-line (wrapped) task items, and that fails. So the fix is: **each task item (and each requirement/ACC item) must be a single line.**

But wait — how does `MarkdownListItem.text` handle continuation lines? Let me reconsider the error. The error was that Task 0.1's item text was `[x] Task 0.1: Create the ...\n`dev` at...\nstatus: done (2026-08-31).` — so the list parser was folding the indented continuation lines into the item's text (including the newlines). Then `_MARKER_PATTERN.match` failed, because `.*$` doesn't span newlines... no, actually, `.match` is anchored at the start, and `(?P<description>.*)` — `.` doesn't match `\n`, so `.*` stops at the first newline, and then `$` needs to match. Without the MULTILINE flag, `$` only matches at end of string. Since there's more content after the first newline, `$` fails. So the overall match fails → AssertionError.

So the rule is: **task/requirement/ACC list items must be single-line** (no wrapped continuation lines within an item).

This also means that my multi-line wrapped `### Requirements` items, `### Acceptance Criteria` items, and task items all need to be single-line. Let me check which of my items are multi-line:

Requirements — I wrote them as long single bullets, but they may be wrapped. Let me check. Looking at what I wrote:

```
- REQ-001: Add a generic `@mcp.tool(name="delete")` in `general/tools/delete.py` with signature `def delete(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk","dec","sop","feat","vcr"]) -> str`; eleven private adapters `_delete_<d>(id_) -> str`; a shared `_ADAPTERS: dict[str, Callable[[str], str]]` dispatch table — mirroring `set_status.py`'s structure. On success it returns the deleted path as a `str` (the file path for the ten flat domains, the folder path for `feat`).
```

Is this single-line in the file? I wrote it as one long line (no explicit newlines in the middle). Good. But wait, did I wrap any of them? Let me check REQ-002, REQ-003, etc. I think I wrote them as single long lines. Let me verify. Actually, the parse error occurred at the **first** phase's **TaskItem** (Phase 0, Task 0.1), which means the Requirements, ACCs, Scope, Dependencies, Design Notes, Related Decisions all parsed correctly (the parser processes in order and reached the Task List). So the Requirements and ACCs must have been single-line.

Wait, the parser processes Plan's fields in order: overview, requirements, acceptance_criteria, scope, dependencies, design_notes, related_decisions, task_list. It failed at task_list (Phase 0 items). So everything before it parsed fine. So my Requirements and ACCs were fine (single-line). The problem is specifically the wrapped task items in the Task List.

Let me look at the actual task items I wrote. I wrapped them:

```
- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from
  `dev` at
  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) —
  status: done (2026-08-31).
```

Yes, multi-line. I need to make each task item a single line.

But this is a readability problem — single-line task items become very long lines. But that's the parseable format (matching the template, which has single-line items). Let me check the template's task items: `- [ ] Task 1.1: A short description of one task in this phase.` — single line. Yes.

So I need to rewrite all task items as single lines. Let me also double-check that none of my other list items (Included, Explicitly Out Of Scope, Depends On, Blocks, Related Decisions) are multi-line. Those are free-form `MarkdownSection4`/`MarkdownSection3` bullet lists — do they have the same single-line constraint? They are plain `MarkdownListItem`s (not TaskItems), and their `.text` may be able to handle multi-line. Let me check: `Included` is `MarkdownSection4` with free-form content. The bullets inside are just part of the section's text (free-form), not parsed as structured items. So multi-line is fine there. The constraint applies only to structurally parsed list items: Requirements (`RequirementItem`), Acceptance Criteria (`AcceptanceCriterionItem`/`TaskItem`), and Task List items (`TaskItem`).

Wait, but Requirements uses `RequirementItem(MarkdownListItem)` with `_REQUIREMENT_ITEM_PATTERN = re.compile(r"^REQ-\d{3}: (?P<description>.+)$")` — `.+` doesn't match newlines, so requirement items also need to be single-line. And they parsed correctly, so they must have been single-line. Good.

So the only fix needed: make all task items in the Task List single-line.

Let me reconsider: my task items have em-dashes and `—` status suffixes. As a single line it would look like:
`- [x] Task 0.1: Create the feat-36-delete worktree/branch from dev at /home/user/... (dev left untouched) — status: done (2026-08-31).`

That's long but fine. Let me rewrite the entire Task List section with single-line items.

Actually, let me reconsider the whole approach. Rather than hand-editing many lines, let me rewrite the README's Task List section (and verify nothing else is multi-line where it would break). Let me re-read the file I wrote, identify all multi-line task items, and fix them.

Let me re-read the task list portion of the file I wrote.

Actually, the cleanest thing is: rewrite the entire Task List section with single-line items. Let me use the edit tool to replace the multi-line task items. But there are many. Let me reconsider — maybe I should just rewrite the whole file with single-line task items. That's safest. But the file is large.

Alternatively, I could reduce the wrapping. Let me identify exactly which items are multi-line. From what I wrote, all task items in Phases 1–5 are wrapped across multiple lines, plus Phase 0's items. Let me just rewrite the entire Task List section.

Let me re-read the current Task List section to get the exact text for the edit.

Actually, let me rewrite the whole file to be safe and consistent, making all structurally-parsed list items single-line. Let me carefully reconstruct it.

Wait — rewriting the whole file is risky in terms of introducing new errors. Let me do a targeted edit of just the Task List section instead, since that's the only part that failed. Let me read the exact current text of the Task List section.

Let me read the file's task list section.

Key finding: the **template parses** but the shipped **feat-33-vcr README does not** — so I must follow the template's format, and structurally-parsed list items (Requirements/ACCs/Task items) must be **single-line**. My Requirements/ACCs parsed fine; only the wrapped Task List items broke it. Let me read the exact Task List text and fix it.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md",
  "offset": 300,
  "limit": 80
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md</path>
<type>file</type>
<content>
300: - `id`: the only free-form input. Two independent layers stop injection:
301:   1. **Format validation** (`validate_id`, before any I/O): no `/`, `\`, or `..`
302:      (`assert_no_traversal`), plus a strict domain format (canonical UUID for the ten
303:      UUID domains; `feat-NNN-slug` for `feat`). A value like `../../etc/passwd` fails
304:      both the traversal and the format checks and is rejected with a `ValueError`
305:      before the filesystem is touched.
306:   2. **Containment** (`assert_within`, after resolution, inside the lock): the resolved
307:      path must be `is_relative_to` the domain's base directory. This is defense-in-depth
308:      against any future gap in layer 1 (e.g. a domain whose resolver builds a path from
309:      the id, as `feat` does).
310: - The ten flat domains' resolvers (`find_<d>_path`) scan and compare parsed ids rather
311:   than joining the id into a path, so they are already injection-safe; the `feat`
312:   resolver (`find_feat_path_by_id`) *does* join `base_dir / id / README.md`, which is
313:   precisely why the two-layer guard matters and is why `assert_feat_id` +
314:   `assert_within` are both applied for `feat`.
315: 
316: #### 6. Error contract (REQ-005)
317: 
318: | Condition | Raised | Where | Filesystem touched? |
319: |---|---|---|---|
320: | `id` has `/`, `\`, `..`, or wrong format for `type` | `ValueError` | public `delete`, via `validate_id` | No (before dispatch) |
321: | unknown `type` string (Python-level) | `ValueError` | `validate_id` | No |
322: | no document with `id` in `type`'s domain | domain `XNotFoundError` | adapter, via `load_by_id` | No (read-only scan) |
323: | resolved path escapes base dir | `ValueError` | adapter, via `assert_within` | No |
324: | `unlink`/`rmtree` I/O failure | `DeleteError` (wraps `OSError`) | adapter | Partial at most |
325: 
326: #### 7. The new ADR (REQ-007)
327: 
328: Created via the `create_adr` MCP tool (per ADR 898bfcd0, ADRs are authored only
329: through structured tools), then `specmgr adr-toc`. Title: **"Replace domain-specific
330: delete tools with a generic type-dispatched delete tool"**. Suggested body:
331: - *Context and Problem Statement*: eleven unimplemented `delete_<d>` stubs inflate the
332:   tool surface; no delete path-safety exists; the issue (#36) asks for one generic,
333:   safe, locked delete.
334: - *Decision Drivers*: minimal tool surface; explicit `type` keeps id resolution
335:   single-domain; injection safety; reuse of existing per-domain locks/resolvers;
336:   filesystem-is-source-of-truth.
337: - *Considered Options*: (1) generic `delete(id, type)` with per-domain adapters + a
338:   reusable `_path_safety` module (chosen); (2) implement each `delete_<d>` stub
339:   independently (rejected: eleven near-duplicates, no shared safety); (3) uuid-only
340:   id resolution scanning all domains (rejected: cross-domain UUID ambiguity, full-dir
341:   scan on the write path — same reasons ADR 36905d5b rejected it for `update`).
342: - *Decision Outcome*: Option 1; ADR excluded (no `delete_adr` ever existed; deleting an
343:   ADR risks breaking other ADRs' "superseded by X" references); convention — every
344:   current and future domain implements a `delete` adapter in the generic tool, never a
345:   per-domain `delete_<d>` tool.
346: - *Consequences*: breaking (eleven tools removed, one added — the 0.x MCP tool list is
347:   the only client contract, recorded in `CHANGELOG.md`); `get`/`update`/`set_status`
348:   can now adopt `_path_safety` for their own injection protection in a future change.
349: - *More Information*: this feature plan; related ADRs 36905d5b, 8cf940c5, 33c5ab08,
350:   898bfcd0.
351: 
352: #### 8. Documentation propagation (REQ-007)
353: 
354: - `AGENTS.md`: in each of the eleven per-domain Status bullets, replace the
355:   "`delete_<d>` stub" / "`delete_<d>` (stub, not yet implemented)" mention with a note
356:   that deletion goes through the generic `delete` tool (`type="<d>"`); delete the
357:   "Still genuinely missing" bullet "`delete_req`/…/`delete_vcr` are stubs, not yet
358:   implemented"; in the `general/` bullet, add `delete` to the `general/tools/` list and
359:   add a sentence that all eleven whole-body domains implement a `delete` adapter there
360:   (ADR-excluded). Keep the `ac` "future domain" convention note in sync (a future domain
361:   adds a `delete` adapter too).
362: - `server.py` module docstring: remove the eleven per-domain `delete_<d>` stub mentions
363:   from the domain tool paragraphs; add `delete` to the "General tools
364:   (`general/tools/`)" paragraph describing it (eleven whole-body domains, ADR excluded,
365:   returns the deleted path, safety/lock/error contract in one line).
366: - `CHANGELOG.md`: under `[Unreleased]`, a `### Changed`/`### Removed` entry: removed the
367:   eleven `delete_<d>` stub tools; added the generic `delete` tool; added reusable
368:   `general/tools/_path_safety.py`. Mark breaking (0.x).
369: - Regenerate `docs/`: `specmgr docs` (API docs + `docs/GENERATED.md`), `specmgr
370:   mcp-docs` (`docs/MCP.md`), `specmgr adr-toc` (`docs/adr/README.md`) — each run twice
371:   to confirm a stable fixed point (no drift).
372: 
373: #### 9. Test design (REQ-008)
374: 
375: `tests/general/tools/test__path_safety.py` — pure unit tests, no filesystem:
376: - `assert_no_traversal`: accepts a plain id; rejects `""`, `"../x"`, `"a/b"`, `"a\b"`,
377:   `".."`, `"a/../b"` (each a `ValueError`).
378: - `assert_uuid`: accepts a canonical lowercase UUID; rejects uppercase, a 31-char
379:   string, a string with `/`, and a `feat-1-x` string.

(Showing lines 300-379 of 540. Use offset=380 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 61.9s)

_Thinking:_

The bullet points in the Design Notes are free-form (inside `MarkdownSection3`/`MarkdownSection4`), so being multi-line is fine — they parsed without any issue. The only problem is the items in the Task List (the `TaskItem`s). Let me read the Task List section and rewrite those items into single lines.

Let me read from around line 395 (the Task List) to the end.

Design Notes bullets are free-form (parsed fine). Let me read the Task List section to rewrite its items as single lines.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md",
  "limit": 75,
  "offset": 395
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md</path>
<type>file</type>
<content>
395: - unknown id: assert the domain `XNotFoundError`.
396: - I/O failure: mock `Path.unlink` (or `shutil.rmtree` for `feat`) to raise `OSError`;
397:   assert `DeleteError` is raised and its message contains the path.
398: - locking: spy/mock the domain `<d>_lock` and assert it is entered for the delete.
399: 
400: The eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files are deleted (REQ-002);
401: no replacement per-domain delete tests are added — coverage moves entirely to
402: `tests/general/tools/test_delete.py`.
403: 
404: ### Related Decisions
405: 
406: - New ADR (created in Phase 4, REQ-007): "Replace domain-specific delete tools with a
407:   generic type-dispatched delete tool" — the architecture-level record of this feature's
408:   decision and of the forward convention that every domain implements a `delete` adapter
409:   in the generic tool.
410: - ADR 36905d5b-8057-4294-8665-c7eed5534db0 — the `update`/`set_status` generic-tool
411:   precedent this feature extends with `delete`.
412: - ADR 8cf940c5-3100-485c-a12d-14b59b631712 — `feat`'s folder-per-document addressing,
413:   which drives `feat`'s distinct adapter and id format.
414: - ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 — filesystem is the sole source of truth
415:   (delete removes the on-disk file; there is no separate deletion record).
416: - ADR 898bfcd0-85f9-462f-93a8-747bda4166c8 — ADRs are authored/edited only through MCP
417:   structured tools (governs Phase 4's `create_adr` step).
418: 
419: ### Task List
420: 
421: #### Phase 0: Worktree, branch, and design plan (designer)
422: 
423: - [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from `dev` at
424:   `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) —
425:   status: done (2026-08-31).
426: - [x] Task 0.2: Author this feature README (the full design) — status: done (2026-08-31).
427: 
428: #### Phase 1: Reusable path-safety module (Phase-Orchestrator)
429: 
430: - [ ] Task 1.1: Add `general/tools/_path_safety.py` exactly per Design Notes §1
431:   (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`,
432:   `assert_within`; `ValueError` on failure; no I/O) — depends on: Task 0.2 —
433:   status: not-started.
434: - [ ] Task 1.2: Add `tests/general/tools/test__path_safety.py` per Design Notes §9 —
435:   depends on: Task 1.1 — status: not-started.
436: 
437: #### Phase 2: The generic delete tool (Phase-Orchestrator)
438: 
439: - [ ] Task 2.1: Add `general/tools/delete.py` per Design Notes §2–§6 (`DeleteError`,
440:   eleven `_delete_<d>` adapters, `_ADAPTERS`, `@mcp.tool(name="delete")` public
441:   function calling `validate_id` then dispatching) — depends on: Task 1.1 —
442:   status: not-started.
443: - [ ] Task 2.2: Add `tests/general/tools/test_delete.py` per Design Notes §9 —
444:   depends on: Task 2.1 — status: not-started.
445: 
446: #### Phase 3: Retire the eleven delete stubs (Phase-Orchestrator)
447: 
448: - [ ] Task 3.1: Delete the eleven `src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` files —
449:   depends on: Task 2.1 — status: not-started.
450: - [ ] Task 3.2: In each of the eleven `<d>/tools/__init__.py`, remove the
451:   `from .delete_<d> import delete_<d>` line, the `delete_<d>` `__all__` entry, and the
452:   stub mention in the module docstring — depends on: Task 3.1 — status: not-started.
453: - [ ] Task 3.3: Delete the eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files —
454:   depends on: Task 3.2 — status: not-started.
455: 
456: #### Phase 4: Decision and documentation propagation (Phase-Orchestrator)
457: 
458: - [ ] Task 4.1: Create the new ADR via the `create_adr` MCP tool per Design Notes §7,
459:   set it `accepted`, and run `specmgr adr-toc` — depends on: Task 3.3 —
460:   status: not-started.
461: - [ ] Task 4.2: Update `AGENTS.md` per Design Notes §8 — depends on: Task 3.3 —
462:   status: not-started.
463: - [ ] Task 4.3: Update `server.py`'s module docstring per Design Notes §8 — depends on:
464:   Task 3.3 — status: not-started.
465: - [ ] Task 4.4: Add the `CHANGELOG.md` `[Unreleased]` entry per Design Notes §8 —
466:   depends on: Task 3.3 — status: not-started.
467: - [ ] Task 4.5: Regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`, `specmgr
468:   adr-toc`), each run twice to confirm no drift — depends on: Tasks 4.1–4.4 —
469:   status: not-started.

(Showing lines 395-469 of 540. Use offset=470 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 60.6s)

_Thinking:_

I need to rewrite all the task items as single lines. Let me replace the entire Task List section. I'll read the remaining part (lines 470–540) to get the end of the Task List (Phase 5) and the Progress section, then do the replacement.

Actually, I'll replace from line 419 (### Task List) through the end of Phase 5. Let me read the rest.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md",
  "limit": 30,
  "offset": 470
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md</path>
<type>file</type>
<content>
470: 
471: #### Phase 5: Quality gate and sign-off (Phase-Orchestrator)
472: 
473: - [ ] Task 5.1: Run the full gate — `ruff format --check`, `ruff check`, `vulture
474:   src/ whitelist.py --min-confidence 60`, the full `unittest` suite, and advisory
475:   `pylint` — and fix any failures — depends on: Task 4.5 — status: not-started.
476: - [ ] Task 5.2: Walk ACC-001..ACC-008, mark each `[x]` with a concrete justification
477:   (test file / tool / doc proving it), update Current Status, and bump this README's
478:   frontmatter `status`/`updated` — depends on: Task 5.1 — status: not-started.
479: 
480: ## Progress
481: 
482: ### Current Status
483: 
484: **As of 2026-08-31**: Design complete (Phase 0). The `feat-36-delete` worktree/branch
485: was cut from `dev` and this README captures the full, implementer-ready design: the
486: generic `delete` tool, the reusable `_path_safety` module, the eleven stub removals,
487: the locking/error contract, the new ADR, and the documentation propagation. No source
488: code has been written yet — implementation (Phases 1–5) is delegated to the
489: Phase-Orchestrator. All three open design questions were resolved with the requester:
490: ADR is excluded (eleven whole-body domains only), `feat` deletes its whole folder, and
491: the tool returns the deleted path as a `str`.
492: 
493: ### Blockers
494: 
495: - None currently.
496: 
497: ### Updates
498: 
499: <!-- Newest entry first -- prepend new entries directly below this comment. -->

(Showing lines 470-499 of 540. Use offset=500 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 179.8s)

_Thinking:_

Next, let's replace the entire task list section (from `### Task List` to the end of Phase 5, right before `## Progress`) with single-line task items. We'll do the edit by replacing the old multi-line task list block with the new single-line one.

The old block starts at line 419 with `### Task List` and ends at line 478 (Task 5.2). Let's construct the replacement content.

New task list with single-line items:

```
### Task List

#### Phase 0: Worktree, branch, and design plan (designer)

- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from `dev` at `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) — status: done (2026-08-31).
- [x] Task 0.2: Author this feature README (the full design) — status: done (2026-08-31).

#### Phase 1: Reusable path-safety module (Phase-Orchestrator)

- [ ] Task 1.1: Add `general/tools/_path_safety.py` exactly per Design Notes §1 (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, `assert_within`; `ValueError` on failure; no I/O) — depends on: Task 0.2 — status: not-started.
- [ ] Task 1.2: Add `tests/general/tools/test__path_safety.py` per Design Notes §9 — depends on: Task 1.1 — status: not-started.

#### Phase 2: The generic delete tool (Phase-Orchestrator)

- [ ] Task 2.1: Add `general/tools/delete.py` per Design Notes §2–§6 (`DeleteError`, eleven `_delete_<d>` adapters, `_ADAPTERS`, `@mcp.tool(name="delete")` public function calling `validate_id` then dispatching) — depends on: Task 1.1 — status: not-started.
- [ ] Task 2.2: Add `tests/general/tools/test_delete.py` per Design Notes §9 — depends on: Task 2.1 — status: not-started.

#### Phase 3: Retire the eleven delete stubs (Phase-Orchestrator)

- [ ] Task 3.1: Delete the eleven `src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` files — depends on: Task 2.1 — status: not-started.
- [ ] Task 3.2: In each of the eleven `<d>/tools/__init__.py`, remove the `from .delete_<d> import delete_<d>` line, the `delete_<d>` `__all__` entry, and the stub mention in the module docstring — depends on: Task 3.1 — status: not-started.
- [ ] Task 3.3: Delete the eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files — depends on: Task 3.2 — status: not-started.

#### Phase 4: Decision and documentation propagation (Phase-Orchestrator)

- [ ] Task 4.1: Create the new ADR via the `create_adr` MCP tool per Design Notes §7, set it `accepted`, and run `specmgr adr-toc` — depends on: Task 3.3 — status: not-started.
- [ ] Task 4.2: Update `AGENTS.md` per Design Notes §8 — depends on: Task 3.3 — status: not-started.
- [ ] Task 4.3: Update `server.py`'s module docstring per Design Notes §8 — depends on: Task 3.3 — status: not-started.
- [ ] Task 4.4: Add the `CHANGELOG.md` `[Unreleased]` entry per Design Notes §8 — depends on: Task 3.3 — status: not-started.
- [ ] Task 4.5: Regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`, `specmgr adr-toc`), each run twice to confirm no drift — depends on: Tasks 4.1–4.4 — status: not-started.

#### Phase 5: Quality gate and sign-off (Phase-Orchestrator)

- [ ] Task 5.1: Run the full gate — `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, the full `unittest` suite, and advisory `pylint` — and fix any failures — depends on: Task 4.5 — status: not-started.
- [ ] Task 5.2: Walk ACC-001..ACC-008, mark each `[x]` with a concrete justification (test file / tool / doc proving it), update Current Status, and bump this README's frontmatter `status`/`updated` — depends on: Task 5.1 — status: not-started.
```

Wait a moment — there's a subtle point about TaskItem's `content` field: `content: list[MarkdownParagraph] | None = None`. In other words, TaskItem can have additional content paragraphs. But that's for the detailed content of tasks. It's not needed this time.

Now, one concern: single-line items containing backticks and special characters. The `TaskItem` marker regex `^\[( |x|X)\]\s*(?P<description>.*)$` — description is `.*` (single line). No problem.

However, I need to double-check: do the Requirements and ACC items also need to be single-line? Since they were parsed correctly, they were single-line. Good. Just to be safe, let me re-examine the Requirements section to confirm they are single-line. Actually, the parser passed through Requirements and ACC and failed at Task List, so they're fine.

But wait — let me reconsider. Let me check: did the parser really pass through Requirements? The error was `1 validation error for Phase`, and the input was `{'items': [- [x] Task 0.1...`. In other words, it reached the Phase (Task List). Therefore Requirements, ACC, Scope, Dependencies, Design Notes, and Related Decisions were all parsed normally. Good.

Now, let me also reconsider that the bullets in Design Notes §7 (the ADR body suggestions) and §8 are multi-line — those are free-form section text, and they were parsed normally. No problem.

So, the only thing that needs fixing is the Task List items. Let me replace them.

I'll use the edit tool to replace the entire task list block. oldString needs to match exactly. Let me construct oldString from the content I read (lines 419–478). That's a big block. Let's do it carefully.

Actually, to reduce the risk of mismatches, I could also replace each phase's task items individually. But the entire block is cleaner. Let me construct the exact oldString.

Let me get the exact text. From what I read:

```
### Task List

#### Phase 0: Worktree, branch, and design plan (designer)

- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from `dev` at
  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) —
  status: done (2026-08-31).
- [x] Task 0.2: Author this feature README (the full design) — status: done (2026-08-31).

#### Phase 1: Reusable path-safety module (Phase-Orchestrator)

- [ ] Task 1.1: Add `general/tools/_path_safety.py` exactly per Design Notes §1
  (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`,
  `assert_within`; `ValueError` on failure; no I/O) — depends on: Task 0.2 —
  status: not-started.
- [ ] Task 1.2: Add `tests/general/tools/test__path_safety.py` per Design Notes §9 —
  depends on: Task 1.1 — status: not-started.
...
```

This is a large block. Let me do the replacement with the edit tool. I'll include the entire block from `### Task List` to the end of Task 5.2.

Let me carefully write oldString and newString. oldString must match the file contents exactly, including indentation (2 spaces for continuation lines).

I'll do it in one edit. Let me construct it.

Now I'll replace the entire Task List with single-line items (the only parse-breaking part).

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md",
  "oldString": "### Task List\n\n#### Phase 0: Worktree, branch, and design plan (designer)\n\n- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from `dev` at\n  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) —\n  status: done (2026-08-31).\n- [x] Task 0.2: Author this feature README (the full design) — status: done (2026-08-31).\n\n#### Phase 1: Reusable path-safety module (Phase-Orchestrator)\n\n- [ ] Task 1.1: Add `general/tools/_path_safety.py` exactly per Design Notes §1\n  (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`,\n  `assert_within`; `ValueError` on failure; no I/O) — depends on: Task 0.2 —\n  status: not-started.\n- [ ] Task 1.2: Add `tests/general/tools/test__path_safety.py` per Design Notes §9 —\n  depends on: Task 1.1 — status: not-started.\n\n#### Phase 2: The generic delete tool (Phase-Orchestrator)\n\n- [ ] Task 2.1: Add `general/tools/delete.py` per Design Notes §2–§6 (`DeleteError`,\n  eleven `_delete_<d>` adapters, `_ADAPTERS`, `@mcp.tool(name=\"delete\")` public\n  function calling `validate_id` then dispatching) — depends on: Task 1.1 —\n  status: not-started.\n- [ ] Task 2.2: Add `tests/general/tools/test_delete.py` per Design Notes §9 —\n  depends on: Task 2.1 — status: not-started.\n\n#### Phase 3: Retire the eleven delete stubs (Phase-Orchestrator)\n\n- [ ] Task 3.1: Delete the eleven `src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` files —\n  depends on: Task 2.1 — status: not-started.\n- [ ] Task 3.2: In each of the eleven `<d>/tools/__init__.py`, remove the\n  `from .delete_<d> import delete_<d>` line, the `delete_<d>` `__all__` entry, and the\n  stub mention in the module docstring — depends on: Task 3.1 — status: not-started.\n- [ ] Task 3.3: Delete the eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files —\n  depends on: Task 3.2 — status: not-started.\n\n#### Phase 4: Decision and documentation propagation (Phase-Orchestrator)\n\n- [ ] Task 4.1: Create the new ADR via the `create_adr` MCP tool per Design Notes §7,\n  set it `accepted`, and run `specmgr adr-toc` — depends on: Task 3.3 —\n  status: not-started.\n- [ ] Task 4.2: Update `AGENTS.md` per Design Notes §8 — depends on: Task 3.3 —\n  status: not-started.\n- [ ] Task 4.3: Update `server.py`'s module docstring per Design Notes §8 — depends on:\n  Task 3.3 — status: not-started.\n- [ ] Task 4.4: Add the `CHANGELOG.md` `[Unreleased]` entry per Design Notes §8 —\n  depends on: Task 3.3 — status: not-started.\n- [ ] Task 4.5: Regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`, `specmgr\n  adr-toc`), each run twice to confirm no drift — depends on: Tasks 4.1–4.4 —\n  status: not-started.\n\n#### Phase 5: Quality gate and sign-off (Phase-Orchestrator)\n\n- [ ] Task 5.1: Run the full gate — `ruff format --check`, `ruff check`, `vulture\n  src/ whitelist.py --min-confidence 60`, the full `unittest` suite, and advisory\n  `pylint` — and fix any failures — depends on: Task 4.5 — status: not-started.\n- [ ] Task 5.2: Walk ACC-001..ACC-008, mark each `[x]` with a concrete justification\n  (test file / tool / doc proving it), update Current Status, and bump this README's\n  frontmatter `status`/`updated` — depends on: Task 5.1 — status: not-started.",
  "newString": "### Task List\n\n#### Phase 0: Worktree, branch, and design plan (designer)\n\n- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from `dev` at `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) — status: done (2026-08-31).\n- [x] Task 0.2: Author this feature README (the full design) — status: done (2026-08-31).\n\n#### Phase 1: Reusable path-safety module (Phase-Orchestrator)\n\n- [ ] Task 1.1: Add `general/tools/_path_safety.py` exactly per Design Notes §1 (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, `assert_within`; `ValueError` on failure; no I/O) — depends on: Task 0.2 — status: not-started.\n- [ ] Task 1.2: Add `tests/general/tools/test__path_safety.py` per Design Notes §9 — depends on: Task 1.1 — status: not-started.\n\n#### Phase 2: The generic delete tool (Phase-Orchestrator)\n\n- [ ] Task 2.1: Add `general/tools/delete.py` per Design Notes §2–§6 (`DeleteError`, eleven `_delete_<d>` adapters, `_ADAPTERS`, `@mcp.tool(name=\"delete\")` public function calling `validate_id` then dispatching) — depends on: Task 1.1 — status: not-started.\n- [ ] Task 2.2: Add `tests/general/tools/test_delete.py` per Design Notes §9 — depends on: Task 2.1 — status: not-started.\n\n#### Phase 3: Retire the eleven delete stubs (Phase-Orchestrator)\n\n- [ ] Task 3.1: Delete the eleven `src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` files — depends on: Task 2.1 — status: not-started.\n- [ ] Task 3.2: In each of the eleven `<d>/tools/__init__.py`, remove the `from .delete_<d> import delete_<d>` line, the `delete_<d>` `__all__` entry, and the stub mention in the module docstring — depends on: Task 3.1 — status: not-started.\n- [ ] Task 3.3: Delete the eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files — depends on: Task 3.2 — status: not-started.\n\n#### Phase 4: Decision and documentation propagation (Phase-Orchestrator)\n\n- [ ] Task 4.1: Create the new ADR via the `create_adr` MCP tool per Design Notes §7, set it `accepted`, and run `specmgr adr-toc` — depends on: Task 3.3 — status: not-started.\n- [ ] Task 4.2: Update `AGENTS.md` per Design Notes §8 — depends on: Task 3.3 — status: not-started.\n- [ ] Task 4.3: Update `server.py`'s module docstring per Design Notes §8 — depends on: Task 3.3 — status: not-started.\n- [ ] Task 4.4: Add the `CHANGELOG.md` `[Unreleased]` entry per Design Notes §8 — depends on: Task 3.3 — status: not-started.\n- [ ] Task 4.5: Regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`, `specmgr adr-toc`), each run twice to confirm no drift — depends on: Tasks 4.1–4.4 — status: not-started.\n\n#### Phase 5: Quality gate and sign-off (Phase-Orchestrator)\n\n- [ ] Task 5.1: Run the full gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, the full `unittest` suite, and advisory `pylint`) and fix any failures — depends on: Task 4.5 — status: not-started.\n- [ ] Task 5.2: Walk ACC-001..ACC-008, mark each `[x]` with a concrete justification (test file / tool / doc proving it), update Current Status, and bump this README's frontmatter `status`/`updated` — depends on: Task 5.1 — status: not-started."
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 77.5s)

_Thinking:_

Now, let's re-verify the parsing. However, I also need to check whether the Requirements and ACC items might be multi-line. The parser previously passed through those (it failed at the task list), so they should be fine. But just to be safe, let's also check whether the Requirements and ACC items are single-line — if the previous parse reached the task list, then those have already been verified. Alright, let's re-run the parse.

Re-validating the parse after the fix.

**Tool: bash**

**Input:**

```json
{
  "command": "/home/user/src/biz.dfch.SpecMgr/.venv/bin/python -c \"\nfrom biz.dfch.specmgr.feat.models.v1 import parse_feat\np = '/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/README.md'\ndoc = parse_feat(open(p, encoding='utf-8').read())\nprint('PARSE OK')\nprint('id        =', doc.frontmatter.id)\nprint('type      =', doc.frontmatter.type)\nprint('status    =', doc.frontmatter.status)\nprint('version   =', doc.frontmatter.version)\npl = doc.body.plan\nprint('reqs      =', len(pl.requirements.items))\nprint('accs      =', len(pl.acceptance_criteria.items))\nprint('phases    =', [(ph.number, ph.title, len(ph.items)) for ph in pl.task_list.phases])\nprint('dep_on    =', bool(pl.dependencies and pl.dependencies.depends_on))\nprint('blocks    =', bool(pl.dependencies and pl.dependencies.blocks))\nprint('design    =', bool(pl.design_notes and pl.design_notes.text.strip()))\nprint('related   =', bool(pl.related_decisions and pl.related_decisions.text.strip()))\npr = doc.body.progress\nprint('updates   =', [(u.timestamp, u.title) for u in pr.updates.updates])\nprint('decisions =', [(d.timestamp, d.title) for d in pr.decisions_made.decisions] if pr.decisions_made else None)\n# round-trip render check\ns = str(doc)\nprint('roundtrip len =', len(s))\n\"\n"
}
```

**Output:**

```
PARSE OK
id        = feat-36-delete
type      = feat
status    = planning
version   = 1.0.0
reqs      = 8
accs      = 8
phases    = [(0, 'Worktree, branch, and design plan (designer)', 2), (1, 'Reusable path-safety module (Phase-Orchestrator)', 2), (2, 'The generic delete tool (Phase-Orchestrator)', 2), (3, 'Retire the eleven delete stubs (Phase-Orchestrator)', 3), (4, 'Decision and documentation propagation (Phase-Orchestrator)', 5), (5, 'Quality gate and sign-off (Phase-Orchestrator)', 2)]
dep_on    = True
blocks    = True
design    = True
related   = True
updates   = [('2026-08-31 15:37:40.000Z', 'Feature designed; worktree and plan authored (Phase 0 complete)')]
decisions = [('2026-08-31 15:37:40.000Z', 'ADR excluded from the generic delete tool'), ('2026-08-31 15:37:40.000Z', 'Injection prevention is a reusable, non-I/O module'), ('2026-08-31 15:37:40.000Z', '`feat` deletes its whole folder; the tool returns the deleted path')]
roundtrip len = 34743

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 149.1s)

_Thinking:_

The README currently parses correctly against the feat schema:

- id = feat-36-delete ✓
- type = feat ✓
- status = planning ✓
- version = 1.0.0 ✓
- 8 requirements ✓
- 8 ACCs ✓
- 6 phases (0-5), task counts: 2, 2, 2, 3, 5, 2 = 16 tasks ✓
- depends_on, blocks, design_notes, related_decisions all present ✓
- updates and decisions parse with correct timestamps ✓
- round-trip rendering works (34743 chars) ✓

Next, let me verify that the file is also stable against `mdformat` (the repo uses `specmgr_mdformat` / mdformat). Actually, let me check whether this README matches the format the repo's mdformat would produce. However, this is a `.specmgr/feat` document, and AGENTS.md states that no CI/pre-commit enforcement exists for `.specmgr/` content. So mdformat is not strictly required. That said, for consistency, let me verify whether it's already clean under mdformat. Actually, let me not over-engineer this — feat documents aren't formatted in CI. But it wouldn't hurt to check whether mdformat would make changes. Let me run the mdformat tool against it and see if it reports "changed" or not. Actually, `specmgr_mdformat` formats markdown files in place. Let me check whether it's idempotent / already clean.

Hmm, but if I run mdformat and it makes changes, that's fine (it just reformats). However, reformatting could re-wrap lines, potentially breaking the single-line task items! mdformat by default doesn't re-wrap text (it preserves line breaks within paragraphs unless a wrap option is set). Actually, mdformat might normalize things. Let me be careful — I don't want to run mdformat and risk breaking the parse. The template and existing features are the ground truth. My file parses, and that's the key requirement. Let me skip running mdformat on this to avoid any risk of re-wrapping.

Actually, let me reconsider. The repo has a `specmgr_mdformat` MCP tool and mdformat as a pre-commit hook, but only for `docs/adr/**/*.md` (adr-toc hook) and src. Let me check the pre-commit config for whether .specmgr files get mdformat'd. AGENTS.md explicitly states: "No CI/pre-commit enforcement exists for `.specmgr/` content". So mdformat is not applied to feature READMEs. Good — I don't need to worry about it. My file parses, and that's what matters for the feat tools (get_feat, list_feat, compact_history, update).

Next, let me confirm the worktree/branch state is clean and verify that dev is untouched. Also, I should decide whether to git add/commit the README. The user said "do not commit anything to 'dev'." They didn't say not to commit to feat-36-delete. But should I commit the README to the feat-36-delete branch?

Let me think about the workflow. The user wants the feature to exist on a separate worktree branch. The README (plan) is the deliverable. Should I commit it? The instruction was "as soon as you enter build mode, create a git worktree branch and write the plan." It doesn't explicitly say to commit. However, leaving the README uncommitted in the worktree means it won't persist if the worktree is discarded, and git won't track it.

Given the repo's conventions (conventional commits, and features are developed on branches), I think committing the README to the `feat-36-delete` branch is the right move — it records the design on the branch. And it satisfies "do not commit anything to dev" (I'm committing to feat-36-delete, not dev).

But wait — the guidance says "never commit changes unless the user explicitly asks you to." The user did not explicitly ask me to commit. They said "create a git worktree branch and write the plan." Hmm. Writing the plan to a file is explicit. Committing is not explicit.

Let me reconsider. The system prompt is emphatic: "NEVER commit changes unless the user explicitly asks you to. It is VERY IMPORTANT to only commit when explicitly asked, otherwise the user will feel that you are being too proactive."

The user said "do not commit anything to 'dev'." This is a constraint about dev, not a request to commit to feat-36-delete. So I should not commit — I should just create the worktree/branch and write the plan file (leave it uncommitted, or ask).

Actually, let me re-read the exact wording: "Do not commit anything in 'dev'. As soon as you are in build mode you create the git worktree branch and write the plan."

So the explicit instructions are:

1. Do not commit to dev. (Constraint)
2. Create the git worktree branch. (Done)
3. Write the plan. (Done — README written)

There is no explicit request to commit the plan to feat-36-delete. Given the strong "never commit unless explicitly asked" guidance, I should leave the README uncommitted and inform the user, letting them decide whether to commit (or ask for confirmation). That's the safest and most correct behavior.

But leaving it uncommitted is a bit awkward, because then the "plan" isn't recorded in git. However, the user is clearly managing this workflow (they'll have the Phase-Orchestrator implement, and presumably commit). And they were explicit about not committing to dev. Let me leave the README as an untracked/new file in the worktree and report the state, offering to commit to feat-36-delete if desired.

Actually, let me reconsider whether to commit. The phrase "create the git worktree branch and write the plan" — the deliverable is the branch + the plan file. A branch with no commits is just a ref pointing to dev's HEAD, plus the untracked README. That's fine as a working state. The user (or the orchestrator) will commit as work progresses. Given the explicit "never commit unless asked" rule and the fact that the user only constrained dev (didn't request a commit to feat-36-delete), I'll leave it uncommitted.

Hmm, but let me reconsider just one more time. If I don't commit, then the feat-36-delete branch is identical to dev (same HEAD), and the README is an untracked file in the worktree. If the user then runs the Phase-Orchestrator, the orchestrator would commit the README + implementation. That's a reasonable flow. And it respects "don't commit unless asked."

Decision: leave the README uncommitted. Verify the worktree shows it as a new untracked file, confirm dev is untouched, and report.

Let me check git status in the worktree to confirm the README is there and untracked, and confirm dev is clean/untouched.

Let me also double-check: is there any chance the user expects a commit? They said "write the plan." Writing = creating the file. I've done that. I'll report clearly and offer to commit.

Let me verify the final state.

README parses cleanly against the feat schema (8 REQs, 8 ACCs, 6 phases, 16 tasks, round-trips). Let me verify the final worktree/branch state and that `dev` is untouched.

**Tool: bash**

**Input:**

```json
{
  "command": "echo \"=== feat-36-delete worktree status ===\" && git -C /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete status -sb && echo && echo \"=== branch vs dev (should be same HEAD, no commits ahead) ===\" && git -C /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete log --oneline -1 && git -C /home/user/src/biz.dfch.SpecMgr log --oneline -1 dev && echo && echo \"=== dev working tree (main checkout) must be clean ===\" && git -C /home/user/src/biz.dfch.SpecMgr status -s && echo \"(clean if no output above)\" && echo && echo \"=== new plan file present ===\" && ls -la /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete/.specmgr/feat/feat-36-delete/"
}
```

**Output:**

```
=== feat-36-delete worktree status ===
## feat-36-delete
?? .specmgr/feat/feat-36-delete/

=== branch vs dev (should be same HEAD, no commits ahead) ===
6d6bf2f chore(release): bump version to v0.15.0
6d6bf2f chore(release): bump version to v0.15.0

=== dev working tree (main checkout) must be clean ===
(clean if no output above)

=== new plan file present ===
total 44
drwxrwxr-x  2 user user  4096 Aug 31 17:53 .
drwxrwxr-x 22 user user  4096 Aug 31 17:46 ..
-rw-rw-r--  1 user user 34868 Aug 31 18:04 README.md

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 67.5s)

_Thinking:_

Everything is in order:

- `feat-36-delete` worktree is on branch `feat-36-delete`, HEAD = `6d6bf2f` (same as dev, no commits ahead).
- New untracked file: `.specmgr/feat/feat-36-delete/README.md` (the plan).
- `dev` (main checkout) is clean and unchanged.
- README parses against the feat schema.

Now, per the "never commit unless explicitly asked" guidance, I'll leave the README uncommitted. The user only constrained dev. I'll report the state and offer to commit to feat-36-delete if they want.

Let me update the todos to completed.

Let me finalize the todo list.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Create git worktree + branch feat-36-delete from dev (dev untouched)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Author .specmgr/feat/feat-36-delete/README.md design plan in the worktree",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Verify worktree/branch state and that dev is untouched",
      "status": "completed",
      "priority": "medium"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Create git worktree + branch feat-36-delete from dev (dev untouched)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Author .specmgr/feat/feat-36-delete/README.md design plan in the worktree",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Verify worktree/branch state and that dev is untouched",
    "status": "completed",
    "priority": "medium"
  }
]
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 86.1s)

_Thinking:_

Done. Let me give the user a concise final report.

I'll summarize the following:

- Created a worktree at /home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete, branch feat-36-delete (branched from dev @ 6d6bf2f), dev unchanged.
- Created the design README at .specmgr/feat/feat-36-delete/README.md (within the worktree), validated against the feat schema.
- Key design points (reusable \_path_safety, 11 domains, feat's rmtree, path returns, lock, errors, ADR, docs).
- README is untracked / uncommitted (per the policy of not committing unless instructed). Suggest committing to feat-36-delete.

Per the instructions, I'll keep it concise (fewer than 4 lines unless detail is requested — but this is a task-completion report, and the user will want to know the state and the offer to commit). I'll wrap it up briefly.

Done. Design complete — no implementation code written, `dev` untouched.

**Worktree/branch**

- `feat-36-delete` created from `dev` tip (`6d6bf2f`), checked out at `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete`. Main `dev` checkout is clean.

**Plan** — `.specmgr/feat/feat-36-delete/README.md` (in the worktree), validated against the `feat` schema (parses + round-trips; 8 REQs, 8 ACCs, Phases 0–5 / 16 tasks):

- **REQ-001** generic `delete(id, type)` in `general/tools/delete.py` — 11 whole-body domains, ADR excluded; returns the deleted path as `str`.
- **REQ-003** the reusable injection-prevention module `general/tools/_path_safety.py` (`assert_no_traversal`/`assert_uuid`/`assert_feat_id`/`validate_id`/`assert_within`) — pure, no I/O, wired into `delete` now and adoptable by `get`/`update`/`set_status` later with zero rework.
- **REQ-004/005** per-domain lock reuse; `ValueError` (bad id, pre-fs) / `XNotFoundError` (missing) / `DeleteError` (I/O).
- **REQ-006** 10× `unlink`, `feat`× `shutil.rmtree` of the whole folder.
- **REQ-007** new ADR + `AGENTS.md`/`server.py`/`CHANGELOG`/`docs` propagation.

The README is currently **untracked** (I didn't commit, since you only constrained `dev` and didn't ask me to commit). Want me to commit it to `feat-36-delete` (e.g. `docs(feat-36): add generic delete tool design plan`), or leave it for the Phase-Orchestrator to commit with the implementation?

______________________________________________________________________

## User

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-2 · 0.0s)

**Tool: bash**

**Input:**

```json
{
  "command": "git status"
}
```

**Output:**

```
On branch dev
Your branch is up to date with 'origin/dev'.

nothing to commit, working tree clean

```

______________________________________________________________________
