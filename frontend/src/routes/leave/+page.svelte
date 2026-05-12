<script lang="ts">
	import type { LeaveResponse } from '$lib/types';
	import { onMount } from 'svelte';

	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	import { getLeaveStatus } from '$lib/services/api';

	import FeedbackMessage from '$lib/components/common/FeedbackMessage.svelte';
	import LeaveRequestCard from '$lib/components/leave/LeaveRequestCard.svelte';
	import LeaveRequestForm from '$lib/components/leave/LeaveRequestForm.svelte';

	let leaveRequests: LeaveResponse[] = [];
	let isLoadingRequests = true;
	let errorMessage: string | null = null;

	onMount(async () => {
		try {
			leaveRequests = await getLeaveStatus();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to load leave requests.';
		} finally {
			isLoadingRequests = false;
		}
	});

	function handleNewRequest(event: CustomEvent<LeaveResponse>) {
		leaveRequests = [event.detail, ...leaveRequests];
	}
</script>

<div class="min-h-screen bg-slate-50 p-6">
	<div class="mx-auto max-w-2xl space-y-8">
		<div class="page-header">
			<h1 class="page-title">Leave Request</h1>
			<button class="button-secondary" onclick={() => goto(resolve('/chat'))}>
				Back to Chat
			</button>
		</div>

		<LeaveRequestForm on:submitted={handleNewRequest} />

		<div class="card-padded space-y-4 shadow-xl">
			<h2 class="text-lg font-semibold text-slate-800">Your Requests</h2>

			<FeedbackMessage type="error" message={errorMessage} />

			{#if isLoadingRequests}
				<p class="message-muted">Loading your requests...</p>
			{:else if leaveRequests.length === 0}
				<p class="message-muted">No leave requests submitted yet.</p>
			{:else}
				<div class="space-y-3">
					{#each leaveRequests as request}
						<LeaveRequestCard {request} />
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
