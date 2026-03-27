# The Question Every Photonics Engineer Asks Backwards

### Why inverse design is not just faster — it is categorically different

---

*This is the second post in the **Precision with Light** founding series. If you missed the first post — the story of six research papers and the platform they made inevitable — [you can read it here](https://github.com/nunofernandes-plight/Precision-with-Light-The-Photonics-Platform/blob/main/substack-articles/post1_founding_narrative.md).*

---

## The Wrong Question

Every simulation tool ever built for photonics answers the same question.

Given this geometry — this core diameter, this cladding structure, this refractive index profile — what does the light do?

It is a reasonable question. It is the question that COMSOL answers, that Ansys Lumerical answers, that RP Fiber Power answers. Run the finite element solver, apply Maxwell's equations to the geometry you have defined, and the software tells you the mode profile, the loss, the dispersion, the nonlinear coefficient. Fast, accurate, trustworthy.

The problem is that it is the wrong question.

The question that engineers actually need answered is different. A biomedical imaging researcher doesn't start with a fiber geometry and wonder what it does. They start with a clinical requirement — a 770nm probe beam for two-photon imaging through tissue — and ask: *what fiber do I need to build?* An industrial laser engineer doesn't start with a waveguide cross-section and observe the dispersion profile. They specify a target: zero-dispersion wavelength at 1030nm, anomalous dispersion across the Yb gain bandwidth, confinement loss below 0.01 dB/km. Then they ask: *what geometry produces this?*

That is the inverse problem. And for thirty years of modern photonics engineering, it has had no software answer. The inverse problem belonged entirely to human intuition, accumulated domain knowledge, and exhaustive manual search through design space.

Until it doesn't have to.

---

## What Makes a Problem Invertible

To understand why inverse design is only now becoming practical, it helps to understand what makes a physical design problem tractable as a machine learning task.

Three conditions must hold.

**The forward mapping must be learnable.** The relationship between geometry and optical performance must be a well-defined function — not random, not chaotic, but a continuous mapping that a neural network can approximate. For photonic crystal fibers, the relationship between pitch Λ, hole diameter d, and operating wavelength λ on one side, and effective index n_eff, mode area A_eff, and dispersion D(λ) on the other, is exactly this kind of mapping. Nonlinear and high-dimensional, but continuous and learnable.

**The design space must be searchable.** There must be enough geometric variation, produced at reasonable computational cost, to build a training dataset. This is where the traditional FEM bottleneck has been a barrier. A single Lumerical FDTD simulation of a complex PCF geometry can take hours. A comprehensive training dataset requires tens of thousands of these simulations. The cost is prohibitive unless you have a supercomputing cluster and weeks of patience.

**The physics must be enforced.** A naive neural network will happily predict geometries that are faster to generate than physically valid. An n_eff that exceeds the silica refractive index. A dispersion curve that violates causality. A mode area that is geometrically impossible for the specified core radius. These "hallucinated" solutions are the central danger of applying machine learning to physics problems without appropriate constraints.

The sixth paper in the founding corpus — a 2023 paper from MDPI Photonics on inverse design of photonic crystal fibers for four-wave mixing — demonstrated that all three conditions can be satisfied simultaneously, and that the result is not just a faster version of the existing workflow. It is a categorically different capability.

---

## The Four-Wave Mixing Proof

Four-wave mixing is a third-order nonlinear optical process. Two pump photons at frequency ω_p interact inside a fiber to generate a signal photon at ω_s and an idler at ω_i, conserving energy: 2ω_p = ω_s + ω_i.

The efficiency of this frequency conversion depends critically on phase matching — the condition that the wave vectors of all participating waves remain synchronized along the interaction length. In mathematical terms:

Δβ = β(ω_s) + β(ω_i) − 2β(ω_p) + 2γP = 0

where γ is the nonlinear coefficient of the fiber and P is the pump power. The propagation constants β(ω) are themselves functions of the fiber's dispersion profile D(λ), which is determined entirely by the fiber's cross-sectional geometry.

The target application was biomedical imaging. The requirement: a 1064nm pump laser — widely available, commercially mature — generating a signal at exactly **770nm**. That wavelength is not arbitrary. It sits in the first biological transparency window, where tissue scattering and water absorption are simultaneously minimized. It matches the excitation wavelength of specific fluorescent probes used in two-photon microscopy. It enables imaging depths and resolutions not achievable at longer wavelengths.

The engineering challenge: find a photonic crystal fiber geometry whose dispersion profile satisfies the phase matching condition for this specific pump-signal pair. In traditional practice, this means running hundreds of FEM simulations, computing D(λ) for each candidate geometry, checking whether the phase matching condition is satisfied, and iterating. Days of expert work, at minimum.

The paper's approach was different. A deep neural network was trained on a library of geometry-to-dispersion mappings — thousands of PCF geometries, each characterized by its pitch, hole diameter ratio, and core structure, each paired with its numerically computed dispersion profile. Once trained, the network learned the inverse mapping: given a target dispersion profile that satisfies phase matching for the desired pump-signal pair, synthesize the PCF geometry that produces it.

Forward simulation time per geometry: hours.
Inverse design inference time: **under one millisecond.**

The network produced a manufacturable PCF geometry whose dispersion profile, when verified by FEM, satisfied the phase matching condition for 1064nm → 770nm conversion. The result was not approximate. It was not a good starting point for further manual optimization. It was the answer.

---

## Why This Is Not Just Speed

The temptation is to frame inverse design as an acceleration technology. Weeks become milliseconds. That framing is accurate but insufficient.

The more important consequence is that it changes *who can design photonic devices*.

With traditional FEM-based forward design, producing a novel PCF geometry for a specific application requires: familiarity with the FEM solver and its mesh convergence behavior, deep intuition about the geometry-performance mapping, access to expensive software licenses, and weeks of available time. This is the profile of a senior optical engineer with a decade of specialist experience. Most photonics companies have one or two such people. Most academic research groups have one.

With inverse design, the workflow becomes: specify the target performance. Receive candidate geometries. Verify with a single forward simulation. The required expertise shifts from "how to navigate the design space" to "how to specify the target correctly." A junior engineer with solid optics fundamentals can produce design candidates that previously required rare specialist knowledge.

This has a direct consequence for innovation velocity. If the design bottleneck is removed, the fabrication and characterization cycle becomes the rate-limiting step — and that cycle is already getting faster with MPW (Multi-Project Wafer) services and automated characterization platforms. The entire R&D pipeline accelerates.

---

## The Physics Constraint Problem — And Why It Cannot Be Ignored

Inverse design without physics enforcement is dangerous in ways that are easy to underestimate.

A standard neural network trained to map optical targets to geometries will occasionally produce outputs that satisfy the training loss while violating physical reality. The three most common failure modes in photonics inverse design are:

**Evanescent field violations.** The predicted effective index Re(n_eff) exceeds the core material index — physically impossible, since guided modes must satisfy n_clad < Re(n_eff) < n_core. A network that has never been explicitly constrained to respect this boundary will violate it in corner cases of the parameter space.

**Fabrication rule violations.** The predicted geometry has feature sizes below the lithographic resolution limit of the target process. A sub-100nm air hole in a PCF cannot be reliably drawn with a stack-and-draw fabrication process. A ring resonator with a 2µm radius cannot be fabricated in AIM Photonics' 300mm SOI process where the practical minimum is approximately 5µm. Geometries that ignore these rules are academically interesting and industrially useless.

**Topological discontinuities.** The network interpolates through a region of design space that corresponds to a discontinuous change in guidance mechanism — for example, from index-guiding to bandgap-guided operation in a PCF. The interpolated geometries in between are not physical solutions; they correspond to no stable guided mode. Standard neural networks cannot detect these discontinuities and will synthesize geometries that fall into them.

Physics-Informed Neural Networks (PINNs) address the first failure mode directly, by incorporating the residual of the governing wave equation into the training loss:

L_total = w₁ · L_data + w₂ · L_physics

where L_physics is the norm of the Helmholtz equation residual evaluated at the predicted field and eigenvalue. A network that violates Maxwell's equations is penalized during training, not just at inference time. The result is a model that has internalized the physics, not just approximated the data.

The second and third failure modes require a different mechanism: a design rule constraint database, queried before generation rather than after. This is the architectural innovation at the heart of the **DSR-CRAG** system that powers this platform — Dual-State Corrective Retrieval-Augmented Generation. When a design request arrives at the Intent Layer, the first operation is not generation. It is retrieval: pull the relevant fabrication constraints for the target process node, apply them as hard boundaries, and only then allow the generative engine to operate within the feasible space.

The difference between a generative AI that synthesizes photonic devices and one that synthesizes *manufacturable* photonic devices is this constraint layer. Without it, the platform produces interesting geometries. With it, it produces designs that can be taped out.

---

## Inverse Design at the Silicon Photonics Scale

The fiber inverse design proof of concept is compelling, but fiber geometry is a relatively low-dimensional problem. The PCF design space is spanned by three to six continuous parameters, and the fabrication process is a single draw-tower operation. Silicon photonics design is more complex by an order of magnitude.

A silicon photonic integrated circuit involves dozens to hundreds of individual components — waveguides, bends, directional couplers, ring resonators, grating couplers, modulators, photodetectors — each with its own geometry, each interacting with adjacent components through optical coupling and thermal crosstalk. The design space is not three-dimensional. It is effectively infinite.

A 2025 paper in Nature Communications demonstrated inverse design on the silicon nitride platform — the same Si₃N₄ material used by QuiX Quantum for their quantum photonic processors, and an increasingly important platform for both classical and quantum photonic integration. The results were striking: freeform inverse-designed devices achieved up to a **1,200× reduction in footprint** compared to conventional designs, while maintaining minimum feature sizes of 160nm — well within the capability of standard photolithography. A wavelength-division multiplexer, a five-mode multiplexer, and a polarization beam splitter: three different device types, all compressed by three orders of magnitude in area, all fabricated and characterized successfully.

A 1,200× footprint reduction is not an incremental improvement. It is a qualitative change in what silicon photonic integration density is possible. It means functions that previously required a millimeter of waveguide length can be implemented in a micrometer. At the scale of a co-packaged optics switch PIC — carrying 16 channels, each at 200Gbps, on a chip that must fit within the thermal and area budget of a data center ASIC package — this kind of density improvement is the difference between feasible and infeasible.

---

## The Process Design Kit: Physics Constraints Made Machine-Readable

There is one more layer of the inverse design story that rarely appears in academic papers but is essential to any platform that aims to produce real devices.

Process Design Kits — PDKs — are the machine-readable specifications that foundries provide to designers. A PDK encodes, in software, the complete set of constraints that a fabrication process imposes: minimum feature sizes, layer thicknesses, doping profiles, metal stack definitions, design rule checks. Every silicon photonic circuit that reaches a foundry does so through a PDK.

The current state of photonic PDKs mirrors the state of photonic simulation tools before inverse design: powerful, necessary, and requiring deep specialist knowledge to use. Different foundries provide PDKs in different formats, for different design tools, maintained by separate teams. The result is fragmentation: a design optimized for the AIM Photonics 300mm process cannot be trivially ported to IMEC iSiPP50G or IHP SG25H5 without reconstructing the constraint layers from scratch.

The OpenEPDA initiative — developed at TU Eindhoven and validated through the JePPIX European MPW consortium — is attempting to solve this with a standardized, software-independent PDK representation. One dataset from the foundry, compiled into any design tool's native format. The approach has been validated with three foundries and four EDA tool vendors.

For the Precision with Light platform, OpenEPDA-compatible PDK ingestion is not a nice-to-have. It is the mechanism by which the DSR-CRAG constraint database stays current as foundry processes evolve. When AIM Photonics updates their process design rules — as they do with each process node revision — an OpenEPDA-formatted update is ingested, the constraint database updates automatically, and every subsequent design generated by the platform reflects the new rules. No manual constraint re-entry. No risk of designing to stale DRC rules.

The physics is enforced by the PINNs. The fabrication rules are enforced by the PDK. Together, they make the guarantee: every geometry this platform produces is not just physically valid, but foundry-ready.

---

## What This Means for the Platform

The inverse design capability described in this post is not a feature of the Precision with Light platform. It is the platform's core value proposition, stated precisely:

*A system that takes optical performance targets as input, enforces hard physical and fabrication constraints before generation, synthesizes manufacturable geometries using physics-informed generative AI, and verifies the results against industry-standard solvers before delivery.*

The FWM paper demonstrated this for fiber photonics. The Nature Communications Si₃N₄ paper demonstrated it for integrated silicon photonics. The PDK standardization work provides the constraint layer that makes the generated designs foundry-ready. The multi-level PINN framework from the latest computational physics literature provides the architecture that prevents physical constraint violations during generation.

The pieces are all present. The platform assembles them.

---

## What Comes Next

**Post 3** — *"From Glass to Qubits: Silicon Photonics, Co-Packaged Optics, and the Platform Under the Platform"*: the data center AI infrastructure story, programmable photonic meshes, quantum photonic processors, and why the MPW batch endpoint changes the economics of photonics R&D.

**Post 4** — *"Why AI Needs Physics: The Case Against Black-Box Surrogates in Photonics Design"*: the rigorous argument for physics-informed approaches, what the latest PINN methodology says about surrogate models you can actually trust, and the multi-fidelity simulation strategy that makes verification tractable.

**Post 5** — *"Open for Business"*: the complete platform architecture, the partnership model, and how to get involved — whether as a research collaborator, an industry partner, or an academic institution seeking access.

---

*If inverse design is a problem space your team is working on — in fiber photonics, silicon photonics, or anywhere in the broader landscape of computational electromagnetics — I want to hear from you. The design software layer for the next decade of photonics is being built now.*

*Subscribe below to follow the series.*

---

**Nuno Edgar Nunes Fernandes**
*Founder, Precision with Light*
*[precisionwithlight.substack.com](https://precisionwithlight.substack.com) · [GitHub](https://github.com/nunofernandes-plight/Precision-with-Light-The-Photonics-Platform)*
