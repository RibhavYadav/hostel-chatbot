import { authStore } from '$lib/stores/authStore';
import type { LoginForm, RegisterForm } from '$lib/types';

// All functions are temporary until backend is connected via API
export async function register(form: RegisterForm): Promise<boolean> {
	try {
		authStore.register(form);
		return true;
	} catch (error) {
		console.error('Registering failed: ', error);
		return false;
	}
}

export async function login(form: LoginForm): Promise<boolean> {
	try {
		authStore.login(form);
		return true;
	} catch (error) {
		console.error('Login failed: ', error);
		return false;
	}
}

export async function logout(): Promise<boolean> {
	try {
		authStore.logout();
		return true;
	} catch (error) {
		console.error('Logout failed: ', error);
		return false;
	}
}
