import { adminAuthStore } from '$lib/stores/adminAuthStore';
import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';

/**
 * Disables server-side rendering for all admin routes.
 * Required because adminAuthStore reads from localStorage which
 * is only available in the browser, not on the server.
 */
export const ssr = false;

/**
 * Protects all admin routes from unauthenticated access.
 * Skips protection for /admin/login and /admin/register so
 * admins can reach those pages without a token.
 * All other /admin/* routes redirect to /admin/login if the
 * admin is not authenticated.
 */
export function load({ url }: { url: URL }) {
	const publicPaths = ['/admin/login', '/admin/register'];
	if (publicPaths.includes(url.pathname)) return;

	const auth = get(adminAuthStore);
	if (!auth.isLoggedIn) {
		throw redirect(302, '/admin/login');
	}
}
