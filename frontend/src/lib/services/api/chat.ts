import { BASE_URL, authenticatedFetch, authHeaders } from '$lib/services/api/utils';
import type { LeaveRequest, LeaveResponse, BotResponse } from '$lib/types';

/**
 * Sends a student message to the NLP model and returns the bot response.
 * Calls POST /chat with the JWT token in the Authorization header.
 * The response includes the bot message, predicted intent, and requiresForm flag.
 * Throws an error if the token is missing, invalid, or the request fails.
 */
export async function sendMessage(message: string): Promise<BotResponse> {
	const response = await authenticatedFetch(
		`${BASE_URL}/chat`,
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json', ...authHeaders() },
			body: JSON.stringify({ message }),
		},
		false
	);

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
	const response = await authenticatedFetch(
		`${BASE_URL}/leave/submit`,
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json', ...authHeaders() },
			body: JSON.stringify(request),
		},
		false
	);

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
	const response = await authenticatedFetch(
		`${BASE_URL}/leave/status`,
		{
			method: 'GET',
			headers: { 'Content-Type': 'application/json', ...authHeaders() },
		},
		false
	);

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to fetch leave status.');
	}

	return response.json();
}
