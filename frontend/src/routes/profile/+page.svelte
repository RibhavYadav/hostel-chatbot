<script lang="ts">
	import { resolve } from '$app/paths';

	import { authStore } from '$lib/stores/authStore';

	import ProfileCard from '$lib/components/profile/ProfileCard.svelte';

	/**
	 * The current student's profile data from the auth store.
	 * Always defined on this page because the route guard
	 * redirects unauthenticated users to /login.
	 */
	const student = $authStore.currentUser!;
	const studentFields = [
		{ label: 'Name', value: student.name },
		{ label: 'Registration Number', value: student.registrationNumber },
		{ label: 'Email', value: student.emailID },
		{ label: 'Department', value: student.department },
	];
</script>

<div class="flex min-h-screen items-center justify-center bg-slate-50 p-4">
	<div class="auth-card">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-slate-900">Profile</h1>
			<p class="mt-1 text-sm text-slate-500">Your account details</p>
		</div>

		<div class="space-y-4">
			<ProfileCard fields={studentFields} />

			<div class="flex gap-3">
				<a
					href={resolve('/chat')}
					class="flex-1 rounded-lg border border-slate-200 py-2 text-center text-sm font-medium text-slate-600 hover:bg-slate-100">
					Back to Chat
				</a>
				<a
					href={resolve('/change-password')}
					class="flex-1 rounded-lg bg-indigo-600 py-2 text-center text-sm font-semibold text-white hover:bg-indigo-700">
					Change Password
				</a>
			</div>
		</div>
	</div>
</div>
