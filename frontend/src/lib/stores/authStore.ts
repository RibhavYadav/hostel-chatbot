import type { AuthState, Student } from '$lib/types';
import { writable } from 'svelte/store';

import { clearToken, getToken, saveToken } from '$lib/services/api';

// Session restoration
/**
 * On store creation, checks localStorage for an existing token and student
 * profile. Restores the session after a page reload without requiring
 * the student to log in again.
 */
function getStoredStudent(): Student | null {
	const stored = localStorage.getItem('auth_student');

	if (!stored) return null;

	try {
		return JSON.parse(stored) as Student;
	} catch {
		return null;
	}
}

function buildInitialState(): AuthState {
	const token = getToken();
	const student = getStoredStudent();

	if (token && student) {
		return { currentUser: student, isLoggedIn: true, errorMessage: null };
	}

	return { currentUser: null, isLoggedIn: false, errorMessage: null };
}

// Store and actions
const authState = writable<AuthState>(buildInitialState());

/**
 * Sets the authenticated student in the store after a successful login.
 * Saves the token to localStorage via saveToken and stores the student
 * profile as JSON so the session survives page reloads.
 */
function loginSuccess(token: string, student: Student): void {
	saveToken(token);
	localStorage.setItem('auth_student', JSON.stringify(student));
	authState.set({ currentUser: student, isLoggedIn: true, errorMessage: null });
}

/**
 * Sets an error message in the store.
 * Called by authService when a login or register API call fails.
 * Leaves the current session state unchanged.
 */
function setError(message: string): void {
	authState.update((state) => ({ ...state, errorMessage: message }));
}

/** Clears any existing error message from the store. */
function clearError(): void {
	authState.update((state) => ({ ...state, errorMessage: null }));
}

/**
 * Clears the student session completely.
 * Removes the token and stored student profile from localStorage.
 * Resets the store to the logged-out state.
 */
function logout(): void {
	clearToken();
	localStorage.removeItem('auth_student');
	authState.set({ currentUser: null, isLoggedIn: false, errorMessage: null });
}

// Export
/**
 * Svelte store for student authentication state.
 * Subscribe to read currentUser, isLoggedIn, and errorMessage reactively.
 * Use loginSuccess after a successful API login response.
 * Use logout to clear the session.
 * Use setError to display error messages from failed API calls.
 */
function createAuthStore() {
	const { subscribe } = authState;
	return {
		subscribe,
		loginSuccess,
		setError,
		clearError,
		logout,
	};
}

export const authStore = createAuthStore();
