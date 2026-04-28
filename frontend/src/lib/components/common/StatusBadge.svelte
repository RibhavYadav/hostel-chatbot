<script lang="ts">
	export let status: 'pending' | 'approved' | 'rejected';

	const statusClasses = {
		approved: 'badge-green',
		rejected: 'badge-red',
		pending: 'badge-yellow',
	};

	function formatStatus(s: string): string {
		return s.charAt(0).toUpperCase() + s.slice(1);
	}
</script>

<span class={statusClasses[status]}>
	{formatStatus(status)}
</span>
