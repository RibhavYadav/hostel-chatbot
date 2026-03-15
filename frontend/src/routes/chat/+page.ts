import { authStore } from '$lib/stores/authStore';
import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';

export function load() {
	const auth = get(authStore);
	if (!auth.isLoggedIn) {
		throw redirect(302, '/login');
	}
}
