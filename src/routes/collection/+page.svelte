<script>
    import CollectionCard from
'#lib/CollectionCard.svelte'

    let {data} = $props()
</script>

<h1>My collection</h1>

{#if data.items.length ===0}
     <p>ยังไม่มี Artifact เลย ลองไปสแกน QR ในพิพิธภัณฑ์ดูเลย!</p>
{:else}
    {#each data.items as item }
        <a href="/collection/{item.collection_id}">
            <CollectionCard
                name={item.artifact_name}
                imageUrl={item.artifact_image_url}
                scannedAt={item.scanned_at}
            />
        </a> 
    {/each}   
{/if}