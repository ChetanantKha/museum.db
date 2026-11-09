import random
from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session, select
from database import engine
from models import (ArtifactDB, FactionDB, UserDB, UserCollectionDB, QuizAnswers,
                    QuizAttemptDB, QuizModeDB, DrawRequest, DrawCollectDB, QuizRewardDB, FavoriteDB, FavoriteOrderDB, TargetDB, ItemChoice,
                    DeleteConfirmation, ScanRequest, ScanUnlockRequest)
from quiz_rules import QUIZ_RULES


def validate_user_id(user_id: int):
    if user_id <= 0:
        raise HTTPException(status_code=422, detail='รหัสผู้ใช้ไม่ถูกต้อง')


def collected(session: Session, user_id: int, artifact_id: int):
    return session.exec(select(UserCollectionDB).where(
        UserCollectionDB.user_id == user_id, UserCollectionDB.artifact_id == artifact_id,
        UserCollectionDB.is_collected == True)).first()


def require_player(session: Session, user_id: int):
    validate_user_id(user_id)
    user = session.get(UserDB, user_id)
    owned = session.exec(select(UserCollectionDB).where(
        UserCollectionDB.user_id == user_id, UserCollectionDB.is_collected == True)).first()
    if user is None or owned is None:
        raise HTTPException(status_code=409, detail='กรุณาทำ Quiz หรือ Draw Your Fate ก่อน')


def require_artifact(session: Session, user_id: int, artifact_id: int):
    require_player(session, user_id)
    if artifact_id <= 0:
        raise HTTPException(status_code=422, detail='รหัสวัตถุไม่ถูกต้อง')
    artifact = session.get(ArtifactDB, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail='ไม่พบวัตถุนี้')
    return artifact


def grant_quiz_reward(session: Session, user_id: int, artifact: ArtifactDB):
    # การ์ดที่มีอยู่ก่อนรอบนี้ไม่ถือเป็นรางวัลใหม่ และ Reset ต้องไม่ลบใบนั้น
    if collected(session, user_id, artifact.id) is not None:
        return False
    entry = session.exec(select(UserCollectionDB).where(
        UserCollectionDB.user_id == user_id, UserCollectionDB.artifact_id == artifact.id)).first()
    if entry is None:
        entry = UserCollectionDB(user_id=user_id, artifact_id=artifact.id,
            scanned_at=datetime.now().isoformat(), is_collected=True)
    entry.is_collected = True
    entry.scanned_at = datetime.now().isoformat()
    session.add(entry)
    reward = session.get(QuizRewardDB, user_id)
    if reward is None:
        reward = QuizRewardDB(user_id=user_id, artifact_id=artifact.id)
    reward.artifact_id = artifact.id
    reward.is_deleted = False
    session.add(reward)
    return True


def quiz_result(session: Session, attempt: QuizAttemptDB):
    artifact = session.get(ArtifactDB, attempt.matched_artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail='ไม่พบการ์ดผล Quiz')
    faction = session.get(FactionDB, artifact.faction_id)
    if faction is None:
        raise HTTPException(status_code=404, detail='ไม่พบ Faction')
    starter = session.get(ArtifactDB, attempt.starter_artifact_id) if attempt.starter_artifact_id else None
    mode = session.get(QuizModeDB, attempt.user_id)
    receipt = session.get(DrawCollectDB, attempt.user_id)
    reward = session.get(QuizRewardDB, attempt.user_id)
    result = {
        'user_id': attempt.user_id,
        'artifact_id': artifact.id,
        'is_collected': collected(session, attempt.user_id, artifact.id) is not None,
        'rewarded_in_this_quiz': reward is not None and not reward.is_deleted,
        'collected_in_this_draw': receipt is not None and not receipt.is_deleted and receipt.artifact_id == artifact.id,
        'is_random': mode is not None and mode.is_random,
        'mode_known': mode is not None,
        'matched_faction': faction.name, 'starting_artifact': artifact.name,
        'image_url': artifact.image_url,
        'starter_artifact': starter.name if starter else None,
        'reward_granted': False
    }
    if not result['is_random']:
        result['ans_1'] = attempt.ans_1
        result['ans_2'] = attempt.ans_2
        result['ans_3'] = attempt.ans_3
        result['ans_4'] = attempt.ans_4
        result['ans_5'] = attempt.ans_5
    return result


def save_quiz(answers: QuizAnswers, update: bool, draw: bool = False):
    validate_user_id(answers.user_id)
    choices = [answers.ans_1, answers.ans_2, answers.ans_3, answers.ans_4, answers.ans_5]
    pattern = ''
    if not draw:
        for choice in choices:
            if choice != 'like' and choice != 'nope':
                raise HTTPException(status_code=422, detail='กรุณาตอบ LIKE หรือ NOPE ให้ครบ 5 ข้อ')
            pattern += '1' if choice == 'like' else '2'
    with Session(engine) as session:
        attempt = session.get(QuizAttemptDB, answers.user_id)
        if update and (attempt is None or attempt.is_deleted):
            raise HTTPException(status_code=404, detail='ไม่พบผล Quiz ที่ต้องการแก้ไข')
        if not update and attempt is not None and not attempt.is_deleted:
            raise HTTPException(status_code=409, detail='มีผล Quiz แล้ว กรุณาเลือกแก้คำตอบเดิม')
        mode = session.get(QuizModeDB, answers.user_id)
        if update and mode is not None and mode.is_random:
            raise HTTPException(status_code=409, detail='ผลสุ่มไม่มีคำตอบให้แก้ไข กรุณา Reset เพื่อเริ่ม Quiz ใหม่')
        if draw:
            artifacts = session.exec(select(ArtifactDB)).all()
            if not artifacts:
                raise HTTPException(status_code=404, detail='ไม่มีการ์ดให้สุ่ม')
            artifact = random.choice(artifacts)
        else:
            artifact = session.exec(select(ArtifactDB).where(ArtifactDB.name == QUIZ_RULES.get(pattern))).first()
        if artifact is None or session.get(FactionDB, artifact.faction_id) is None:
            raise HTTPException(status_code=404, detail='ไม่พบการ์ดหรือ Faction ตามกติกาเดิม')
        user = session.get(UserDB, answers.user_id)
        if user is None:
            user = UserDB(id=answers.user_id, username='Explorer', email='test@example.com')
            session.add(user)
        previous = session.exec(select(UserCollectionDB).where(
            UserCollectionDB.user_id == answers.user_id, UserCollectionDB.is_collected == True)).first()
        starter_id = attempt.starter_artifact_id if attempt is not None else None
        if starter_id is None and previous is not None:
            starter_id = previous.artifact_id
        granted = False
        if not update:
            reward = session.get(QuizRewardDB, answers.user_id)
            if reward is not None:
                reward.is_deleted = True
                session.add(reward)
            if not draw:
                granted = grant_quiz_reward(session, answers.user_id, artifact)
            if granted and starter_id is None:
                starter_id = artifact.id
        if attempt is None:
            attempt = QuizAttemptDB(user_id=answers.user_id,
                ans_1=answers.ans_1, ans_2=answers.ans_2, ans_3=answers.ans_3,
                ans_4=answers.ans_4, ans_5=answers.ans_5, matched_artifact_id=artifact.id)
        attempt.ans_1 = answers.ans_1
        attempt.ans_2 = answers.ans_2
        attempt.ans_3 = answers.ans_3
        attempt.ans_4 = answers.ans_4
        attempt.ans_5 = answers.ans_5
        attempt.matched_artifact_id = artifact.id
        attempt.starter_artifact_id = starter_id
        attempt.is_deleted = False
        session.add(attempt)
        if mode is None:
            mode = QuizModeDB(user_id=answers.user_id)
        mode.is_random = draw
        session.add(mode)
        if not update:
            receipt = session.get(DrawCollectDB, answers.user_id)
            if receipt is not None:
                receipt.is_deleted = True
                session.add(receipt)
        session.commit()
        session.refresh(attempt)
        result = quiz_result(session, attempt)
        result['reward_granted'] = granted
        return result


def artifact_preview(artifact: ArtifactDB):
    return {'artifact_id': artifact.id, 'name': artifact.name, 'image_url': artifact.image_url,
            'gallery_name': artifact.gallery_name, 'room_no': artifact.room_no}


def check_code(session: Session, request: ScanRequest):
    require_player(session, request.user_id)
    code = request.qr_code_val.strip()
    if not code or len(code) > 64:
        raise HTTPException(status_code=422, detail='กรุณากรอกรหัส 1–64 ตัวอักษร')
    artifact = session.exec(select(ArtifactDB).where(ArtifactDB.qr_code_val == code)).first()
    if artifact is None:
        raise HTTPException(status_code=404, detail='รหัสไม่ถูกต้อง หรือไม่พบวัตถุนี้')
    if collected(session, request.user_id, artifact.id) is not None:
        raise HTTPException(status_code=409, detail='คุณปลดล็อกวัตถุนี้ไปแล้ว')
    target = session.get(TargetDB, request.user_id)
    if target is not None and not target.is_deleted and target.artifact_id != artifact.id:
        raise HTTPException(status_code=409, detail='รหัสไม่ตรงกับเป้าหมายที่เลือก กรุณาดูคำใบ้อีกครั้ง')
    return artifact


def register_routes(app):
    @app.post('/personas/draw', tags=['Persona'])
    def draw_card(request: DrawRequest):
        # ไม่มีการสุ่มคำตอบ LIKE/NOPE: สุ่มจากการ์ดในฐานข้อมูลโดยตรง
        answers = QuizAnswers(user_id=request.user_id,
            ans_1='', ans_2='', ans_3='', ans_4='', ans_5='')
        return save_quiz(answers, False, True)

    @app.post('/personas/collect', tags=['Persona'])
    def collect_drawn_card(request: ItemChoice):
        validate_user_id(request.user_id)
        if request.artifact_id <= 0:
            raise HTTPException(status_code=422, detail='รหัสการ์ดไม่ถูกต้อง')
        with Session(engine) as session:
            attempt = session.get(QuizAttemptDB, request.user_id)
            if attempt is None or attempt.is_deleted:
                raise HTTPException(status_code=404, detail='ไม่พบผลสุ่ม กรุณาสุ่มการ์ดก่อน')
            mode = session.get(QuizModeDB, request.user_id)
            if mode is not None and not mode.is_random:
                raise HTTPException(status_code=409, detail='ผลนี้เป็น Quiz ไม่ใช่ผลสุ่ม')
            if attempt.matched_artifact_id != request.artifact_id:
                raise HTTPException(status_code=409, detail='การ์ดไม่ตรงกับผลสุ่มล่าสุด กรุณาโหลดหน้าใหม่')
            artifact = session.get(ArtifactDB, request.artifact_id)
            if artifact is None or session.get(UserDB, request.user_id) is None:
                raise HTTPException(status_code=404, detail='ไม่พบการ์ดหรือผู้ใช้')
            if collected(session, request.user_id, artifact.id) is not None:
                raise HTTPException(status_code=409, detail='การ์ดนี้อยู่ใน My Collection แล้ว')
            entry = session.exec(select(UserCollectionDB).where(
                UserCollectionDB.user_id == request.user_id,
                UserCollectionDB.artifact_id == artifact.id)).first()
            if entry is None:
                entry = UserCollectionDB(user_id=request.user_id, artifact_id=artifact.id,
                    scanned_at=datetime.now().isoformat(), is_collected=True)
            entry.is_collected = True
            entry.scanned_at = datetime.now().isoformat()
            session.add(entry)
            receipt = session.get(DrawCollectDB, request.user_id)
            if receipt is None:
                receipt = DrawCollectDB(user_id=request.user_id, artifact_id=artifact.id)
            receipt.artifact_id = artifact.id
            receipt.is_deleted = False
            session.add(receipt)
            if attempt.starter_artifact_id is None:
                attempt.starter_artifact_id = artifact.id
                session.add(attempt)
            # รองรับผลสุ่มจากรุ่นเก่าที่ไม่มีข้อมูล mode โดยยืนยันตอนเก็บเท่านั้น
            if mode is None:
                session.add(QuizModeDB(user_id=request.user_id, is_random=True))
            target = session.get(TargetDB, request.user_id)
            if target is not None and not target.is_deleted and target.artifact_id == artifact.id:
                target.is_deleted = True
                session.add(target)
            session.commit()
            return {'success': True, 'artifact_id': artifact.id}

    @app.post('/personas/quiz', tags=['Persona'])
    def create_quiz(answers: QuizAnswers):
        return save_quiz(answers, False)

    @app.get('/quiz/results/{user_id}', tags=['Quiz'])
    def read_quiz(user_id: int):
        validate_user_id(user_id)
        with Session(engine) as session:
            attempt = session.get(QuizAttemptDB, user_id)
            if attempt is None or attempt.is_deleted:
                raise HTTPException(status_code=404, detail='ยังไม่มีผล Quiz ที่บันทึกไว้')
            return quiz_result(session, attempt)

    @app.put('/quiz/results/{user_id}', tags=['Quiz'])
    def update_quiz(user_id: int, answers: QuizAnswers):
        if user_id != answers.user_id:
            raise HTTPException(status_code=422, detail='รหัสผู้ใช้ไม่ตรงกัน')
        return save_quiz(answers, True)

    @app.delete('/quiz/results/{user_id}', tags=['Quiz'])
    def remove_quiz(user_id: int, confirmation: DeleteConfirmation):
        validate_user_id(user_id)
        if not confirmation.confirmed:
            raise HTTPException(status_code=422, detail='กรุณายืนยันการล้างผล Quiz')
        with Session(engine) as session:
            attempt = session.get(QuizAttemptDB, user_id)
            if attempt is None or attempt.is_deleted:
                raise HTTPException(status_code=404, detail='ไม่พบผล Quiz ที่ต้องการล้าง')
            removed_card = False
            mode = session.get(QuizModeDB, user_id)
            if mode is not None and mode.is_random:
                receipt = session.get(DrawCollectDB, user_id)
            else:
                receipt = session.get(QuizRewardDB, user_id)
            if receipt is not None and not receipt.is_deleted:
                entry = collected(session, user_id, receipt.artifact_id)
                if entry is not None:
                    # Soft delete เฉพาะการ์ดที่ได้รับจาก Quiz หรือ Collect จาก Draw รอบนี้
                    entry.is_collected = False
                    session.add(entry)
                    removed_card = True
                    favorite = session.get(FavoriteDB, (user_id, receipt.artifact_id))
                    if favorite is not None:
                        favorite.is_deleted = True
                        session.add(favorite)
                receipt.is_deleted = True
                session.add(receipt)
            attempt.is_deleted = True
            session.add(attempt)
            session.commit()
            return {'success': True, 'removed_card': removed_card}

    @app.post('/collections/favorites', tags=['Collection'])
    def add_favorite(request: ItemChoice):
        with Session(engine) as session:
            require_artifact(session, request.user_id, request.artifact_id)
            if collected(session, request.user_id, request.artifact_id) is None:
                raise HTTPException(status_code=409, detail='เพิ่มรายการโปรดได้เฉพาะการ์ดที่ปลดล็อกแล้ว')
            favorite = session.get(FavoriteDB, (request.user_id, request.artifact_id))
            if favorite is not None and not favorite.is_deleted:
                raise HTTPException(status_code=409, detail='อยู่ในรายการโปรดแล้ว')
            if favorite is None:
                favorite = FavoriteDB(user_id=request.user_id, artifact_id=request.artifact_id)
            favorite.is_deleted = False
            session.add(favorite)
            # เก็บลำดับทุกครั้งที่เพิ่ม Favorite สำเร็จ ใบล่าสุดได้เลขสูงสุด
            positions = session.exec(select(FavoriteOrderDB).where(
                FavoriteOrderDB.user_id == request.user_id)).all()
            next_position = 1
            for position in positions:
                if position.position >= next_position:
                    next_position = position.position + 1
            order = session.get(FavoriteOrderDB, (request.user_id, request.artifact_id))
            if order is None:
                order = FavoriteOrderDB(user_id=request.user_id,
                    artifact_id=request.artifact_id, position=next_position)
            order.position = next_position
            session.add(order)
            session.commit()
            return {'success': True}

    @app.delete('/collections/favorites', tags=['Collection'])
    def remove_favorite(request: ItemChoice):
        with Session(engine) as session:
            require_artifact(session, request.user_id, request.artifact_id)
            favorite = session.get(FavoriteDB, (request.user_id, request.artifact_id))
            if favorite is None or favorite.is_deleted:
                raise HTTPException(status_code=404, detail='การ์ดนี้ไม่ได้อยู่ในรายการโปรด')
            favorite.is_deleted = True
            session.add(favorite)
            session.commit()
            return {'success': True}

    @app.get('/clue/target/{user_id}', tags=['Clue'])
    def read_target(user_id: int):
        validate_user_id(user_id)
        with Session(engine) as session:
            first = session.exec(select(UserCollectionDB).where(
                UserCollectionDB.user_id == user_id, UserCollectionDB.is_collected == True)).first()
            if first is None:
                return {'has_quiz':False, 'completed':False, 'selected':False}
            artifacts = session.exec(select(ArtifactDB)).all()
            remaining = 0
            for artifact in artifacts:
                if collected(session, user_id, artifact.id) is None:
                    remaining += 1
            target = session.get(TargetDB, user_id)
            if target is not None and not target.is_deleted:
                artifact = session.get(ArtifactDB, target.artifact_id)
                if artifact is not None and collected(session, user_id, artifact.id) is None:
                    return {'has_quiz':True, 'completed':False, 'selected':True,
                        'artifact_id':artifact.id, 'clue_text':artifact.clue_text,
                        'gallery_name':artifact.gallery_name, 'room_no':artifact.room_no}
            return {'has_quiz':True, 'completed':len(artifacts) > 0 and remaining == 0, 'selected':False}

    @app.post('/clue/target', tags=['Clue'])
    def select_target(request: ItemChoice):
        with Session(engine) as session:
            require_artifact(session, request.user_id, request.artifact_id)
            if collected(session, request.user_id, request.artifact_id) is not None:
                raise HTTPException(status_code=409, detail='เลือกได้เฉพาะการ์ดที่ยังล็อก')
            target = session.get(TargetDB, request.user_id)
            if target is not None and not target.is_deleted and target.artifact_id == request.artifact_id:
                raise HTTPException(status_code=409, detail='เลือกเป้าหมายนี้ไว้แล้ว')
            if target is None:
                target = TargetDB(user_id=request.user_id, artifact_id=request.artifact_id)
            target.artifact_id = request.artifact_id
            target.is_deleted = False
            session.add(target)
            session.commit()
            return {'success':True}

    @app.delete('/clue/target', tags=['Clue'])
    def cancel_target(request: ItemChoice):
        with Session(engine) as session:
            require_artifact(session, request.user_id, request.artifact_id)
            target = session.get(TargetDB, request.user_id)
            if target is None or target.is_deleted:
                raise HTTPException(status_code=404, detail='ไม่มีเป้าหมายให้ยกเลิก')
            if target.artifact_id != request.artifact_id:
                raise HTTPException(status_code=409, detail='เป้าหมายเปลี่ยนไปแล้ว กรุณาโหลดหน้าใหม่')
            target.is_deleted = True
            session.add(target)
            session.commit()
            return {'success':True}

    @app.post('/collections/check-code', tags=['Collection'])
    def preview_code(request: ScanRequest):
        with Session(engine) as session:
            return {'item':artifact_preview(check_code(session, request))}

    @app.post('/collections/scan', tags=['Collection'])
    def unlock(request: ScanUnlockRequest):
        if not request.confirmed:
            raise HTTPException(status_code=422, detail='กรุณายืนยันการปลดล็อก')
        with Session(engine) as session:
            artifact = check_code(session, request)
            if artifact.id != request.artifact_id:
                raise HTTPException(status_code=409, detail='การ์ดไม่ตรงกับรหัสที่ตรวจไว้ กรุณาตรวจใหม่')
            old = session.exec(select(UserCollectionDB).where(
                UserCollectionDB.user_id == request.user_id, UserCollectionDB.artifact_id == artifact.id)).first()
            if old is None:
                old = UserCollectionDB(user_id=request.user_id, artifact_id=artifact.id,
                    scanned_at=datetime.now().isoformat(), is_collected=True)
            old.is_collected = True
            old.scanned_at = datetime.now().isoformat()
            session.add(old)
            target = session.get(TargetDB, request.user_id)
            if target is not None and not target.is_deleted and target.artifact_id == artifact.id:
                target.is_deleted = True
                session.add(target)
            session.commit()
            return {'message':'ปลดล็อกสำเร็จ', 'item':artifact_preview(artifact)}
