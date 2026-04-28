<script lang="ts">
	export let label: string;
	export let value: number;
	export let valueClass: string = 'text-slate-900';
</script>

<div class="card-padded">
	<p class="message-muted">{label}</p>
	<p class="mt-1 text-3xl font-bold {valueClass}">{value}</p>
</div>
