<script>
    let { data } = $props()
</script>

<h1>{data.artifact.name}</h1>
<img src={data.artifact.image_url} alt={data.artifact.name} width="300">

<p>ห้อง {data.artifact.room_no} — {data.artifact.gallery_name}</p>
<p>เบาะแส: {data.artifact.clue_text}</p>
<p>เก็บเมื่อ {data.collection.scanned_at}</p>

<a href="/collection">กลับไปหน้าของสะสม</a>