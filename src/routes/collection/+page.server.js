import { items } from './data-empty.js'

export function load({ url }) {
    const isEmpty = url.searchParams.get('empty') === '1'

    return {
        items: isEmpty ? [] : items
    }
}