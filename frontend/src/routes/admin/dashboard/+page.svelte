<script lang="ts">
	import { onMount } from 'svelte';
	import { adminAuthStore } from '$lib/stores/adminAuthStore';
	import { adminGetLeaveRequests, adminGetChatLogs } from '$lib/services/api';
	import type { LeaveResponse, ChatLogEntry } from '$lib/types';

	let totalLeave = 0;
	let pendingLeave = 0;
	let totalChatLogs = 0;
	let isLoading = true;

	/**
	 * Fetches summary statistics for the dashboard on mount.
	 * Loads leave requests and chat logs concurrently using Promise.all.
	 * Falls back to zero counts if a fetch fails due to team permissions.
	 */
	onMount(async () => {
		const team = $adminAuthStore.currentAdmin?.adminTeam;

		const results = await Promise.allSettled([
			team === 'it' ? Promise.resolve([]) : adminGetLeaveRequests(),
			team === 'warden' ? Promise.resolve([]) : adminGetChatLogs(),
		]);

		if (results[0].status === 'fulfilled') {
			const leave = results[0].value as LeaveResponse[];
			totalLeave = leave.length;
			pendingLeave = leave.filter((r) => r.status === 'pending').length;
		}

		if (results[1].status === 'fulfilled') {
			totalChatLogs = (results[1].value as ChatLogEntry[]).length;
		}

		isLoading = false;
	});
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-bold text-slate-900">Dashboard</h1>
		<p class="text-sm text-slate-500">
			Welcome, {$adminAuthStore.currentAdmin?.emailID}
		</p>
	</div>

	{#if isLoading}
		<p class="text-sm text-slate-500">Loading...</p>
	{:else}
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
			<!-- Total leave -->
			<div class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
				<p class="text-sm text-slate-500">Total Leave Requests</p>
				<p class="mt-1 text-3xl font-bold text-slate-900">{totalLeave}</p>
			</div>

			<!-- Pending leave -->
			<div class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
				<p class="text-sm text-slate-500">Pending Approval</p>
				<p class="mt-1 text-3xl font-bold text-yellow-600">{pendingLeave}</p>
			</div>

			<!-- Chat logs -->
			<div class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
				<p class="text-sm text-slate-500">Total Chat Logs</p>
				<p class="mt-1 text-3xl font-bold text-slate-900">{totalChatLogs}</p>
			</div>
		</div>
	{/if}
</div>
