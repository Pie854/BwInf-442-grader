from supabase import create_client
import os
from math import dist

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]

supabase = create_client(url, key)

WRONG=-1

# Dummy evaluator
def evaluate(content: str):
    scs=[]
    for i in range(1,11):
        with open(f"inputs/roboter{str(i).zfill(2)}.txt", "r") as f: lines = list(map(int,f.read().split()))[::-1]
        print(lines)
        def input(): return lines.pop()
        lines1 = content.splitlines()
        def output(): return lines1.pop()
        s=input()
        n=input()
        idtn=dict()
        #ntid=n*[0]
        x=[]
        y=[]
        for i in range(n):
            id=input()
            #ntid[i]=id
            idtn[id]=i
            x.append(input())
            y.append(input())
        score=int(output())
        if s!=int(output()):
            scs.append(WRONG)
            continue
        sn=n*[0]
        p=1
        for i in range(score):
            l=map(int,output().split())[0]
            x0,y0=map(int,output().split())
            ids=map(int,output().split())
            rl=len(ids)
            cx=x0
            cy=y0
            d=0
            for i in range(rl):
                ni=idtn[ids[i]]
                sn[ni]=1
                if (d>s):
                    p=0
                    break
                nx=x[ni]
                ny=y[ni]
                d+=dist((nx,ny),(cx,cy))
                cx,cy=nx,ny
            if p==0:break
            nx=x0
            ny=y0
            d+=dist((nx,ny),(cx,cy))
            cx,cy=nx,ny
            if (d>s):
                p=0
                break
        for i in range(n):
            if (sn[i]==0): p=0
        if p==0:
            scs.append(WRONG)
            continue
        scs.append(score)
    return scs







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