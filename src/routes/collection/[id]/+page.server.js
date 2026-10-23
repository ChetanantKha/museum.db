import { error } from '@sveltejs/kit'
import { items, artifacts } from '../data.js'

export function load({ params }) {
    const collection = items.find((item) => item.collection_id === Number(params.id))

    if (!collection) error(404)

    const artifact = artifacts.find((a) => a.id === collection.artifact_id)

    if (!artifact) error(404)

    return {
        collection,
        artifact
    }
}