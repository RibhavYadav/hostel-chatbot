/**
 * Disables server-side rendering for the root route.
 * Required because authStore reads from localStorage which
 * is only available in the browser, not on the server.
 */
export const ssr = false;