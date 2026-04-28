import { loginAdmin, registerAdmin } from '$lib/services/api';
import { adminAuthStore } from '$lib/stores/adminAuthStore';
import type { AdminLoginForm, AdminRegisterForm } from '$lib/types';

/**
 * Registers a new admin account.
 * Calls POST /admin/register via index.ts.
 * Clears any existing error before the request.
 * Sets an error message in adminAuthStore on failure.
 * Returns true on success, false on failure.
 */
export async function registerAdminUser(form: AdminRegisterForm): Promise<boolean> {
	try {
		adminAuthStore.clearError();
		await registerAdmin(form.emailID, form.adminTeam, form.password, form.confirmPassword);
		return true;
	} catch (error) {
		adminAuthStore.setError(error instanceof Error ? error.message : 'Admin registration failed.');
		return false;
	}
}

/**
 * Authenticates an admin against the backend.
 * Calls POST /admin/login via index.ts.
 * On success calls adminAuthStore.loginSuccess to store the token and admin profile.
 * On failure sets an error message in adminAuthStore.
 * Returns true on success, false on failure.
 */
export async function loginAdminUser(form: AdminLoginForm): Promise<boolean> {
	try {
		adminAuthStore.clearError();
		const response = await loginAdmin(form.emailID, form.password);
		adminAuthStore.loginSuccess(response.access_token, response.admin);
		return true;
	} catch (error) {
		adminAuthStore.setError(error instanceof Error ? error.message : 'Admin login failed.');
		return false;
	}
}

/**
 * Logs out the current admin.
 * Clears the token and admin profile from localStorage via adminAuthStore.logout.
 * Returns true always.
 */
export async function logoutAdmin(): Promise<boolean> {
	adminAuthStore.logout();
	return true;
}