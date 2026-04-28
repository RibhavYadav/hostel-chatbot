<script lang="ts">
	export let message: string | null = null;
	export let type: 'error' | 'success' | 'muted' = 'error';

	const classMap = {
		error: 'message-error',
		success: 'message-success',
		muted: 'message-muted',
	};
</script>

{#if message}
	<p class={classMap[type]}>{message}</p>
{/if}
