import { BASE_URL, authenticatedFetch, authHeaders } from '$lib/services/api/utils';
import type { TokenResponse } from '$lib/types';

/**
 * Registers a new student account.
 * Sends registration details to POST /auth/register.
 * Throws an error with the backend detail message if registration fails.
 */
export async function registerStudent(
	registrationNumber: number,
	emailID: string,
	password: string,
	confirmPassword: string
): Promise<{ message: string }> {
	const response = await fetch(`${BASE_URL}/auth/register`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ registrationNumber, emailID, password, confirmPassword }),
	});

	if (!response.ok) {
		const error = await response.json();
		if (Array.isArray(error.detail)) {
			throw new Error(error.detail.map((e: { msg: string }) => e.msg).join(' '));
		}
		throw new Error(error.detail ?? 'Registration failed.');
	}

	return response.json();
}

/**
 * Authenticates a student and returns a TokenResponse.
 * Sends credentials to POST /auth/login.
 * The returned access_token must be saved via saveToken() immediately.
 * Throws an error with the backend detail message if login fails.
 */
export async function loginStudent(
	registrationNumber: number,
	emailID: string,
	password: string
): Promise<TokenResponse> {
	const response = await fetch(`${BASE_URL}/auth/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ registrationNumber, emailID, password }),
	});

	if (!response.ok) {
		const error = await response.json();
		if (Array.isArray(error.detail)) {
			throw new Error(error.detail.map((e: { msg: string }) => e.msg).join(' '));
		}
		throw new Error(error.detail ?? 'Registration failed.');
	}

	return response.json();
}

/**
 * Changes the password for the authenticated student.
 * Calls POST /auth/change-password with the JWT token.
 * Verifies the current password before applying the change.
 * Throws an error with the backend detail message if the change fails.
 */
export async function changePassword(
	currentPassword: string,
	newPassword: string,
	confirmNewPassword: string
): Promise<{ message: string }> {
	const response = await authenticatedFetch(
		`${BASE_URL}/auth/change-password`,
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json', ...authHeaders() },
			body: JSON.stringify({ currentPassword, newPassword, confirmNewPassword }),
		},
		false
	);

	if (!response.ok) {
		const error = await response.json();
		if (Array.isArray(error.detail)) {
			throw new Error(error.detail.map((e: { msg: string }) => e.msg).join(' '));
		}
		throw new Error(error.detail ?? 'Password change failed.');
	}

	return response.json();
}
