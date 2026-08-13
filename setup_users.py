import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
con = psycopg.connect(os.getenv("DATABASE_URL"))
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)""")


con.commit()
con.close()
print("เสร็จแล้ว")