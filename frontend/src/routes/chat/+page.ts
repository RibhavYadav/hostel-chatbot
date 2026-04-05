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
 * Protects the chat route from unauthenticated access.
 * Reads the current auth state from authStore.
 * If the student is not logged in, redirects to /login.
 * Runs only in the browser due to ssr = false.
 */
export function load() {
	const auth = get(authStore);
	if (!auth.isLoggedIn) {
		throw redirect(302, '/login');
	}
}