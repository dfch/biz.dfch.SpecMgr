Validation of the Applicability Matrix

Overall assessment: the matrix is a good foundation, and I would retain its basic structure. However, I recommend several corrections and clarifications before treating it as the baseline for an architecture assessment catalogue.

My assessment is that the matrix is conceptually sound, but it needs refinement in three areas:

    Mathematical consistency and matrix semantics.
    Completeness and balance of the viewpoint-to-quality mappings.
    Rules for applicability, tailoring and safety assessment.

I would distinguish between two questions:

    Is the matrix internally consistent? This can be checked objectively.
    Are the assignments architecturally appropriate? These require expert judgement and should be validated against the intended assessment scope.

1. Conformance with ISO/IEC 25010:2023

The nine quality characteristics are correct, and their order matches ISO/IEC 25010:2023.
Code	Quality characteristic	Assessment
FS	Functional Suitability	Correct
PE	Performance Efficiency	Correct
CO	Compatibility	Correct
IC	Interaction Capability	Correct
RE	Reliability	Correct
SE	Security	Correct
MA	Maintainability	Correct
FL	Flexibility	Correct
SA	Safety	Correct

The 2023 edition introduced several relevant changes compared with the 2011 edition:

    Safety became a separate quality characteristic.
    Usability was replaced by Interaction Capability.
    Portability was replaced by Flexibility.
    Scalability became a subcharacteristic of Flexibility.
    Resistance became a subcharacteristic of Security.

Your terminology reflects the 2023 model rather than accidentally mixing the 2011 terminology.

One important distinction: ISO/IEC 25010 defines a product quality model, not an architecture viewpoint model. Your matrix is therefore a proposed architectural assessment framework that uses ISO quality characteristics as its quality dimension. That is perfectly reasonable, but it should be explicitly documented.

Sources: ISO/IEC 25010:2023 — official ISO publication and IEC publication record.
2. Mathematical consistency: primary-cell count

There is one definite error.

Your stated count is 30 primary cells, but the table contains 28.

Here is the breakdown:
Viewpoint	Primary cells	Count
VP01 Context	FS, CO	2
VP02 Functional	FS, IC	2
VP03 Logical	MA, FL	2
VP04 Information/Data	CO, RE, SE	3
VP05 Application/Software	MA, FL	2
VP06 Integration/Interface	CO, RE, SE, FL	4
VP07 Technology/Infrastructure	PE, FL	2
VP08 Deployment	PE, RE, FL	3
VP09 Security	SE	1
VP10 Operational	PE, RE, MA	3
VP11 Development/Construction	MA, FL	2
VP12 Runtime/Process	PE, RE	2
VP13 Safety	RE, SA	2
Total		28

Correction: VP06 contains four primary cells, not three. The total is therefore 28.

Recommendation: Change the stated count from 30 to 28.

This is worth correcting before the matrix becomes a reference for catalogue sizing or assessment coverage.

# 3. Architectural assessment of the assignments

The distribution is generally plausible. I would not attempt to make the matrix symmetrical: different viewpoints naturally have different relationships with quality characteristics.

However, some assignments deserve particular attention.

## 3.1 Functional Suitability (FS)

Currently:

    VP01 Context: P
    VP02 Functional: P
    VP03 Logical: S
    VP04 Information/Data: S
    VP05 Application/Software: S
    VP09 Security: S
    VP12 Runtime/Process: S
    VP13 Safety: S

Assessment: Mostly good.

The two primary assignments make sense:

    Context establishes what the system must achieve and its boundaries.
    Functional describes the functions and responsibilities that fulfil those needs.

I would retain these assignments.

One consideration: logical and application architectures can also be important sources of functional suitability evidence. Keeping them secondary is reasonable if the assessment focuses on functional completeness and correctness in VP02, with architectural cross-checks elsewhere.

## 3.2 Performance Efficiency (PE)

Currently, primary in:

    VP07 Technology/Infrastructure
    VP08 Deployment
    VP10 Operational
    VP12 Runtime/Process

Assessment: Good.

This is a particularly coherent distribution.

The four viewpoints cover different performance concerns:
Viewpoint	Performance focus
Technology/Infrastructure	Capacity and resource availability
Deployment	Resource allocation and deployment topology
Operational	Monitoring, capacity management and performance objectives
Runtime/Process	Execution behaviour, latency and throughput

I would retain all four primary assignments.

One important consideration: Performance Efficiency also includes resource utilization and capacity. These should not become exclusively infrastructure concerns. Your secondary assignments in Logical, Information/Data, Application and Integration provide appropriate coverage.

## 3.3 Compatibility (CO)

Currently:

    VP01 Context: P
    VP04 Information/Data: P
    VP06 Integration/Interface: P

Assessment: Good, with one potential omission.

Compatibility includes:

    Co-existence.
    Interoperability.

VP06 is an obvious primary viewpoint.

VP04 is also appropriate because information structures, semantics, formats and data exchange are central to interoperability.

VP01 is useful because external systems, actors and environmental dependencies establish the compatibility context.

I would consider whether VP05 Application/Software should be primary instead of secondary.

My preference, however, would be to retain it as secondary: application-level compatibility can be assessed through integration contracts and technology choices without duplicating the integration assessment.

## 3.4 Interaction Capability (IC)

Currently:

    VP02 Functional: P
    VP01 Context: S
    VP05 Application/Software: S
    VP09 Security: S
    VP10 Operational: S
    VP13 Safety: S

Assessment: Reasonable, but the applicability rule needs refinement.

ISO/IEC 25010:2023 defines Interaction Capability in relation to interaction between specified users and a system through its user interface.

This means that your emphasis on human interaction is appropriate.

However, I would avoid the expression:

    For back-end systems without human users, mark the whole column inapplicable.

There are back-end systems without ordinary end users but with:

    Administrators.
    Operators.
    Support personnel.
    Maintenance personnel.
    Emergency operators.

These people may interact with the system through management interfaces, monitoring consoles or administrative tools.

Suggested rule:

Apply Interaction Capability wherever the assessed product provides user-facing, operator-facing, administrative or maintenance interfaces. If no relevant human interaction exists within the assessment scope, mark the characteristic inapplicable with one scope-level justification.

This is more precise and avoids overlooking operational interfaces.

## 3.5 Reliability (RE)

Currently primary in:

    VP04 Information/Data
    VP06 Integration/Interface
    VP08 Deployment
    VP10 Operational
    VP12 Runtime/Process
    VP13 Safety

Assessment: Very good.

Reliability is appropriately distributed across the architecture.

The assignments cover:

    Data integrity and persistence.
    Integration failure handling.
    Deployment resilience.
    Operational availability and recovery.
    Runtime fault tolerance.
    Safety-related failure behaviour.

I particularly like the primary assignment in VP13.

Safety and reliability are closely related, but they are not interchangeable. A reliable system is not necessarily safe, and a safe system may require specific behaviour when reliability is compromised.

The distinction should be preserved in the criteria catalogue.

## 3.6 Security (SE)

Currently:

    VP04 Information/Data: P
    VP06 Integration/Interface: P
    VP09 Security: P

Assessment: Good.

The three primary assignments are defensible.

They represent:

    Information protection.
    Communication and integration protection.
    Cross-cutting security architecture.

The Security viewpoint should remain the home of the comprehensive security criteria.

The other primary cells should focus on their respective architectural concerns rather than reproducing the entire security assessment.

I would also retain secondary security checks in Technology/Infrastructure, Deployment, Runtime and Operational.

These are important places where security architecture decisions become concrete.

## 3.7 Maintainability (MA)

Currently primary in:

    VP03 Logical
    VP05 Application/Software
    VP10 Operational
    VP11 Development/Construction

Assessment: Good.

This distribution makes architectural sense.

In particular:

    Logical architecture determines structural modularity.
    Application architecture determines software decomposition.
    Development architecture determines construction practices.
    Operational architecture determines maintainability in service.

I would retain these assignments.

## 3.8 Flexibility (FL)

Currently primary in:

    VP03 Logical
    VP05 Application/Software
    VP06 Integration/Interface
    VP07 Technology/Infrastructure
    VP08 Deployment
    VP11 Development/Construction

Assessment: Good, although the scope needs careful definition.

Flexibility is broader than portability.

Under ISO/IEC 25010:2023, it includes:

    Adaptability.
    Scalability.
    Installability.
    Replaceability.

Your distribution is appropriate because these properties are influenced by architectural structure, technology, integration, deployment and development decisions.

I would ensure that the catalogue explicitly covers scalability. It is particularly important not to reduce Flexibility to technology portability.

## 3.9 Safety (SA)

Currently:

    VP13 Safety: P
    All other applicable viewpoints: S, except VP11.

Assessment: Good conceptual decision.

I support having a dedicated Safety viewpoint and a dedicated Safety quality characteristic.

The distinction between them is important:

    VP13 Safety assesses the architectural mechanisms and decisions that establish and preserve safety.
    SA assesses the quality of the product concerning safety.

This creates a useful cross-check mechanism.

One assignment I would reconsider is VP11 Development/Construction × SA.

I would lean towards S rather than a dash.

Development practices can affect safety through:

    Safe coding practices.
    Verification and validation.
    Configuration control.
    Safety-related change management.
    Traceability of safety requirements.

There is a legitimate argument for excluding these concerns from the architecture assessment itself, but I would not exclude them automatically.

My recommendation: change VP11 × SA from - to S.

# 4. Structural issues in the matrix

Beyond individual assignments, I see three issues worth resolving before expanding the criteria catalogue.

## 4.1 Define the difference between primary and secondary more precisely

Your definitions are:

    P: Full criteria.
    S: A few cross-check criteria.

This is understandable, but there is a potential ambiguity.

For example, Security has three primary cells:

    VP04 × SE
    VP06 × SE
    VP09 × SE

If all three contain the full Security criteria, you will inevitably duplicate assessment work.

I recommend defining P and S as follows:
Marking	Recommended definition
P	Primary assessment responsibility. Contains the complete set of criteria relevant to that viewpoint-characteristic intersection.
S	Secondary assessment responsibility. Contains selected cross-check criteria that validate or complement primary assessments.
-	No default assessment criteria. Can be activated through tailoring.

The important distinction is that P does not mean the entire quality characteristic is assessed independently in every primary cell.

It means full coverage of the relevant concerns within that viewpoint.

This is particularly important for Security, Reliability and Flexibility.

## 4.2 Distinguish applicability from assessment responsibility

I would slightly change your terminology.

A dash does not necessarily mean that a quality characteristic is inapplicable.

It means that you have not assigned default assessment responsibility to that intersection.

For example:

    Security × Technology may be secondary or primary depending on the architecture.
    Functional Suitability × Deployment may become relevant for certain deployment-related functional constraints.
    Interaction Capability × Runtime may be relevant where runtime interaction behaviour is important.

Therefore, I recommend using:

- = No default criteria assigned

rather than:

- = Not applicable by default

This avoids conflating two different concepts:

    Whether a quality characteristic applies to the assessed system.
    Whether a particular viewpoint has assessment responsibility for it.

This distinction will make the tailoring rules considerably cleaner.

## 4.3 Define what happens to secondary cells during tailoring

You currently specify that removing a primary cell requires justification.

But what happens if an assessor decides that a secondary cell is unnecessary?

I suggest:

    Removing P requires a written justification.
    Removing S requires no justification, unless the assessment methodology explicitly requires that cross-check.
    Activating - requires no justification, but the reason should be recorded if it introduces additional assessment scope.

This keeps the assessment proportionate without weakening its accountability.

# 5. Review of the tailoring rules

I would retain your existing rules, with some refinements.
Rule	Assessment	Recommendation
Removing P requires justification	Good	Retain
Activating a dash is allowed	Good	Retain
IC mostly concerns user interfaces	Good	Clarify operators and administrators
Safety is opt-in	Good	Retain, with explicit scope justification
Counts and markings require review	Good	Retain
Safety gate

I particularly support the safety gate.

It prevents two undesirable situations:

    Safety being silently ignored in a safety-relevant system.
    Safety assessment being unnecessarily imposed on systems where it is genuinely outside the scope.

I would slightly strengthen the rule.

When safety is declared relevant:

    VP13 must be included.
    The SA column must be included.
    Primary and secondary criteria must be assessed according to the matrix.
    Exclusions of individual primary cells require justification.

When safety is declared not relevant:

    VP13 is excluded.
    The SA column is excluded.
    The justification is recorded at assessment-scope level.

A subsequent change in safety relevance requires a new documented decision.

One additional consideration: safety relevance should not be determined solely by whether the system is directly involved in controlling physical equipment. Software that influences decisions or actions with potential safety consequences may also be safety-relevant.

# 6. My recommended changes

I would make only a small number of changes to your original matrix.
Location	Current	Recommendation	Reason
VP11 × SA	-	S	Development practices can influence safety
IC tailoring rule	No human users	No relevant human interaction	Includes operators and administrators
Dash definition	Not applicable by default	No default criteria assigned	Separates applicability from responsibility
P definition	Full criteria	Full viewpoint-specific criteria	Avoids duplication
S tailoring	Not specified	Define removal rules	Completes tailoring logic

I would not make broad changes to the remaining P/S assignments at this stage.

They are sufficiently defensible for an initial assessment framework.

# 7. An additional recommendation: validate the matrix against representative architectures

Before expanding the criteria catalogue, I would perform a small validation exercise.

Use three contrasting architectural scenarios:
Scenario	What it validates
Traditional enterprise application	Functional, application, data, integration and operational coverage
Distributed cloud-native platform	Performance, flexibility, reliability, deployment and security coverage
Safety-relevant cyber-physical system	Safety gate, reliability/safety interaction and infrastructure coverage

For each scenario, ask three questions:

    Does every important architectural quality concern have at least one primary assessment location?
    Are the secondary cells providing useful cross-checks rather than duplicating primary criteria?
    Are there important quality concerns that cannot be naturally assigned to any viewpoint?

This is more valuable than trying to establish theoretically perfect P/S assignments without testing them against real architectures.

# 8. Final verdict

My assessment:
Dimension	Verdict
ISO/IEC 25010:2023 alignment	Very good
Viewpoint coverage	Good
Primary/secondary distinction	Good, needs clarification
Security coverage	Very good
Reliability coverage	Very good
Safety integration	Very good
Interaction Capability applicability	Needs refinement
Tailoring rules	Good, incomplete
Readiness for catalogue development	Nearly ready

I would approve this matrix as a draft foundation, subject to the clarifications above.

The most important architectural decision I would preserve is the separation between:

    Quality characteristics, which describe what quality properties need to be assessed.
    Viewpoints, which describe where those properties become architecturally visible.
    Primary and secondary cells, which describe the assessment responsibility and depth.

That separation gives the methodology a strong foundation.
One final architectural principle

I would explicitly add this principle to the methodology:

    A quality characteristic may be relevant across multiple architectural viewpoints, but its assessment should be coordinated to avoid duplicated criteria, inconsistent conclusions and gaps in coverage. Primary cells establish assessment responsibility; secondary cells provide complementary evidence and cross-checks.

This principle will become particularly important when you start developing the actual assessment criteria.

My recommendation: freeze the matrix structure after these refinements, then validate it against the three representative architectures before investing in the detailed criteria catalogue.
