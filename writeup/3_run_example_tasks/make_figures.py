"""Problem 7: three figures from the saved HumanEval, SWE-bench and Terminal-Bench trajectories.

Run from the repository root:
    uv run --with matplotlib python writeup/3_run_example_tasks/make_figures.py
"""
import glob
import json
import os
import re
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT = "writeup/3_run_example_tasks"
ART = os.path.join(OUT, "artifacts")
RUNS = [
    ("HumanEval", "humaneval-agent/humaneval-0__*"),
    ("SWE-bench", "swebench-django-11099/django__django-11099__*"),
    ("Terminal-Bench", "terminal-bench-model-extraction/model-extraction-relu-logits__*"),
]
TASK_COLOR = {"HumanEval": "#2a78d6", "SWE-bench": "#eb6834", "Terminal-Bench": "#1baf7a"}
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"
SUBMIT = "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": INK, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
})


def load(pattern):
    """Return the agent's work steps as dicts: step id, command, return code."""
    path = glob.glob(os.path.join(ART, pattern, "agent", "trajectory.json"))[0]
    steps = []
    for s in json.load(open(path))["steps"]:
        if s.get("source") != "agent" or not s.get("tool_calls"):
            continue
        cmd = s["tool_calls"][0]["arguments"].get("command", "")
        if SUBMIT in cmd:
            continue  # the submit command is not work on the task
        content = (s.get("observation", {}).get("results") or [{}])[0].get("content", "")
        m = re.search(r'"returncode":\s*(-?\d+)', content)
        steps.append({"id": s["step_id"], "cmd": cmd, "rc": int(m.group(1)) if m else 0})
    return steps


def program(cmd):
    """Name of the program a command starts with (after any 'cd X &&' or VAR=value)."""
    first = cmd.strip().splitlines()[0] if cmd.strip() else ""
    m = re.match(r"\s*cd\s+\S+\s*&&\s*(.*)", first)
    if m:
        first = m.group(1)
    toks = first.split()
    while toks and re.match(r"^[A-Za-z_]\w*=", toks[0]):
        toks = toks[1:]
    if not toks:
        return "other"
    name = os.path.basename(toks[0])
    if name.startswith("python"):
        return "python"
    if name == "cat" and "<<" in first:
        return "cat <<EOF (write file)"
    if name == "cat":
        return "cat (read file)"
    if name == "git" and len(toks) > 1:
        return "git " + toks[1]
    return name


WRITE_PATTERNS = [
    r"(?:^|[^0-9&>])>{1,2}\s*([~./]?[A-Za-z_/][\w./-]*)",  # shell redirect to a file
    r"\bsed\s+-i\S*\s+.*?\s([\w./-]+\.\w+)\s*$",           # sed -i ... file
    r"open\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"][wa]",       # Python open(path, 'w')
    r"\btee\s+(?:-a\s+)?([\w./-]+)",                       # tee file
]


FILE_EXT = r"\.(?:py|txt|npy|json|md|sh|cfg|toml|ya?ml|csv|log|html|rst|js|c|h)$"


def writes_solution_file(cmd):
    """True if the command writes a file outside /tmp and /dev, i.e. edits the deliverable."""
    for pat in WRITE_PATTERNS:
        for target in re.findall(pat, cmd, flags=re.MULTILINE):
            looks_like_file = target.startswith(("/", "./", "~/")) or re.search(FILE_EXT, target)
            if looks_like_file and not target.startswith(("/tmp", "/dev")):
                return True
    return False


data = {name: load(pattern) for name, pattern in RUNS}
names = [n for n, _ in RUNS]

# ---------------------------------------------------------------- figure 1
counts = {n: Counter(program(s["cmd"]) for s in data[n]) for n in names}
share = {n: {p: 100 * c / len(data[n]) for p, c in counts[n].items()} for n in names}
total = Counter()
for n in names:
    for p, v in share[n].items():
        total[p] += v
top = [p for p, _ in total.most_common(9)]

fig, ax = plt.subplots(figsize=(9, 6))
h = 0.26
for i, n in enumerate(names):
    ys = [j + (i - 1) * h for j in range(len(top))]
    ax.barh(ys, [share[n].get(p, 0) for p in top], height=h - 0.03,
            color=TASK_COLOR[n], label=f"{n} ({len(data[n])} commands)")
ax.set_yticks(range(len(top)))
ax.set_yticklabels(top)
ax.invert_yaxis()
ax.set_xlabel("Share of the agent's commands in that task (%)")
ax.set_title("Which programs the agent ran, by task", loc="left", fontweight="bold")
ax.xaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.legend(frameon=False, loc="lower right")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "bash-command-usage.png"), dpi=200)
plt.close(fig)

print("=== bash-command-usage: commands per program (count, % of task) ===")
for p in top:
    print(f"{p:26s}" + "".join(f"{n}: {counts[n].get(p, 0):2d} ({share[n].get(p, 0):4.1f}%)   " for n in names))

# ---------------------------------------------------------------- figure 2
EXPLORE, IMPLEMENT = "#c3c2b7", "#6250d6"
fig, ax = plt.subplots(figsize=(9, 3.4))
print("\n=== exploration-to-implementation: first command that writes a file outside /tmp ===")
for row, n in enumerate(names):
    steps = data[n]
    idx = next((i for i, s in enumerate(steps) if writes_solution_file(s["cmd"])), len(steps))
    pct = 100 * idx / len(steps)
    ax.barh(row, pct, color=EXPLORE, height=0.5)
    ax.barh(row, 100 - pct, left=pct, color=IMPLEMENT, height=0.5)
    ax.plot([pct, pct], [row - 0.33, row + 0.33], color=INK, linewidth=2)
    if idx < len(steps):
        label = f"command {idx + 1} of {len(steps)} (step {steps[idx]['id']})"
        print(f"{n}: command {idx + 1} of {len(steps)} = step {steps[idx]['id']} = {pct:.0f}% of the way through")
        print("   ", steps[idx]["cmd"].strip().splitlines()[0][:110])
    else:
        label = "no solution file written"
        print(f"{n}: no write found")
    ha, dx = ("right", -1.5) if pct > 60 else ("left", 1.5)
    ax.text(pct + dx, row - 0.36, label, ha=ha, va="bottom", fontsize=9)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names)
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xlabel("Progress through the agent's commands (%)")
ax.set_title("When the agent first edited the solution", loc="left", fontweight="bold")
ax.legend(handles=[Patch(color=EXPLORE, label="Exploring (before the first write outside /tmp)"),
                   Patch(color=IMPLEMENT, label="Implementing (from the first write onward)")],
          frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "exploration-to-implementation.png"), dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- figure 3
# Each command is counted once, under the first activity below that it matches.
TEST_RUN = r"(?:^|[\s;&|])(?:pytest|\S*runtests\.py)\b|-m\s+(?:doctest|unittest|pytest)\b|python\S*\s+\S*test\S*\.py"
READ_PROGRAMS = {"cat", "ls", "nl", "sed", "head", "tail", "find", "grep", "wc", "less", "file", "tree"}
ENV_PROGRAMS = {"which", "pip", "pip3", "conda", "uname", "env", "whoami", "pwd", "uv"}


def writes_any_file(cmd):
    return writes_solution_file(cmd.replace("/tmp/", "/scratch/"))


def activity(cmd):
    prog = os.path.basename((program(cmd).split() or ["other"])[0])
    if writes_any_file(cmd):
        return "Edit or create files"
    if re.search(TEST_RUN, cmd, flags=re.MULTILINE):
        return "Run tests"
    if re.search(r"(?:^|[\s;&|/])python[\d.]*\s", cmd, flags=re.MULTILINE):
        return "Run own scripts and experiments"
    if re.search(r"(?:^|[\s;&|])git\s+(?:log|show|status|diff|branch|blame)\b", cmd, flags=re.MULTILINE):
        return "Inspect git history and state"
    if prog in READ_PROGRAMS or program(cmd) == "git grep":
        return "Inspect and search files"
    if prog in ENV_PROGRAMS:
        return "Check the environment"
    return "Other"


ACTIVITIES = [
    ("Inspect and search files", "#2a78d6"),
    ("Inspect git history and state", "#eb6834"),
    ("Check the environment", "#1baf7a"),
    ("Edit or create files", "#eda100"),
    ("Run tests", "#e87ba4"),
    ("Run own scripts and experiments", "#6250d6"),
    ("Other", "#c3c2b7"),
]
SHORT = {"Inspect and search files": "files", "Inspect git history and state": "git",
         "Check the environment": "env", "Edit or create files": "edit", "Run tests": "tests",
         "Run own scripts and experiments": "scripts", "Other": "other"}
acts = {n: Counter(activity(s["cmd"]) for s in data[n]) for n in names}

fig, ax = plt.subplots(figsize=(10, 4.2))
for row, n in enumerate(names):
    left = 0.0
    for label, color in ACTIVITIES:
        c = acts[n].get(label, 0)
        pct = 100 * c / len(data[n])
        if c == 0:
            continue
        ax.barh(row, pct, left=left, height=0.55, color=color, edgecolor=SURFACE, linewidth=2)
        if pct >= 6:
            dark_text = color in ("#eda100", "#c3c2b7")
            ax.text(left + pct / 2, row, str(c), ha="center", va="center", fontsize=9,
                    color=INK if dark_text else "#ffffff", fontweight="bold")
        left += pct
ax.set_yticks(range(len(names)))
ax.set_yticklabels([f"{n}\n({len(data[n])} commands)" for n in names])
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xlabel("Share of the agent's commands in that task (%); numbers in bars are command counts")
ax.set_title("How the agent spent its commands, by activity", loc="left", fontweight="bold")
ax.legend(handles=[Patch(color=c, label=l) for l, c in ACTIVITIES], frameon=False,
          loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "effort-distribution.png"), dpi=200)
plt.close(fig)

print("\n=== effort-distribution: commands per activity (count, % of task) ===")
for label, _ in ACTIVITIES:
    print(f"{label:34s}" + "".join(f"{n}: {acts[n].get(label, 0):2d} ({100 * acts[n].get(label, 0) / len(data[n]):4.1f}%)   " for n in names))
for n in names:
    print(f"\n{n}: activity of each command, in order")
    print("   " + " | ".join(f"{s['id']}:{SHORT[activity(s['cmd'])]}" for s in data[n]))

print("\nSaved bash-command-usage.png, effort-distribution.png, exploration-to-implementation.png in", OUT)