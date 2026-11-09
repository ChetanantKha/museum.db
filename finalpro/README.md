# Relic Explorer Backend

รัน Backend จากโฟลเดอร์ backend เพื่อใช้ database.db เดิมของกลุ่ม:

```sh
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

จาก root รัน `npm run dev` และเปิดพอร์ตที่ Vite แสดง

รายละเอียด Assignment 6, actions, validation และ soft delete: [ASSIGNMENT6.md](ASSIGNMENT6.md)

ทดสอบจาก root:

```sh
npm run check
npm run build
node --test tests/assignment6.test.mjs
python -m pip install httpx
python tests/backend_integration.py
```

httpx ใช้เฉพาะการทดสอบ Backend tests สร้างฐานข้อมูลชั่วคราว ไม่แก้ข้อมูลจริง
