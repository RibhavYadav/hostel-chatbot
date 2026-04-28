<script lang="ts">
	import { resolve } from '$app/paths';
	import { adminAuthStore } from '$lib/stores/adminAuthStore';

	const admin = $adminAuthStore.currentAdmin!;

	/** Formats the admin team string in title case for display. */
	function formatTeam(team: string): string {
		return team.charAt(0).toUpperCase() + team.slice(1).toLowerCase();
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-slate-50 p-4">
	<div class="auth-card">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-slate-900">Admin Profile</h1>
			<p class="mt-1 text-sm text-slate-500">Your account details</p>
		</div>

		<div class="space-y-4">
			<div class="space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
				<div>
					<p class="text-xs font-medium text-slate-400">Email</p>
					<p class="mt-0.5 text-sm font-medium text-slate-800">{admin.emailID}</p>
				</div>
				<div>
					<p class="text-xs font-medium text-slate-400">Admin Team</p>
					<p class="mt-0.5 text-sm font-medium text-slate-800">{formatTeam(admin.adminTeam)}</p>
				</div>
			</div>

			<div class="flex gap-3">
				<a
					href={resolve('/admin/dashboard')}
					class="flex-1 rounded-lg border border-slate-200 py-2 text-center text-sm font-medium text-slate-600 hover:bg-slate-100">
					Back to Dashboard
				</a>
				<a
					href={resolve('/admin/change-password')}
					class="flex-1 rounded-lg bg-indigo-600 py-2 text-center text-sm font-semibold text-white hover:bg-indigo-700">
					Change Password
				</a>
			</div>
		</div>
	</div>
</div>
