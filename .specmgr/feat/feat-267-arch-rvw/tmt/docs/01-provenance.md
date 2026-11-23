# Provenance and Coverage

## Attribution

- Telescope design: TMT Observatory Corporation (TMT International Observatory).
- SysML model: Jet Propulsion Laboratory, California Institute of Technology, published at
  https://github.com/Open-MBEE/TMT-SysML-Model under the Apache License, Version 2.0.
  Copyright (c) 2016, California Institute of Technology ("Caltech"). U.S. Government sponsorship
  acknowledged. All rights reserved. The full notice, its conditions and its disclaimer are in the
  file `NOTICE` of this folder.
- Method and environment: Executable System Engineering Method (ESEM) and OpenMBEE.
- Publications on the model:
  - R. Karban, F. G. Dekens, S. Herzig, M. Elaasar, N. Jankevičius, "Creating system engineering
    products with executable models in a model-based engineering environment", Proc. SPIE 9911,
    99110B, 2016.
  - S. Herzig, R. Karban, G. Trancho, F. Dekens, N. Jankevičius, M. Troy, "Analyzing the Operational
    Behavior of the Alignment and Phasing System of the Thirty Meter Telescope using SysML",
    AO4ELT5, 2017.
  - R. Karban, A. G. Crawford, G. Trancho, M. Zamparelli, S. Herzig, I. Gomes, M. Pettete, E. Brower,
    "The OpenSE Cookbook", Proc. SPIE 10705, 2018.

This workspace is a derived work and is not endorsed by Caltech, JPL or the TMT Observatory Corporation.

## Source

Open-MBEE/TMT-SysML-Model (Apache-2.0), file `EA/TMT_mtip.zip` (MTIP 2022x export of 2025-06-12).
Packages used: `01 TMT PO/System Model/TMT Observatory/.../Logical Design` (34 logical system components)
and `02 JPL/System Model/APS` (APS mission, logical design, physical design).

Every element and relationship carries `origin` (Extracted, Inferred or Proposed) and `provenance`
(the SysML package path, connector or behaviour it comes from). See TXT 30983f27, section 8.3.

## Limits of the source

- The MTIP export holds no activity-partition membership. The observatory workflows cannot be
  attributed to subsystems automatically, so most observatory-level relationships are Inferred from
  behaviour and workflow step names.
- The block `TMT Observatory System Logical` has only two connectors (ESW <-> AO Sequencer).
- TTS, NSEN and ESEN are acronyms the model does not expand. They are tagged `Unresolved` and stay
  disconnected.
- The SysML model has no deployment. The deployment environment is Proposed, except the APS optical
  bench (APS Physical Design).
- The groups (Observatory software, Telescope, ...) are a presentation choice, not SysML packages.

## Viewpoint coverage (TXT 30983f27, section 8.1)

| Viewpoint | View | Coverage here |
|-----------|------|---------------|
| VP01 Context | context | partial: two APS stakeholders only; the model has no observatory-level actors |
| VP02 Functional | containers, aps-neighbours, laser-safety, aps-components | partial |
| VP03 Information | none | none: the SysML item and interface definitions are not mapped |
| VP04 Concurrency | aps-guide-loop | partial, between processes; order Inferred |
| VP05 Development | aps-components | partial |
| VP06 Deployment | deployment | illustrative, Proposed |
| VP07 Operational | deployment | none beyond node placement |
| XV CrossView | none | the safety relevance is a model property |
