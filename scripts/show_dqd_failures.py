import json
import sys
from pathlib import Path

# Usage : python scripts/show_dqd_failures.py [chemin.json] [--fatal]
args = [a for a in sys.argv[1:] if not a.startswith("--")]
only_fatal = "--fatal" in sys.argv

if args:
    path = Path(args[0])
else:
    files = sorted(Path("runs").glob("*/validation/*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        sys.exit("Aucun JSON DQD trouvé dans runs/*/validation/")
    path = files[-1]

data = json.loads(path.read_text(encoding="utf-8"))
checks = data.get("CheckResults", [])

def get(c, *names):
    for n in names:
        if n in c and c[n] is not None:
            return c[n]
    return ""

failed = [c for c in checks if get(c, "failed", "FAILED") == 1]
if only_fatal:
    failed = [c for c in failed if str(get(c, "checkSeverity", "severity")).lower() == "fatal"]

print(f"Fichier : {path}")
print(f"{len(failed)} contrôle(s) échoué(s) sur {len(checks)}\n")

for c in failed:
    table = get(c, "cdmTableName")
    field = get(c, "cdmFieldName")
    print(f"[{str(get(c, 'checkSeverity', 'severity')).upper()}] {get(c, 'checkName')} "
          f"({get(c, 'checkLevel')}) sur {table}.{field}")
    print(f"  Description : {get(c, 'checkDescription')}")
    print(f"  Violations  : {get(c, 'numViolatedRows')} lignes "
          f"({get(c, 'pctViolatedRows')}), seuil {get(c, 'thresholdValue')}")
    if get(c, "error"):
        print(f"  Erreur      : {get(c, 'error')}")
    print()
