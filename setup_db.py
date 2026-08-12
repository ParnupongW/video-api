import sqlite3
import csv

con = sqlite3.connect("videos.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY, title TEXT, views INTEGER, likes INTEGER, date DATE)")

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
        "INSERT INTO videos (title, views, likes, date) VALUES (?, ?, ?, ?)",
        (v["title"], v["views"], v["likes"], v["date"])
    )

con.commit()
con.close()
print("เสร็จแล้ว")