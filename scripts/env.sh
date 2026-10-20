# Source with the workspace path:  source scripts/env.sh <workspace>
# Exports WS, ORCH, PY (python with the measurement dependencies), PYTHONPATH (cloned xsec first),
# MVA_AUX, MVA_DF_MC, MVA_DF_DATA, MODEL (clone), MEAS (clone), WORKERS, MVA_PRIVATE.
ORCH=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
WS=$(realpath "${1:?usage: source scripts/env.sh <workspace>}")
export ORCH WS
export MODEL=$WS/model MEAS=$WS/measurement
export PY=$(cat "$WS/.python" 2>/dev/null || echo python3)
export PYTHONPATH=$MEAS/xsec${PYTHONPATH:+:$PYTHONPATH}
export MVA_AUX=$(python3 "$ORCH/scripts/config.py" mva_aux)
export MVA_DF_MC=$(python3 "$ORCH/scripts/config.py" df_mc)
export MVA_DF_DATA=$(python3 "$ORCH/scripts/config.py" df_data)
export WORKERS=$(python3 "$ORCH/scripts/config.py" workers)
export MPLBACKEND=Agg
# human-only store of the MINERvA GENIE prediction (plots only; agents must never see it)
export MVA_PRIVATE=$WS/plots/_genie
