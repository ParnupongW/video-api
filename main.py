from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import datetime

app = FastAPI(title="Video Analytics API")



# ── ส่วนที่ 1: ประกาศหน้าตาข้อมูลที่จะรับ ──
class VideoIn(BaseModel):
    title: str
    views: int
    likes: int

def load_videos():
    rows =[]
    with open("data.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i,row in enumerate(reader, start=1):
            row["id"] = i
            row["views"] = int(row["views"])
            row["likes"] = int(row["likes"])
            rows.append(row)
    return rows

def save_videos():
    with open("data.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "views", "likes", "date"])
        writer.writeheader()
        writer.writerows(videos)

videos = load_videos()


@app.delete("/videos/{video_id}")
def delete_video(video_id: int):
    for v in videos:
        if v["id"] == video_id:
            videos.remove(v)
            save_videos()
            return v
    raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")

@app.put("/videos/{video_id}")
def put_video(video: VideoIn, video_id: int):
    for v in videos:
        if v["id"] == video_id:
            v.update(video.model_dump())
            save_videos()
            return v
    raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")
    
@app.get("/")
def home():
    return {"message": "สวัสดีครับ API ทำงานแล้ว"}

@app.get("/videos/{video_id}")
def get_video(video_id: int):
    for v in videos:
        if v["id"] == video_id:
            return v
    raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")

@app.get("/videos")
def list_videos(min_views: int = 0):
    result = [v for v in videos if v["views"] >= min_views]
    return {"count": len(result), "videos": result}

# ── ส่วนที่ 2: POST — เพิ่มวิดีโอใหม่ ──
@app.post("/videos", status_code=201)
def create_video(video: VideoIn):
    new_id = max([v["id"] for v in videos]) + 1
    new_video = {"id": new_id, **video.model_dump()}
    videos.append(new_video)
    datetime.date.today()
    save_videos()
    return new_video

# ── ส่วนที่ 3: คำนวณ engagement (ของถนัดอยู่แล้ว) ──
@app.get("/videos/{video_id}/engagement")
def get_engagement(video_id: int):
    for v in videos:
        if v["id"] == video_id:
            rate = (v["likes"] / v["views"]) * 100
            return {"title": v["title"], "engagement_rate": round(rate, 2)}
    raise HTTPException(status_code=404, detail="ไม่พบวิดีโอ")

