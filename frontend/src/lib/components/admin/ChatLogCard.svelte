<script lang="ts">
	import type { ChatLogEntry } from '$lib/types';
	import { createEventDispatcher } from 'svelte';

	export let log: ChatLogEntry;
	export let availableTags: string[] = [];
	export let selectedTag: string | undefined = undefined;

	const dispatch = createEventDispatcher<{ promote: { logId: number; targetTag: string } }>();

	function formatConfidence(confidence: number): string {
		return `${(confidence * 100).toFixed(1)}%`;
	}

	function handlePromote() {
		dispatch('promote', {
			logId: log.id,
			targetTag: selectedTag ?? log.predictedTag,
		});
	}
</script>

<div class="card-item space-y-2 {log.promoted ? 'opacity-60' : ''}">
	<div class="flex items-start justify-between gap-4">
		<div class="flex-1 space-y-1">
			<p class="text-sm font-medium text-slate-800">{log.message}</p>
			<p class="form-hint">
				Confidence: {formatConfidence(log.confidence)} ·
				{new Date(log.timestamp).toLocaleString()}
			</p>
		</div>
		<div class="shrink-0">
			{#if log.promoted}
				<span class="badge-green">Promoted</span>
			{:else}
				<div class="flex items-center gap-2">
					<select bind:value={selectedTag} class="select-field">
						<option value={undefined}>{log.predictedTag} (predicted)</option>
						{#each availableTags.filter((t) => t !== log.predictedTag) as tag}
							<option value={tag}>{tag}</option>
						{/each}
					</select>
					<button class="button-ghost" onclick={handlePromote}> Promote </button>
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
