from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI(title="Video Analytics API")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()
con = psycopg.connect(os.getenv("DATABASE_URL"), row_factory=dict_row)
cur = con.cursor()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# ── ส่วนที่ 1: ประกาศหน้าตาข้อมูลที่จะรับ ──
class VideoIn(BaseModel):
    title: str
    views: int
    likes: int

class UserIn(BaseModel):
    username: str
    password: str

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="token ไม่ถูกต้องหรือหมดอายุ")

def load_videos():
    cur.execute("SELECT * FROM videos")
    rows = cur.fetchall()
    return [dict(row) for row in rows]

def save_videos():
    with open("data.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "views", "likes", "date"])
        writer.writeheader()
        writer.writerows(videos)

@app.delete("/videos/{video_id}")
def delete_video(video_id: int, current_user: str = Depends(get_current_user)):       
    cur.execute("DELETE FROM videos WHERE id = %s", (video_id,))
    con.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")
    return {"message": "ลบแล้ว"}

@app.put("/videos/{video_id}")
def put_video(video: VideoIn, video_id: int, current_user: str = Depends(get_current_user)):   
    cur.execute("UPDATE videos SET title = %s, views = %s, likes = %s WHERE id = %s", (video.title, video.views, video.likes, video_id))
    con.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")
    return {"message": "แก้ไขแล้ว"}
    
    
@app.get("/")
def home():
    return {"message": "สวัสดีครับ API ทำงานแล้ว"}

@app.get("/videos/{video_id}")
def get_video(video_id: int):
    videos = load_videos()
    for v in videos:
        if v["id"] == video_id:
            return v
    raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")

@app.get("/videos")
def list_videos(min_views: int = 0):
    videos = load_videos()
    result = [v for v in videos if v["views"] >= min_views]
    return {"count": len(result), "videos": result}

# ── ส่วนที่ 2: POST — เพิ่มวิดีโอใหม่ ──
@app.post("/videos", status_code=201)
def create_video(video: VideoIn, current_user: str = Depends(get_current_user)):
    cur.execute("INSERT INTO videos (title, views, likes) VALUES (%s, %s, %s) RETURNING id", (video.title, video.views, video.likes))
    con.commit()
    new_id = cur.fetchone()["id"]
    return {"message": "เพิ่มข้อมูลเรียบร้อย", "id": new_id}

# ── ส่วนที่ 3: คำนวณ engagement (ของถนัดอยู่แล้ว) ──
@app.get("/videos/{video_id}/engagement")
def get_engagement(video_id: int):
    videos = load_videos()
    for v in videos:
        if v["id"] == video_id:
            rate = (v["likes"] / v["views"]) * 100
            return {"title": v["title"], "engagement_rate": round(rate, 2)}
    raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")

@app.post("/register")
def register(user: UserIn):
    hashed = pwd_context.hash(user.password)
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user.username, hashed))
    con.commit()
    return{"message": "สมัครสำเร็จ"}

@app.post("/login")
def login(user: OAuth2PasswordRequestForm = Depends()):
    cur.execute("SELECT * FROM users WHERE username = %s", (user.username,))
    db_user = cur.fetchone()
    expire = datetime.utcnow() + timedelta(hours=24)
    token = jwt.encode(
        {"sub": user.username, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    if db_user is None:
        raise HTTPException(status_code=401, detail="username หรือ password ไม่ถูกต้อง")
    if not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="username หรือ password ไม่ถูกต้อง")
    return {"access_token": token, "token_type": "bearer"}
    

    

