from supabase import create_client
import os

# Verbindung zu Supabase
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]

supabase = create_client(url, key)

# Dummy-Evaluator
def evaluate(content):
    return 10

# Neue Submissions holen
rows = supabase.table("submissions") \
    .select("*") \
    .eq("processed", False) \
    .execute()

print("Found submissions:", len(rows.data))

# Alle neuen Submissions bearbeiten
for row in rows.data:

    print("Processing:", row["filename"])

    # Datei herunterladen
    data = supabase.storage \
        .from_("submissions") \
        .download(row["filename"])

    # Lokal speichern
    with open("submission.txt", "wb") as f:
        f.write(data)

    # Datei lesen
    with open("submission.txt", "r") as f:
        content = f.read()

    print("Content:")
    print(content)

    # Bewerten
    score = evaluate(content)

    print("Score:", score)

    # Als verarbeitet markieren
    supabase.table("submissions") \
        .update({
            "processed": True
        }) \
        .eq("id", row["id"]) \
        .execute()

    print("Marked as processed")