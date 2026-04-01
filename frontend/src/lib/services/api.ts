import type { BotResponse, TokenResponse, LeaveRequest, LeaveResponse } from '$lib/types';

/**
 * Base URL for all backend API requests.
 * Reads from the BITE_API_URL environment variable if set,
 * otherwise fall back to local backend development server.
 */
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// Token storage

/**
 * Saves the JWT token to localStorage.
 * Called immediately after a successful login response.
 * Persists across page reloads and browser tabs.
 */
export function saveToken(token: string): void {
	localStorage.setItem('auth_token', token);
}

/**
 * Retrieves the JWT token from localStorage.
 * Returns null if the user is not logged in or the token has been cleared.
 */
export function getToken(): string | null {
	return localStorage.getItem('auth_token');
}

/**
 * Removes the JWT token from localStorage.
 * Called on logout to ensure the token cannot be reused.
 */
export function clearToken(): void {
	localStorage.removeItem('auth_token');
}

// Auth header builder

/**
 * Builds the Authorization header for protected endpoint requests.
 * Returns an empty object if no token is stored so the spread
 * operator in fetch calls adds nothing when the user is not logged in.
 */
function authHeaders(): Record<string, string> {
	const token = getToken();
	if (!token) return {};

	return { Authorization: `Bearer ${token}` };
}

// Auth endpoints

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
		throw new Error(error.detail ?? 'Login failed.');
	}

	return response.json();
}

// Chat endpoint

/**
 * Sends a student message to the NLP model and returns the bot response.
 * Calls POST /chat with the JWT token in the Authorization header.
 * The response includes the bot message, predicted intent, and requiresForm flag.
 * Throws an error if the token is missing, invalid, or the request fails.
 */
export async function sendMessage(message: string): Promise<BotResponse> {
	const response = await fetch(`${BASE_URL}/chat`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...authHeaders(),
		},
		body: JSON.stringify({ message }),
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Chat request failed.');
	}

	return response.json();
}

// Leave endpoints

/**
 * Submits a new leave request for the authenticated student.
 * Calls POST /leave/submit with the JWT token in the Authorization header.
 * Returns the created leave record including its id and initial pending status.
 * Throws an error if the dates are invalid or the request fails.
 */
export async function submitLeaveRequest(request: LeaveRequest): Promise<LeaveResponse> {
	const response = await fetch(`${BASE_URL}/leave/submit`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...authHeaders(),
		},
		body: JSON.stringify(request),
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Leave request submission failed.');
	}

	return response.json();
}

/**
 * Retrieves all leave requests for the authenticated student.
 * Calls GET /leave/status with the JWT token in the Authorization header.
 * Returns an array ordered by most recent submission first.
 * Returns an empty array if no requests have been submitted.
 */
export async function getLeaveStatus(): Promise<LeaveResponse[]> {
	const response = await fetch(`${BASE_URL}/leave/status`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			...authHeaders(),
		},
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to fetch leave status.');
	}

	return response.json();
}
