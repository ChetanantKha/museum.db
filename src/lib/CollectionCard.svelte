<script>
    let { name, imageUrl, scannedAt } = $props()
</script>

<div>
    <img src={imageUrl} alt={name} width="120">
    <h2>{name}</h2>
    <p>เก็บเมื่อ {scannedAt}</p>
</div>

<hr>