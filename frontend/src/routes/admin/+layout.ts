import { requireAdminAuth } from '$lib/guards';

export const ssr = false;

/**
 * Protects all admin routes from unauthenticated access.
 * Delegates to requireAdminAuth which skips the check for
 * /admin/login and /admin/register.
 */
export function load({ url }: { url: URL }) {
	requireAdminAuth(url);
}