from supabase import create_client
import os

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]

supabase = create_client(url, key)

rows = supabase.table("submissions") \
    .select("*") \
    .eq("processed", False) \
    .execute()

print(rows.data)

for row in rows.data:

    data = supabase.storage \
        .from_("submissions") \
        .download(row["filename"])

    with open("submission.zip", "wb") as f:
        f.write(data)