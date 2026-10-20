# Experimentalist: MINERvA measurements, the open data, and cross-section methodology

Your measurements use the MINERvA medium-energy (ME) FHC open data and the analysis framework in
`measurement/` (selection on reco quantities, background subtraction/sideband fits, D'Agostini
unfolding, efficiency correction, flux and target normalisation, systematic universes). Signal
definitions should be **topological and in a restricted phase space** (e.g. θμ < 20°, p∥ > 1.5 GeV/c
for MINOS-matched muons), as in published MINERvA analyses.

## The detector, the flux, the method
- L. Aliaga et al. (MINERvA), "Design, Calibration, and Performance of the MINERvA Detector", Nucl. Instrum. Meth. A 743, 130 (2014) — arXiv:1305.5199 — acceptance, resolutions, calibration.
- L. Aliaga et al. (MINERvA), "Neutrino Flux Predictions for the NuMI Beam", Phys. Rev. D 94, 092005 (2016); Erratum PRD 95, 039903 (2017) — arXiv:1607.00704.
- E. Valencia et al. (MINERvA), "Constraint of the MINERvA medium energy neutrino flux using neutrino-electron elastic scattering", Phys. Rev. D 100, 092001 (2019) — arXiv:1906.00111 — the ν–e constraint used here.
- L. Zazueta et al. (MINERvA), "Improved constraint on the MINERvA medium energy neutrino flux using ν̄e⁻→ν̄e⁻ data", Phys. Rev. D 107, 012001 (2023) — arXiv:2209.05540.
- G. D'Agostini, "A Multidimensional unfolding method based on Bayes' theorem", Nucl. Instrum. Meth. A 362, 487 (1995); "Improved iterative Bayesian unfolding" — arXiv:1010.0632.
- L. Koch & S. Dolan, "Treatment of flux shape uncertainties in unfolded, flux-averaged neutrino cross-section measurements", Phys. Rev. D 102, 113012 (2020) — arXiv:2009.00552.

## The seed measurements of the corpus (reproduced in measurement/)
- D. Ruterbories et al. (MINERvA), "Measurement of inclusive charged-current νμ cross sections as a function of muon kinematics at ⟨Eν⟩∼6 GeV on hydrocarbon", Phys. Rev. D 104, 092007 (2021) — arXiv:2106.16210.
- D. Ruterbories et al. (MINERvA), "Simultaneous Measurement of Proton and Lepton Kinematics in Quasielasticlike νμ-Hydrocarbon Interactions from 2 to 20 GeV", Phys. Rev. Lett. 129, 021803 (2022) — arXiv:2203.08022.
- D. Ruterbories et al. (MINERvA), LE vs ME QE-like triple-differential comparison — arXiv:2606.00745.
- MINERvA ME νμ CC1π⁺ differential cross sections (tracked + untracked pions) — arXiv:2605.24224.

## Other MINERvA measurements: ideas, signal definitions, selections
- M.F. Carneiro et al. (MINERvA), "High-Statistics Measurement of Neutrino Quasielasticlike Scattering at 6 GeV on a Hydrocarbon Target", Phys. Rev. Lett. 124, 121801 (2020) — arXiv:1912.09890.
- D. Ruterbories et al. (MINERvA), "Measurement of Quasielastic-Like Neutrino Scattering at ⟨Eν⟩∼3.5 GeV on a Hydrocarbon Target", Phys. Rev. D 99, 012004 (2019) — arXiv:1811.02774 — a complete QE-like analysis chain.
- X.-G. Lu et al., "Measurement of nuclear effects in neutrino interactions with minimal dependence on neutrino energy", Phys. Rev. C 94, 015503 (2016) — arXiv:1512.05748 — transverse kinematic imbalance (δpT, δαT, δφT).
- X.-G. Lu et al. (MINERvA), "Measurement of final-state correlations in neutrino muon-proton mesonless production on hydrocarbon at ⟨Eν⟩=3 GeV", Phys. Rev. Lett. 121, 022504 (2018) — arXiv:1805.05486 — TKI at LE.
- M.V. Ascencio et al. (MINERvA), "Measurement of inclusive charged-current νμ scattering on hydrocarbon at ⟨Eν⟩∼6 GeV with low three-momentum transfer", Phys. Rev. D 106, 032001 (2022) — arXiv:2110.13372 — Eavail vs q3; 2p2h sensitive.
- P.A. Rodrigues et al. (MINERvA), "Identification of nuclear effects in neutrino-carbon interactions at low three-momentum transfer", Phys. Rev. Lett. 116, 071802 (2016) — arXiv:1511.05944.
- A. Filkins et al. (MINERvA), "Double-differential inclusive charged-current νμ cross sections on hydrocarbon in MINERvA at ⟨Eν⟩∼3.5 GeV", Phys. Rev. D 101, 112007 (2020) — arXiv:2002.12496.
- C.L. McGivern et al. (MINERvA), "Cross sections for νμ and ν̄μ induced pion production on hydrocarbon in the few-GeV region using MINERvA", Phys. Rev. D 94, 052005 (2016) — arXiv:1606.07127.

Going further: INSPIRE search `collaboration:MINERvA` for π⁰, π⁻, neutron, proton-multiplicity,
Eν/Q² and nuclear-target analyses; read their signal definitions and systematics sections.
