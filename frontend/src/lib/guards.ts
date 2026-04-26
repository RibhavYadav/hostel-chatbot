import { authStore } from '$lib/stores/authStore';
import { adminAuthStore } from '$lib/stores/adminAuthStore';
import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';

/**
 * Redirects unauthenticated students to /login.
 * Call from load() in any student-protected +page.ts.
 * Safe to call without arguments — reads authStore directly.
 */
export function requireStudentAuth(): void {
	const auth = get(authStore);
	if (!auth.isLoggedIn) {
		throw redirect(302, '/login');
	}
}

/**
 * Redirects unauthenticated admins to /admin/login.
 * Skips the check for public admin paths so login and register
 * pages remain accessible without a token.
 * Call from load({ url }) in admin/+layout.ts.
 */
export function requireAdminAuth(url: URL): void {
	const publicPaths = ['/admin/login', '/admin/register'];
	if (publicPaths.includes(url.pathname)) return;

	const auth = get(adminAuthStore);
	if (!auth.isLoggedIn) {
		throw redirect(302, '/admin/login');
	}
}
