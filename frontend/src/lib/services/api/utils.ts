/**
 * Base URL for all backend API requests.
 * Reads from the VITE_API_URL environment variable if set,
 * otherwise fall back to local backend development server.
 */
export const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

/**
 * Guard all localStorage calls with a browser check.
 */
export function isBrowser(): boolean {
	return typeof window !== 'undefined';
}

/**
 * Saves the JWT token to localStorage.
 * Called immediately after a successful login response.
 * Persists across page reloads and browser tabs.
 */
export function saveToken(token: string): void {
	if (!isBrowser()) return;
	localStorage.setItem('auth_token', token);
}

/**
 * Retrieves the JWT token from localStorage.
 * Returns null if the user is not logged in or the token has been cleared.
 */
export function getToken(): string | null {
	if (!isBrowser()) return null;
	return localStorage.getItem('auth_token');
}

/**
 * Removes the JWT token from localStorage.
 * Called on logout to ensure the token cannot be reused.
 */
export function clearToken(): void {
	if (!isBrowser()) return;
	localStorage.removeItem('auth_token');
}

/**
 * Saves the admin JWT token to localStorage under a separate key.
 * Kept separate from the student token so both sessions can
 * coexist without overwriting each other.
 */
export function saveAdminToken(token: string): void {
	if (!isBrowser()) return;
	localStorage.setItem('admin_auth_token', token);
}

/**
 * Retrieves the JWT token from localStorage.
 * Returns null if the user is not logged in or the token has been cleared.
 */
export function getAdminToken(): string | null {
	if (!isBrowser()) return null;
	return localStorage.getItem('admin_auth_token');
}

/**
 * Removes the JWT token from localStorage.
 * Called on logout to ensure the token cannot be reused.
 */
export function clearAdminToken(): void {
	if (!isBrowser()) return;
	localStorage.removeItem('admin_auth_token');
}

/**
 * Builds the Authorization header for protected endpoint requests.
 * Returns an empty object if no token is stored so the spread
 * operator in fetch calls adds nothing when the user is not logged in.
 */
export function authHeaders(): Record<string, string> {
	const token = getToken();
	if (!token) return {};

	return { Authorization: `Bearer ${token}` };
}

/**
 * Builds the Authorization header for protected endpoint requests.
 * Returns an empty object if no token is stored so the spread
 * operator in fetch calls adds nothing when the user is not logged in.
 */
export function adminAuthHeaders(): Record<string, string> {
	const token = getAdminToken();
	if (!token) return {};
	return { Authorization: `Bearer ${token}` };
}

/**
 * Handles a 401 Unauthorized response from any API call.
 * Clears the appropriate session from localStorage and redirects
 * to the login page. Uses window.location.href for a full reload
 * so all component state is cleared along with the session.
 * Called automatically by authenticatedFetch on every 401.
 */
export function handleUnauthorized(isAdmin: boolean = false): void {
	if (!isBrowser()) return;

	if (isAdmin) {
		clearAdminToken();
		localStorage.removeItem('admin_admin');
		window.location.href = '/admin/login';
	} else {
		clearToken();
		localStorage.removeItem('auth_student');
		window.location.href = '/login';
	}
}

/**
 * Wrapper around fetch for all authenticated API requests.
 * Automatically intercepts 401 Unauthorized responses, clears
 * the session, and redirects to the login page so expired tokens
 * are handled globally rather than per-endpoint.
 * isAdmin determines which token and session to clear on 401.
 * All other error statuses are returned to the caller for handling.
 */
export async function authenticatedFetch(
	url: string,
	options: RequestInit,
	isAdmin: boolean = false
): Promise<Response> {
	const response = await fetch(url, options);

	if (response.status === 401) {
		handleUnauthorized(isAdmin);
		throw new Error('Session expired. Please log in again.');
	}

	return response;
}
