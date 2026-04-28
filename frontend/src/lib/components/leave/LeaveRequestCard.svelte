<script lang="ts">
	import type { LeaveResponse } from '$lib/types';

	import StatusBadge from '$lib/components/common/StatusBadge.svelte';

	export let request: LeaveResponse;
</script>

<div class="card-item space-y-1">
	<div class="flex items-center justify-between">
		<span class="font-medium text-slate-700">
			{request.departureDate} → {request.returnDate}
		</span>
		<StatusBadge status={request.status} />
	</div>
	<p class="message-muted">{request.reason}</p>
	<p class="form-hint">
		Submitted: {new Date(request.submittedAt).toLocaleDateString()}
	</p>
</div>
