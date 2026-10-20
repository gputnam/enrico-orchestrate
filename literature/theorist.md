# Theorist: models of neutrino–nucleus scattering and how generators implement them

The model in `model/` starts as CCQE only (Llewellyn Smith with BBBA05 vector and dipole axial
form factors, relativistic Fermi gas, no 2p2h, no pion production, no DIS, no FSI). At MINERvA ME
energies the missing channels dominate the inclusive cross section, and FSI reshape every hadronic
observable. The references below cover each ingredient. Implement from the primary papers and use
the generator manuals to see practical choices.

## Quasielastic and the nuclear ground state
- C.H. Llewellyn Smith, "Neutrino Reactions at Accelerator Energies", Phys. Rept. 3, 261 (1972).
- R.A. Smith & E.J. Moniz, "Neutrino reactions on nuclear targets", Nucl. Phys. B 43, 605 (1972); Erratum B 101, 547 (1975) — RFG.
- A. Bodek & J.L. Ritchie, "Fermi Motion Effects in Deep Inelastic Lepton Scattering from Nuclear Targets", Phys. Rev. D 23, 1070 (1981).
- J. Nieves, J.E. Amaro, M. Valverde, "Inclusive quasi-elastic neutrino reactions", Phys. Rev. C 70, 055503 (2004) — arXiv:nucl-th/0408005 — LFG + RPA.
- O. Benhar et al., "Electron- and neutrino-nucleus scattering in the impulse approximation regime", Phys. Rev. D 72, 053005 (2005) — arXiv:hep-ph/0506116 — spectral function.
- R. Bradford et al., "A New parameterization of the nucleon elastic form-factors", Nucl. Phys. B Proc. Suppl. 159, 127 (2006) — arXiv:hep-ex/0602017 — BBBA05.
- A.S. Meyer et al., "Deuterium target data for precision neutrino-nucleus cross sections", Phys. Rev. D 93, 113015 (2016) — arXiv:1603.03048 — z-expansion axial form factor.

## Multinucleon (2p2h / MEC)
- J. Nieves, I. Ruiz Simo, M.J. Vicente Vacas, "Inclusive Charged-Current Neutrino-Nucleus Reactions", Phys. Rev. C 83, 045501 (2011) — arXiv:1102.2777 — Valencia 2p2h.
- R. Gran et al., "Neutrino-nucleus quasi-elastic and 2p2h interactions up to 10 GeV", Phys. Rev. D 88, 113007 (2013) — arXiv:1307.8105 — Valencia model at MINERvA energies, as used in generators.
- M. Martini et al., "A Unified approach for nucleon knock-out, coherent and incoherent pion production in neutrino interactions with nuclei", Phys. Rev. C 80, 065501 (2009) — arXiv:0910.2622.
- J.E. Amaro et al., "Neutrino-nucleus scattering in the SuSA model", Eur. Phys. J. ST 230, 4321 (2021) — arXiv:2106.02857.

## Pion production, resonances, shallow and deep inelastic
- D. Rein & L.M. Sehgal, "Neutrino Excitation of Baryon Resonances and Single Pion Production", Annals Phys. 133, 79 (1981).
- Ch. Berger & L.M. Sehgal, "Lepton mass effects in single pion production by neutrinos", Phys. Rev. D 76, 113004 (2007) — arXiv:0709.4378.
- E. Hernandez, J. Nieves, M. Valverde, "Weak Pion Production off the Nucleon", Phys. Rev. D 76, 033005 (2007) — arXiv:hep-ph/0701149.
- M. Kabirnezhad, "Single pion production in neutrino-nucleon Interactions", Phys. Rev. D 97, 013002 (2018) — arXiv:1711.02403.
- C. Wilkinson et al., "Reanalysis of bubble chamber measurements of muon-neutrino induced single pion production", Phys. Rev. D 90, 112017 (2014) — arXiv:1411.4482 — free-nucleon constraints.
- A. Bodek & U.K. Yang, "Modeling deep inelastic cross-sections in the few GeV region", Nucl. Phys. B Proc. Suppl. 112, 70 (2002) — arXiv:hep-ex/0203009; A. Bodek, I. Park, U.K. Yang, Nucl. Phys. B Proc. Suppl. 139, 113 (2005) — arXiv:hep-ph/0411202; A. Bodek & U.K. Yang — arXiv:1011.6592.

## Final-state interactions
- L.L. Salcedo et al., "Computer Simulation of Inclusive Pion Nuclear Reactions", Nucl. Phys. A 484, 557 (1988).
- T. Golan, C. Juszczak, J.T. Sobczyk, "Final State Interactions Effects in Neutrino-Nucleus Interactions", Phys. Rev. C 86, 015505 (2012) — arXiv:1202.4197 — NuWro cascade.
- O. Buss et al., "Transport-theoretical Description of Nuclear Reactions", Phys. Rept. 512, 1 (2012) — arXiv:1106.1344 — GiBUU.

Going further: for any ingredient, follow the citations of the primary papers and search for the
data that constrain it, e.g. electron scattering and bubble-chamber data. INSPIRE "refersto" queries
show the follow-up literature.
