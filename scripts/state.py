#!/usr/bin/env python3
"""State machine bookkeeping for a closed-loop run workspace.

States: phenomenologist -> (experimentalist | theorist) -> phenomenologist -> ...

    state.py init     WS RUN_ID          create state.json / history.md (after bootstrap)
    state.py show     WS                 print state.json
    state.py begin    WS ROLE            record the start of a step (git heads, corpus size); ROLE must be the current state
    state.py decide   WS                 validate decisions/step_<n>.json (phenomenologist) and move to the chosen state
    state.py complete WS ROLE            validate the experimentalist/theorist outputs and return to phenomenologist
    state.py validate WS                 corpus integrity check
    state.py current-version WS | next-version WS | step WS
Exit status != 0 with a message on any validation failure (the orchestrator re-dispatches the agent).
"""
import datetime
import json
import os
import subprocess
import sys

ROLES = ("phenomenologist", "experimentalist", "theorist")


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def die(msg):
    print(f"STATE ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load(ws):
    p = os.path.join(ws, "state.json")
    if not os.path.exists(p):
        die(f"{p} missing (run bootstrap)")
    return json.load(open(p))


def save(ws, st):
    st["updated"] = now()
    tmp = os.path.join(ws, "state.json.tmp")
    json.dump(st, open(tmp, "w"), indent=2)
    os.replace(tmp, os.path.join(ws, "state.json"))


def history(ws, text):
    with open(os.path.join(ws, "history.md"), "a") as f:
        f.write(text.rstrip() + "\n\n")


def git_head(repo):
    return subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def git_changed(repo, a, b):
    out = subprocess.run(["git", "-C", repo, "diff", "--name-only", a, b], capture_output=True, text=True).stdout
    return [x for x in out.split("\n") if x]


def index(ws):
    p = os.path.join(ws, "corpus", "index.json")
    return json.load(open(p)) if os.path.exists(p) else []


def vnum(v):
    return int(v.lstrip("v"))


def validate_corpus(ws, version=None):
    errs = []
    idx = index(ws)
    if not idx:
        errs.append("corpus/index.json is empty or missing")
    for e in idx:
        d = os.path.join(ws, "corpus", e["id"])
        for f in ("definition.md", "result.npz", "comparison.txt", "projections.txt", "metrics.json"):
            if not os.path.exists(os.path.join(d, f)):
                errs.append(f"{e['id']}: missing {f}")
        mp = os.path.join(d, "metrics.json")
        if os.path.exists(mp):
            m = json.load(open(mp))
            if "model" not in m:
                errs.append(f"{e['id']}: no model comparison in metrics.json")
            if version and m.get("model_version") != version:
                errs.append(f"{e['id']}: model_version {m.get('model_version')} != {version}")
            if not os.path.isdir(os.path.join(ws, "plots", f"model_{m.get('model_version')}", e["id"])):
                errs.append(f"{e['id']}: no plots in plots/model_{m.get('model_version')}/")
        rp = os.path.join(d, "result.npz")
        if os.path.exists(rp):
            import zipfile
            names = zipfile.ZipFile(rp).namelist()
            if any(n.startswith(("genie", "truth")) for n in names):
                errs.append(f"{e['id']}: result.npz contains a GENIE/truth prediction (must be in plots/_genie only)")
    if not os.path.exists(os.path.join(ws, "corpus", "summary.txt")):
        errs.append("corpus/summary.txt missing")
    return errs


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    cmd, ws = sys.argv[1], os.path.abspath(sys.argv[2])
    if cmd == "init":
        run_id = sys.argv[3]
        errs = validate_corpus(ws, "v0")
        if errs:
            die("bootstrap corpus invalid:\n  " + "\n  ".join(errs))
        st = dict(run_id=run_id, created=now(), state="phenomenologist", step=0, model_version="v0",
                  n_experimentalist=0, n_theorist=0, corpus_size=len(index(ws)), current=None, steps=[])
        save(ws, st)
        history(ws, f"# Closed-loop run {run_id}\n\nStarted {now()}.  Seed corpus: {len(index(ws))} measurements "
                    f"({', '.join(e['id'] for e in index(ws))}); model v0 = base CCQE (RFG, dipole axial, no FSI).")
        print(f"initialised {ws}/state.json")
    elif cmd == "show":
        print(json.dumps(load(ws), indent=2))
    elif cmd == "step":
        print(load(ws)["step"])
    elif cmd == "current-version":
        print(load(ws)["model_version"])
    elif cmd == "next-version":
        print(f"v{vnum(load(ws)['model_version']) + 1}")
    elif cmd == "validate":
        errs = validate_corpus(ws, load(ws)["model_version"])
        if errs:
            die("\n  ".join(["corpus invalid:"] + errs))
        print("corpus OK")
    elif cmd == "begin":
        role = sys.argv[3]
        st = load(ws)
        if role != st["state"]:
            die(f"current state is {st['state']}, not {role}")
        if st.get("current") and st["current"]["role"] == role:
            print(f"step {st['step']}: {role} already in progress since {st['current']['started']} (resuming)")
            return
        st["current"] = dict(role=role, step=st["step"], started=now(), model_head=git_head(os.path.join(ws, "model")),
                             measurement_head=git_head(os.path.join(ws, "measurement")), corpus_size=len(index(ws)),
                             corpus_ids=[e["id"] for e in index(ws)])
        save(ws, st)
        print(f"step {st['step']}: {role} started")
    elif cmd == "decide":
        st = load(ws)
        cur = st.get("current") or die("no step in progress (state.py begin)")
        if cur["role"] != "phenomenologist":
            die("decide is for the phenomenologist step")
        p = os.path.join(ws, "decisions", f"step_{cur['step']}.json")
        if not os.path.exists(p):
            die(f"{p} not written")
        try:
            d = json.load(open(p))
        except json.JSONDecodeError as e:
            die(f"{p}: invalid JSON ({e})")
        if d.get("next") not in ("experimentalist", "theorist"):
            die(f"{p}: 'next' must be 'experimentalist' or 'theorist', got {d.get('next')!r}")
        for k in ("rationale", "brief"):
            if not isinstance(d.get(k), str) or len(d[k].strip()) < 20:
                die(f"{p}: '{k}' missing or too short")
        st["steps"].append(dict(step=cur["step"], role="phenomenologist", decision=d["next"], finished=now(),
                                model_version=st["model_version"], corpus_size=len(index(ws))))
        history(ws, f"## Step {cur['step']} — phenomenologist → {d['next']}\n\n**Rationale.** {d['rationale'].strip()}\n\n"
                    f"**Brief for the {d['next']}.** {d['brief'].strip()}")
        st["state"], st["step"], st["current"] = d["next"], st["step"] + 1, None
        st["brief"] = d["brief"]
        save(ws, st)
        print(f"decision: {d['next']}")
    elif cmd == "complete":
        role = sys.argv[3]
        st = load(ws)
        cur = st.get("current") or die("no step in progress (state.py begin)")
        if cur["role"] != role or role not in ("experimentalist", "theorist"):
            die(f"step in progress is {cur['role']}, not {role}")
        errs = []
        rep = os.path.join(ws, "reports", f"step_{cur['step']}_{role}.md")
        if not os.path.exists(rep) or os.path.getsize(rep) < 200:
            errs.append(f"report {rep} missing or too short")
        mhead, xhead = git_head(os.path.join(ws, "model")), git_head(os.path.join(ws, "measurement"))
        if role == "experimentalist":
            new = [e["id"] for e in index(ws) if e["id"] not in cur["corpus_ids"]]
            if not new:
                errs.append("no new corpus entry was added")
            if xhead == cur["measurement_head"]:
                errs.append("no new commit in the measurement clone")
            if mhead != cur["model_head"]:
                errs.append("the experimentalist must not change the model clone")
            errs += validate_corpus(ws, st["model_version"])
        else:
            nv = f"v{vnum(st['model_version']) + 1}"
            if mhead == cur["model_head"]:
                errs.append("no new commit in the model clone")
            else:
                changed = git_changed(os.path.join(ws, "model"), cur["model_head"], mhead)
                if not any(c.endswith(".md") for c in changed):
                    errs.append("the model commit does not update any .md documentation (theory/ or README)")
            if len(index(ws)) != cur["corpus_size"]:
                errs.append("the theorist must not add or remove corpus entries")
            errs += validate_corpus(ws, nv)
        if errs:
            die("\n  ".join([f"{role} step {cur['step']} incomplete:"] + errs))
        summary = open(rep).read().strip()
        entry = dict(step=cur["step"], role=role, finished=now(), report=os.path.relpath(rep, ws))
        if role == "experimentalist":
            entry["new_entries"] = new
            st["n_experimentalist"] += 1
            head = f"## Step {cur['step']} — experimentalist added {', '.join(new)} (model {st['model_version']})"
        else:
            st["model_version"] = nv
            entry["model_commit"] = mhead
            st["n_theorist"] += 1
            head = f"## Step {cur['step']} — theorist: model {nv} (commit {mhead[:10]})"
        entry["model_version"], entry["corpus_size"] = st["model_version"], len(index(ws))
        st["steps"].append(entry)
        st["corpus_size"] = len(index(ws))
        history(ws, f"{head}\n\n{summary}\n\nCorpus summary after this step:\n\n```\n"
                    f"{open(os.path.join(ws, 'corpus', 'summary.txt')).read().rstrip()}\n```")
        st["state"], st["step"], st["current"], st["brief"] = "phenomenologist", st["step"] + 1, None, None
        save(ws, st)
        print(f"{role} step complete; model {st['model_version']}, corpus {st['corpus_size']} entries")
    else:
        die(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
