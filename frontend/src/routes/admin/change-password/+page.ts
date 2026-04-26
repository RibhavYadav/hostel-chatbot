import { requireAdminAuth } from '$lib/guards';

export const ssr = false;

/**
 * Protects the admin change password route.
 * Redirects to /admin/login if the admin is not authenticated.
 */
export function load({ url }: { url: URL }) {
	requireAdminAuth(url);
}