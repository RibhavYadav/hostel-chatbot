<script lang="ts">
	import { loginAdminUser } from '$lib/services/adminAuthService';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { adminAuthStore } from '$lib/stores/adminAuthStore';
	import type { AdminLoginForm } from '$lib/services/api';

	let isLoading = false;
	let errorMessage: string | null = null;

	let form: AdminLoginForm = {
		emailID: '',
		password: '',
	};

	/**
	 * Handles admin login form submission.
	 * Validates that both fields are filled before calling the API.
	 * On success redirects to the admin dashboard.
	 * On failure displays the error from adminAuthStore.
	 */
	async function handleSubmit(): Promise<void> {
		errorMessage = null;

		if (!form.emailID) {
			errorMessage = 'Please enter your email address.';
			return;
		}
		if (!form.password) {
			errorMessage = 'Please enter your password.';
			return;
		}

		isLoading = true;
		const success = await loginAdminUser(form);
		if (success) {
			isLoading = false;
			await goto(resolve('/admin/dashboard'));
		} else {
			errorMessage = $adminAuthStore.errorMessage;
			isLoading = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-slate-50 p-4">
	<div class="auth-card">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-slate-900">Admin Login</h1>
			<p class="mt-1 text-sm text-slate-500">Sign in to the admin portal</p>
		</div>

		<form on:submit|preventDefault={handleSubmit} class="space-y-4">
			<!-- Email -->
			<div>
				<label for="emailID" class="mb-1 block text-sm font-medium text-slate-700">
					Admin Email
				</label>
				<input
					type="email"
					id="emailID"
					bind:value={form.emailID}
					placeholder="admin@college.edu"
					class="input-field"
					required />
			</div>

			<!-- Password -->
			<div>
				<label for="password" class="block text-sm font-medium text-slate-700"> Password </label>
				<input
					type="password"
					id="password"
					bind:value={form.password}
					placeholder="********"
					class="input-field"
					required />
			</div>

			{#if errorMessage}
				<p class="text-sm text-red-500">{errorMessage}</p>
			{/if}

			<button type="submit" class="button-primary w-full" disabled={isLoading}>
				{isLoading ? 'Please wait...' : 'Sign In'}
			</button>
		</form>

		<p class="text-center text-sm text-slate-600">
			<a
				href={resolve('/admin/register')}
				class="font-medium text-indigo-600 hover:text-indigo-700">
				No account? Register
			</a>
		</p>
	</div>
</div>
