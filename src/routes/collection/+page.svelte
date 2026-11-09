<script>
    import CollectionCard from '#lib/CollectionCard.svelte'

    let { data, form } = $props()
    let collections = $derived(data.collections || [])
</script>

<h1>My collection</h1>

{#if form?.message}<p role="status">{form.message}</p>{/if}
{#if form?.error}<p class="error" role="alert">{form.error}</p>{/if}

{#if data.offline}
    <p class="error">โหลดคอลเลกชันไม่สำเร็จ กรุณาตรวจ Backend แล้วโหลดใหม่</p>
{:else if collections.length === 0}
    <p>ยังไม่มี Artifact เลย ลองไปสแกน QR ในพิพิธภัณฑ์ดูเลย!</p>
{:else}
    {#each collections as item}
        <CollectionCard
            artifactId={item.artifact_id}
            name={item.name}
            imageUrl={item.image_url}
            scannedAt={item.scanned_at}
            isLocked={item.is_locked}
            isFavorite={item.is_favorite}
        />
    {/each}
{/if}

<style>
    .error { color: #e66; }
</style>
