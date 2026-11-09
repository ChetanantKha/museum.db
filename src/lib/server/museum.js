import { fail } from '@sveltejs/kit';

export const api = 'http://127.0.0.1:8000';
export const userId = 1;

/**
 * @param {import('@sveltejs/kit').RequestEvent} event
 * @param {string} path
 * @param {string} method
 * @param {string} message
 */
export async function itemAction({ request, fetch }, path, method, message) {
    const data = await request.formData();
    const artifactId = Number(data.get('artifact_id'));
    if (!(artifactId > 0) || artifactId % 1 !== 0) return fail(400, { error: 'กรุณาเลือกวัตถุให้ถูกต้อง' });
    try {
        const response = await fetch(`${api}${path}`, {
            method, headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, artifact_id: artifactId })
        });
        if (!response.ok) {
            const error = await response.json();
            return fail(response.status, { error: typeof error.detail === 'string' ? error.detail : 'ทำรายการไม่สำเร็จ' });
        }
        return { message };
    } catch {
        return fail(503, { error: 'เชื่อมต่อ Backend ไม่ได้ ยังไม่ได้เปลี่ยนข้อมูล' });
    }
}
