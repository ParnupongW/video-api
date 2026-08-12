from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import datetime
import sqlite3

app = FastAPI(title="Video Analytics API")


con = sqlite3.connect("videos.db", check_same_thread=False)
con.row_factory = sqlite3.Row
cur = con.cursor()

# ── ส่วนที่ 1: ประกาศหน้าตาข้อมูลที่จะรับ ──
class VideoIn(BaseModel):
    title: str
    views: int
    likes: int

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
def delete_video(video_id: int):       
    cur.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    con.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")
    return {"message": "ลบแล้ว"}

@app.put("/videos/{video_id}")
def put_video(video: VideoIn, video_id: int):   
    cur.execute("UPDATE videos SET title = ?, views = ?, likes = ? WHERE id = ?", (video.title, video.views, video.likes, video_id))
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
def create_video(video: VideoIn):
    cur.execute("INSERT INTO videos (title, views, likes) VALUES (?, ?, ?)", (video.title, video.views, video.likes))
    con.commit()
    return {"message": "เพิ่มข้อมูลเรียบร้อย", "id": cur.lastrowid}

# ── ส่วนที่ 3: คำนวณ engagement (ของถนัดอยู่แล้ว) ──
@app.get("/videos/{video_id}/engagement")
def get_engagement(video_id: int):
    videos = load_videos()
    for v in videos:
        if v["id"] == video_id:
            rate = (v["likes"] / v["views"]) * 100
            return {"title": v["title"], "engagement_rate": round(rate, 2)}
    raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")

