#!/bin/bash
# Run the model in the workspace clone and compare it with every corpus measurement.
#   scripts/predict.sh <ws>             final: new model version v<k+1>; overwrites the corpus comparisons
#                                       and writes plots/model_v<k+1>/ with earlier versions (theorist, once the change is done)
#   scripts/predict.sh <ws> --trial     scratch: corpus copy in scratch/trial_corpus, no plots, corpus untouched
#   scripts/predict.sh <ws> --version vN   explicit version (bootstrap: v0)
set -euo pipefail
ORCH=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$ORCH/scripts/env.sh" "$1"
MODE=${2:-final}
if [ "$MODE" = --trial ]; then
  OUT=$WS/scratch/trial_model.root
  "$MODEL/scripts/run_loop_prediction.sh" "$OUT"
  rm -rf "$WS/scratch/trial_corpus"; cp -r "$WS/corpus" "$WS/scratch/trial_corpus"
  "$PY" -m xsec.corpus predict --corpus "$WS/scratch/trial_corpus" --model "$OUT" --model-version trial | tail -n +1
  echo "== trial comparison in $WS/scratch/trial_corpus (current corpus: $WS/corpus/summary.txt)"
  exit 0
fi
if [ "$MODE" = --version ]; then VER=$3; else VER=$(python3 "$ORCH/scripts/state.py" next-version "$WS"); fi
OUT=$WS/model_out/model_$VER.root
echo "== model $VER -> $OUT"
"$MODEL/scripts/run_loop_prediction.sh" "$OUT"
rm -rf "$WS/plots/model_$VER"
"$PY" -m xsec.corpus predict --corpus "$WS/corpus" --model "$OUT" --model-version "$VER"
"$PY" "$ORCH/scripts/plot_models.py" "$WS" "$VER"
cp "$WS/corpus/summary.txt" "$WS/plots/model_$VER/summary.txt"
git -C "$MODEL" rev-parse HEAD > "$WS/plots/model_$VER/model_commit.txt"
git -C "$MODEL" diff --quiet HEAD -- . ':!data/cache' || echo "WARNING: model clone has uncommitted changes (commit them)"
ln -sfn "model_$VER.root" "$WS/model_out/current.root"
# every version's model file is kept (~0.8 GB each): the plots compare the current model with earlier ones
echo "== model $VER compared with $(python3 -c "import json;print(len(json.load(open('$WS/corpus/index.json'))))") corpus entries"
