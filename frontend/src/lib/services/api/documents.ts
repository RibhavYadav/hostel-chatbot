import type { DocumentInfo, IntentSuggestion, SuggestionResult } from '$lib/types';

import { adminAuthHeaders, authenticatedFetch, BASE_URL } from '$lib/services/api/utils';

/**
 * Returns metadata for all uploaded PDF documents.
 * Calls GET /admin/documents with the admin JWT token.
 * Accessible by CSO and IT teams only.
 */
export async function adminListDocuments(): Promise<DocumentInfo[]> {
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/documents`,
		{
			method: 'GET',
			headers: { ...adminAuthHeaders() },
		},
		true
	);

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

	const response = await authenticatedFetch(
		`${BASE_URL}/admin/documents/upload`,
		{
			method: 'POST',
			headers: { ...adminAuthHeaders() },
			body: formData,
		},
		true
	);

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Upload failed.');
	}

	return response.json();
}

/**
 * Deletes a PDF file from the documents directory.
 * The document index should be rebuilt after deletion via
 * adminReindex for the change to take effect in document analysis.
 * Accessible by CSO and IT teams only.
 */
export async function adminDeleteDocument(filename: string): Promise<{ message: string }> {
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/documents/${encodeURIComponent(filename)}`,
		{
			method: 'DELETE',
			headers: { ...adminAuthHeaders() },
		},
		true
	);

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
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/documents/analyze/${encodeURIComponent(filename)}`,
		{
			method: 'POST',
			headers: { ...adminAuthHeaders() },
		},
		true
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
	const response = await authenticatedFetch(
		`${BASE_URL}/admin/documents/apply`,
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json', ...adminAuthHeaders() },
			body: JSON.stringify({ suggestions }),
		},
		true
	);

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail ?? 'Failed to apply suggestions.');
	}

	return response.json();
}
