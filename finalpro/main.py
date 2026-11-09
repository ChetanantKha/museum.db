import random
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from questions import questions
from assignment6 import register_routes
from database import engine, init_db
from models import (
    Artifact, ArtifactDB, Faction, FactionDB, Persona, PersonaDB,
    QuizAnswers, ScanRequest, User, UserCollection, UserCollectionDB,
    UserDB, CollectionItemResponse, FavoriteDB, FavoriteOrderDB
)

def seed_db():
    with Session(engine) as session:
        if not session.exec(select(FactionDB)).first():
            egypt = FactionDB(name="Egypt", total_rooms=4, description="อารยธรรมลุ่มแม่น้ำไนล์")
            greece = FactionDB(name="Greece", total_rooms=4, description="ดินแดนแห่งเทพเจ้าและนักปราชญ์")
            rome = FactionDB(name="Rome", total_rooms=4, description="จักรวรรดิโรมันอันยิ่งใหญ่")
            asia = FactionDB(name="Asia", total_rooms=10, description="ศิลปะและโบราณวัตถุแห่งเอเชีย")
            europe = FactionDB(name="Europe", total_rooms=10, description="ประวัติศาสตร์และอารยธรรมยุโรป")
            middle_east = FactionDB(name="Middle East", total_rooms=10, description="ดินแดนตะวันออกกลางและอาระเบีย")
            americas = FactionDB(name="Americas", total_rooms=5, description="อารยธรรมแห่งทวีปอเมริกา")
            africa = FactionDB(name="Africa", total_rooms=5, description="ศิลปะและอารยธรรมแห่งทวีปแอฟริกา")
            
            session.add_all([egypt, greece, rome, asia, europe, middle_east, americas, africa])
            session.commit()
            
            artifacts = [
                ArtifactDB(
                    name="Colossal granite image of King Ramesses ll", 
                    room_no="4", 
                    gallery_name="Egyptian sculpture", 
                    qr_code_val="QR-1", 
                    clue_text="Colossal granite image of King Ramesses ll", 
                    silhouette_url="",
                    image_url="/images/artifact/Colossal granite image of King Ramesses ll.webp",
                    faction_id=egypt.id
                ),
                ArtifactDB(
                    name="Brass head of an Ooni", 
                    room_no="25", 
                    gallery_name="Africa", 
                    qr_code_val="QR-2", 
                    clue_text="Brass head of an Ooni", 
                    silhouette_url="",
                    image_url="/images/artifact/Brass head of an Ooni.webp",
                    faction_id=africa.id
                ),
                ArtifactDB(
                    name="The Sutton hoo helmet", 
                    room_no="41", 
                    gallery_name="Sutton Hoo and Europe", 
                    qr_code_val="QR-3", 
                    clue_text="The Sutton hoo helmet", 
                    silhouette_url="",
                    image_url="/images/artifact/The Sutton hoo helmet.webp",
                    faction_id=europe.id
                ),
                ArtifactDB(
                    name="The Portland Vase", 
                    room_no="70", 
                    gallery_name="Roman Empire", 
                    qr_code_val="QR-4", 
                    clue_text="The Portland Vase", 
                    silhouette_url="",
                    image_url="/images/artifact/The Portland Vase.webp",
                    faction_id=rome.id
                ),
                ArtifactDB(
                    name="Bust of Sir Hans Sloane", 
                    room_no="1", 
                    gallery_name="Enlightenment", 
                    qr_code_val="QR-5", 
                    clue_text="Bust of Sir Hans Sloane", 
                    silhouette_url="",
                    image_url="/images/artifact/Bust os Sir Hans Sloane.webp",
                    faction_id=europe.id
                ),
                ArtifactDB(
                    name="Relief panel from the Harpy Tomb", 
                    room_no="15", 
                    gallery_name="Greece: Athens and Lycia", 
                    qr_code_val="QR-6", 
                    clue_text="Relief panel from the Harpy Tomb", 
                    silhouette_url="",
                    image_url="/images/artifact/Relief panel from the Harpy Tomb.jpg",
                    faction_id=greece.id
                ),
                ArtifactDB(
                    name="Double-headed serpent mosaic", 
                    room_no="27", 
                    gallery_name="Mexico", 
                    qr_code_val="QR-7", 
                    clue_text="Double-headed serpent mosaic", 
                    silhouette_url="",
                    image_url="/images/artifact/Double-headed serpent mosaic.webp",
                    faction_id=americas.id
                ),
                ArtifactDB(
                    name="The goddess tara", 
                    room_no="33", 
                    gallery_name="China and South Asia", 
                    qr_code_val="QR-8", 
                    clue_text="The goddess tara", 
                    silhouette_url="",
                    image_url="/images/artifact/The goddess tara.webp",
                    faction_id=asia.id
                ),
                ArtifactDB(
                    name="The Great Departure of Prince Siddhartha", 
                    room_no="33a", 
                    gallery_name="India :Amaravati", 
                    qr_code_val="QR-9", 
                    clue_text="The Great Departure of Prince Siddhartha", 
                    silhouette_url="",
                    image_url="/images/artifact/The Great Departure of Prince Siddhartha.jpg",
                    faction_id=asia.id
                ),
                ArtifactDB(
                    name="The Bacchic platter from the Mildenhall treasure", 
                    room_no="49", 
                    gallery_name="Roman Britain", 
                    qr_code_val="QR-10", 
                    clue_text="The Bacchic platter from the Mildenhall treasure", 
                    silhouette_url="",
                    image_url="/images/artifact/The Bacchic platter from the Mildenhall treasure.jpg",
                    faction_id=rome.id
                ),
                ArtifactDB(
                    name="Gold griffin-headed armlet", 
                    room_no="52", 
                    gallery_name="Ancient lran", 
                    qr_code_val="QR-11", 
                    clue_text="Gold griffin-headed armlet", 
                    silhouette_url="",
                    image_url="/images/artifact/Gold griffin-headed armlet.jpg",
                    faction_id=middle_east.id
                ),
                ArtifactDB(
                    name="Calcite incense burner showing a camel rider", 
                    room_no="53", 
                    gallery_name="Ancient South Arabia", 
                    qr_code_val="QR-12", 
                    clue_text="Calcite incense burner showing a camel rider", 
                    silhouette_url="",
                    image_url="/images/artifact/Calcite incense burner showing a camel rider.jpg",
                    faction_id=middle_east.id
                ),
                ArtifactDB(
                    name="Christian wall-painting", 
                    room_no="66", 
                    gallery_name="Ethiopia and Coptic Egypt", 
                    qr_code_val="QR-13", 
                    clue_text="Christian wall-painting", 
                    silhouette_url="",
                    image_url="/images/artifact/Christian wall-painting.jpg",
                    faction_id=egypt.id
                ),
                ArtifactDB(
                    name="White porcelain 'moon jar'", 
                    room_no="67", 
                    gallery_name="Korea", 
                    qr_code_val="QR-14", 
                    clue_text="White porcelain 'moon jar'", 
                    silhouette_url="",
                    image_url="/images/artifact/White porcelain 'moon jar'.webp",
                    faction_id=asia.id
                ),
                ArtifactDB(
                    name="Fragment of a stone panel from the South-West Palace of Sennacherib", 
                    room_no="9", 
                    gallery_name="Assyria: Nineveh", 
                    qr_code_val="QR-15", 
                    clue_text="Fragment of a stone panel from the South-West Palace of Sennacherib", 
                    silhouette_url="",
                    image_url="/images/artifact/Fragment of a stone panel from the South-West Palace of Sennacherib.jpg",
                    faction_id=middle_east.id
                ),
                ArtifactDB(
                    name="Carved jade terrapin, India", 
                    room_no="33", 
                    gallery_name="China and South Asia", 
                    qr_code_val="QR-16", 
                    clue_text="Carved jade terrapin", 
                    silhouette_url="",
                    image_url="/images/artifact/Carved jade terrapin, India.jpg",
                    faction_id=asia.id
                ),
            ]
            session.add_all(artifacts)
            session.commit()
            print("ดึงข้อมูล Artifacts ทั้งหมด 16 รายการลงฐานข้อมูลเรียบร้อยแล้ว")

init_db()
seed_db()

app = FastAPI(title="Relic Explorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ระบบ Quiz Data & Persona
# ==========================================
@app.get('/quiz/questions', tags=['Quiz'])
def get_questions():
    return questions


# ==========================================
# ระบบ Clue Target (ล็อกเป้าหมายประจำตัว)
# ==========================================

# ==========================================
# ระบบ Artifacts (จัดการหลังบ้าน)
# ==========================================
@app.get("/artifacts/", tags=["Artifacts"])
async def get_all_artifacts():
    with Session(engine) as session:
        return session.exec(select(ArtifactDB)).all()

@app.post("/artifacts/", tags=["Artifacts"])
async def create_artifact(artifact: Artifact):
    with Session(engine) as session:
        new_artifact = ArtifactDB(**artifact.dict())
        session.add(new_artifact)
        session.commit()
        session.refresh(new_artifact)
        return new_artifact

# ==========================================
# ระบบ Collection (ดึงข้อมูลของสะสม)
# ==========================================
@app.get("/collections/by-user/{user_id}", tags=["Collection"], response_model=list[CollectionItemResponse])
async def collection_read_by_user(user_id: int):
    with Session(engine) as session:
        user = session.exec(select(UserDB).where(UserDB.id == user_id)).first()
        if not user:
            return []

        all_artifacts = session.exec(select(ArtifactDB)).all()
        collections = session.exec(select(UserCollectionDB).where(UserCollectionDB.user_id == user_id, UserCollectionDB.is_collected == True)).all()
        collected_map = {c.artifact_id: c.scanned_at for c in collections}

        result = []
        for artifact in all_artifacts:
            is_locked = artifact.id not in collected_map
            
            if is_locked:
                result.append(CollectionItemResponse(
                    artifact_id=artifact.id,
                    name="???", 
                    room_no=artifact.room_no,
                    gallery_name=artifact.gallery_name,
                    clue_text=artifact.clue_text,
                    image_url=None,
                    silhouette_url=artifact.silhouette_url,
                    is_locked=True,
                    scanned_at=None
                ))
            else:
                favorite = session.get(FavoriteDB, (user_id, artifact.id))
                result.append(CollectionItemResponse(
                    artifact_id=artifact.id,
                    name=artifact.name,
                    room_no=artifact.room_no,
                    gallery_name=artifact.gallery_name,
                    clue_text=artifact.clue_text,
                    image_url=artifact.image_url,
                    silhouette_url=artifact.silhouette_url,
                    is_locked=False,
                    scanned_at=collected_map[artifact.id],
                    is_favorite=(favorite is not None and not favorite.is_deleted)
                ))
                
        # เรียง Favorite ล่าสุดก่อน ส่วนการ์ดอื่นคงลำดับเดิม
        orders = session.exec(select(FavoriteOrderDB).where(
            FavoriteOrderDB.user_id == user_id)).all()
        positions = {order.artifact_id: order.position for order in orders}
        result.sort(key=lambda item: positions.get(item.artifact_id, 0)
                    if item.is_favorite else -1, reverse=True)
        return result

# ==========================================
# ระบบ Scan (ส่งโค้ดเพื่อปลดล็อก)
# ==========================================

register_routes(app)
