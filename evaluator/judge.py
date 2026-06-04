import json
import zipfile
from pathlib import Path

ZIP_FILE = Path("submission.zip")

if not ZIP_FILE.exists():
    raise Exception("submission.zip not found")


# ZIP entpacken
with zipfile.ZipFile(ZIP_FILE, "r") as z:
    z.extractall("submission")


# Dummy-Bewertung:
# Summe aller Zahlen in den .out Dateien

total_score = 0

for i in range(1, 11):
    file = Path(f"submission/{i}.out")

    if not file.exists():
        raise Exception(f"Missing {i}.out")

    value = int(file.read_text().strip())

    total_score += value


# Username aus Datei lesen
username = Path("username.txt").read_text().strip()


# Leaderboard laden
leaderboard_path = Path("data/leaderboard.json")

leaderboard = json.loads(
    leaderboard_path.read_text()
)


# Alten Eintrag entfernen
leaderboard = [
    x for x in leaderboard
    if x["user"] != username
]


# Neuen Eintrag hinzufügen
leaderboard.append({
    "user": username,
    "score": total_score
})


# Sortieren
leaderboard.sort(
    key=lambda x: x["score"]
)


# Speichern
leaderboard_path.write_text(
    json.dumps(leaderboard, indent=2)
)

print("Done.")