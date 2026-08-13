# Video Analytics API

REST API สำหรับจัดการข้อมูลสถิติวิดีโอ พร้อมคำนวณ engagement rate  
สร้างด้วย FastAPI + PostgreSQL, deploy บน Render

**Live demo:** https://video-api-ugm9.onrender.com/docs

---

## Tech Stack

- **FastAPI** — web framework
- **PostgreSQL** — ฐานข้อมูล (เชื่อมต่อผ่าน psycopg)
- **Pydantic** — validation อัตโนมัติ
- **Render** — hosting
- **JWT (python-jose) + passlib** — authentication

---

## Endpoints

| Method | Path | คำอธิบาย |
|---|---|---|
| GET | `/videos` | ดูวิดีโอทั้งหมด (กรองด้วย `?min_views=`) |
| GET | `/videos/{id}` | ดูวิดีโอรายตัว |
| GET | `/videos/{id}/engagement` | คำนวณ engagement rate |
| POST | `/videos` | เพิ่มวิดีโอใหม่ |
| PUT | `/videos/{id}` | แก้ไขข้อมูล |
| DELETE | `/videos/{id}` | ลบวิดีโอ |

ทุก endpoint มี validation และ status code ตามมาตรฐาน REST (200 / 201 / 404 / 422)

---
## Authentication

ใช้ JWT token — รหัสผ่านเก็บเป็น bcrypt hash

| Method | Path | คำอธิบาย |
|---|---|---|
| POST | `/register` | สมัครสมาชิก |
| POST | `/login` | ล็อกอิน รับ access token |

`GET` เรียกได้โดยไม่ต้องมี token  
`POST` / `PUT` / `DELETE` ต้องแนบ token ใน header

## การติดตั้ง

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

สร้างไฟล์ `.env` แล้วใส่: DATABASE_URL=postgresql://...
สร้างตารางและนำเข้าข้อมูลตั้งต้น:

```bash
python setup_db.py
python setup_users.py
```

รันเซิร์ฟเวอร์:

```bash
fastapi dev main.py
```

เปิด http://127.0.0.1:8000/docs

---

## หมายเหตุ

โปรเจกต์นี้เริ่มจากการเก็บข้อมูลด้วยไฟล์ CSV แล้วย้ายมาใช้ SQLite และ PostgreSQL ตามลำดับ