import type { Admin, AdminAuthState } from '$lib/types';
import { writable } from 'svelte/store';

import { clearAdminToken, getAdminToken, saveAdminToken } from '$lib/services/api';

// Session restoration
/**
 * Reads the stored admin profile from localStorage.
 * Returns null if no profile is stored or if the stored data is malformed.
 */
function getStoredAdmin(): Admin | null {
	const stored = localStorage.getItem('admin_admin');

	if (!stored) return null;

	try {
		return JSON.parse(stored) as Admin;
	} catch {
		return null;
	}
}

/**
 * Builds the initial store state by checking localStorage.
 * If both a token and admin profile exist the session is restored.
 * Otherwise the store starts in the logged-out state.
 */
function buildInitialState(): AdminAuthState {
	const token = getAdminToken();
	const admin = getStoredAdmin();

	if (token && admin) {
		return { currentAdmin: admin, isLoggedIn: true, errorMessage: null };
	}

	return { currentAdmin: null, isLoggedIn: false, errorMessage: null };
}

// Store and actions
const adminAuthState = writable<AdminAuthState>(buildInitialState());

/**
 * Sets the authenticated admin in the store after a successful login.
 * Saves the token to localStorage via saveAdminToken and stores the admin
 * profile as JSON so the session survives page reloads.
 */
function loginSuccess(token: string, admin: Admin): void {
	saveAdminToken(token);
	localStorage.setItem('admin_admin', JSON.stringify(admin));
	adminAuthState.set({ currentAdmin: admin, isLoggedIn: true, errorMessage: null });
}

/**
 * Sets an error message in the store.
 * Called by adminAuthService when a login or register API call fails.
 * Leaves the current session state unchanged.
 */
function setError(message: string): void {
	adminAuthState.update((state) => ({ ...state, errorMessage: message }));
}

/** Clears any existing error message from the store. */
function clearError(): void {
	adminAuthState.update((state) => ({ ...state, errorMessage: null }));
}

/**
 * Clears the admin session completely.
 * Removes the token and stored admin profile from localStorage.
 * Resets the store to the logged-out state.
 */
function logout(): void {
	clearAdminToken();
	localStorage.removeItem('admin_admin');
	adminAuthState.set({ currentAdmin: null, isLoggedIn: false, errorMessage: null });
}

// Export
/**
 * Svelte store for admin authentication state.
 * Subscribe to read currentAdmin, isLoggedIn, and errorMessage reactively.
 * Use loginSuccess after a successful admin API login response.
 * Use logout to clear the admin session.
 * Use setError to display error messages from failed API calls.
 */
function createAdminAuthStore() {
	const { subscribe } = adminAuthState;
	return {
		subscribe,
		loginSuccess,
		setError,
		clearError,
		logout,
	};
}

export const adminAuthStore = createAdminAuthStore();
