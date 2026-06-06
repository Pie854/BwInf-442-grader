from supabase import create_client
import os

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]

supabase = create_client(url, key)

# Dummy evaluator
def evaluate(content):

    return [10] * 10

# Neue submissions holen
rows = supabase.table("submissions") \
    .select("*") \
    .eq("processed", False) \
    .execute()

print("Found:", len(rows.data))

for row in rows.data:

    print("Processing:", row["username"])

    # Datei herunterladen
    data = supabase.storage \
        .from_("submissions") \
        .download(row["filename"])

    # Datei speichern
    with open("submission.txt", "wb") as f:
        f.write(data)

    # Datei lesen
    with open("submission.txt", "r") as f:
        content = f.read()

    print(content)

    # Bewerten
    scores = evaluate(content)

    print("Scores:", scores)

    # Alten leaderboard-Eintrag laden
    existing = supabase.table("leaderboard") \
        .select("*") \
        .eq("username", row["username"]) \
        .execute()

    # Neuer User
    if len(existing.data) == 0:

        data = {
            "username": row["username"]
        }

        for i in range(10):
            data[f"s{i+1}"] = scores[i]

        supabase.table("leaderboard") \
            .insert(data) \
            .execute()

    # Existierender User
    else:

        old = existing.data[0]

        data = {}

        for i in range(10):

            key = f"s{i+1}"

            data[key] = max(old[key], scores[i])

        supabase.table("leaderboard") \
            .update(data) \
            .eq("username", row["username"]) \
            .execute()

    # Submission als verarbeitet markieren
    supabase.table("submissions") \
        .update({
            "processed": True
        }) \
        .eq("id", row["id"]) \
        .execute()

    print("Done")