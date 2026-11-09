# Assignment 6 — integration in /Users/puffypuifai/411

โค้ดชุดนี้ใช้ Faction/Artifact/UserCollection และ database.db ของกลุ่มเดิม
ไม่ใช้ quiz.db หรือฐานข้อมูลสาธิตของโฟลเดอร์เก่า

## รัน

จาก backend (แบบเดียวกับ main.py เดิม):

```sh
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

จาก root ของโปรเจค: `npm run dev` แล้วเปิด /collection ที่พอร์ต Vite
ไฟล์ database.py เดิมใช้ sqlite:///database.db จึงต้องเปิด Backend จากโฟลเดอร์ backend

## ที่เพิ่ม

- Collection: addFavorite/removeFavorite ใช้ artifact_id ตาม schema ของกลุ่ม
  การ์ดที่ปลดล็อกกดได้ ใบที่ล็อกเห็นปุ่มปิดไว้และลิงก์ไป /unlock
- Clue: selectTarget/cancelTarget บันทึกเป้าหมายลงฐานข้อมูล โหลดหน้าใหม่แล้วไม่เปลี่ยนเอง
- Unlock: checkCode แสดง preview ก่อน และ unlock ตรวจรหัส/เป้าหมาย/การยืนยันซ้ำก่อนบันทึก
- Quiz: create/update/remove และ draw เดิมยังทำงาน
  ข้อมูลคำถามเดิมย้ายเป็น Python list/dict ใน questions.py
  กติกา pattern ทั้ง 32 แบบของกลุ่มเก็บใน quiz_rules.py โดยไม่เปลี่ยนผล

## ข้อมูลที่มีอยู่แล้ว

เพิ่มเฉพาะตาราง QuizAttemptDB, FavoriteDB, TargetDB ผ่าน create_all ตามบทเรียน
ไม่ล้าง database.db ไม่เปลี่ยน schema ตารางเดิม และไม่เปลี่ยนการ์ดที่เก็บไว้
is_favorite เป็นฟิลด์ response เพิ่มเติม ไม่ใช่คอลัมน์ในตารางการ์ดเดิม

บัญชีที่เคยรับการ์ดก่อนอัปเดตยังดู Clue/Collection/Unlock และเพิ่มรายการโปรดได้ทันที
เนื่องจากชุดเดิมไม่ได้เก็บคำตอบ Quiz ย้อนหลังไว้ จึงไม่สามารถแสดงคำตอบเก่าได้
หากต้องการบันทึกคำตอบ ให้ทำ Quiz/Draw อีกครั้ง ระบบจะบันทึกผลโดยไม่แจกการ์ดซ้ำ

Quiz update อัปเดตผล Persona ตามกติกาเดิม แต่ไม่เปลี่ยน/เพิ่มการ์ดใน Collection
Quiz remove ใช้ is_deleted=True เก็บคำตอบและรหัสการ์ดเริ่มต้นไว้
ทำใหม่หลังลบจะใช้แถวเดิม ไม่ได้การ์ดเริ่มต้นเพิ่ม
รายการโปรดและเป้าหมายใช้ soft delete เช่นกัน

## Validation

ตรวจทั้ง form action และ FastAPI: คำตอบครบ/like/nope, ID ถูกต้อง, ยืนยันก่อนลบ,
ต้องผ่าน Quiz เพื่อเล่น, ห้ามเลือกวัตถุที่สะสมแล้ว, ห้าม favorite การ์ดที่ล็อก,
ห้ามเพิ่ม favorite ซ้ำ, ยกเลิกได้เฉพาะเป้าหมายปัจจุบัน, รหัสไม่ว่างไม่เกิน 64 ตัวอักษร,
ตรวจรหัสและสถานะซ้ำก่อนยืนยันปลดล็อก และป้องกันปลดล็อกซ้ำ

ยังใช้ผู้ใช้จำลองหมายเลข 1 ตามโค้ดกลุ่มเดิม ไม่ใช่ระบบ login
ใช้ FastAPI/Pydantic/SQLModel, Python functions/if/for/list/dict และ Svelte load/props/state/if/each/forms/fail ตามบทเรียน
ไม่มีไลบรารีหน้าเว็บหรือระบบ migration เพิ่มเติม

## ตรวจสอบ

```sh
npm run check
npm run build
node --test tests/assignment6.test.mjs
```

## Draw Your Fate

Draw ใช้ POST /personas/draw รับเพียง user_id และสุ่ม Artifact จากฐานข้อมูลโดยตรง
ไม่สร้างคำตอบ LIKE/NOPE ให้ผู้ใช้ ไม่ส่งรายการคำตอบกลับ และไม่แสดงปุ่ม Edit Saved Answers
เก็บโหมดไว้ใน QuizModeDB แยกจากตารางเดิม เพื่อจำพฤติกรรมหลังรีเฟรชโดยไม่แก้ schema เดิม
ผลจากการตอบ Quiz ปกติยังแสดงรายการคำตอบและแก้ไขได้
ผลสุ่มยัง Reset ได้ และการสุ่มหลัง Reset ไม่แจกการ์ดเริ่มต้นซ้ำ

## COLLECT THIS CARD

ผล Draw ใหม่ไม่เพิ่ม UserCollection โดยอัตโนมัติ แสดงปุ่ม COLLECT THIS CARD ให้ผู้ใช้ยืนยันเก็บ
POST /personas/collect ตรวจรหัสผู้ใช้ ผลสุ่มล่าสุด artifact_id และสถานะสะสมก่อนบันทึก
หลังเก็บแล้วปุ่มเป็น COLLECTED และอ่านสถานะจากฐานข้อมูลหลังรีเฟรชได้
ถ้าสุ่มได้การ์ดที่อยู่ใน Collection แล้วจะแสดง COLLECTED ทันที ไม่สร้างรายการซ้ำ
Reset ผลสุ่มที่ยังไม่ Collect ไม่เปลี่ยน Collection ส่วนที่ Collect แล้วจะนำเฉพาะการ์ดจากรอบนั้นออก
การตอบ Quiz ตามปกติยังให้การ์ดเริ่มต้นตามกติกาเดิม

## Reset ผล Draw

ตั้งแต่การอัปเดตนี้ Collect บันทึก DrawCollectDB เพื่อระบุการ์ดจากรอบสุ่มปัจจุบัน
Reset หลัง Collect เปลี่ยน UserCollectionDB.is_collected เป็น False เฉพาะการ์ดจากรอบนั้น
และ soft-delete Favorite ของใบนั้นด้วย ไม่กระทบการ์ดอื่น
หากไม่ได้ Collect หรือสุ่มได้ใบที่เป็นเจ้าของอยู่แล้ว Reset ไม่ลบการ์ดใน Collection
ถ้าได้การ์ดผ่าน Unlock ระหว่างมีผลสุ่ม แต่ไม่ได้ Collect ก็จะไม่ลบใบนั้น
ไม่ใช้การเดาว่าการ์ดเก่ามาจาก Draw หรือ Unlock เพราะข้อมูลก่อนหน้านี้ไม่แยกที่มา
การติดตามรอบเริ่มจาก Collect หลังอัปเดตนี้ ไม่ลบข้อมูลเก่าย้อนหลังอัตโนมัติ

## Quiz result card and Reset

หลังยืนยันคำตอบ Quiz ให้แสดงเฉพาะการ์ดและ Faction ไม่แสดงคำตอบหรือปุ่ม Edit Saved Answers
ผู้ใช้แก้รายข้อได้ใน Review ก่อนส่งเท่านั้น หลังส่งแล้วใช้ Reset เพื่อทำใหม่
Quiz แต่ละรอบเพิ่มการ์ดผลเข้า Collection อัตโนมัติหากยังไม่มี และบันทึก QuizRewardDB
Reset ทำ soft delete การสะสมและ Favorite เฉพาะรางวัลใหม่จากรอบนั้น
ถ้าการ์ดผลมีอยู่ก่อน Quiz จะไม่เพิ่มซ้ำและ Reset จะไม่ลบใบนั้น
ต่างจาก Draw ที่ยังต้องกด COLLECT THIS CARD ก่อนเก็บ
