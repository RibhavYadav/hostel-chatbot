import type { LoginForm, RegisterForm } from '$lib/types';

import { authStore } from '$lib/stores/authStore';
import { loginStudent, registerStudent } from '$lib/services/api';

/**
 * Registers a new student account.
 * Calls POST /auth/register via index.ts.
 * Clears any existing error on success.
 * Sets an error message in authStore on failure.
 * Returns true on success, false on failure.
 */
export async function register(form: RegisterForm): Promise<boolean> {
	try {
		authStore.clearError();
		await registerStudent(
			form.registrationNumber,
			form.emailID,
			form.password,
			form.confirmPassword
		);
		return true;
	} catch (error) {
		authStore.setError(error instanceof Error ? error.message : 'Registration failed.');
		return false;
	}
}

/**
 * Authenticates a student against the backend.
 * Calls POST /auth/login via index.ts.
 * On success calls authStore.loginSuccess to store the token and student profile.
 * On failure sets an error message in authStore.
 * Returns true on success, false on failure.
 */
export async function login(form: LoginForm): Promise<boolean> {
	try {
		authStore.clearError();
		const response = await loginStudent(form.registrationNumber, form.emailID, form.password);
		authStore.loginSuccess(response.access_token, response.student);
		return true;
	} catch (error) {
		authStore.setError(error instanceof Error ? error.message : 'Login failed.');
		return false;
	}
}

/**
 * Logs out the current student.
 * Clears the token and student profile from localStorage via authStore.logout.
 * Returns true always.
 */
export async function logout(): Promise<boolean> {
	authStore.logout();
	return true;
}
