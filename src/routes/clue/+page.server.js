import { api, userId, itemAction } from '../../lib/server/museum.js'

export async function load({ fetch }) {
    try {
        const response = await fetch(`${api}/clue/target/${userId}`)
        const items = await fetch(`${api}/collections/by-user/${userId}`)
        if (!response.ok || !items.ok) return { target: null, lockedItems: [], offline: true }
        const target = await response.json()
        const collections = await items.json()
        const lockedItems = []
        for (const item of collections) if (item.is_locked) lockedItems.push(item)
        return { target, lockedItems, offline: false }
    } catch {
        return { target: null, lockedItems: [], offline: true }
    }
}

export const actions = {
    selectTarget: (event) => itemAction(event, '/clue/target', 'POST', 'เลือกเป้าหมายแล้ว'),
    cancelTarget: (event) => itemAction(event, '/clue/target', 'DELETE', 'ยกเลิกเป้าหมายแล้ว')
}
