<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { authStore } from '$lib/stores/authStore';
	import { changePassword } from '$lib/services/api';

	let isLoading = false;
	let errorMessage: string | null = null;
	let successMessage: string | null = null;

	let currentPassword = '';
	let newPassword = '';
	let confirmNewPassword = '';

	/**
	 * Handles password change form submission.
	 * Validates that all fields are filled and new passwords match
	 * before calling the backend. On success shows a confirmation
	 * and redirects to chat after a short delay.
	 */
	async function handleSubmit(): Promise<void> {
		errorMessage = null;
		successMessage = null;

		if (!currentPassword) {
			errorMessage = 'Please enter your current password.';
			return;
		}
		if (!newPassword) {
			errorMessage = 'Please enter a new password.';
			return;
		}
		if (newPassword !== confirmNewPassword) {
			errorMessage = 'New passwords do not match.';
			return;
		}
		if (newPassword === currentPassword) {
			errorMessage = 'New password must be different from current password.';
			return;
		}

		isLoading = true;
		try {
			const result = await changePassword(currentPassword, newPassword, confirmNewPassword);
			successMessage = result.message;
			setTimeout(() => goto(resolve('/chat')), 2000);
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Password change failed.';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-slate-50 p-4">
	<div class="auth-card">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-slate-900">Change Password</h1>
			<p class="mt-1 text-sm text-slate-500">
				{$authStore.currentUser?.emailID}
			</p>
		</div>

		<form on:submit|preventDefault={handleSubmit} class="space-y-4">
			<div>
				<label for="currentPassword" class="mb-1 block text-sm font-medium text-slate-700">
					Current Password
				</label>
				<input
					type="password"
					id="currentPassword"
					bind:value={currentPassword}
					placeholder="********"
					class="input-field"
					required />
			</div>

			<div>
				<label for="newPassword" class="mb-1 block text-sm font-medium text-slate-700">
					New Password
				</label>
				<input
					type="password"
					id="newPassword"
					bind:value={newPassword}
					placeholder="********"
					class="input-field"
					required />
				<p class="mt-1 text-xs text-slate-400">
					Min. 8 characters, one uppercase letter, one number.
				</p>
			</div>

			<div>
				<label for="confirmNewPassword" class="mb-1 block text-sm font-medium text-slate-700">
					Confirm New Password
				</label>
				<input
					type="password"
					id="confirmNewPassword"
					bind:value={confirmNewPassword}
					placeholder="********"
					class="input-field"
					required />
			</div>

			{#if errorMessage}
				<p class="text-sm text-red-500">{errorMessage}</p>
			{/if}
			{#if successMessage}
				<p class="text-sm text-green-600">{successMessage} Redirecting...</p>
			{/if}

			<button type="submit" class="button-primary w-full" disabled={isLoading}>
				{isLoading ? 'Updating...' : 'Update Password'}
			</button>
		</form>

		<p class="text-center text-sm text-slate-600">
			<a href={resolve('/chat')} class="font-medium text-indigo-600 hover:text-indigo-700">
				Back to Chat
			</a>
		</p>
	</div>
</div>
