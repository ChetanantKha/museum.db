<script>
    let { data, form } = $props()
</script>

<h1>Clue</h1>

{#if form?.message}<p role="status">{form.message}</p>{/if}
{#if form?.error}<p role="alert" style="color: #e66">{form.error}</p>{/if}

{#if data.offline}
    <p role="alert">โหลดคำใบ้ไม่สำเร็จ กรุณาตรวจ Backend แล้วโหลดใหม่</p>
{:else if !data.target || !data.target.has_quiz}
    <div class="locked-box">
        <div class="icon">🔒</div>
        <h2>Clue Locked</h2>
        <p>{data.target?.message || 'กรุณาทำ Quiz หรือกด Draw Your Fate ก่อนเพื่อดูคำใบ้แรก'}</p>
        <a href="/quiz" class="gold-btn">ไปทำ Quiz →</a>
    </div>
{:else if data.target.completed}
    <div class="completed-box">
        <div class="icon">🏆</div>
        <h2>Collection Completed!</h2>
        <p>คุณเก็บคอลเลกชันครบทั้งหมดแล้ว</p>
    </div>
{:else if data.target.selected}
    <div class="clue-container">
        <p class="eyebrow">CURRENT TARGET</p>
        <div class="card">
            <div class="question-mark">?</div>
            <p>Mystery Clue</p>
            <h2>"{data.target.clue_text}"</h2>
            <p class="gallery">Gallery: {data.target.gallery_name} (Room {data.target.room_no})</p>
        </div>
        <a href="/unlock" class="gold-btn block">Found It! Enter Code to Unlock →</a>
        <form method="POST" action="?/cancelTarget" style="margin-top: 16px">
            <input type="hidden" name="artifact_id" value={data.target.artifact_id} />
            <button class="gold-btn" type="submit">Cancel Target / ยกเลิกเป้าหมาย</button>
        </form>
    </div>
{:else}
    <h2>Choose Your Next Target</h2>
    <p>เลือกคำใบ้ด้านล่างเพื่อเริ่มค้นหาวัตถุ</p>
{/if}

{#if !data.offline && data.target?.has_quiz && data.lockedItems.length > 0}
    <form method="POST" action="?/selectTarget" class="target-form">
        <label for="target">Select a clue / เลือกเป้าหมาย</label>
        <select id="target" name="artifact_id" required>
            <option value="">Choose a clue</option>
            {#each data.lockedItems as item}
                <option value={item.artifact_id} disabled={data.target.selected && data.target.artifact_id === item.artifact_id}>{item.clue_text} — Room {item.room_no}</option>
            {/each}
        </select>
        <button class="gold-btn" type="submit">Select Target / เลือกเป้าหมาย</button>
    </form>
{/if}

<style>
    .locked-box, .completed-box { text-align: center; padding: 50px 20px; }
    .icon { font-size: 48px; margin-bottom: 12px; }
    .eyebrow { color: #ccad4c; font-size: 12px; letter-spacing: 2px; }
    .card { border: 2px dashed #ccad4c; padding: 30px; border-radius: 12px; text-align: center; margin: 20px 0; }
    .question-mark { font-size: 36px; color: #ff4d4d; font-weight: bold; }
    .gallery { color: #ccad4c; }
    .gold-btn { display: inline-block; background: #ccad4c; color: #14120b; padding: 12px 24px; border-radius: 6px; font-weight: bold; text-decoration: none; border: 0; font: inherit; cursor: pointer; }
    .gold-btn.block { display: block; width: 100%; text-align: center; padding: 14px; box-sizing: border-box; }
    .target-form { display: flex; flex-direction: column; gap: 12px; margin: 24px auto; max-width: 600px; }
    select { padding: 12px; width: 100%; }
</style>
