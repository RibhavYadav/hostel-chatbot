<script lang="ts">
	import { onMount } from 'svelte';
	import { adminGetChatLogs, adminPromoteChatLog, adminRetrain } from '$lib/services/api';
	import type { ChatLogEntry } from '$lib/services/api';

	let logs: ChatLogEntry[] = [];
	let isLoading = true;
	let isRetraining = false;
	let errorMessage: string | null = null;
	let successMessage: string | null = null;
	let openTag: string | null = null;
	let allTags: string[] = [];
	let selectedTags: Record<number, string> = {};
	let sortBy: 'time' | 'confidence' = 'time';
	let sortOrder: 'asc' | 'desc' = 'desc';

	/**
	 * Loads all chat logs on mount and groups them by predicted intent tag.
	 * Grouping allows admins to review one intent category at a time
	 * rather than scanning a flat chronological list.
	 */
	onMount(async () => {
		try {
			logs = await adminGetChatLogs();
			allTags = [...new Set(logs.map((l) => l.predictedTag))].sort();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to load chat logs.';
		} finally {
			isLoading = false;
		}
	});

	/**
	 * Groups the flat log list into a map of intent tag to log entries.
	 * Derived reactively so it updates when a log is promoted.
	 */
	$: groupedLogs = logs.reduce(
		(acc, log) => {
			if (!acc[log.predictedTag]) acc[log.predictedTag] = [];
			acc[log.predictedTag].push(log);
			return acc;
		},
		{} as Record<string, ChatLogEntry[]>
	);

	/**
	 * Sorts logs within each intent group by the selected field and order.
	 * Reactive so it updates immediately when sort controls change.
	 */
	$: sortedGroupedLogs = Object.fromEntries(
		Object.entries(groupedLogs).map(([tag, tagLogs]) => [
			tag,
			[...tagLogs].sort((a, b) => {
				const multiplier = sortOrder === 'desc' ? -1 : 1;
				if (sortBy === 'confidence') {
					return multiplier * (a.confidence - b.confidence);
				}
				return multiplier * (new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
			}),
		])
	);

	/** Sorted intent tags — unpromoted-heavy intents appear first. */
	$: sortedTags = Object.keys(groupedLogs).sort((a, b) => {
		const unpromotedA = groupedLogs[a].filter((l) => !l.promoted).length;
		const unpromotedB = groupedLogs[b].filter((l) => !l.promoted).length;
		return unpromotedB - unpromotedA;
	});

	/**
	 * Promotes a chat log using the admin-selected intent tag.
	 * Falls back to the predicted tag if no override was selected.
	 */
	async function handlePromote(logId: number, predictedTag: string) {
		const targetTag = selectedTags[logId] ?? predictedTag;
		try {
			await adminPromoteChatLog(logId, targetTag);
			logs = logs.map((log) => (log.id === logId ? { ...log, promoted: true } : log));
			successMessage = `Message promoted under '${targetTag}'.`;
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Promotion failed.';
		}
	}

	/**
	 * Triggers model retraining on the current intents.json.
	 * Disables the button while retraining is in progress.
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

	/** Toggles the accordion open state for an intent group. */
	function toggleTag(tag: string) {
		openTag = openTag === tag ? null : tag;
	}

	/** Returns a confidence percentage string rounded to one decimal place. */
	function formatConfidence(confidence: number): string {
		return `${(confidence * 100).toFixed(1)}%`;
	}

	/** Returns count of unpromoted logs for a tag. */
	function unpromoted(tag: string): number {
		return groupedLogs[tag].filter((l) => !l.promoted).length;
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold text-slate-900">Chat Logs</h1>
		<div class="flex items-center gap-3">
			<div class="flex items-center gap-2">
				<span class="text-sm text-slate-500">Sort by</span>
				<select
					bind:value={sortBy}
					class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-700">
					<option value="time">Time</option>
					<option value="confidence">Confidence</option>
				</select>
				<select
					bind:value={sortOrder}
					class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-700">
					<option value="desc">Newest / Highest first</option>
					<option value="asc">Oldest / Lowest first</option>
				</select>
			</div>
			<button
				class="button-primary px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
				onclick={handleRetrain}
				disabled={isRetraining}>
				{isRetraining ? 'Retraining...' : 'Retrain Model'}
			</button>
		</div>
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
		<div class="space-y-2">
			{#each sortedTags as tag}
				<div class="rounded-2xl border border-slate-100 bg-white shadow-sm">
					<!-- Accordion header -->
					<button
						class="flex w-full items-center justify-between px-5 py-4 text-left"
						onclick={() => toggleTag(tag)}>
						<div class="flex items-center gap-3">
							<span class="font-semibold text-slate-800">{tag}</span>
							<span class="text-xs text-slate-400">{groupedLogs[tag].length} messages</span>
							{#if unpromoted(tag) > 0}
								<span
									class="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-semibold text-yellow-700">
									{unpromoted(tag)} pending
								</span>
							{/if}
						</div>
						<span class="text-sm text-slate-400">{openTag === tag ? '▲' : '▼'}</span>
					</button>

					<!-- Accordion body -->
					{#if openTag === tag}
						<div class="space-y-3 border-t border-slate-100 px-5 py-4">
							{#each sortedGroupedLogs[tag] as log}
								<div
									class="space-y-2 rounded-xl border border-slate-100 p-3
									{log.promoted ? 'opacity-60' : ''}">
									<div class="flex items-start justify-between gap-4">
										<div class="flex-1 space-y-1">
											<p class="text-sm font-medium text-slate-800">{log.message}</p>
											<p class="text-xs text-slate-400">
												Confidence: {formatConfidence(log.confidence)} ·
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
												<div class="flex items-center gap-2">
													<select
														bind:value={selectedTags[log.id]}
														class="rounded border border-slate-200 px-2 py-1 text-xs text-slate-700">
														<option value={undefined}>{log.predictedTag} (predicted)</option>
														{#each allTags.filter((t) => t !== log.predictedTag) as tag}
															<option value={tag}>{tag}</option>
														{/each}
													</select>
													<button
														class="rounded-lg bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-100"
														onclick={() => handlePromote(log.id, log.predictedTag)}>
														Promote
													</button>
												</div>
											{/if}
										</div>
									</div>
									<div class="rounded-lg bg-slate-50 px-3 py-2">
										<p class="text-xs text-slate-600">
											<span class="font-medium">Bot:</span>
											{log.botResponse}
										</p>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>
