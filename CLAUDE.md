# orchestrate/

Closed-loop agentic iteration between a neutrino-interaction model (`nuflow`, repo enrico-model) and
MINERvA open-data cross-section measurements (repo enrico-measurement). Entry point: the `/xsec-loop`
slash command (`.claude/commands/xsec-loop.md`); sub-agents in `.claude/agents/`; workspace scripts in
`scripts/`; reading lists in `literature/`; see README.md for the data model.

- Run workspaces live in `runs/<run-id>/` (git-ignored): `model/` and `measurement/` clones on branch
  `loop/<run-id>`, `corpus/`, `results/`, `model_out/`, `decisions/`, `reports/`, `history.md`,
  `state.json`, and `plots/` — **plots are for humans only: never read, grep or list files under
  `runs/*/plots/`** (agents work from the text files in `corpus/`). `plots/_genie/` holds the MINERvA
  GENIE predictions: the model is judged against data only, never against GENIE or other generators.
- Python for the measurement tools: `$(cat runs/<id>/.python)` with `source scripts/env.sh runs/<id>`.
