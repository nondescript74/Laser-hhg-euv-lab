"""Reference bibliography for the Laser-HHG-EUV Lab platform.

Maps citation numbers to full academic and patent references.
Used by the citation rendering system to display interactive footnotes
across all visualization pages.
"""

# Each entry: citation number -> {short, full, url (optional), type}
REFERENCES = {
    # ── U.S. Patents ──
    1: {
        "short": "IBM, 1978",
        "full": "US4099062A — Thomson-CSF/IBM (1978). Electron beam lithography process using overlapping exposures at reduced dose.",
        "type": "patent",
    },
    2: {
        "short": "IMS, 2015",
        "full": "US20150347660A1 — IMS Nanofabrication (2015). Compensation of dose inhomogeneity using overlapping exposure spots in multi-beam lithography.",
        "type": "patent",
    },
    3: {
        "short": "IMS, 2016",
        "full": "US9373482B2 — IMS Nanofabrication (2016). Customizing a particle-beam writer using a convolution kernel representing a point spreading function.",
        "type": "patent",
    },
    4: {
        "short": "IMS, 2020",
        "full": "US10651010B2 — IMS Nanofabrication (2020). Non-linear dose- and blur-dependent edge placement correction for multi-beam lithography.",
        "type": "patent",
    },
    5: {
        "short": "Applied Materials, 2023",
        "full": "US20230185196A1 — Applied Materials (2023). Pre-exposure photoresist curing to shift resist solubility response curve.",
        "type": "patent",
    },
    6: {
        "short": "ASML, 2014",
        "full": "US8730452B2 — ASML (2014). Source and mask optimization with intensity/shape and phase/magnitude control.",
        "type": "patent",
    },
    7: {
        "short": "ASML, 2012",
        "full": "NL2009372A — ASML (2012). Methods to control EUV exposure dose in lithographic systems.",
        "type": "patent",
    },
    8: {
        "short": "Holographic Litho, 1992",
        "full": "US5142385A (1992). Holographic lithography using two coherent beams with phase-locked control.",
        "type": "patent",
    },
    9: {
        "short": "Particle MB, 2006",
        "full": "US6989546 (2006). Particle multibeam lithography with individually controllable beamlets.",
        "type": "patent",
    },
    10: {
        "short": "KLA REBL",
        "full": "US7566882B1 — KLA-Tencor. REBL rotating platter lithography with DLP-based reflective blanking array.",
        "type": "patent",
    },
    11: {
        "short": "IMS MB Exposure",
        "full": "US8378320B2 — IMS. Method for multi-beam exposure on a target with controlled overlap margins.",
        "type": "patent",
    },
    12: {
        "short": "IMS Charged-Particle",
        "full": "US9053906B2 — IMS. Method for charged-particle multi-beam exposure with per-beamlet dose control.",
        "type": "patent",
    },
    13: {
        "short": "ASML SMO, 2014",
        "full": "US20140282291A1 — ASML (2014). Source-mask optimization for lithography processes.",
        "type": "patent",
    },
    14: {
        "short": "MIT SBIL",
        "full": "WO2001035168A1 — MIT. Scanning beam interference lithography for large-area periodic nanostructures.",
        "type": "patent",
    },
    15: {
        "short": "Pixel Blending",
        "full": "US20140192334A1. Pixel blending for multi-beam lithography with overlapping aperture images.",
        "type": "patent",
    },
    16: {
        "short": "Dose + Deflection",
        "full": "US5393987A. Dose modulation combined with sub-pixel deflection for electron beam lithography.",
        "type": "patent",
    },
    17: {
        "short": "Laser Welding",
        "full": "US6740845B2. Laser welding with beam oscillation to create shaped melt pools.",
        "type": "patent",
    },
    18: {
        "short": "Extended DOF",
        "full": "US7876417B2. Extended depth of focus lithography via pupil-plane modification.",
        "type": "patent",
    },
    19: {
        "short": "ASML Lens Heating",
        "full": "US20130212543A1 — ASML. Lens heating aware source-mask optimization.",
        "type": "patent",
    },

    # ── Journal articles & conference papers ──
    20: {
        "short": "Fukuda et al., 1987",
        "full": "Fukuda, H. et al. \"FLEX: Focus Latitude Enhancement Exposure.\" IEEE Electron Device Letters, 1987. Multiple focal plane exposures to extend DOF.",
        "type": "article",
        "url": "https://doi.org/10.1109/EDL.1987.26600",
    },
    21: {
        "short": "Appl. Phys. Express, 2021",
        "full": "\"Dependence of dose rate on sensitivity of resist under ultra-high flux EUV pulse irradiation.\" Applied Physics Express, 2021. Demonstrates dose-rate reciprocity failure in EUV resists.",
        "type": "article",
    },
    22: {
        "short": "Fruchter & Hook, 2002",
        "full": "Fruchter, A.S. & Hook, R.N. \"Drizzle: A method for the linear reconstruction of undersampled images.\" Publications of the Astronomical Society of the Pacific, 2002.",
        "type": "article",
    },
    23: {
        "short": "Cutrona et al., 1961",
        "full": "Cutrona, L.J. et al. \"Synthetic aperture radar.\" Proc. IRE, 1961. Foundational SAR paper describing coherent aperture synthesis.",
        "type": "article",
    },
    24: {
        "short": "Liang et al., 2026",
        "full": "Liang, Y. et al. \"Diffraction-limit-breaking digital projection lithography via multi-exposure strategies for high-density nanopatterning.\" Microsystems & Nanoengineering 12, 18 (2026).",
        "type": "article",
        "url": "https://doi.org/10.1038/s41378-025-00878-3",
    },
    25: {
        "short": "Goodman",
        "full": "Goodman, J.W. Statistical Optics. Wiley, 2nd ed. Foundational treatment of coherence theory and speckle phenomena.",
        "type": "book",
    },
    26: {
        "short": "Born & Wolf",
        "full": "Born, M. & Wolf, E. Principles of Optics. Cambridge University Press, 7th ed. Definitive reference on electromagnetic theory of propagation, interference, and diffraction.",
        "type": "book",
    },
    27: {
        "short": "Hopkins, 1951",
        "full": "Hopkins, H.H. \"The concept of partial coherence in optics.\" Proc. Royal Society A, 1951. Transmission cross-coefficient (TCC) formalism for partially coherent imaging.",
        "type": "article",
    },
    28: {
        "short": "Diff. Litho Framework, 2024",
        "full": "Open-Source Differentiable Lithography Imaging Framework. arXiv 2409.15306, 2024. Computational graph for gradient-based lithography optimization.",
        "type": "article",
        "url": "https://arxiv.org/abs/2409.15306",
    },
    29: {
        "short": "Neural Lithography, 2023",
        "full": "Neural Lithography. SIGGRAPH Asia 2023, arXiv 2309.17343. Fully differentiable photolithography simulator for inverse design.",
        "type": "article",
        "url": "https://arxiv.org/abs/2309.17343",
    },
    30: {
        "short": "LithoSim, 2025",
        "full": "LithoSim: A Large, Holistic Lithography Simulation. NeurIPS 2025, CUHK. GPU-accelerated lithography simulation benchmark.",
        "type": "article",
    },
    31: {
        "short": "ResGNN-OPC, 2024",
        "full": "ResGNN-OPC. Optica, 2024. Graph neural network for fast optical proximity correction with 6000× acceleration.",
        "type": "article",
    },
    32: {
        "short": "Stochastic EUV, 2024",
        "full": "\"Stochasticity in EUV lithography predicted by principal component analysis.\" Journal of Applied Physics, 2024.",
        "type": "article",
    },

    # ── Technology references used on site pages ──
    40: {
        "short": "IMS MBMW-101",
        "full": "IMS Nanofabrication (now ASML) MBMW-101 Multi-Beam Mask Writer. 262,144 programmable beamlets (512×512), 16 gray levels per pixel, 0.1 nm address grid. BACUS/SPIE 2016.",
        "type": "technology",
    },
    41: {
        "short": "NVIDIA cuLitho",
        "full": "NVIDIA cuLitho GPU-accelerated computational lithography platform. 40× speedup over CPU for litho simulation. Production deployment at TSMC with Synopsys, 2024.",
        "type": "technology",
    },
    42: {
        "short": "Mack Dissolution",
        "full": "Mack, C.A. \"Analytical expression for the standing wave intensity in photoresist.\" Applied Optics, 1986. Mack dissolution rate model: R = R_max × (a−1)/(a+1) where a = (E/E_th)^n.",
        "type": "article",
    },
    43: {
        "short": "ASML EUV Platform",
        "full": "ASML NXE:3600D / NXE:3800E EUV lithography scanner. ~185 WPH, 250W source power, NA 0.33. Reference platform for fleet economics comparison.",
        "type": "technology",
    },
    44: {
        "short": "HHG Theory",
        "full": "Lewenstein, M. et al. \"Theory of high-harmonic generation by low-frequency laser fields.\" Physical Review A 49, 2117 (1994). Three-step model of HHG.",
        "type": "article",
        "url": "https://doi.org/10.1103/PhysRevA.49.2117",
    },
    45: {
        "short": "Corkum, 1993",
        "full": "Corkum, P.B. \"Plasma perspective on strong-field multiphoton ionization.\" Physical Review Letters 71, 1994 (1993). Semi-classical three-step model for HHG.",
        "type": "article",
        "url": "https://doi.org/10.1103/PhysRevLett.71.1994",
    },
    46: {
        "short": "Multibeam Corp MEBL",
        "full": "Multibeam Corporation MEBL-550. ~1M digital beamlets, sub-nm address grid. SkyWater Foundry partnership with Synopsys data path integration.",
        "type": "technology",
    },

    # ── Patent-specific references (Claim evidence) ──
    50: {
        "short": "NNLS Algorithm",
        "full": "Lawson, C.L. & Hanson, R.J. Solving Least Squares Problems. SIAM Classics in Applied Mathematics, 1995. Non-negative least squares (NNLS) algorithm for PSF decomposition.",
        "type": "book",
    },
    51: {
        "short": "Gerchberg-Saxton",
        "full": "Gerchberg, R.W. & Saxton, W.O. \"A practical algorithm for the determination of phase from image and diffraction plane pictures.\" Optik 35, 237 (1972). Iterative phase retrieval.",
        "type": "article",
    },
    52: {
        "short": "Pattern Collapse",
        "full": "AFM measurements of EUV resist pattern collapse forces at 40 nm half-pitch and below. Capillary-force-driven mechanical failure in high-aspect-ratio features.",
        "type": "article",
    },
    53: {
        "short": "Resist Thinning",
        "full": "EUV resist thinning studies: thickness loss increases linearly with dose. Higher dose yields better CD control but less remaining resist for etch transfer.",
        "type": "article",
    },
    54: {
        "short": "EUV Stochastics",
        "full": "Stochastic defects in EUV lithography: photon shot noise causes missing contacts and bridging defects at sub-20nm pitch. Fewer photons per unit dose than DUV.",
        "type": "article",
    },
    55: {
        "short": "EUV Plasma Damage",
        "full": "EUV-induced resist degradation pathways: PAG decomposition, outgassing, hydrogen plasma etching during exposure. ASML/imec studies.",
        "type": "article",
    },

    # ── HHG primary sources (added in P1 reframing pass) ──
    100: {
        "short": "Shiner et al., 2009",
        "full": (
            "Shiner, A.D. et al. \"Wavelength scaling of high harmonic "
            "generation efficiency.\" Physical Review Letters 103, "
            "073902 (2009). Foundational measurement of the "
            "lambda^-(6.3 +/- 1.1) and lambda^-(6.5 +/- 1.1) "
            "single-atom efficiency anti-scaling in Xe and Kr over "
            "800-1850 nm. Anchors the eta(lambda) ~ lambda^-(5..6.5) "
            "law used by backend/hhg_analytical.efficiency_scaling."
        ),
        "type": "article",
        "url": "https://doi.org/10.1103/PhysRevLett.103.073902",
    },
    101: {
        "short": "Lewenstein et al., 1994",
        "full": (
            "Lewenstein, M., Balcou, Ph., Ivanov, M.Yu., L'Huillier, A., "
            "& Corkum, P.B. \"Theory of high-harmonic generation by "
            "low-frequency laser fields.\" Physical Review A 49, 2117 "
            "(1994). The strong-field approximation (SFA) underlying "
            "every parameterized HHG single-atom calculation in this "
            "repo, including the cutoff law E_cut = 3.17 U_p + I_p."
        ),
        "type": "article",
        "url": "https://doi.org/10.1103/PhysRevA.49.2117",
    },
    102: {
        "short": "Wikmark et al., 2022",
        "full": (
            "Wikmark, H. et al. \"Wide-bandwidth high-harmonic radiation "
            "from a self-compressed pre-ionised plasma.\" Nature "
            "Scientific Reports (2022). Demonstrates phase-matching "
            "with a pre-ionised medium, extending the phase-matched "
            "bandwidth by pre-selecting the ionisation fraction "
            "before the driving pulse arrives. Anchors the "
            "phase-matching window proxy in "
            "backend/hhg_analytical.phase_matching_window."
        ),
        "type": "article",
    },
    103: {
        "short": "Coherent / KMLabs XUUS-4",
        "full": (
            "Coherent / KMLabs XUUS-4 white paper: tabletop "
            "high-harmonic source delivering ~1e11 photons/s/harmonic "
            "at 35 nm (Ar) and ~1.5e7 photons/s/harmonic at 13.5 nm "
            "(He), with beamline throughput further reducing delivered "
            "flux to 0.1-10 percent of source. Industrial benchmark "
            "anchoring SOURCE_SIDE_LITERATURE_ANCHORS in "
            "backend/optical_pipeline."
        ),
        "type": "technology",
    },
    104: {
        "short": "Carstens et al., 2024",
        "full": (
            "Carstens, H. et al. \"Cavity-enhanced high-harmonic "
            "generation for high-power and high-repetition-rate VUV/EUV "
            "sources.\" arXiv:2410.11589 (2024). State-of-the-field "
            "review of CE-HHG cavities for >10 MHz EUV at 10-100 eV; "
            "establishes that femtosecond enhancement cavities at the "
            "NIR driver wavelength are physically distinct from any "
            "DUV vdW intracavity modulation stack."
        ),
        "type": "article",
        "url": "https://arxiv.org/abs/2410.11589",
    },
    105: {
        "short": "ELI-ALPS pulse duration, 2025",
        "full": (
            "ELI-ALPS / SYLOS team. \"Systematic study of HHG yield as "
            "a function of pulse duration.\" arXiv:2507.10153 (2025). "
            "Demonstrates the non-monotonic interaction between pulse "
            "duration and yield: below saturation, longer pulses yield "
            "more total XUV photons (linear dependence); at near-"
            "saturation intensities, shorter pulses outperform because "
            "high free-electron density destroys phase matching. "
            "Justifies pulse duration as a defensible modelling variable."
        ),
        "type": "article",
    },
    106: {
        "short": "ArXiv 2509.02867 (open-source HHG sim)",
        "full": (
            "Open-source C++ HHG simulation program, BSD-licensed "
            "(arXiv:2509.02867, 2025). Handles both macroscopic and "
            "microscopic aspects of HHG. Software reference only; "
            "no output of this program is reproduced or claimed in "
            "this repo."
        ),
        "type": "technology",
        "url": "https://arxiv.org/abs/2509.02867",
    },
    107: {
        "short": "Corkum, 1993",
        "full": (
            "Corkum, P.B. \"Plasma perspective on strong-field "
            "multiphoton ionization.\" Physical Review Letters 71, "
            "1994 (1993). Semi-classical three-step model (ionisation "
            "- acceleration - recombination) that complements the "
            "Lewenstein SFA treatment."
        ),
        "type": "article",
        "url": "https://doi.org/10.1103/PhysRevLett.71.1994",
    },
    108: {
        "short": "ASML LPP source",
        "full": (
            "ASML laser-produced-plasma (LPP) EUV source: 250 W at "
            "13.5 nm intermediate focus on NXE:3600D / NXE:3800E "
            "scanners. Reference number for the LPP gap statement; "
            "not a benchmark this repo claims to approach."
        ),
        "type": "technology",
    },

    # ── Dose engine / Phoenix references ──
    59: {
        "short": "In-Situ Photodiodes",
        "full": "In-situ monitor photodiodes for real-time dose feedback. Sensor array provides spatially resolved intensity measurements at the wafer plane for adaptive dose correction.",
        "type": "technology",
    },
    60: {
        "short": "Adaptive Dose Correction",
        "full": "Dynamic correction factor computation for drive signal updates. Bayesian hypothesis weighting across nominal, thermal-drift, and source-aging states enables real-time dose compensation.",
        "type": "technology",
    },
}


# ── Patent claim descriptions for Claim badges ──
CLAIMS = {
    1: "Resist-Aware Lateral PSF Synthesis in Multibeam Lithography",
    4: "Joint Spatial-Temporal Optimization for Resist-Aware PSF Synthesis",
    5: "PSF Synthesis Lithographic Exposure Platform (System)",
    6: "PSF Decomposition with Execution and Metrology Feedback",
    7: "Coherent PSF Synthesis for FEG E-Beam Sources",
    8: "Temporal Coherence Gating with Hardware Actuation",
    9: "Coherence-Enhanced Dose Efficiency",
    10: "Dual-Regime Compositing System",
    11: "N-Dimensional Parameter Space (Tiers 1-3)",
    12: "Vector PSF with Polarization Control (DUV)",
    14: "GPU-Accelerated PSF Optimization with Resist-Aware Forward Model",
    15: "Per-Feature PSF Programming as Alternative to Mask-Level OPC",
    16: "Joint PSF-Temporal Co-Optimization with Stochastic Resist Model",
}
