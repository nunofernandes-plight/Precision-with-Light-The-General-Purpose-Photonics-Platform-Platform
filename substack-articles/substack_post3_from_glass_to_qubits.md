# From Glass to Qubits: Silicon Photonics and the Platform Under the Platform

### How a data center crisis, a programmable chip, and a twenty-mode quantum processor point to the same software gap

---

*This is the third post in the **Precision with Light** founding series. Post 1 covered the six research papers that made the platform inevitable. Post 2 explained why inverse design is not just faster — it is categorically different. This post moves from fiber to silicon, from laboratory to data center, and from classical to quantum.*

---

## The Wall Nobody Talks About

Somewhere in a data center outside Phoenix, a network switch is consuming 300 watts. Of those 300 watts, approximately 30% — nearly 100 watts — is spent not on switching, not on logic, not on memory. It is spent moving electrical signals across a few centimetres of copper trace between the switch ASIC and its optical transceivers, sitting in pluggable cages on the faceplate of the chassis.

Copper at high frequency is inefficient. At 100 Gbps per lane, a centimetre of copper trace dissipates measurable power. At 200 Gbps per lane — the rate that data centers are moving to now, driven by AI training workloads — the loss doubles. At 400 Gbps, it doubles again. The scaling law is brutal: as data rates climb to serve the bandwidth demands of million-GPU AI clusters, the power cost of the electrical interconnect between ASIC and optics becomes the dominant term in the system power budget.

The industry name for the solution is **Co-Packaged Optics** (CPO). The concept is simple: move the optical transceiver from the faceplate of the chassis to the surface of the package substrate, millimetres from the switch ASIC rather than centimetres away. Eliminate the high-speed electrical trace. Replace it with a silicon photonic waveguide — which carries light, not electrons, and dissipates essentially no power in transit.

NVIDIA announced their Spectrum-X Ethernet Photonics switches in 2026, delivering 409.6 Tb/s of bandwidth with co-packaged optics integrated directly onto the ASIC package. Each switch contains up to 16 co-packaged photonic integrated circuits. Analysts at IDTechEx project the CPO market will grow at a compound annual rate of 37% from 2026, reaching over $20 billion by 2036.

There are, at last count, not enough photonic integrated circuit designers in the world to design all of those PICs.

That is the gap this platform fills.

---

## Why Silicon Won

Before co-packaged optics became the dominant discussion in data center networking, silicon photonics spent fifteen years as an interesting research platform that kept almost but never quite reaching industrial scale. The reasons it finally did — and why it specifically won over competing platforms like Indium Phosphide, Lithium Niobate, or polymer waveguides — are instructive for understanding what your platform needs to design.

Silicon photonics' singular advantage is its **fabrication infrastructure**. The same 193nm deep-UV lithography that makes transistors at Intel and TSMC can pattern silicon waveguides with 10nm precision. The same 300mm wafer handling equipment that drives semiconductor economics applies to photonic chips. The design rule vocabulary — minimum feature sizes, layer thicknesses, doping profiles — is identical to CMOS. A silicon photonics foundry is, structurally, a CMOS foundry with a few additional process steps.

This gives silicon photonics a cost and scaling trajectory that no other photonic platform can match. A silicon photonic chip fabricated at AIM Photonics on a 300mm wafer costs a fraction of what the same function would cost in InP or LiNbO₃, and the cost per wafer improves with each process node generation.

The tradeoff is well-understood: silicon's high refractive index contrast — n_Si ≈ 3.47 versus n_SiO₂ ≈ 1.44 — enables sub-micron waveguide dimensions and tight bends, but imposes extremely stringent fabrication tolerances. A 10nm variation in waveguide width shifts the effective mode index by a measurable amount, which changes the resonant wavelength of a ring filter, which shifts the channel allocation of a WDM system. At the scale of a co-packaged switch PIC with 16 wavelength channels per port and 32 ports per chip, yield management becomes the central engineering challenge.

A 2018 review by Wim Bogaerts at Ghent University/IMEC and Lukas Chrostowski at UBC — the canonical reference document for silicon photonic circuit design methodology — states this precisely: *nanometer-scale variations in waveguide core width or thickness can have non-negligible effects on the performance of photonic circuits, and large complex circuits will automatically suffer more from variability than simple circuits.* The paper maps the design flow from schematic capture through layout, simulation, and verification, and identifies variability analysis and photonic-electronic co-simulation as the open challenges that the field had not yet solved.

Six years later, those challenges remain open. And the data center industry's requirement for CPO has made solving them urgent rather than merely interesting.

---

## The PDK Gap: Rules Without a Solver

Every silicon photonic circuit that reaches a foundry does so through a **Process Design Kit** — a PDK. The PDK is the machine-readable specification of everything the fabrication process constrains: waveguide dimensions, bend radii, coupling gaps, doping profiles, layer thicknesses, design rule checks. It is the contract between the designer and the foundry.

The current state of photonic PDKs has a structural problem.

Each foundry provides PDKs in different formats, for different design tools, maintained by independent support teams. A design optimized for the AIM Photonics 300mm process in Cadence Virtuoso cannot be trivially ported to IMEC iSiPP50G in Mentor Pyxis, or to IHP SG25H5 in KLayout. The constraint information is the same — the physics doesn't change by foundry — but the representation is proprietary, tool-specific, and manually maintained.

The consequence is fragmentation. A research group that designs at one foundry, then wants to compare fabrication outcomes at a second, must rebuild their constraint layer from scratch. A startup that wins access to an MPW run at a European foundry through JePPIX, then wants to tape out at an American foundry through AIM Photonics, faces the same reconstruction. Expert time spent recreating constraint tables that should be machine-generated.

**OpenEPDA** — developed at TU Eindhoven and validated through the JePPIX consortium with three foundries and four EDA tool vendors — proposes a solution: a standardized, software-independent PDK representation. One dataset from the foundry, compilable into any design tool's native format. The same constraint information, expressed once, usable everywhere.

For the Precision with Light platform, OpenEPDA-compatible PDK ingestion is the mechanism by which the DSR-CRAG constraint database stays current automatically. When AIM Photonics updates their process design rules — as they do periodically — the platform ingests the new OpenEPDA-formatted specification, the constraint database updates, and every subsequent design reflects the new rules. No manual re-entry. No stale DRC violations discovered at tape-out.

This matters at the AIM scale: a 5µm radius ring modulator fabricated on their 300mm process — recently characterized and published, achieving over 20nm of bandwidth with 1.5nm/V modulation efficiency — defines the practical minimum bend radius for that process node. Below 5µm, the ring's radiation loss exceeds the free spectral range engineering budget. That constraint is not a guideline. It is a hard wall. The DSR-CRAG engine enforces it before generation, not after.

---

## The Programmable Chip: An FPGA for Photons

In the spring of 2026, a paper appeared in *Laser & Photonics Reviews* from the group of Prof. José Capmany at the University of Valencia — the iTEAM institute, one of the world's leading centres for microwave photonics and programmable photonic systems. The paper introduced a concept that deserves to be recognised as a paradigm shift: **non-uniform programmable photonic waveguide meshes**.

A photonic waveguide mesh is a silicon photonic chip patterned as a two-dimensional lattice of Tunable Basic Units (TBUs) — each TBU is a Mach-Zehnder interferometer with thermo-optic phase shifters that can be set to any splitting ratio from 0 to 100%. The lattice can be reconfigured in software to implement arbitrary linear optical transformations: filters, delay lines, beam formers, matrix multipliers, optical neural network layers. Without changing the hardware. Without new fabrication. By changing the phase settings — a software operation taking microseconds.

This is the photonic equivalent of the Field Programmable Gate Array. Capmany's group coined the term **FPPGA** — Field Programmable Photonic Gate Array — and filed a patent application through Universitat Politècnica de Valencia in 2023. The commercial spinout, iPronics, was acquired and its technology integrated into a major photonic systems company. The mesh concept has moved from research to product.

The non-uniform extension that the 2026 paper introduces is subtle but consequential. A standard hexagonal mesh has uniform unit cell dimensions — every TBU has the same round-trip path length, fixing the Free Spectral Range and temporal resolution of the entire chip at fabrication time. The non-uniform design embeds "defect cells" of different sizes into the otherwise uniform lattice, exploiting the Vernier effect: two slightly different round-trip lengths produce an extended FSR equal to FSR₁ × FSR₂ / |FSR₁ − FSR₂|. Coarse spectral tuning and fine temporal resolution, simultaneously, from a single fabricated chip, through software control alone.

The platform implications are significant. Designing an FPPGA is a two-level problem. The **hardware level** — what mesh topology, how many TBUs, where to place defect cells — is a one-time fabrication decision. The **software level** — what phase settings to program to implement a given optical function — is an infinitely reconfigurable post-fabrication operation. Your platform addresses both: the hardware level through the generative inverse design engine (optimising the mesh topology for a target application space), and the software level through a photonic circuit compiler (mapping a desired transfer function to TBU phase settings). Neither capability exists in any commercial photonic design tool today.

The commercial connection to data centers is direct. The Capmany group's switch characterisations include a 64×64 optical switch array based on Benes topology — precisely the switching architecture used in data center spine-leaf fabrics. A software-programmable 64×64 photonic switch, fabricated in silicon with CMOS-compatible processes, is the device that enables the CPO architectures described in the previous section to be truly flexible rather than hardwired for a single routing configuration.

---

## The Quantum Leap: From 8 Modes to 20

In 2019, a research group spanning QuiX Quantum in Enschede and the University of Twente published a paper in *Optics Express* describing an 8×8 reconfigurable quantum photonic processor — 64 mode pairs, 56 independent Mach-Zehnder interferometers, thermo-optic phase control, all on a silicon nitride chip. It was, at the time, the largest programmable quantum photonic processor demonstrated.

The platform of choice was not silicon-on-insulator. It was **Si₃N₄** — stoichiometric silicon nitride. The reason is one number: two-photon absorption. Silicon's bandgap (1.1 eV) is smaller than the energy of two 1550nm photons (0.8 eV each, total 1.6 eV). In a classical silicon photonic modulator or switch, this two-photon absorption is a minor loss mechanism. In a quantum photonic circuit, where information is encoded in individual photon states, any absorption event destroys the quantum information irreversibly. Si₃N₄ has a bandgap of approximately 5 eV — two photons at any wavelength relevant to quantum communication cannot be absorbed. The qubit survives the waveguide.

By 2022 — published in 2023 — the same group at QuiX Quantum reported a **20-mode universal quantum photonic processor**: 190 independent MZIs, amplitude fidelity of 97.4% for Haar-random unitary matrices, Hong-Ou-Mandel interference visibility of 98%, optical loss of 2.9 dB averaged over all modes. The largest universal QPP ever demonstrated at the time of publication.

The scaling law embedded in this progression — 8 modes in 2019, 20 modes in 2022 — follows a trajectory toward the 50–100 mode processors that theoretical analyses suggest are required for quantum computational advantage in chemistry simulation and optimisation problems. The hardware is scaling. The software layer for programming and verifying these devices is not keeping pace.

A 20-mode QPP has 190 MZIs, each with two phase shifters. The configuration space is 380-dimensional — a 380-dimensional continuous parameter space where each point corresponds to a specific linear optical transformation. Programming the device to implement a target quantum operation (expressed as a unitary matrix U) requires decomposing that unitary into a sequence of MZI settings using algorithms like Clements decomposition or Reck decomposition. This is the **quantum circuit synthesis problem**, and it is an inverse design problem: given the target (a unitary matrix), find the hardware configuration (380 phase settings) that implements it.

A third paper from late 2025 — a theoretical analysis of a quantum algorithm for graph isomorphism implemented on a Gaussian Boson Sampling device — illustrates what these processors will be used for. Graph isomorphism, molecular simulation, quantum chemistry, machine learning kernel estimation: these are the computational targets of the NISQ era. The QPP is the hardware. Your platform, applied to quantum photonics, becomes the design tool that synthesises the Si₃N₄ chip layouts for MPW fabrication and the compiler that maps quantum algorithms to phase configurations.

---

## Inverse Design Closes the Loop

In October 2025, *Nature Communications* published a paper that should be read as the silicon photonics inverse design existence proof.

Three freeform silicon nitride devices — a coarse wavelength-division multiplexer, a five-mode mode division multiplexer, and a polarisation beam splitter — designed by inverse methods, fabricated, and characterised. The footprint reduction compared to conventional designs: **up to 1,200×**. A device that previously required 1,200 square microns of chip area now fits in 1 square micron. Minimum feature sizes of 160nm — within the capability of standard deep-UV photolithography, compatible with production processes.

A 1,200× footprint reduction is not a marginal improvement. It is qualitatively transformative. At the scale of a co-packaged switch PIC — where the photonic IC must fit within the thermal and area budget of a data center ASIC package, where every square micron of chip area costs real money on a 300mm wafer — this kind of density improvement is the difference between feasible and infeasible integration.

The paper is also, structurally, identical in argument to the FWM inverse design paper in the fiber photonics corpus. The forward problem is well-posed. The training data is available. The neural network learns the inverse mapping. The fabricated device matches the design. The proof of concept is complete.

What neither paper addresses is the end-to-end workflow: from a natural language design intent to a fabrication-ready layout file, with hard physical and fabrication constraints enforced at every step, and solver verification integrated before export. That workflow is the platform.

---

## The Stack, Assembled

Reading the three posts in this series together, a single architecture emerges — applicable to fiber photonics, silicon photonics, and quantum photonic processors alike.

At the base is a **physics constraint database**: PDK design rules for silicon foundries, ARROW conditions for anti-resonant fibers, phase matching conditions for nonlinear devices, fabrication tolerances from CVD and two-photon polymerization processes. Machine-readable, automatically updated from standardized PDK representations, enforced before generation.

Above it is a **generative inverse design engine**: physics-informed neural networks that have internalised Maxwell's equations, conditional Wasserstein GANs that synthesise geometry from optical performance targets, surrogate models that reduce hours of FDTD simulation to milliseconds of inference.

Above that is a **verification bridge**: cloud-native FDTD via Tidy3D for silicon photonic components, finite element mode solving via COMSOL for fiber cross-sections, Lumerical FDTD for full three-dimensional device characterisation. Every AI-generated design passes through a solver before leaving the platform.

At the top is a **fabrication export layer**: GDSII for silicon photonics foundry runs, STL for two-photon polymerisation printers, draw tower specifications for specialty fiber manufacturers, OpenEPDA-compatible PDK update ingestion. The platform does not produce designs. It produces designs that can be built.

The fiber corpus that motivated Post 1 described the platform's existence proof in fiber photonics. The silicon photonics corpus described here extends it to the semiconductor domain where the data center, the quantum computer, and the programmable photonic mesh all converge. These are not separate applications of the same tool. They are the same abstract problem — geometry to performance, performance to geometry, with physics as the invariant — expressed in different materials and at different scales.

The platform is the abstraction layer that spans all of them.

---

## What Comes Next in This Series

**Post 4** — *"Why AI Needs Physics: The Case Against Black-Box Surrogates in Photonics Design"*: the rigorous argument for physics-informed over purely data-driven approaches. What the latest PINN methodology literature demonstrates, why the multi-level decomposition of fourth-order PDEs matters for training stability, and what "trustworthy surrogate" actually means in a context where an undetected failure mode sends a design to a $50,000 foundry run.

**Post 5** — *"Open for Business"*: the complete platform architecture, the commercial and academic access model, partnership opportunities, and the roadmap from current state to Multi-Project Wafer batch endpoints and autonomous system-level PIC synthesis.

---

*The data center bandwidth crisis is real. The quantum photonics scaling challenge is real. The photonic design tooling gap — the missing inverse design layer between performance specification and fabrication-ready geometry — is real. If any of these problems intersect with your work, I want to hear from you.*

*Subscribe below to follow the series. The next post will be the most technically demanding one — and the most important for understanding why physics-informed AI is not optional in this domain.*

---

**Nuno Edgar Nunes Fernandes**
*Founder, Precision with Light*
*[precisionwithlight.substack.com](https://precisionwithlight.substack.com) · [GitHub](https://github.com/nunofernandes-plight/Precision-with-Light-The-Photonics-Platform)*
