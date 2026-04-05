<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { submitLeaveRequest, getLeaveStatus } from '$lib/services/api';
	import type { LeaveRequest, LeaveResponse } from '$lib/types';

	// State
	let leaveRequests: LeaveResponse[] = [];
	let isLoadingRequests = true;
	let isSubmitting = false;
	let errorMessage: string | null = null;
	let successMessage: string | null = null;

	let form: LeaveRequest = {
		departureDate: '',
		returnDate: '',
		reason: '',
	};

	// Load existing requests
	/**
	 * Fetches the student's existing leave requests on page mount.
	 * Stores results in leaveRequests for display in the status table.
	 * Sets errorMessage if the fetch fails.
	 */
	onMount(async () => {
		try {
			leaveRequests = await getLeaveStatus();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to load leave requests.';
		} finally {
			isLoadingRequests = false;
		}
	});

	// Form submission
	/**
	 * Validates and submits a new leave request.
	 * Checks that both dates are present and departure is before return.
	 * On success appends the new request to the local list and resets the form.
	 * On failure sets an error message for display.
	 */
	async function handleSubmit() {
		errorMessage = null;
		successMessage = null;

		if (!form.departureDate || !form.returnDate) {
			errorMessage = 'Please select both departure and return dates.';
			return;
		}

		if (new Date(form.departureDate) >= new Date(form.returnDate)) {
			errorMessage = 'Departure date must be before return date.';
			return;
		}

		if (!form.reason.trim()) {
			errorMessage = 'Please provide a reason for your leave.';
			return;
		}

		isSubmitting = true;
		try {
			const newRequest = await submitLeaveRequest(form);
			leaveRequests = [newRequest, ...leaveRequests];
			form = { departureDate: '', returnDate: '', reason: '' };
			successMessage = 'Leave request submitted successfully.';
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Submission failed.';
		} finally {
			isSubmitting = false;
		}
	}

	/** Returns a Tailwind CSS class string based on leave request status. */
	function statusClass(status: string): string {
		if (status === 'approved') return 'bg-green-100 text-green-800';
		if (status === 'rejected') return 'bg-red-100 text-red-800';
		return 'bg-yellow-100 text-yellow-800';
	}
</script>

<div class="min-h-screen bg-slate-50 p-6">
	<div class="mx-auto max-w-2xl space-y-8">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<h1 class="text-2xl font-bold text-slate-900">Leave Request</h1>
			<button class="button-primary px-4 py-2 text-sm" onclick={() => goto(resolve('/chat'))}>
				Back to Chat
			</button>
		</div>

		<!-- Submit form -->
		<div class="space-y-4 rounded-2xl border border-slate-100 bg-white p-6 shadow-xl">
			<h2 class="text-lg font-semibold text-slate-800">Submit New Request</h2>

			<!-- Departure date -->
			<div>
				<label for="departureDate" class="mb-1 block text-sm font-medium text-slate-700">
					Departure Date
				</label>
				<input
					type="date"
					id="departureDate"
					bind:value={form.departureDate}
					class="input-field"
					required />
			</div>

			<!-- Return date -->
			<div>
				<label for="returnDate" class="mb-1 block text-sm font-medium text-slate-700">
					Return Date
				</label>
				<input
					type="date"
					id="returnDate"
					bind:value={form.returnDate}
					class="input-field"
					required />
			</div>

			<!-- Reason -->
			<div>
				<label for="reason" class="mb-1 block text-sm font-medium text-slate-700"> Reason </label>
				<textarea
					id="reason"
					bind:value={form.reason}
					placeholder="Briefly describe the reason for your leave"
					class="input-field resize-none"
					rows="3">
				</textarea>
			</div>

			<!-- Error and success messages -->
			{#if errorMessage}
				<p class="text-sm text-red-500">{errorMessage}</p>
			{/if}
			{#if successMessage}
				<p class="text-sm text-green-600">{successMessage}</p>
			{/if}

			<!-- Submit button -->
			<button
				class="button-primary w-full py-2 disabled:cursor-not-allowed disabled:opacity-50"
				onclick={handleSubmit}
				disabled={isSubmitting}>
				{isSubmitting ? 'Submitting...' : 'Submit Request'}
			</button>
		</div>

		<!-- Status list -->
		<div class="space-y-4 rounded-2xl border border-slate-100 bg-white p-6 shadow-xl">
			<h2 class="text-lg font-semibold text-slate-800">Your Requests</h2>

			{#if isLoadingRequests}
				<p class="text-sm text-slate-500">Loading your requests...</p>
			{:else if leaveRequests.length === 0}
				<p class="text-sm text-slate-500">No leave requests submitted yet.</p>
			{:else}
				<div class="space-y-3">
					{#each leaveRequests as request}
						<div class="space-y-1 rounded-lg border border-slate-200 p-4">
							<div class="flex items-center justify-between">
								<span class="text-sm font-medium text-slate-700">
									{request.departureDate} → {request.returnDate}
								</span>
								<span
									class="rounded-full px-2 py-0.5 text-xs font-semibold {statusClass(
										request.status
									)}">
									{request.status}
								</span>
							</div>
							<p class="text-sm text-slate-500">{request.reason}</p>
							<p class="text-xs text-slate-400">
								Submitted: {new Date(request.submittedAt).toLocaleDateString()}
							</p>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
