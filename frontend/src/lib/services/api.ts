import type {
	BotResponse,
	TokenResponse,
	AdminTokenResponse,
	LeaveRequest,
	LeaveResponse,
	ChatLogEntry,
	IntentEntry,
	DocumentInfo,
	IntentSuggestion,
	SuggestionResult,
} from '$lib/types';

/**
 * Base URL for all backend API requests.
 * Reads from the VITE_API_URL environment variable if set,
 * otherwise fall back to local backend development server.
 */
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// Token storage
/**
 * Guard all localStorage calls with a browser check.
 */
function isBrowser(): boolean {
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

/**
 * Builds the Authorization header for protected endpoint requests.
 * Returns an empty object if no token is stored so the spread
 * operator in fetch calls adds nothing when the user is not logged in.
 */
function adminAuthHeaders(): Record<string, string> {
	const token = getAdminToken();
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

// Leave and chat endpoints

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
	const response = await fetch(`${BASE_URL}/auth/change-password`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...authHeaders(),
		},
		body: JSON.stringify({ currentPassword, newPassword, confirmNewPassword }),
	});

	if (!response.ok) {
		const error = await response.json();
		if (Array.isArray(error.detail)) {
			throw new Error(error.detail.map((e: { msg: string }) => e.msg).join(' '));
		}
		throw new Error(error.detail ?? 'Password change failed.');
	}

	return response.json();
}

// Admin endpoints

/**
 * Fetches all leave requests for admin review.
 * Calls GET /admin/leave/all with the admin JWT token.
 * Accessible by CSO and Warden teams only.
 */
export async function adminGetLeaveRequests(): Promise<LeaveResponse[]> {
	const response = await fetch(`${BASE_URL}/admin/leave/all`, {
		method: 'GET',
		headers: { ...adminAuthHeaders() },
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to fetch leave requests.');
	}

	return response.json();
}

/**
 * Fetches all student chat logs for admin review.
 * Calls GET /admin/chat-logs with the admin JWT token.
 * Optional promoted filter: true returns only promoted logs,
 * false returns only unpromoted logs, omit for all logs.
 * Accessible by CSO and IT teams only.
 */
export async function adminGetChatLogs(promoted?: boolean): Promise<ChatLogEntry[]> {
	const url =
		promoted !== undefined
			? `${BASE_URL}/admin/chat-logs?promoted=${promoted}`
			: `${BASE_URL}/admin/chat-logs`;

	const response = await fetch(url, {
		method: 'GET',
		headers: { ...adminAuthHeaders() },
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to fetch chat logs.');
	}

	return response.json();
}

/**
 * Promotes a chat log message as a training pattern for its predicted intent.
 * Calls POST /admin/promote/{log_id} with the admin JWT token.
 * Marks the log as promoted so it does not appear in the review queue again.
 * Accessible by CSO and IT teams only.
 */
export async function adminPromoteChatLog(logId: number): Promise<{ message: string }> {
	const response = await fetch(`${BASE_URL}/admin/promote/${logId}`, {
		method: 'POST',
		headers: { ...adminAuthHeaders() },
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to promote chat log.');
	}

	return response.json();
}

/**
 * Triggers model retraining using the current intents.json.
 * Calls POST /admin/retrain with the admin JWT token.
 * Returns a message confirming the retrain and reload status.
 * Accessible by CSO and IT teams only.
 */
export async function adminRetrain(): Promise<{ message: string; detail: string }> {
	const response = await fetch(`${BASE_URL}/admin/retrain`, {
		method: 'POST',
		headers: { ...adminAuthHeaders() },
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Retraining failed.');
	}

	return response.json();
}

/**
 * Fetches all intents from the NLP service.
 * Calls GET /admin/intents with the admin JWT token.
 * Returns the intents currently loaded in the server's NLP state.
 * Accessible by CSO and IT teams only.
 */
export async function adminGetIntents(): Promise<IntentEntry[]> {
	const response = await fetch(`${BASE_URL}/admin/intents`, {
		method: 'GET',
		headers: { ...adminAuthHeaders() },
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to fetch intents.');
	}

	return response.json();
}

/**
 * Creates a new intent in intents.json.
 * Calls POST /admin/intents with the admin JWT token.
 * Throws if the tag already exists.
 * Accessible by CSO and IT teams only.
 */
export async function adminCreateIntent(
	tag: string,
	patterns: string[],
	responses: string[]
): Promise<{ message: string }> {
	const response = await fetch(`${BASE_URL}/admin/intents`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...adminAuthHeaders(),
		},
		body: JSON.stringify({ tag, patterns, responses }),
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to create intent.');
	}

	return response.json();
}

/**
 * Updates the patterns or responses or both for an existing intent.
 * Calls PUT /admin/intents/{tag} with the admin JWT token.
 * Fields omitted from the request are left unchanged on the backend.
 * Accessible by CSO and IT teams only.
 */
export async function adminUpdateIntent(
	tag: string,
	patterns?: string[],
	responses?: string[]
): Promise<{ message: string }> {
	const response = await fetch(`${BASE_URL}/admin/intents/${tag}`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
			...adminAuthHeaders(),
		},
		body: JSON.stringify({
			...(patterns !== undefined && { patterns }),
			...(responses !== undefined && { responses }),
		}),
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to update intent.');
	}

	return response.json();
}

/**
 * Deletes an intent and all its patterns and responses from intents.json.
 * Calls DELETE /admin/intents/{tag} with the admin JWT token.
 * This action is irreversible. Restricted to CSO team only.
 */
export async function adminDeleteIntent(tag: string): Promise<{ message: string }> {
	const response = await fetch(`${BASE_URL}/admin/intents/${tag}`, {
		method: 'DELETE',
		headers: { ...adminAuthHeaders() },
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to delete intent.');
	}

	return response.json();
}

/**
 * Updates the status of a leave request to approved or rejected.
 * Calls PUT /admin/leave/{leave_id}/status with the admin JWT token.
 * Sets reviewed_at timestamp on the backend automatically.
 * Accessible by CSO and Warden teams only.
 */
export async function adminUpdateLeaveStatus(
	leaveId: number,
	status: 'approved' | 'rejected'
): Promise<{ message: string }> {
	const response = await fetch(`${BASE_URL}/admin/leave/${leaveId}/status`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
			...adminAuthHeaders(),
		},
		body: JSON.stringify({ status }),
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to update leave status.');
	}

	return response.json();
}

/**
 * Triggers rebuilding of the RAG document index from PDF files.
 * Calls POST /admin/reindex with the admin JWT token.
 * Run after adding or updating PDF files in the documents directory.
 * Accessible by CSO and IT teams only.
 */
export async function adminReindex(): Promise<{ message: string; detail: string }> {
	const response = await fetch(`${BASE_URL}/admin/reindex`, {
		method: 'POST',
		headers: { ...adminAuthHeaders() },
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Reindex failed.');
	}

	return response.json();
}

/**
 * Returns metadata for all uploaded PDF documents.
 * Calls GET /admin/documents with the admin JWT token.
 * Accessible by CSO and IT teams only.
 */
export async function adminListDocuments(): Promise<DocumentInfo[]> {
	const response = await fetch(`${BASE_URL}/admin/documents`, {
		method: 'GET',
		headers: { ...adminAuthHeaders() },
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to fetch documents.');
	}

	return response.json();
}

/**
 * Uploads a PDF file to the documents directory.
 * Uses multipart/form-data - do not set Content-Type manually,
 * the browser sets it automatically with the correct boundary.
 * Accessible by CSO and IT teams only.
 */
export async function adminUploadDocument(file: File): Promise<{ message: string }> {
	const formData = new FormData();
	formData.append('file', file);

	const response = await fetch(`${BASE_URL}/admin/documents/upload`, {
		method: 'POST',
		headers: { ...adminAuthHeaders() },
		body: formData,
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Upload failed.');
	}

	return response.json();
}

/**
 * Deletes a PDF file from the documents directory.
 * The RAG index must be rebuilt after deletion for the
 * change to take effect in retrieval.
 * Accessible by CSO and IT teams only.
 */
export async function adminDeleteDocument(filename: string): Promise<{ message: string }> {
	const response = await fetch(`${BASE_URL}/admin/documents/${encodeURIComponent(filename)}`, {
		method: 'DELETE',
		headers: { ...adminAuthHeaders() },
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Delete failed.');
	}

	return response.json();
}

/**
 * Runs the intent suggestion pipeline on the specified PDF.
 * Returns suggestions grouped by intent for admin review.
 * This call can take 10-30 seconds for large documents.
 * Accessible by CSO and IT teams only.
 */
export async function adminAnalyzeDocument(filename: string): Promise<SuggestionResult> {
	const response = await fetch(
		`${BASE_URL}/admin/documents/analyze/${encodeURIComponent(filename)}`,
		{
			method: 'POST',
			headers: { ...adminAuthHeaders() },
		}
	);

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Analysis failed.');
	}

	return response.json();
}

/**
 * Applies accepted and reviewed suggestions to intents.json.
 * Only suggestions with accepted=true are written.
 * Admin edits to suggestedIntent and type are preserved.
 * Accessible by CSO and IT teams only.
 */
export async function adminApplySuggestions(
	suggestions: IntentSuggestion[]
): Promise<{ message: string; patternsAdded: number; responsesAdded: number; skipped: number }> {
	const response = await fetch(`${BASE_URL}/admin/documents/apply`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...adminAuthHeaders(),
		},
		body: JSON.stringify({ suggestions }),
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to apply suggestions.');
	}

	return response.json();
}
