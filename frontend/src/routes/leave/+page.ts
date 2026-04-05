import { authStore } from '$lib/stores/authStore';
import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';

/**
 * Disables server-side rendering for this route.
 * Required because authStore reads from localStorage which is
 * only available in the browser, not on the server.
 */
export const ssr = false;

/**
 * Protects the leave route from unauthenticated access.
 * If the student is not logged in, redirects to /login.
 */
export function load() {
	const auth = get(authStore);
	if (!auth.isLoggedIn) {
		throw redirect(302, '/login');
	}
}