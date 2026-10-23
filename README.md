# orchestrate — closed-loop measurement ↔ theory iteration

This repo runs a loop of AI agents (Claude Code sub-agents) that improves a neutrino–nucleus
interaction model (`nuflow`, repo **enrico-model**) against a growing corpus of MINERvA open-data
cross-section measurements (repo **enrico-measurement**). The loop is a state machine with three states:

| state | sub-agent | reads | produces | next |
|---|---|---|---|---|
| **phenomenologist** | `.claude/agents/phenomenologist.md` | corpus, history, model docs | `decisions/step_<n>.json` (`next`, `rationale`, `brief`) | experimentalist *or* theorist |
| **experimentalist** | `.claude/agents/experimentalist.md` | corpus, brief, measurement code | one new measurement (code committed to the measurement clone, result + comparisons added to the corpus) | phenomenologist |
| **theorist** | `.claude/agents/theorist.md` | corpus, brief, model code + theory notes | one focused model change (code + tests + theory `.md`, committed to the model clone), a new model version, all comparisons regenerated, new plot set | phenomenologist |

The orchestrator is the slash command **`/xsec-loop`** (`.claude/commands/xsec-loop.md`). It
bootstraps a workspace, dispatches the sub-agent for the current state, and enforces the data model
with `scripts/state.py`. Each agent starts from a curated reading list (`literature/common.md` plus
its role file) and is told to search arXiv/INSPIRE for more and follow citations.

## Installation and setup

Requirements (all present on the Fermilab `sbnd` interactive nodes, EL9):
- CVMFS with `/cvmfs/larsoft.opensciencegrid.org` (spack: gcc 12, cmake, ROOT 6.28, yaml-cpp, HepMC3, Catch2), used by `model/setup.sh`
- Python 3.9 with `venv` and network access to PyPI, or an existing environment with `measurement/requirements.txt`
- Read access to the MINERvA open-data inputs:
  - the flux and reweight auxiliary files (`mva_aux`)
  - the makedf dataframes v1 (`df_mc`, `df_data`, about 36 GB on `/pnfs/sbnd/scratch`; scratch can be purged, so remake them with `measurement/grid/production.sh` if needed)
  - the seed measurement results (`seed_results`), or set `seed_results: rerun` to rerun the four seed measurements from the dataframes (about 15 min)
- `git`, plus access to the two GitHub repositories
- [Claude Code](https://claude.com/claude-code) (`npm install -g @anthropic-ai/claude-code`), logged in
- Disk: about 3 GB per run workspace (clones, model build, venv, corpus, plots), plus about 0.8 GB per model version (every model file is kept)

Steps:
1. Clone this repo: `git clone https://github.com/<owner>/enrico-orchestrate.git orchestrate && cd orchestrate`
2. Edit `loop.yaml`:
   - set `github_owner` (the model and measurement repos are cloned from `https://github.com/<owner>/enrico-{model,measurement}.git`)
   - optionally set the data paths, `python`, `workers` and `runs_dir`
3. Check that the dataframe inputs are readable:
   `ls $(python3 scripts/config.py df_mc) | head; ls $(python3 scripts/config.py seed_results)`
4. Optionally test the bootstrap on its own: `scripts/bootstrap.sh test1` (about 2–5 min). It creates `runs/test1/`.
   Remove it with `rm -rf runs/test1`.

## Running the loop

From this directory:
```bash
claude                                   # interactive; then type:
/xsec-loop 4                             # 4 specialist steps (each preceded by a phenomenologist step)
/xsec-loop 2 --resume run-20261020-1400  # continue a run
```
Or headless, for long unattended runs:
```bash
claude -p "/xsec-loop 6 --run-id myrun" --permission-mode acceptEdits
```
- `.claude/settings.json` allows Bash, file edits and web access for this project, so the agents can
  work unattended.
- It also denies reading `runs/*/plots/`. The plots are for you, not the agents.
- Review `.claude/settings.json` before running. It gives the agents broad shell access inside this
  project.

Each specialist step takes roughly 10–60 minutes: reading, implementation, measurement runs over the
full dataframes, and model builds.

## Data model (per run workspace `runs/<run-id>/`)

```
state.json            state machine: state, step, model_version, steps[] (history), current step, brief
history.md            human/agent-readable log: every decision (rationale + brief), every report, corpus summary after each step
model/                clone of enrico-model,       branch loop/<run-id> (one commit per theorist step)
measurement/          clone of enrico-measurement, branch loop/<run-id> (one commit per experimentalist step)
corpus/               THE DATA MODEL (text for agents)
  index.json          entries: id, measurement dir, class, kwargs, title, origin (seed | step-<n>)
  summary.txt         one line per entry: model chi2/ndf, median |pull|, normalisation ratio
  <id>/definition.md  signal definition, observables + units, selection, motivation
  <id>/result.npz     data, cov_total/stat/sys, bin edges
  <id>/comparison.txt per bin: edges, data, stat/total error, model, ratio, pull, used flag
  <id>/projections.txt 1D projections on each axis (data +- total, model)
  <id>/metrics.json   chi2 (full cov / diagonal), pulls, normalisation, model version
  <id>/model.npy      current model prediction
results/              *_xsec.pkl outputs of new measurements (inputs of the corpus)
model_out/            model samples of every version (model_v<k>.root, current.root symlink to the current one)
  pred/model_v<k>/<id>.npy   cached prediction of each version per measurement (for the plots)
decisions/            step_<n>.json   phenomenologist decisions
reports/              step_<n>_<role>.md  specialist reports
plots/                HUMAN ONLY - never read by the agents
  model_v<k>/<id>/projections.png, slices_<j>.png   data vs MINERvA GENIE vs model v<k> and up to 5 earlier versions
  model_v<k>/summary.txt, model_commit.txt
  _genie/<id>_genie.npz   MINERvA GENIE (MnvTune) prediction per measurement, for the plots only
scratch/              theorist trial comparisons (predict.sh --trial)
```

- Each theorist step writes a new `plots/model_v<k+1>/` for every measurement. Earlier folders are
  never touched, so you can follow how the model evolves.
- Each figure shows the model version of its folder together with up to 5 earlier versions, spaced
  evenly between v0 and that version (`scripts/plot_models.py`), plus the MINERvA GENIE prediction.
  This is why every `model_out/model_v<k>.root` is kept.
- Measurements added by the experimentalist get their plots in the folder of the model version that
  is current when they are added.
- The comparison files in `corpus/` always refer to the current model. The theorist overwrites them
  through `scripts/predict.sh`.

**Comparisons.** The model prediction is computed by applying each measurement's own `signal()` and
`truth()` to nuflow's final-state particles (`measurement/xsec/xsec/genpred.py`). It uses the same
flux as the data (data-POT-weighted, ν–e constrained ME FHC flux, 0–100 GeV) and is normalised per
nucleon. χ² values use the full covariance over bins with fractional uncertainty below 100%.

**The agents never see another generator's prediction.**
- The corpus contains only data and the model under study.
- The MINERvA-tuned GENIE 2.12.6 (MnvTune) prediction of each measurement is kept in the human-only
  `plots/_genie/`. It is drawn only in the plots, so you can compare the model with GENIE yourself.
  - `run_measurement.py` strips it from new results.
  - `state.py validate` fails if it shows up in the corpus.
- `.claude/settings.json` also blocks the agents from reading (these are absolute paths for the current
  installation, so adapt them if you move the data or the source checkouts):
  - the seed result pickles;
  - the published model predictions and papers in the clones' `measurements/*/reference/`;
  - the original source checkouts of the model and measurement repos, which contain result pickles
    that include the GENIE prediction.
- The prompts tell the agents to judge the model against the data only, and to develop it
  independently of existing generators: no ported code or tuned parameters, no predictions as a target.

## Scripts

| script | used by | does |
|---|---|---|
| `scripts/bootstrap.sh <run-id>` | orchestrator | clone, branch, venv, build model, seed corpus, v0 comparison and plots, init state |
| `scripts/predict.sh <ws> [--trial]` | theorist | build + run model, recompare all measurements (new version, plots); `--trial` compares in scratch only |
| `scripts/plot_models.py <ws> <ver> [--only ids] [--entries-as-of]` | predict.sh, add_measurement.sh | human-only plots of `plots/model_<ver>/`: data, GENIE, model `<ver>` and up to 5 earlier versions spaced evenly from v0 |
| `scripts/add_measurement.sh <ws> <name>` | experimentalist | add a measurement's results to the corpus, compare with the current model, plots |
| `scripts/state.py begin/decide/complete/validate/show` | orchestrator | state transitions and data-model validation |
| `scripts/env.sh <ws>` | all | environment (`PY`, `PYTHONPATH` = clone's xsec, data paths) |
| `scripts/config.py [key]` | all | read `loop.yaml` (`LOOP_CONFIG=<file>` overrides) |

## Related documentation
- `measurement/measurements/AUTHORING.md`: the rules for a new measurement (existing dataframe
  columns only, a signal definition the generator can compute, closure)
- `measurement/xsec/xsec/corpus.py`: the corpus format
- `model/README.md` ("Adding a model", "Closed-loop usage") and `model/theory/`: the physics notes
