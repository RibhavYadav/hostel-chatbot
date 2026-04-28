import { requireAdminAuth } from '$lib/guards';

export const ssr = false;

export function load({ url }: { url: URL }) {
	requireAdminAuth(url);
}