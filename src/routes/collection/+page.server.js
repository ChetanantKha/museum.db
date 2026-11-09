import { fail } from '@sveltejs/kit'

const api = 'http://127.0.0.1:8000'
const userId = 1

export async function load({ fetch }) {
    try {
        const response = await fetch(`${api}/collections/by-user/${userId}`)
        if (!response.ok) return { collections: [], offline: true }
        return { collections: await response.json(), offline: false }
    } catch {
        return { collections: [], offline: true }
    }
}

/**
 * @param {import('@sveltejs/kit').RequestEvent} event
 * @param {string} method
 * @param {string} message
 */
async function favoriteAction({ request, fetch }, method, message) {
    const data = await request.formData()
    const artifactId = Number(data.get('artifact_id'))
    if (!(artifactId > 0) || artifactId % 1 !== 0) {
        return fail(400, { error: 'กรุณาเลือกวัตถุให้ถูกต้อง' })
    }
    try {
        const response = await fetch(`${api}/collections/favorites`, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, artifact_id: artifactId })
        })
        if (!response.ok) {
            const error = await response.json()
            return fail(response.status, { error: typeof error.detail === 'string' ? error.detail : 'ทำรายการไม่สำเร็จ' })
        }
        return { message }
    } catch {
        return fail(503, { error: 'เชื่อมต่อ Backend ไม่ได้ ยังไม่ได้เปลี่ยนข้อมูล' })
    }
}

export const actions = {
    addFavorite: (event) => favoriteAction(event, 'POST', 'เพิ่มรายการโปรดแล้ว'),
    removeFavorite: (event) => favoriteAction(event, 'DELETE', 'นำออกจากรายการโปรดแล้ว')
}
