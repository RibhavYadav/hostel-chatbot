<script lang="ts">
	import type { ChatLogEntry } from '$lib/types';
	import { createEventDispatcher } from 'svelte';

	import ChatLogCard from './ChatLogCard.svelte';

	export let tag: string;
	export let logs: ChatLogEntry[];
	export let availableTags: string[] = [];
	export let isOpen: boolean = false;

	const dispatch = createEventDispatcher<{
		toggle: void;
		promote: { logId: number; targetTag: string };
	}>();

	let selectedTags: Record<number, string | undefined> = {};
	$: unpromoted = logs.filter((l) => !l.promoted).length;
</script>

<div class="card">
	<button class="accordion-header" onclick={() => dispatch('toggle')}>
		<div class="flex items-center gap-3">
			<span class="font-semibold text-slate-800">{tag}</span>
			<span class="text-xs text-slate-400">{logs.length} messages</span>
			{#if unpromoted > 0}
				<span class="badge-yellow">{unpromoted} pending</span>
			{/if}
		</div>
		<span class="text-sm text-slate-400">{isOpen ? '▲' : '▼'}</span>
	</button>

	{#if isOpen}
		<div class="accordion-body">
			{#each logs as log}
				<ChatLogCard
					{log}
					{availableTags}
					selectedTag={selectedTags[log.id]}
					on:promote={(e) => dispatch('promote', e.detail)} />
			{/each}
		</div>
	{/if}
</div>
