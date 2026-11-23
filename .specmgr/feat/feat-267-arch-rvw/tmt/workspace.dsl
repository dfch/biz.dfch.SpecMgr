# Derived from the Thirty Meter Telescope SysML model, https://github.com/Open-MBEE/TMT-SysML-Model
# Copyright (c) 2016, California Institute of Technology ("Caltech"). U.S. Government sponsorship acknowledged.
# Licensed under the Apache License, Version 2.0, and the conditions in the file NOTICE of this folder.
# Telescope design: TMT Observatory Corporation. SysML model: Jet Propulsion Laboratory (ESEM, OpenMBEE).
# Not endorsed by Caltech, JPL or the TMT Observatory Corporation.

workspace "TMT Observatory (C4 from the TMT SysML model)" "C4 model of the Thirty Meter Telescope, derived from the Open-MBEE TMT-SysML-Model (Apache-2.0, MTIP export EA/TMT_mtip.zip of 2025-06-12). Viewpoints and property conventions per TXT 30983f27, section 8. Issue 267." {

    !identifiers hierarchical

    # Provenance values used below (TXT 30983f27, section 8.3):
    #   origin Extracted  = an element or connector of the SysML model, MTIP export
    #   origin Inferred   = derived from a behaviour, workflow step or signal name of the SysML model
    #   origin Proposed   = not in the SysML model; illustrative only
    # The MTIP export holds no activity-partition membership, so most links between observatory
    # subsystems are Inferred. The TMT SysML Logical block has only two connectors (ESW <-> AO Sequencer).

    model {
        properties {
            "review.safety.relevant" "yes"
            "review.safety.justification" "The logical design contains the Laser Guide Star Facility, the Laser Interlock System and the Observatory Safety System."
            "origin" "Extracted"
            "provenance" "Open-MBEE/TMT-SysML-Model, EA/TMT_mtip.zip, 2025-06-12"
            "copyright" "Derived from the TMT SysML model, Copyright (c) 2016 California Institute of Technology (Caltech), Apache-2.0. Telescope design: TMT Observatory Corporation. Not endorsed by Caltech, JPL or TMT. See NOTICE."
        }

        apsUser = person "APS User" "Runs alignment and phasing procedures. Stakeholder block of the APS mission." {
            properties {
                "origin" "Extracted"
                "provenance" "02 JPL/APS/03 Mission/05 Stakeholders/APS User"
            }
        }
        apsOperator = person "APS Operator" "Operates the APS. Stakeholder block of the APS mission." {
            properties {
                "origin" "Extracted"
                "provenance" "02 JPL/APS/03 Mission/05 Stakeholders/APS Operator"
            }
        }

        tmt = softwareSystem "TMT Observatory System" "Wide-field alt-az Ritchey-Chretien telescope, 492-segment 30 m primary mirror, active M2, articulated M3, with adaptive optics, lasers and instruments." {
            properties {
                "origin" "Extracted"
                "provenance" "01 TMT PO/System Model/TMT Observatory System/Logical Design/TMT Observatory System Logical"
            }
            !docs docs
            !adrs adrs madr

            group "Observatory software" {
                esw = container "Executive Software" "Coordinates observations: acquisition, guiding, pointing acquisition." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Executive Software"
                    }
                }
                eswSeq = container "ESW Sequencer" "Executive sequencer of the observatory workflows." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/ESW Sequencer"
                    }
                }
                eswAcq = container "ESW Acquisition" "Executive acquisition function." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/ESW Acquisition"
                    }
                }
                cs = container "Common Services" "Shared observatory services used by subsystems." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Common Services"
                    }
                }
                dms = container "Data Management System" "Observatory data management." "Software" {
                    tags "Database"
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Data Management System"
                    }
                }
            }

            group "Telescope" {
                tcs = container "Telescope Control System" "Tracking, main-axis and M3 offsets, guider offsets, M2 moves." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Telescope Control System"
                    }
                }
                aorc = container "TCS aORC" "TCS function, named aORC in the model (not expanded there)." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/TCS aORC"
                    }
                }
                mcs = container "Mount Control System" "Controls the telescope mount axes." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Mount Control System"
                    }
                }
                m1cs = container "M1 Control System" "Controls the 492 primary mirror segments: piston/tip/tilt, warping harness, edge sensors." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/M1 Control System"
                    }
                }
                m2s = container "M2 System" "Active secondary mirror." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/M2 System"
                    }
                }
                m3s = container "M3 System" "Articulated tertiary mirror." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/M3 System"
                    }
                }
                enc = container "Enclosure" "Telescope enclosure." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Enclosure"
                    }
                }
                aps = container "Alignment and Phasing System" "Shack-Hartmann wavefront sensor for the pre-AO wavefront quality: aligns and phases M1, aligns M2 and M3." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Alignment and Phasing System; 02 JPL/APS/Logical Design/APS Logical"
                    }

                    peas = component "Procedure Executive and Analysis Software" "Runs the APS procedures and wavefront analysis; commands every APS assembly." "Software" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/Procedure Executive and Analysis Software"
                        }
                    }
                    sh = component "SH camera" "Shack-Hartmann camera." "Camera" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/SH camera"
                        }
                    }
                    pitTrack = component "PEAS PIT Tracking" "Pupil and image tracking control." "Software" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/PEAS PIT Tracking"
                        }
                    }
                    pita = component "Pupil and Image Tracking Assembly" "Pupil and image tracking optics and camera." "Opto-mechanical assembly" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/Pupil and Image Tracking Assembly"
                        }
                    }
                    aptLoop = component "APT Loop" "Acquisition, pointing and tracking loop; produces guide camera data." "Software" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/APT Loop"
                        }
                    }
                    apta = component "Acquisition Pointing and Tracking Assembly" "Acquisition and tracking optics and camera." "Opto-mechanical assembly" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/Acquisition Pointing and Tracking Assembly"
                        }
                    }
                    insrc = component "Internal Source" "Internal reference light source." "Light source" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/Internal Source"
                        }
                    }
                    sp = component "Shear plate" "Shear plate." "Optical element" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/Shear plate"
                        }
                    }
                    km = component "K-mirror" "Field rotator of the APS." "Opto-mechanical assembly" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/K-mirror"
                        }
                    }
                    bss = component "BeamSplitterStage" "Beam splitter stage." "Opto-mechanical assembly" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/BeamSplitterStage"
                        }
                    }
                    stim = component "Stimulus" "Stimulus source." "Light source" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "APS/Logical Design/Components/Stimulus"
                        }
                    }
                }
            }

            group "Adaptive optics (NFIRAOS)" {
                aoSeq = container "AO Sequencer" "Sequences the adaptive optics system." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/AO Sequencer"
                        "safety.function" "laser-propagation"
                    }
                }
                nfcc = container "NFIRAOS Component Controller" "Controls the NFIRAOS opto-mechanical components." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/NFIRAOS Component Controller"
                    }
                }
                nrtc = container "NRTC" "NFIRAOS real-time controller." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/NRTC"
                    }
                }
                rpg = container "RPG" "Reconstructor parameter generator." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/RPG"
                    }
                }
                dm = container "DM" "Deformable mirror." "Hardware" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/DM"
                    }
                }
                nscu = container "NSCU" "NFIRAOS science calibration unit." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/NSCU"
                    }
                }
                tts = container "TTS" "Named TTS in the model (not expanded there)." "Unknown" {
                    tags "Unresolved"
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/TTS"
                    }
                }
                nsen = container "NSEN" "Named NSEN in the model (not expanded there)." "Unknown" {
                    tags "Unresolved"
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/NSEN"
                    }
                }
                esen = container "ESEN" "Named ESEN in the model (not expanded there)." "Unknown" {
                    tags "Unresolved"
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/ESEN"
                    }
                }
            }

            group "Laser guide stars" {
                lgsf = container "Laser Guide Star Facility" "Generates the laser guide star asterism." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Laser Guide Star Facility"
                    }
                }
                laser = container "Laser" "Laser source." "Hardware" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Laser"
                        "safety.function" "laser-propagation"
                    }
                }
                bto = container "Beam Transfer Optics" "Transfers the laser beams to the launch telescope." "Opto-mechanical assembly" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Beam Transfer Optics"
                    }
                }
                lis = container "Laser Interlock System" "Interlocks laser propagation." "Hardware and software" {
                    tags "Safety"
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Laser Interlock System"
                        "safety.function" "laser-propagation"
                    }
                }
            }

            group "Safety" {
                oss = container "Observatory Safety System" "Observatory-wide safety system." "Hardware and software" {
                    tags "Safety"
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/Observatory Safety System"
                        "safety.function" "laser-propagation"
                    }
                }
            }

            group "Instruments" {
                irisSeq = container "IRIS Sequencer" "Sequences the IRIS instrument." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/IRIS Sequencer"
                    }
                }
                irisDet = container "IRIS Imager Detector" "IRIS imager detector." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/IRIS Imager Detector"
                    }
                }
                irisOiwfs = container "IRIS - OIWFS" "IRIS on-instrument wavefront sensor." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/IRIS - OIWFS"
                    }
                }
                irisPoa = container "IRIS - OIWFS POA" "Probe arms of the IRIS OIWFS." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/IRIS - OIWFS POA"
                    }
                }
                ism = container "ISM" "IRIS support element, slewed and offset in the workflows." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/ISM"
                    }
                }
                wfosSeq = container "WFOS Sequencer" "Sequences the WFOS instrument." "Software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/WFOS Sequencer"
                    }
                }
                wfosOiwfs = container "WFOS OIWFS" "WFOS on-instrument wavefront sensor." "Hardware and software" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "Logical System Components/WFOS OIWFS"
                    }
                }
            }
        }

        # ---------------------------------------------------------------- VP01: people -> system
        apsUser -> tmt.aps.peas "Requests APS procedures" "APS2User port" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector APS User.user2APS -- APS2UserIn; signals APS User -> PEAS"
            }
        }
        apsOperator -> tmt.aps "Operates" "Console" {
            properties {
                "origin" "Proposed"
                "provenance" "Stakeholder block without ports in the SysML model"
            }
        }

        # ---------------------------------------------------------------- APS mission (Extracted connectors + signals)
        tmt.aps.peas -> tmt.m1cs "Commands segment piston/tip/tilt and warping harness" "PEAS2M1CS / APS to M1CS Interface" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector; InterfaceBlock APS to M1CS Interface"
            }
        }
        tmt.m1cs -> tmt.aps.peas "Acknowledges, reports status and segment configuration" "m1cs2PEAS" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector; signals M1 Control System -> PEAS (4)"
            }
        }
        tmt.aps.peas -> tmt.tcs "Requests M2/M3 moves and offsets" "PEAS2TCS" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector; signals PEAS -> TCS"
            }
        }
        tmt.tcs -> tmt.aps.peas "Acknowledges and reports status" "TCS2PEAS" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector; signals TCS -> PEAS (4)"
            }
        }
        tmt.tcs -> tmt.aps.pitTrack "Sends pointing information" "PIT2TCS" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector boundary PEAS2TCSIn -- PIT2TCSIn; signal TCS -> PEAS PIT Tracking"
            }
        }
        tmt.esw -> tmt.aps.peas "Starts APS sessions" "ESW2PEAS" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector; signal ESW -> PEAS"
            }
        }
        tmt.aps.peas -> tmt.esw "Reports results" "PEAS2ESW" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector PEAS2ESWOut -- ESW2PEASIn"
            }
        }
        tmt.esw -> tmt.aps.aptLoop "Starts the APT full-frame guide loop" "ESW2GC" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector GC2ESW; signals ESW -> APT Loop (2); ESW behaviour StartAPTFullFrame"
            }
        }
        tmt.aps.aptLoop -> tmt.esw "Sends guide camera data" "GCData" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector APTDataOut -- GCDataOut; signals APT Loop -> ESW (2)"
            }
        }
        tmt.aps.aptLoop -> tmt.tcs "Sends guide camera data" "guideCamData" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector GCDataOut -- TCS.guideCamDataIn"
            }
        }
        tmt.aps.peas -> tmt.cs "Uses common services" "PEAS2CS" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector PEAS2CSOut -- CS2PEASIn"
            }
        }
        tmt.esw -> tmt.tcs "Sends guider offsets and tracking demands" "ESW2TCS" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Mission connector ESW2TCSOut -- TCS2PEASIn; signals ESW -> TCS (3)"
            }
        }
        tmt.tcs -> tmt.esw "Acknowledges" "TCS2ESW" {
            properties {
                "origin" "Extracted"
                "provenance" "Signals TCS -> ESW (3)"
            }
        }
        tmt.esw -> tmt.aoSeq "Commands AO pointing acquisition" "ESW2AOSeq" {
            properties {
                "origin" "Extracted"
                "provenance" "TMT Observatory System Logical connectors ESW2AOSeq / AOSeq2ESW; signal ESW -> AO Sequencer"
            }
        }

        # ---------------------------------------------------------------- APS internal (Extracted connectors + signals)
        tmt.aps.peas -> tmt.aps.sh "Commands" "PEAS2SH" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector"
            }
        }
        tmt.aps.sh -> tmt.aps.peas "Sends Shack-Hartmann frames and status" "CC_SH2PEAS" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signals SH camera -> PEAS (4)"
            }
        }
        tmt.aps.peas -> tmt.aps.pitTrack "Commands tracking" "PEAS2PITTrack" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector"
            }
        }
        tmt.aps.pitTrack -> tmt.aps.peas "Sends PIT data and status" "PITDataProducerIF" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connectors PITDataOut -- PEAS2PITDataIn; signals PEAS PIT Tracking -> PEAS (4)"
            }
        }
        tmt.aps.peas -> tmt.aps.pita "Commands" "PEAS2PIT" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector"
            }
        }
        tmt.aps.pita -> tmt.aps.peas "Reports status" "PEAS2PIT" {
            properties {
                "origin" "Extracted"
                "provenance" "Signals Pupil and Image Tracking Assembly -> PEAS (6)"
            }
        }
        tmt.aps.pitTrack -> tmt.aps.pita "Controls" "PITT2PITA" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector"
            }
        }
        tmt.aps.pita -> tmt.aps.pitTrack "Sends tracking images" "PITA2PITT" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signals PITA -> PEAS PIT Tracking (2)"
            }
        }
        tmt.aps.pitTrack -> tmt.aps.km "Rotates" "PIT2KMirror" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signal K-mirror -> PEAS PIT Tracking"
            }
        }
        tmt.aps.pitTrack -> tmt.aps.sp "Controls" "PIT2SP" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signal Shear plate -> PEAS PIT Tracking"
            }
        }
        tmt.aps.peas -> tmt.aps.km "Commands" "PEAS2KM" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signals K-mirror -> PEAS (3)"
            }
        }
        tmt.aps.peas -> tmt.aps.sp "Commands" "PEAS2SP" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signals Shear plate -> PEAS (2)"
            }
        }
        tmt.aps.peas -> tmt.aps.insrc "Commands" "PEAS2Insource" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signals Internal Source -> PEAS (4)"
            }
        }
        tmt.aps.peas -> tmt.aps.bss "Commands" "peas2bss" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector"
            }
        }
        tmt.aps.peas -> tmt.aps.stim "Commands" "peas2Stimulus" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signals Stimulus -> PEAS (2)"
            }
        }
        tmt.aps.peas -> tmt.aps.apta "Commands" "PEAS2APT" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signals APTA -> PEAS (2)"
            }
        }
        tmt.aps.peas -> tmt.aps.aptLoop "Commands the loop" "PEAS2APTLoop" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signal APT Loop -> PEAS"
            }
        }
        tmt.aps.aptLoop -> tmt.aps.apta "Controls" "APTL2APTA" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector"
            }
        }
        tmt.aps.apta -> tmt.aps.aptLoop "Sends acquisition images" "APTA2APTL" {
            properties {
                "origin" "Extracted"
                "provenance" "APS Logical connector; signals APTA -> APT Loop (2)"
            }
        }

        # ---------------------------------------------------------------- Observatory (Inferred from behaviour and workflow names)
        tmt.eswSeq -> tmt.tcs "Slews the telescope" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow step Slew TCS Logical"
            }
        }
        tmt.eswSeq -> tmt.aoSeq "Slews the AO system" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow step Slew AOSeq Logical"
            }
        }
        tmt.eswSeq -> tmt.irisSeq "Slews IRIS" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow step Slew IRIS Logical"
            }
        }
        tmt.eswSeq -> tmt.wfosSeq "Slews WFOS" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow step Slew WFOS Logical"
            }
        }
        tmt.eswAcq -> tmt.tcs "Acquires telescope pointing" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow step Acquire Telescope Pointing Logical"
            }
        }
        tmt.tcs -> tmt.mcs "Offsets the main axes and tracks" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "TCS behaviours doOffsetMainAxes, doTracking"
            }
        }
        tmt.tcs -> tmt.m2s "Moves M2 in piston/tip/tilt" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "TCS behaviours SendAck_M2PTTMove, SendAck_M2Status"
            }
        }
        tmt.tcs -> tmt.m3s "Offsets M3 and moves the pupil" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "TCS behaviours doOffsetM3, SendAck_MovePupilUsingM3, SendAck_TakeM3Snapshot"
            }
        }
        tmt.tcs -> tmt.enc "Slews the enclosure" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow step Slew TCS Logical"
            }
        }
        tmt.tcs -> tmt.aorc "Uses" "Function" {
            properties {
                "origin" "Inferred"
                "provenance" "Block name TCS aORC"
            }
        }
        tmt.aoSeq -> tmt.nfcc "Configures NFIRAOS components" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow steps Acquire and Lock PWFS / TTF OIWFS Logical"
            }
        }
        tmt.aoSeq -> tmt.nrtc "Opens and closes the AO loops" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Acquire and Lock LGS Logical Actual steps OPEN_LOOPS, Close FSM, HO and Focus Loops"
            }
        }
        tmt.aoSeq -> tmt.nscu "Calibrates" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow steps CALIBRATE_BACKGROUND (LGS), Calibrate Background"
            }
        }
        tmt.aoSeq -> tmt.ism "Slews and offsets" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow steps Slew / Offset ISM Logical, Reset ISM Logical"
            }
        }
        tmt.rpg -> tmt.nrtc "Provides reconstructor parameters" "Data" {
            properties {
                "origin" "Inferred"
                "provenance" "Block name RPG"
            }
        }
        tmt.nrtc -> tmt.dm "Drives" "Real-time control" {
            properties {
                "origin" "Inferred"
                "provenance" "Block names NRTC, DM"
            }
        }
        tmt.irisOiwfs -> tmt.nrtc "Sends tip/tilt/focus measurements" "Data" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow steps Acquire and Lock TTF OIWFS Logical, TT OIWFS/ODGW Logical"
            }
        }
        tmt.aoSeq -> tmt.lgsf "Requests laser propagation and asterism" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Acquire and Lock LGS Logical Actual steps Offset Laser, setLaserDetune, LGS Asterism Using LACQ VIZ"
            }
        }
        tmt.aoSeq -> tmt.lis "Checks laser propagation permission" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow step Check Laser Propagation Permission Logical"
                "safety.function" "laser-propagation"
            }
        }
        tmt.lgsf -> tmt.laser "Controls" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Block names Laser Guide Star Facility, Laser"
            }
        }
        tmt.lgsf -> tmt.bto "Aligns the beam transfer optics" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow step Align BTO OP Logical"
            }
        }
        tmt.lis -> tmt.laser "Inhibits propagation" "Interlock" {
            tags "Safety"
            properties {
                "origin" "Inferred"
                "provenance" "Block name Laser Interlock System"
                "safety.function" "laser-propagation"
            }
        }
        tmt.oss -> tmt.lis "Sends safety state" "Interlock" {
            tags "Safety"
            properties {
                "origin" "Inferred"
                "provenance" "Block names Observatory Safety System, Laser Interlock System"
                "safety.function" "laser-propagation"
            }
        }
        tmt.irisSeq -> tmt.irisDet "Configures and starts exposures" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow steps Slew IRIS Filter Logical, Block IRIS Filter Logical"
            }
        }
        tmt.irisSeq -> tmt.irisOiwfs "Configures" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow step Acquire and Lock TTF OIWFS Logical"
            }
        }
        tmt.irisOiwfs -> tmt.irisPoa "Positions the probe arms" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Block name IRIS - OIWFS POA"
            }
        }
        tmt.wfosSeq -> tmt.wfosOiwfs "Configures" "Command" {
            properties {
                "origin" "Inferred"
                "provenance" "Workflow steps Acquire Telescope Pointing w/WFOS Logical, Preset with WFOS"
            }
        }
        tmt.irisDet -> tmt.dms "Delivers science data" "Data" {
            properties {
                "origin" "Proposed"
                "provenance" "Not in the SysML model"
            }
        }
        tmt.esw -> tmt.eswSeq "Runs observation workflows" "Function" {
            properties {
                "origin" "Inferred"
                "provenance" "Block names Executive Software, ESW Sequencer; TMT Observation WorkFlow"
            }
        }
        tmt.esw -> tmt.eswAcq "Runs acquisition" "Function" {
            properties {
                "origin" "Inferred"
                "provenance" "ESW behaviours Acquire and Guide, Pointing acquisition"
            }
        }

        # ---------------------------------------------------------------- VP06/VP07: deployment
        summit = deploymentEnvironment "Summit (illustrative)" {
            site = deploymentNode "Observatory site" "Telescope site. Not in the SysML model." "Site" {
                properties {
                    "origin" "Proposed"
                    "provenance" "Not in the SysML model"
                    "failure.domain.region" "summit"
                }
                computerRoom = deploymentNode "Summit computer room" "Hosts the observatory software." "Servers" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "Not in the SysML model"
                        "failure.domain.zone" "computer-room"
                        "failure.domain.placement" "fixed"
                    }
                    containerInstance tmt.esw
                    containerInstance tmt.eswSeq
                    containerInstance tmt.eswAcq
                    containerInstance tmt.cs
                    containerInstance tmt.dms
                    containerInstance tmt.tcs
                    containerInstance tmt.aoSeq
                    containerInstance tmt.irisSeq
                    containerInstance tmt.wfosSeq
                }
                telescope = deploymentNode "Telescope structure" "Mount, mirrors and the APS optical bench." "Telescope" {
                    properties {
                        "origin" "Proposed"
                        "provenance" "Not in the SysML model"
                        "failure.domain.zone" "telescope"
                    }
                    containerInstance tmt.mcs
                    containerInstance tmt.m1cs
                    containerInstance tmt.m2s
                    containerInstance tmt.m3s
                    containerInstance tmt.irisDet
                    apsBench = deploymentNode "APS optical bench" "Optical bench with the SH and PIT assemblies." "Optical bench" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "02 JPL/APS/Physical Design/Design/Optical Bench"
                            "failure.domain.host" "aps-bench"
                        }
                        containerInstance tmt.aps
                    }
                }
            }
        }
    }

    views {
        systemContext tmt "context" "VP01 Context: who uses the TMT Observatory System" {
            include *
            properties {
                "viewpoint" "VP01"
            }
        }
        container tmt "containers" "VP02 Functional: observatory subsystems (logical design)" {
            include *
            properties {
                "viewpoint" "VP02"
            }
        }
        container tmt "aps-neighbours" "VP02 Functional: APS and its interfaces" {
            include tmt.aps
            include ->tmt.aps->
            include apsUser apsOperator
            properties {
                "viewpoint" "VP02"
            }
        }
        container tmt "laser-safety" "VP02 Functional, SA perspective: laser propagation chain" {
            include tmt.aoSeq tmt.lgsf tmt.laser tmt.bto tmt.lis tmt.oss
            properties {
                "viewpoint" "VP02"
            }
        }
        component tmt.aps "aps-components" "VP02 Functional and VP05 Development: APS logical components" {
            include *
            properties {
                "viewpoint" "VP02,VP05"
            }
        }
        dynamic tmt.aps "aps-guide-loop" "VP04 Concurrency: APT guide loop between ESW, APS and TCS (order Inferred)" {
            tmt.esw -> tmt.aps.aptLoop "Starts the APT full-frame guide loop"
            tmt.aps.aptLoop -> tmt.aps.apta "Controls"
            tmt.aps.apta -> tmt.aps.aptLoop "Sends acquisition images"
            tmt.aps.aptLoop -> tmt.esw "Sends guide camera data"
            tmt.esw -> tmt.tcs "Sends guider offsets and tracking demands"
            tmt.tcs -> tmt.esw "Acknowledges"
            properties {
                "viewpoint" "VP04"
            }
        }
        deployment tmt summit "deployment" "VP06 Deployment and VP07 Operational (illustrative, Proposed)" {
            include *
            properties {
                "viewpoint" "VP06,VP07"
            }
        }

        styles {
            element "Person" {
                shape Person
            }
            element "Safety" {
                background #c0392b
                color #ffffff
            }
            element "Unresolved" {
                background #bbbbbb
                border dashed
            }
            element "Database" {
                shape Cylinder
            }
            relationship "Safety" {
                color #c0392b
                thickness 3
            }
        }
    }

    configuration {
        scope softwaresystem
    }
}
