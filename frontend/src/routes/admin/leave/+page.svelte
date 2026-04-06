<script lang="ts">
	import { onMount } from 'svelte';
	import { adminGetLeaveRequests, adminUpdateLeaveStatus } from '$lib/services/api';
	import type { LeaveResponse } from '$lib/types';

	let requests: LeaveResponse[] = [];
	let isLoading = true;
	let errorMessage: string | null = null;
	let successMessage: string | null = null;

	/** Loads all leave requests on mount. */
	onMount(async () => {
		try {
			requests = await adminGetLeaveRequests();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to load leave requests.';
		} finally {
			isLoading = false;
		}
	});

	/**
	 * Approves or rejects a leave request.
	 * Updates the local request status immediately on success
	 * without requiring a page reload.
	 */
	async function handleStatusUpdate(leaveId: number, status: 'approved' | 'rejected') {
		errorMessage = null;
		successMessage = null;

		try {
			await adminUpdateLeaveStatus(leaveId, status);
			requests = requests.map((r) => (r.id === leaveId ? { ...r, status } : r));
			successMessage = `Request ${leaveId} marked as ${status}.`;
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to update status.';
		}
	}

	/** Returns Tailwind classes for the status badge. */
	function statusClass(status: string): string {
		if (status === 'approved') return 'bg-green-100 text-green-800';
		if (status === 'rejected') return 'bg-red-100 text-red-800';
		return 'bg-yellow-100 text-yellow-800';
	}
</script>

<div class="space-y-6">
	<h1 class="text-2xl font-bold text-slate-900">Leave Requests</h1>

	{#if errorMessage}
		<p class="text-sm text-red-500">{errorMessage}</p>
	{/if}
	{#if successMessage}
		<p class="text-sm text-green-600">{successMessage}</p>
	{/if}

	{#if isLoading}
		<p class="text-sm text-slate-500">Loading leave requests...</p>
	{:else if requests.length === 0}
		<p class="text-sm text-slate-500">No leave requests found.</p>
	{:else}
		<div class="space-y-3">
			{#each requests as request}
				<div class="space-y-2 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
					<div class="flex items-start justify-between gap-4">
						<div class="space-y-1">
							<p class="text-sm font-medium text-slate-800">
								Student ID: {request.studentId}
							</p>
							<p class="text-sm text-slate-600">
								{request.departureDate} → {request.returnDate}
							</p>
							<p class="text-sm text-slate-500">{request.reason}</p>
							<p class="text-xs text-slate-400">
								Submitted: {new Date(request.submittedAt).toLocaleDateString()}
							</p>
						</div>
						<div class="flex shrink-0 flex-col items-end gap-2">
							<span
								class="rounded-full px-2 py-0.5 text-xs font-semibold {statusClass(
									request.status
								)}">
								{request.status}
							</span>
							{#if request.status === 'pending'}
								<div class="flex gap-2">
									<button
										class="rounded-lg bg-green-50 px-3 py-1 text-xs font-semibold text-green-700 hover:bg-green-100"
										onclick={() => handleStatusUpdate(request.id, 'approved')}>
										Approve
									</button>
									<button
										class="rounded-lg bg-red-50 px-3 py-1 text-xs font-semibold text-red-700 hover:bg-red-100"
										onclick={() => handleStatusUpdate(request.id, 'rejected')}>
										Reject
									</button>
								</div>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
