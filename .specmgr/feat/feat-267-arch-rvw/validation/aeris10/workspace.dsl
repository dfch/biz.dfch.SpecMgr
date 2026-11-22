workspace "AERIS-10" "Phase 120 validation run (class: safety-relevant cyber-physical system): AERIS-10 PLFM phased-array radar, github.com/NawfalMotii79/PLFM_RADAR, branch main, commit 62d4c55 (2026-10-14). Variant modelled: AERIS-10E with the 50T production board (FT2232H)." {

    !identifiers hierarchical

    model {
        properties {
            "review.safety.relevant" "yes"
            "review.safety.justification" "AERIS-10E radiates from 16 x 10 W GaN PAs at 10.5 GHz into a 32x16 array (RF exposure of people), has high-current PA rails, a rotating antenna and a thermal runaway risk. No hazard analysis exists in the repository."
            "origin" "Extracted"
            "provenance" "README.md (Technical Specifications, Hardware Components), 9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp handleSystemError comments; hazard analysis absence: search of README.md, CONTRIBUTING.md, docs/*.html, 1_Project_Description/Project_Description.docx"
        }

        operator = person "Operator" "Starts the radar, sets waveform and processing parameters, watches targets on the map." {
            properties {
                "origin" "Extracted"
                "provenance" "1_Project_Description/Project_Description.docx (GUI Connection and System Arming), 9_Firmware/9_3_GUI/v7/dashboard.py"
            }
        }

        bystander = person "Bystander" "A person in the main beam near the antenna. Does not use the system, but is exposed to the RF energy. Stands for the hazard receiver." {
            tags "Inferred"
            properties {
                "origin" "Inferred"
                "provenance" "Derived from the output power (README.md, 10W x 16) and the 360 degree mechanical scan (README.md). No document in the repository names exposed persons"
            }
        }

        gnss = softwareSystem "GNSS" "Satellite navigation signals received by the UM982 module. Position and heading of the radar." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/um982_gps.c, main.cpp um982_* calls"
            }
        }

        tiles = softwareSystem "Map tile servers" "OpenStreetMap, Google Maps, Google Satellite, Google Hybrid, ESRI Satellite. Background map of the GUI." {
            tags "External"
            properties {
                "origin" "Extracted"
                "provenance" "9_Firmware/9_3_GUI/v7/map_widget.py lines 9, 134-140; v7/models.py class TileServer"
            }
        }

        aeris = softwareSystem "AERIS-10" "10.5 GHz pulse LFM phased-array radar: chirp generation, electronic beam steering (ADAR1000), mechanical azimuth scan, FPGA signal processing, host GUI." {
            properties {
                "origin" "Extracted"
                "provenance" "README.md, 2_Functional Diagram & Interconnection Matrices/RADAR_V6.drawio"
            }

            fpga = container "FPGA gateware" "Chirp timing and DAC waveform, ADC capture, DDC, matched filter, range decimation, MTI, Doppler FFT, CFAR, USB data and command interface. Bitstream for XC7A50T (production) or XC7A200T (premium dev)." "Verilog, Vivado 2025.2, Artix-7" {
                properties {
                    "origin" "Extracted"
                    "provenance" "9_Firmware/9_2_FPGA/radar_system_top.v, constraints/README.md, docs/release-notes.html"
                    "deployment.unit" "bitstream"
                }

                chirp = component "Chirp controller and transmitter" "PLFM chirp FSM, chirp memory, DAC interface. TX mixer enable = STM32 master enable AND FSM state LONG_CHIRP or SHORT_CHIRP." "Verilog" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "plfm_chirp_controller.v lines 84-88, radar_transmitter.v lines 146-152"
                    }
                }
                receiver = component "Receiver chain" "AD9484 interface (400 MHz), DDC (NCO, CIC, FIR), matched filter, range bin decimator, MTI canceller, Doppler processor." "Verilog" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "radar_receiver_final.v, ddc_400m.v, matched_filter_processing_chain.v, mti_canceller.v, doppler_processor.v"
                    }
                }
                cfar = component "CFAR detector" "CA/GO/SO CFAR with host-configurable guard, train, alpha and mode." "Verilog" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "cfar_ca.v, docs/release-notes.html v0.1.5-cfar"
                    }
                }
                usbIf = component "USB data interface and command decode" "FT2232H (USB_MODE=1) or FT601 (USB_MODE=0), compile-time choice. Host opcodes 0x01-0x31, 0xFF to registers in clk_100m via toggle CDC." "Verilog" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "usb_data_interface_ft2232h.v, usb_data_interface.v, radar_system_top.v lines 951-961, constraints/README.md USB_MODE"
                    }
                }
                selfTest = component "FPGA self-test" "Board self-test triggered by opcode 0x30, result flags read back by 0x31." "Verilog" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "fpga_self_test.v, radar_system_top.v lines 281-292"
                    }
                }

                usbIf -> chirp "Sets chirp timing registers (0x10-0x15, no range check) and radar mode" "register write, CDC" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "radar_system_top.v lines 951-961 (host_long_chirp_cycles <= usb_cmd_value)"
                    }
                }
                usbIf -> cfar "Sets CFAR guard, train, alpha, mode (0x21-0x25)" "register write" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "docs/release-notes.html v0.1.5-cfar"
                    }
                }
                receiver -> cfar "Range-Doppler magnitudes" "on-chip stream" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "docs/reports.html Build 25 hierarchy (rx_inst, cfar_inst)"
                    }
                }
                cfar -> usbIf "Detections" "on-chip stream" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "docs/release-notes.html 0773001 (doppler/cfar data_pending flags)"
                    }
                }
                usbIf -> selfTest "Triggers (0x30)" "register write" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "radar_system_top.v line 281"
                    }
                }
            }

            mcu = container "MCU firmware" "Power sequencing, clock and LO setup, beam steering tables, PA bias calibration, health monitoring and emergency stop, stepper motor, GPS/IMU/barometer. Bare-metal super loop, no RTOS." "C/C++, STM32F746, HAL" {
                properties {
                    "origin" "Extracted"
                    "provenance" "9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp (no freertos or cmsis_os include, grep count 0)"
                    "deployment.unit" "firmware image"
                }

                loop = component "Main loop and scan sequencer" "Health check, GPS, LO lock poll, temperature and Idq every 5 s, runRadarPulseSequence (15 beam positions, stepper step), AGC outer loop." "C++" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "main.cpp lines 2031-2180, 507-575"
                    }
                }
                health = component "Health monitor and emergency stop" "checkSystemHealth (clock, LO lock, ADAR1000 comm and >85 C, IMU, barometer, GPS fix age >30 s, Idq >2.5 A or <0.1 A, temperature >75 C, loop stall >60 s). Critical errors latch Emergency_Stop: TX mixers off, PA rails off, hold loop with IWDG refresh. IWDG about 4 s." "C++" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "main.cpp lines 633-760, 820-858, 861-950, 2835-2836; tests/test_gap3_*.c"
                        "safety.function" "SF-1 TX inhibit and PA rail cutoff"
                    }
                }
                beam = component "ADAR1000 manager" "Phase tables for 31 beam positions, TX/RX switching, PA and LNA bias of the beamformers." "C++" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "9_1_1_C_Cpp_Libraries/ADAR1000_Manager.cpp, main.cpp lines 447-477"
                    }
                }
                lo = component "Clock and LO manager" "AD9523-1 setup and sync, ADF4382A TX and RX setup, lock status." "C" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "9_1_1_C_Cpp_Libraries/ad9523.c, adf4382a_manager.c"
                    }
                }
                paBias = component "PA bias control" "DAC5578 Vg per channel, ADS7830 Idq per channel, closed-loop calibration at boot." "C" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "README.md (DAC5578, ADS7830), 9_1_1_C_Cpp_Libraries/DA5578.c, ADS7830.c"
                    }
                }
                usbCdc = component "USB CDC handler" "Sends GPS and pitch packets to the host. The start-flag wait was removed (STM32-006)." "C++" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "9_1_1_C_Cpp_Libraries/USBHandler.cpp, main.cpp lines 342-350, 1822-1835"
                    }
                }

                loop -> health "Calls once per loop iteration" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "main.cpp line 2037"
                    }
                }
                loop -> beam "Sets beam pattern per position" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "main.cpp lines 525-545"
                    }
                }
                health -> lo "Reads lock status" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "main.cpp lines 674-684"
                    }
                }
                health -> paBias "Reads Idq, clears DAC via CLR pin" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "main.cpp lines 737-747, 824-826"
                    }
                }
            }

            gui = container "Radar GUI V7" "Range-Doppler and target display, map, host commands, recording and replay. Older Tk bring-up dashboard V65 exists in parallel." "Python 3, PyQt6, pyftdi" {
                properties {
                    "origin" "Extracted"
                    "provenance" "9_Firmware/9_3_GUI/v7/, GUI_versions.txt, radar_protocol.py"
                }

                dashboard = component "Dashboard" "Main window, settings, target table." "PyQt6" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "v7/dashboard.py"
                    }
                }
                protocol = component "Radar protocol" "Packet parsing, opcode commands, FT2232H and FT601 connections, acquisition thread." "Python, pyftdi, ftd3xx" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "radar_protocol.py lines 53-110, 297-334"
                    }
                }
                workers = component "Workers" "QThreads: radar data, GPS data, replay." "PyQt6 QThread" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "v7/workers.py lines 48, 241, 411"
                    }
                }
                mapW = component "Map widget" "Map with selectable tile server and target overlay." "PyQt6" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "v7/map_widget.py"
                    }
                }

                dashboard -> protocol "Sends opcodes" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "v7/hardware.py imports RadarProtocol, Opcode"
                    }
                }
                workers -> protocol "Reads frames through" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "v7/workers.py line 50"
                    }
                }
                dashboard -> mapW "Shows targets on" "function call" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "v7/dashboard.py, v7/map_widget.py"
                    }
                }
            }

            recordings = container "Recordings" "Recorded radar frames for replay." "HDF5 files on the host" {
                tags "Database"
                properties {
                    "origin" "Extracted"
                    "provenance" "GUI_versions.txt (GUI_V65_Tk: HDF5 recording, replay), radar_protocol.py DataRecorder"
                }
            }
        }

        operator -> aeris.gui "Starts, configures and watches" "GUI" {
            properties {
                "origin" "Extracted"
                "provenance" "Project_Description.docx (GUI Connection and System Arming)"
            }
        }
        aeris.gui.protocol -> aeris.fpga.usbIf "Commands (opcodes) and radar data" "USB 2.0 FT2232H 245 synchronous FIFO" {
            properties {
                "origin" "Extracted"
                "provenance" "radar_protocol.py lines 8-9, 312-316; constraints/README.md USB_MODE"
                "trust.boundary.crossing" "yes"
            }
        }
        aeris.mcu.usbCdc -> aeris.gui.workers "GPS and pitch packets" "USB CDC virtual COM port" {
            properties {
                "origin" "Extracted"
                "provenance" "v7/hardware.py lines 44-55, main.cpp lines 1822-1829"
                "trust.boundary.crossing" "yes"
            }
        }
        aeris.mcu.loop -> aeris.fpga.chirp "New chirp, new elevation, new azimuth toggles; mixers master enable" "GPIO (PD8, PD9, PD10, PD11)" {
            properties {
                "origin" "Extracted"
                "provenance" "main.cpp lines 487, 526, 557, 1985 (PD11 HIGH at boot), 2042; radar_system_top.v lines 75-78"
                "safety.function" "SF-1 TX inhibit (PD11 LOW disables TX mixer through the FPGA AND gate)"
            }
        }
        aeris.fpga.receiver -> aeris.mcu.loop "AGC enable and saturation flags" "GPIO (DIG_5 PD13, DIG_6 PD14)" {
            properties {
                "origin" "Extracted"
                "provenance" "main.cpp lines 2182-2190"
            }
        }
        aeris.mcu.beam -> aeris.fpga "SPI to the ADAR1000s, level-shifted through FPGA pins (3V3 to 1V8)" "SPI pass-through" {
            properties {
                "origin" "Extracted"
                "provenance" "radar_system_top.v lines 50-61"
            }
        }
        aeris.gui.mapW -> tiles "Loads map tiles" "HTTPS" {
            properties {
                "origin" "Inferred"
                "provenance" "v7/map_widget.py tile servers; protocol not read in the code"
                "trust.boundary.crossing" "yes"
            }
        }
        aeris.gui.workers -> aeris.recordings "Writes and replays frames" "file I/O" {
            properties {
                "origin" "Extracted"
                "provenance" "GUI_versions.txt, v7/replay.py"
            }
        }
        aeris.mcu.loop -> gnss "Receives position and heading" "UM982 over UART5" {
            properties {
                "origin" "Extracted"
                "provenance" "main.cpp lines 1780-1805, 2064-2070"
            }
        }
        aeris.fpga.chirp -> bystander "Radiates RF energy through the array towards" "10.5 GHz, up to 16 x 10 W (AERIS-10E)" {
            tags "Inferred"
            properties {
                "origin" "Inferred"
                "provenance" "README.md output power and mechanical scan; the path DAC, mixer, ADAR1000, ADTR1107, PA, antenna is in RADAR_V6.drawio. A C4 relationship to a person stands for an energy path here, which C4 does not define"
            }
        }

        field = deploymentEnvironment "Field installation AERIS-10E" {
            radar = deploymentNode "Radar unit" "Enclosure with rotating antenna assembly, slip ring, stepper motor and cooling fans." "Mechanical assembly" {
                properties {
                    "origin" "Extracted"
                    "provenance" "README.md Miscellaneous Components, 8_Utils/Mechanical_Drawings/"
                    "failure.domain.host" "radar-unit"
                    "trust.boundary" "radar-hardware"
                }
                perspectives {
                    "VP06-RE-090" "Missing. No availability or recovery target in README.md, docs/*.html or Project_Description.docx (searched)." "Unassessable"
                    "VP06-RE-100" "Documented (RADAR_V6.drawio, README.md). One power board, one AD9523 clock, one MCU, one FPGA: each stops the radar. No target to judge the effect against." "Partially"
                    "VP06-RE-110" "Inapplicable: one radar unit, no redundant instances by design." "Inapplicable"
                    "VP06-RE-120" "Documented (main.cpp 633-950). Detection by a polled health check and IWDG (4 s). No failover: critical faults latch a safe stop, manual reset. Detection time not stated." "Partially"
                    "VP06-RE-130" "Inapplicable: no persistent state on the unit; registers reset to defaults (radar_system_top.v line 919)." "Inapplicable"
                    "VP06-RE-140" "Documented (main.cpp 727-731, 953, 2002). GNSS loss is a non-critical error with recovery; error_count is reset only at boot, so after more than 10 errors the unit enters safe mode (Inferred, not run on hardware). Tile servers affect the GUI map only." "Partially"
                    "VP06-RE-150" "Insufficient. The 5 Gap-3 MCU tests run in CI (Measured, Pipeline, run 38498070468) but test a copy of the logic, not main.cpp; no hardware fault test record (board-day worksheet empty)." "Unassessable"
                }

                mainBoard = deploymentNode "Main board" "DAC, mixers, beamformers, front ends, FPGA, MCU. 10 layers." "PCB, Eagle 7.4" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch, 4_7_Production Files/Gerber_Main_Board (L1-L10)"
                    }

                    fpgaDev = deploymentNode "FPGA device" "XC7A50T-2FTG256I on the production board." "Xilinx Artix-7" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "constraints/README.md Four Targets, xc7a50t_ftg256.xdc"
                        }
                        fpgaInst = containerInstance aeris.fpga
                    }
                    mcuDev = deploymentNode "Microcontroller" "STM32F746ZGT7." "ARM Cortex-M7" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "RADAR_V6.drawio, README.md"
                        }
                        mcuInst = containerInstance aeris.mcu
                    }
                    dac = infrastructureNode "DAC" "Chirp waveform at 120 MHz CMOS." "AD9708" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "RADAR_V6.drawio"
                        }
                    }
                    txMixer = infrastructureNode "TX mixer" "Up-conversion. Enable net MIX_TX_EN." "LTC5552" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "RADAR_V6.drawio, RADAR_Main_Board.sch net MIX_TX_EN"
                        }
                    }
                    beamformer = infrastructureNode "Beamformers" "4 x 4-channel phase shifters and VGAs." "ADAR1000" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "README.md, RADAR_V6.drawio"
                        }
                    }
                    frontEnd = infrastructureNode "Front ends" "16 x T/R front ends (LNA and PA, about 1 W each on AERIS-10N)." "ADTR1107" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "README.md (16x ADTR1107, Output Power ~1W x 16)"
                        }
                    }
                }

                synthBoard = deploymentNode "Frequency synthesizer board" "OCXO 10 MHz, clock generator, TX and RX LOs." "PCB" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch, RADAR_V6.drawio"
                    }
                    clockGen = infrastructureNode "Clock generator" "Phase-aligned clocks for LOs, DAC, ADC, FPGA." "AD9523-1" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "README.md"
                        }
                    }
                    los = infrastructureNode "Local oscillators" "TX 10.5 GHz and RX 10.5 GHz +/- IF." "2 x ADF4382" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "RADAR_V6.drawio"
                        }
                    }
                }

                powerBoard = deploymentNode "Power board" "All rails. PA rails +5V0_PA_1..3, +5V5_PA switched by MCU enables. No net named STOP, KILL, INTERLOCK or EMERG (scripted search of net names)." "PCB, Eagle 9.6.2" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "4_6_Schematics/PowerBoard/PowerBoard.sch net names (grep of <net name=...>, 2026-11-22); RADAR_Main_Board.sch EN_+5V5_PA, EN/DIS_RFPA_VDD"
                        "failure.domain.host" "power-board"
                    }
                    regulators = infrastructureNode "PA rail regulators" "Switched supplies for the PA and front-end stages." "Regulators with enable" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "PowerBoard.sch nets EN_+5V0_PA1..3, EN_+5V5_PA"
                        }
                    }
                }

                paBoard = deploymentNode "PA board" "One 10 W GaN power amplifier per channel. AERIS-10E only." "PCB" 16 {
                    properties {
                        "origin" "Extracted"
                        "provenance" "README.md (16x Power Amplifier Boards, QPA2962), 4_6_Schematics/PowerAmplifierBoard/RF_PA.sch"
                    }
                    pa = infrastructureNode "Power amplifier" "10 W GaN. Vg from DAC5578, Idq through 5 mOhm shunt." "QPA2962" {
                        properties {
                            "origin" "Extracted"
                            "provenance" "README.md"
                        }
                    }
                }

                antenna = infrastructureNode "Antenna array" "32x16 dielectric-filled slotted waveguide array, electronic steering +/-45 degrees, mechanical 360 degrees." "Waveguide array" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "README.md Technical Specifications, 4_6_Schematics/Antennas/Waveguide/"
                    }
                }
                stepper = infrastructureNode "Stepper motor and slip ring" "Rotates the antenna assembly, 200 steps per revolution." "Stepper, slip ring" {
                    properties {
                        "origin" "Extracted"
                        "provenance" "main.cpp lines 198-199, 561-566; 8_Utils/Mechanical_Drawings/SlipRing.dwg"
                    }
                }
            }

            host = deploymentNode "Host computer" "Runs the GUI, connected by two USB cables." "Python 3.8+ on a PC" {
                properties {
                    "origin" "Extracted"
                    "provenance" "README.md Prerequisites, radar_protocol.py, v7/hardware.py"
                    "failure.domain.host" "host-pc"
                    "trust.boundary" "operator-host"
                }
                containerInstance aeris.gui
                containerInstance aeris.recordings
            }

            internet = deploymentNode "Public Internet" "" "Internet" {
                tags "Inferred"
                properties {
                    "origin" "Inferred"
                    "provenance" "Tile servers in v7/map_widget.py are public services"
                    "trust.boundary" "internet"
                }
                softwareSystemInstance tiles
            }

            field.radar.mainBoard.dac -> field.radar.mainBoard.txMixer "Chirp at IF" "analog" {
                properties {
                    "origin" "Extracted"
                    "provenance" "RADAR_V6.drawio (To TX Mixer, LPF)"
                }
            }
            field.radar.synthBoard.los -> field.radar.mainBoard.txMixer "TX LO 10.5 GHz" "RF, twinax" {
                properties {
                    "origin" "Extracted"
                    "provenance" "RADAR_V6.drawio (Local Oscillator ADF4382 TX, Twinax connectors)"
                }
            }
            field.radar.synthBoard.clockGen -> field.radar.synthBoard.los "Reference clocks" "LVDS, CMOS" {
                properties {
                    "origin" "Extracted"
                    "provenance" "README.md Frequency Synthesizer Board"
                }
            }
            field.radar.mainBoard.txMixer -> field.radar.mainBoard.beamformer "RF TX, split 16 ways" "RF" {
                properties {
                    "origin" "Extracted"
                    "provenance" "RADAR_V6.drawio (Combiner EP4RKU+, ADAR1000)"
                }
            }
            field.radar.mainBoard.beamformer -> field.radar.mainBoard.frontEnd "Phase-shifted RF per channel" "RF" {
                properties {
                    "origin" "Extracted"
                    "provenance" "RADAR_V6.drawio"
                }
            }
            field.radar.mainBoard.frontEnd -> field.radar.paBoard.pa "RF drive per channel" "RF" {
                properties {
                    "origin" "Extracted"
                    "provenance" "README.md (PA boards used only for AERIS-10E)"
                }
            }
            field.radar.paBoard.pa -> field.radar.antenna "10 W per channel" "RF" {
                tags "Inferred"
                properties {
                    "origin" "Inferred"
                    "provenance" "README.md output power 10W x 16; the connection is not read in RF_PA.sch"
                    "safety.function" "hazard source: radiated RF energy"
                }
            }
            field.radar.powerBoard.regulators -> field.radar.paBoard.pa "PA supply" "DC rail" {
                properties {
                    "origin" "Extracted"
                    "provenance" "PowerBoard.sch nets +5V0_PA_1..3, +5V5_PA"
                }
            }
            field.radar.mainBoard.mcuDev.mcuInst -> field.radar.powerBoard.regulators "Enables and cuts PA rails (EN_+5V0_PA1..3, EN_+5V5_PA, EN/DIS_RFPA_VDD)" "GPIO" {
                properties {
                    "origin" "Extracted"
                    "provenance" "main.cpp lines 838-848, RADAR_Main_Board.sch nets"
                    "safety.function" "SF-1 TX inhibit and PA rail cutoff"
                }
            }
            field.radar.mainBoard.fpgaDev.fpgaInst -> field.radar.mainBoard.txMixer "TX mixer enable" "GPIO MIX_TX_EN" {
                properties {
                    "origin" "Extracted"
                    "provenance" "plfm_chirp_controller.v lines 84-88, RADAR_Main_Board.sch net MIX_TX_EN"
                    "safety.function" "SF-1 TX inhibit"
                }
            }
            field.radar.mainBoard.fpgaDev.fpgaInst -> field.radar.mainBoard.dac "Waveform samples" "8-bit CMOS 120 MHz" {
                properties {
                    "origin" "Extracted"
                    "provenance" "radar_system_top.v lines 32-34, RADAR_V6.drawio"
                }
            }
            field.radar.mainBoard.mcuDev.mcuInst -> field.radar.stepper "Steps the antenna" "GPIO STEPPER_CLK+, STEPPER_CW+" {
                properties {
                    "origin" "Extracted"
                    "provenance" "main.cpp lines 561-566, RADAR_Main_Board.sch nets"
                }
            }
        }
    }

    views {
        systemContext aeris "context" "VP01 Context" {
            include *
            autoLayout lr
        }
        container aeris "containers" "VP02 Functional (software part only)" {
            include *
            autoLayout lr
        }
        component aeris.fpga "fpgaComponents" "VP02 Functional, FPGA" {
            include *
            autoLayout lr
        }
        component aeris.mcu "mcuComponents" "VP02 Functional and VP04 Concurrency (in part), MCU" {
            include *
            autoLayout lr
        }
        component aeris.gui "guiComponents" "VP02 Functional, GUI" {
            include *
            autoLayout lr
        }
        deployment aeris field "deployment" "VP06 Deployment, hardware structure and RF energy path" {
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
            element "Inferred" {
                border dashed
            }
            relationship "Inferred" {
                style dashed
            }
        }
    }

    configuration {
        scope softwaresystem
    }
}
