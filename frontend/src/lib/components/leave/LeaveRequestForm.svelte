<script lang="ts">
	import type { LeaveRequest, LeaveResponse } from '$lib/types';
	import { createEventDispatcher } from 'svelte';

	import { submitLeaveRequest } from '$lib/services/api';

	import FeedbackMessage from '$lib/components/common/FeedbackMessage.svelte';

	/**
	 * Dispatched when a leave request is submitted successfully.
	 * The parent page uses this to prepend the new request to its list.
	 */
	const dispatch = createEventDispatcher<{ submitted: LeaveResponse }>();

	let isSubmitting = false;
	let errorMessage: string | null = null;
	let successMessage: string | null = null;

	let form: LeaveRequest = { departureDate: '', returnDate: '', reason: '' };

	/**
	 * Validates and submits the leave request form.
	 * Dispatches a submitted event with the new record on success.
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
			form = { departureDate: '', returnDate: '', reason: '' };
			successMessage = 'Leave request submitted successfully.';
			dispatch('submitted', newRequest);
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Submission failed.';
		} finally {
			isSubmitting = false;
		}
	}
</script>

<div class="card-padded space-y-4 shadow-xl">
	<h2 class="text-lg font-semibold text-slate-800">Submit New Request</h2>

	<div>
		<label for="departureDate" class="form-label">Departure Date</label>
		<input
			type="date"
			id="departureDate"
			bind:value={form.departureDate}
			class="input-field"
			required />
	</div>

	<div>
		<label for="returnDate" class="form-label">Return Date</label>
		<input type="date" id="returnDate" bind:value={form.returnDate} class="input-field" required />
	</div>

	<div>
		<label for="reason" class="form-label">Reason</label>
		<textarea id="reason" bind:value={form.reason} class="input-field resize-none" rows="3"
		></textarea>
	</div>

	<FeedbackMessage type="error" message={errorMessage} />
	<FeedbackMessage type="success" message={successMessage} />

	<button
		class="button-primary w-full disabled:opacity-50"
		onclick={handleSubmit}
		disabled={isSubmitting}>
		{isSubmitting ? 'Submitting...' : 'Submit Request'}
	</button>
</div>
