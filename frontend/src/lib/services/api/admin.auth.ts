import { BASE_URL, authenticatedFetch, adminAuthHeaders } from '$lib/services/api/utils';
import type { AdminTokenResponse } from '$lib/types';

/**
 * Registers a new admin account.
 * Sends registration details to POST /admin/register.
 * Throws an error with the backend detail message if registration fails.
 */
export async function registerAdmin(
	emailID: string,
	adminTeam: string,
	password: string,
	confirmPassword: string
): Promise<{ message: string }> {
	const response = await fetch(`${BASE_URL}/admin/register`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ emailID, adminTeam, password, confirmPassword }),
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
 * Authenticates an admin and returns an AdminTokenResponse.
 * Sends credentials to POST /admin/login.
 * The returned access_token must be saved via saveAdminToken() immediately.
 * Throws an error with the backend detail message if login fails.
 */
export async function loginAdmin(emailID: string, password: string): Promise<AdminTokenResponse> {
	const response = await fetch(`${BASE_URL}/admin/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ emailID, password }),
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
 * Changes the password for the authenticated admin.
 * Calls POST /admin/change-password with the admin JWT token.
 * Verifies the current password before applying the change.
 * Throws an error with the backend detail message if the change fails.
 */
export async function adminChangePassword(
	currentPassword: string,
	newPassword: string,
	confirmNewPassword: string
): Promise<{ message: string }> {
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/change-password`,
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json', ...adminAuthHeaders() },
			body: JSON.stringify({ currentPassword, newPassword, confirmNewPassword }),
		},
		true
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
