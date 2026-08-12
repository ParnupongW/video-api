import os
import csv
import psycopg
from dotenv import load_dotenv

load_dotenv()
con = psycopg.connect(os.getenv("DATABASE_URL"))
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS videos")
cur.execute("""CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title TEXT,
    views INTEGER,
    likes INTEGER,
    date DATE
)""")

# อ่าน CSV เอง ไม่พึ่ง main.py
rows = []
with open("data.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, start=1):
        row["id"] = i
        row["views"] = int(row["views"])
        row["likes"] = int(row["likes"])
        rows.append(row)

for v in rows:
    cur.execute(
        "INSERT INTO videos (title, views, likes, date) VALUES (%s, %s, %s, %s)",
        (v["title"], v["views"], v["likes"], v["date"])
    )

con.commit()
con.close()
print("เสร็จแล้ว")