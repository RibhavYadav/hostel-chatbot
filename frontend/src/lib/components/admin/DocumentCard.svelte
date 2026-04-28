<script lang="ts">
	import type { DocumentInfo } from '$lib/types';
	import { createEventDispatcher } from 'svelte';

	export let doc: DocumentInfo;
	export let isAnalyzing: boolean = false;

	const dispatch = createEventDispatcher<{ analyze: string; delete: string }>();

	function formatSize(bytes: number): string {
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}
</script>

<div class="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3">
	<div>
		<p class="text-sm font-medium text-slate-800">{doc.filename}</p>
		<p class="form-hint">{formatSize(doc.size)}</p>
	</div>
	<div class="flex gap-2">
		<button
			class="button-ghost disabled:opacity-50"
			onclick={() => dispatch('analyze', doc.filename)}
			disabled={isAnalyzing}>
			{isAnalyzing ? 'Analyzing...' : 'Analyze'}
		</button>
		<button class="button-danger" onclick={() => dispatch('delete', doc.filename)}> Delete </button>
	</div>
</div>
