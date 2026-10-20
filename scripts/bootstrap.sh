#!/bin/bash
# Create a run workspace: clone model/ and measurement/ from GitHub (branch loop/<run-id>), set up
# python, build the model, seed the corpus with the existing measurements and make the v0 comparison.
#   scripts/bootstrap.sh <run-id>
set -euo pipefail
ORCH=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
RUN=${1:?usage: bootstrap.sh <run-id>}
cfg() { python3 "$ORCH/scripts/config.py" "$1"; }
RUNS=$(cfg runs_dir); WS=$RUNS/$RUN
[ -e "$WS/state.json" ] && { echo "workspace $WS already initialised (resume instead)"; exit 1; }
mkdir -p "$WS"/{corpus,results,model_out,plots,decisions,reports,logs,scratch}
for r in model measurement; do
  if [ ! -d "$WS/$r/.git" ]; then
    echo "== cloning $(cfg ${r}_repo) -> $WS/$r"
    git clone -q --branch "$(cfg ${r}_ref)" "$(cfg ${r}_repo)" "$WS/$r"
    git -C "$WS/$r" checkout -q -b "loop/$RUN"
  fi
done
PYCFG=$(cfg python)
if [ "$PYCFG" = auto ]; then
  if [ ! -x "$WS/venv/bin/python" ]; then
    echo "== creating venv"
    python3 -m venv "$WS/venv"
    "$WS/venv/bin/pip" install -q -r "$WS/measurement/requirements.txt"
  fi
  echo "$WS/venv/bin/python" > "$WS/.python"
else
  echo "$PYCFG" > "$WS/.python"
fi
source "$ORCH/scripts/env.sh" "$WS"
"$PY" -c "import xsec, numpy, uproot, awkward, matplotlib; print('xsec from', xsec.__file__)" | grep -q "$MEAS/xsec" \
  || { echo "python does not import the cloned xsec"; exit 1; }
SEED=$(cfg seed_results)
for m in $(cfg seed_measurements); do
  if [ "$SEED" = rerun ]; then
    echo "== running seed measurement $m from the DFs"
    "$PY" "$MEAS/measurements/run_measurement.py" "$m" --results-root "$WS/results" -j "$WORKERS" \
      --mc "$MVA_DF_MC" --data "$MVA_DF_DATA" > "$WS/logs/seed_$m.log" 2>&1
    ROOTDIR=$WS/results
  else
    ROOTDIR=$SEED
  fi
  "$PY" -m xsec.corpus add --corpus "$WS/corpus" --measurement "$m" --results-root "$ROOTDIR" --origin seed
done
"$ORCH/scripts/predict.sh" "$WS" --version v0
python3 "$ORCH/scripts/state.py" init "$WS" "$RUN"
echo "== bootstrap complete: $WS"
