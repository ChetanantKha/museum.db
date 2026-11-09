<script>
    let { artifactId, name, imageUrl, scannedAt, isLocked, isFavorite } = $props()
</script>

<div class="card {isLocked ? 'locked' : 'unlocked'}">
    {#if isLocked}
        <div class="question-mark">?</div>
        <h2>???</h2>
    {:else}
        <img src={imageUrl} alt={name} width="120">
        <h2>{name}</h2>
        <p>เก็บเมื่อ {scannedAt}</p>
        <form method="POST" action={isFavorite ? '?/removeFavorite' : '?/addFavorite'}>
            <input type="hidden" name="artifact_id" value={artifactId} />
            <button type="submit">{isFavorite ? 'REMOVE FAVORITE' : 'ADD FAVORITE'}</button>
        </form>
    {/if}
</div>

<hr>

<style>
    .card.locked { opacity: 0.6; }
    .question-mark { font-size: 2rem; }
</style>
