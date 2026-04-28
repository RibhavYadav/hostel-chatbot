import type { ChatLogEntry, IntentEntry, LeaveResponse } from '$lib/types';

import { adminAuthHeaders, authenticatedFetch, BASE_URL } from '$lib/services/api/utils';

/**
 * Fetches all leave requests for admin review.
 * Calls GET /admin/leave/all with the admin JWT token.
 * Accessible by CSO and Warden teams only.
 */
export async function adminGetLeaveRequests(): Promise<LeaveResponse[]> {
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/leave/all`,
		{
			method: 'GET',
			headers: { ...adminAuthHeaders() },
		},
		true
	);

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

	const response = await authenticatedFetch(
		url,
		{
			method: 'GET',
			headers: { ...adminAuthHeaders() },
		},
		true
	);

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to fetch chat logs.');
	}

	return response.json();
}

/**
 * Promotes a chat log message as a training pattern.
 * Calls POST /admin/promote/{log_id} with the admin JWT token.
 * targetTag overrides the predicted intent if the admin selects
 * a different one from the dropdown before promoting.
 * Accessible by CSO and IT teams only.
 */
export async function adminPromoteChatLog(
	logId: number,
	targetTag?: string
): Promise<{ message: string }> {
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/promote/${logId}`,
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json', ...adminAuthHeaders() },
			body: JSON.stringify({ targetTag: targetTag ?? null }),
		},
		true
	);

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
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/retrain`,
		{
			method: 'POST',
			headers: { ...adminAuthHeaders() },
		},
		true
	);

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
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/intents`,
		{
			method: 'GET',
			headers: { ...adminAuthHeaders() },
		},
		true
	);

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
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/intents`,
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json', ...adminAuthHeaders() },
			body: JSON.stringify({ tag, patterns, responses }),
		},
		true
	);

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
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/intents/${tag}`,
		{
			method: 'PUT',
			headers: { 'Content-Type': 'application/json', ...adminAuthHeaders() },
			body: JSON.stringify({
				...(patterns !== undefined && { patterns }),
				...(responses !== undefined && { responses }),
			}),
		},
		true
	);

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
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/intents/${tag}`,
		{
			method: 'DELETE',
			headers: { ...adminAuthHeaders() },
		},
		true
	);

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
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/leave/${leaveId}/status`,
		{
			method: 'PUT',
			headers: { 'Content-Type': 'application/json', ...adminAuthHeaders() },
			body: JSON.stringify({ status }),
		},
		true
	);

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to update leave status.');
	}

	return response.json();
}
