<script lang="ts">
	import type { IntentEntry } from '$lib/types';
	import { createEventDispatcher } from 'svelte';

	export let intent: IntentEntry;
	export let isEditing: boolean = false;
	export let isCso: boolean = false;
	export let isSaving: boolean = false;

	export let editPatterns: string = intent.patterns.join(', ');
	export let editResponses: string = intent.responses.join(', ');

	const dispatch = createEventDispatcher<{
		edit: void;
		cancelEdit: void;
		delete: void;
		save: { patterns: string; responses: string };
	}>();
</script>

<div class="space-y-3 card p-4">
	<div class="flex items-center justify-between">
		<div>
			<span class="font-semibold text-slate-800">{intent.tag}</span>
			<span class="ml-3 text-xs text-slate-400">
				{intent.patterns.length} patterns · {intent.responses.length} responses
			</span>
		</div>
		<div class="flex gap-2">
			<button
				class="button-secondary"
				onclick={() => (isEditing ? dispatch('cancelEdit') : dispatch('edit'))}>
				{isEditing ? 'Cancel' : 'Edit'}
			</button>
			{#if isCso}
				<button class="button-danger" onclick={() => dispatch('delete')}> Delete </button>
			{/if}
		</div>
	</div>

	{#if isEditing}
		<div class="space-y-3 border-t border-slate-100 pt-3">
			<div>
				<label class="form-label"
					>Patterns <span class="text-slate-400">(comma separated)</span></label>
				<textarea bind:value={editPatterns} class="input-field resize-none" rows="3"></textarea>
			</div>
			<div>
				<label class="form-label"
					>Responses <span class="text-slate-400">(comma separated)</span></label>
				<textarea bind:value={editResponses} class="input-field resize-none" rows="3"></textarea>
			</div>
			<button
				class="button-primary px-4 disabled:opacity-50"
				onclick={() => dispatch('save', { patterns: editPatterns, responses: editResponses })}
				disabled={isSaving}>
				{isSaving ? 'Saving...' : 'Save Changes'}
			</button>
		</div>
	{:else}
		<div class="space-y-2 border-t border-slate-100 pt-3">
			<p class="message-muted font-medium">Patterns</p>
			<div class="flex flex-wrap gap-1">
				{#each intent.patterns as pattern}
					<span class="badge bg-slate-100 text-slate-600">{pattern}</span>
				{/each}
			</div>
			<p class="message-muted mt-2 font-medium">Responses</p>
			<div class="space-y-1">
				{#each intent.responses as response, i}
					<p class="text-xs text-slate-600">{i + 1}. {response}</p>
				{/each}
			</div>
		</div>
	{/if}
</div>
