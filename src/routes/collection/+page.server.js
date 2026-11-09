import { api, userId, itemAction } from '../../lib/server/museum.js'

export async function load({ fetch }) {
    try {
        const response = await fetch(`${api}/collections/by-user/${userId}`)
        if (!response.ok) return { collections: [], offline: true }
        return { collections: await response.json(), offline: false }
    } catch {
        return { collections: [], offline: true }
    }
}

export const actions = {
    addFavorite: (event) => itemAction(event, '/collections/favorites', 'POST', 'เพิ่มรายการโปรดแล้ว'),
    removeFavorite: (event) => itemAction(event, '/collections/favorites', 'DELETE', 'นำออกจากรายการโปรดแล้ว')
}
