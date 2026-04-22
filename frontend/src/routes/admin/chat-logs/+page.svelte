<script lang="ts">
	import { onMount } from 'svelte';
	import {
		adminGetChatLogs,
		adminPromoteChatLog,
		adminRetrain,
		adminReindex,
	} from '$lib/services/api';
	import type { ChatLogEntry } from '$lib/types';

	let logs: ChatLogEntry[] = [];
	let isLoading = true;
	let isRetraining = false;
	let isReindexing = false;
	let errorMessage: string | null = null;
	let successMessage: string | null = null;

	/**
	 * Loads all chat logs on mount.
	 * Fetches unpromoted logs first so the review queue
	 * shows the most actionable items at the top.
	 */
	onMount(async () => {
		try {
			logs = await adminGetChatLogs();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to load chat logs.';
		} finally {
			isLoading = false;
		}
	});

	/**
	 * Promotes a chat log message as a training pattern.
	 * Updates the local log entry to show promoted status immediately
	 * without requiring a full page reload.
	 */
	async function handlePromote(logId: number) {
		try {
			await adminPromoteChatLog(logId);
			logs = logs.map((log) => (log.id === logId ? { ...log, promoted: true } : log));
			successMessage = 'Message promoted as training pattern.';
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Promotion failed.';
		}
	}

	/**
	 * Triggers model retraining on the current intents.json.
	 * Disables the button while retraining is in progress.
	 * Shows the detail message from the backend on completion.
	 */
	async function handleRetrain() {
		isRetraining = true;
		errorMessage = null;
		successMessage = null;
		try {
			const result = await adminRetrain();
			successMessage = result.message;
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Retraining failed.';
		} finally {
			isRetraining = false;
		}
	}

	/**
	 * Triggers rebuilding of the RAG document index.
	 * Run after adding or updating PDF files in the documents directory.
	 */
	async function handleReindex() {
		isReindexing = true;
		errorMessage = null;
		successMessage = null;
		try {
			const result = await adminReindex();
			successMessage = result.detail;
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Reindex failed.';
		} finally {
			isReindexing = false;
		}
	}

	/** Returns a confidence percentage string rounded to one decimal place. */
	function formatConfidence(confidence: number): string {
		return `${(confidence * 100).toFixed(1)}%`;
	}
</script>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<h1 class="text-2xl font-bold text-slate-900">Chat Logs</h1>
		<button
			class="button-primary px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
			onclick={handleReindex}
			disabled={isReindexing}>
			{isReindexing ? 'Indexing...' : 'Re-index Documents'}
		</button>
		<button
			class="button-primary px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
			onclick={handleRetrain}
			disabled={isRetraining}>
			{isRetraining ? 'Retraining...' : 'Retrain Model'}
		</button>
	</div>

	{#if errorMessage}
		<p class="text-sm text-red-500">{errorMessage}</p>
	{/if}
	{#if successMessage}
		<p class="text-sm text-green-600">{successMessage}</p>
	{/if}

	{#if isLoading}
		<p class="text-sm text-slate-500">Loading chat logs...</p>
	{:else if logs.length === 0}
		<p class="text-sm text-slate-500">No chat logs found.</p>
	{:else}
		<!-- Chat logs display -->
		<div class="space-y-3">
			{#each logs as log}
				<div class="space-y-2 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
					<div class="flex items-start justify-between gap-4">
						<div class="flex-1 space-y-1">
							<p class="text-sm font-medium text-slate-800">{log.message}</p>
							<p class="text-xs text-slate-500">
								Intent: <span class="font-semibold text-indigo-600">{log.predictedTag}</span>
								- Confidence: {formatConfidence(log.confidence)}
							</p>
							<p class="text-xs text-slate-400">
								{new Date(log.timestamp).toLocaleString()}
							</p>
						</div>
						<div class="shrink-0">
							{#if log.promoted}
								<span
									class="rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700">
									Promoted
								</span>
							{:else}
								<button
									class="rounded-lg bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-100"
									onclick={() => handlePromote(log.id)}>
									Promote
								</button>
							{/if}
						</div>
					</div>
					<div class="rounded-lg bg-slate-50 px-3 py-2">
						<p class="text-xs text-slate-600">
							<span class="font-medium">Bot response:</span>
							{log.botResponse}
						</p>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
