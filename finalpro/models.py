from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField, SQLModel

class Faction(BaseModel):
    name: str = Field(examples=["Egypt"])
    total_rooms: int = Field(examples=[25])
    description: str = Field(examples=["Egyptian Sculpture Gallery"])

class FactionDB(SQLModel, table=True):
    id: int | None = SQLField(default=None, primary_key=True)
    name: str
    total_rooms: int
    description: str

class User(BaseModel):
    username: str = Field(examples=["Puifai"])
    email: str = Field(examples=["puifai@example.com"])

class UserDB(SQLModel, table=True):
    id: int | None = SQLField(default=None, primary_key=True)
    username: str
    email: str

class Persona(BaseModel):
    title: str = Field(examples=["The Rosetta Mystic"])
    faction_id: int = Field(examples=[1])
    image_url: str = Field(examples=["https://example.com/rosetta.png"])
    description: str = Field(examples=["A codebreaker drawn to ancient scripts"])

class PersonaDB(SQLModel, table=True):
    id: int | None = SQLField(default=None, primary_key=True)
    title: str
    faction_id: int = SQLField(foreign_key="factiondb.id")
    image_url: str
    description: str

class Artifact(BaseModel):
    name: str = Field(examples=["Rosetta Stone"])
    room_no: str = Field(examples=["4"])
    gallery_name: str = Field(examples=["Egyptian Sculpture Gallery"])
    qr_code_val: str = Field(examples=["QR-ROSETTA-001"])
    silhouette_url: str = Field(examples=["https://example.com/silhouette-rosetta.png"])
    image_url: str = Field(examples=["https://example.com/rosetta-full.png"])
    clue_text: str = Field(examples=["Three scripts, one message"])
    faction_id: int = Field(examples=[1])

class ArtifactDB(SQLModel, table=True):
    id: int | None = SQLField(default=None, primary_key=True)
    name: str
    room_no: str
    gallery_name: str
    qr_code_val: str
    silhouette_url: str
    image_url: str
    clue_text: str
    faction_id: int = SQLField(foreign_key="factiondb.id")

class UserCollection(BaseModel):
    user_id: int = Field(examples=[1])
    artifact_id: int = Field(examples=[1])
    scanned_at: str = Field(examples=["2026-09-09T12:00:00"])
    is_collected: bool = Field(default=True)

class UserCollectionDB(SQLModel, table=True):
    id: int | None = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="userdb.id")
    artifact_id: int = SQLField(foreign_key="artifactdb.id")
    scanned_at: str
    is_collected: bool = True

# =================================================================
# Business-logic Request/Response Schemas
# =================================================================
# =================================================================
# Business-logic Request/Response Schemas
# =================================================================
class QuizAnswers(BaseModel):
    user_id: int = Field(examples=[1])
    ans_1: str = Field(examples=["like"])
    ans_2: str = Field(examples=["nope"])
    ans_3: str = Field(examples=["like"])
    ans_4: str = Field(examples=["nope"])
    ans_5: str = Field(examples=["like"])

class ScanRequest(BaseModel):
    user_id: int = Field(examples=[1])
    qr_code_val: str = Field(examples=["QR-ROSETTA-001"])

class CollectionItemResponse(BaseModel):
    artifact_id: int
    name: str | None
    room_no: str
    gallery_name: str
    clue_text: str
    image_url: str | None
    silhouette_url: str
    is_locked: bool
    scanned_at: str | None
    is_favorite: bool = False

# Assignment 6: ตารางใหม่ ไม่แก้ schema หรือล้างข้อมูล Collection เดิม
class QuizAttemptDB(SQLModel, table=True):
    user_id: int = SQLField(primary_key=True)
    ans_1: str
    ans_2: str
    ans_3: str
    ans_4: str
    ans_5: str
    matched_artifact_id: int
    starter_artifact_id: int | None = None
    is_deleted: bool = False


class FavoriteDB(SQLModel, table=True):
    user_id: int = SQLField(primary_key=True)
    artifact_id: int = SQLField(primary_key=True)
    is_deleted: bool = False


class TargetDB(SQLModel, table=True):
    user_id: int = SQLField(primary_key=True)
    artifact_id: int
    is_deleted: bool = False


class ItemChoice(BaseModel):
    user_id: int
    artifact_id: int


class DeleteConfirmation(BaseModel):
    confirmed: bool = False


class ScanUnlockRequest(ScanRequest):
    artifact_id: int
    confirmed: bool = False


class FavoriteOrderDB(SQLModel, table=True):
    # แยกตารางเพื่อรักษา schema และข้อมูล Favorite เดิม
    user_id: int = SQLField(primary_key=True)
    artifact_id: int = SQLField(primary_key=True)
    position: int


class QuizModeDB(SQLModel, table=True):
    # เก็บวิธีรับผลแยกตาราง จึงไม่ต้องเปลี่ยน schema คำตอบเก่า
    user_id: int = SQLField(primary_key=True)
    is_random: bool = False


class DrawRequest(BaseModel):
    user_id: int


class DrawCollectDB(SQLModel, table=True):
    # บันทึกเฉพาะการ์ดที่กด Collect จากผลสุ่มรอบปัจจุบัน
    user_id: int = SQLField(primary_key=True)
    artifact_id: int
    is_deleted: bool = False


class QuizRewardDB(SQLModel, table=True):
    # การ์ดที่เพิ่มให้อัตโนมัติจาก Quiz รอบปัจจุบัน ไม่รวมใบที่เป็นเจ้าของอยู่ก่อน
    user_id: int = SQLField(primary_key=True)
    artifact_id: int
    is_deleted: bool = False
