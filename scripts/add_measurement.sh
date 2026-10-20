#!/bin/bash
# Add the entries of measurements/<name>/corpus.json (results already produced with
# measurements/run_measurement.py --results-root <ws>/results) to the corpus and compare them with
# the current model.  Plots go to plots/model_<current>/<id>/.
#   scripts/add_measurement.sh <ws> <name>
set -euo pipefail
ORCH=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$ORCH/scripts/env.sh" "$1"
NAME=${2:?usage: add_measurement.sh <ws> <measurement dir name>}
VER=$(python3 "$ORCH/scripts/state.py" current-version "$WS")
STEP=$(python3 "$ORCH/scripts/state.py" step "$WS")
[ -e "$WS/model_out/current.root" ] || { echo "no current model file"; exit 1; }
IDS=$("$PY" -c "import json,sys; print(' '.join(e['id'] for e in json.load(open('$MEAS/measurements/$NAME/corpus.json'))))")
"$PY" -m xsec.corpus add --corpus "$WS/corpus" --measurement "$NAME" --results-root "$WS/results" --origin "step-$STEP"
"$PY" -m xsec.corpus predict --corpus "$WS/corpus" --model "$WS/model_out/current.root" --model-version "$VER" \
  --plots "$WS/plots/model_$VER" --only $IDS
cp "$WS/corpus/summary.txt" "$WS/plots/model_$VER/summary.txt"
