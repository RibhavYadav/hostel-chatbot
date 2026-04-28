<script lang="ts">
	export let fields: { label: string; value: string | number }[];
</script>

<div class="space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
	{#each fields as field}
		<div>
			<p class="form-hint font-medium">{field.label}</p>
			<p class="mt-0.5 text-sm font-medium text-slate-800">{field.value}</p>
		</div>
	{/each}
</div>
