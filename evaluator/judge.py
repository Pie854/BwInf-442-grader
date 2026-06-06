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

    print("===================================")
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

    print("Content:")
    print(content)

    # Bewerten
    scores = evaluate(content)

    print("Scores:", scores)

    # Bestehenden leaderboard-Eintrag laden
    print("Loading leaderboard row...")

    existing = supabase.table("leaderboard") \
        .select("*") \
        .eq("username", row["username"]) \
        .execute()

    print("Existing data:")
    print(existing.data)

    # Neuer User
    if len(existing.data) == 0:

        print("Creating new leaderboard entry")

        leaderboard_data = {
            "username": row["username"]
        }

        for i in range(10):
            leaderboard_data[f"s{i+1}"] = scores[i]

        result = supabase.table("leaderboard") \
            .insert(leaderboard_data) \
            .execute()

        print("Insert result:")
        print(result)

    # Existierender User
    else:

        print("Updating existing leaderboard entry")

        old = existing.data[0]

        update_data = {}

        for i in range(10):

            field = f"s{i+1}"

            update_data[field] = max(old[field], scores[i])

        result = supabase.table("leaderboard") \
            .update(update_data) \
            .eq("username", row["username"]) \
            .execute()

        print("Update result:")
        print(result)

    # Submission als verarbeitet markieren
    print("Marking submission as processed")

    result = supabase.table("submissions") \
        .update({
            "processed": True
        }) \
        .eq("id", row["id"]) \
        .execute()

    print(result)

    print("Done")