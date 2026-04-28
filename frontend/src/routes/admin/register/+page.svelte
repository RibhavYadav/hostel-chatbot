<script lang="ts">
	import { registerAdminUser } from '$lib/services/adminAuthService';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { adminAuthStore } from '$lib/stores/adminAuthStore';
	import type { AdminRegisterForm } from '$lib/services/api';

	let isLoading = false;
	let errorMessage: string | null = null;

	let form: AdminRegisterForm = {
		emailID: '',
		adminTeam: '',
		password: '',
		confirmPassword: '',
	};

	/**
	 * Handles admin registration form submission.
	 * Validates all fields and password match before calling the API.
	 * On success redirects to /admin/login.
	 * On failure displays the error from adminAuthStore.
	 */
	async function handleRegister(): Promise<void> {
		errorMessage = null;

		if (!form.emailID) {
			errorMessage = 'Please enter your email address.';
			return;
		}
		if (!form.adminTeam) {
			errorMessage = 'Please select your admin team.';
			return;
		}
		if (!form.password) {
			errorMessage = 'Please enter a password.';
			return;
		}
		if (form.password !== form.confirmPassword) {
			errorMessage = 'Passwords do not match.';
			return;
		}

		isLoading = true;
		const success = await registerAdminUser(form);
		if (success) {
			isLoading = false;
			await goto(resolve('/admin/login'));
		} else {
			errorMessage = $adminAuthStore.errorMessage;
			isLoading = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-slate-50 p-4">
	<div class="auth-card">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-slate-900">Admin Register</h1>
			<p class="mt-1 text-sm text-slate-500">Create your admin account</p>
		</div>

		<form on:submit|preventDefault={handleRegister} class="space-y-4">
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

			<!-- Admin team -->
			<div>
				<label for="adminTeam" class="mb-1 block text-sm font-medium text-slate-700">
					Admin Team
				</label>
				<select id="adminTeam" bind:value={form.adminTeam} class="input-field" required>
					<option value="" disabled>Select your team</option>
					<option value="cso">CSO</option>
					<option value="warden">Warden</option>
					<option value="it">IT</option>
				</select>
			</div>

			<!-- Password -->
			<label for="password" class="block text-sm font-medium text-slate-700"> Password </label>
			<input
				type="password"
				id="password"
				bind:value={form.password}
				placeholder="********"
				class="input-field"
				required />
			<p class="text-xs text-slate-400">Min. 8 characters, one uppercase letter, one number.</p>

			<!-- Confirm password -->
			<label for="confirmPassword" class="block text-sm font-medium text-slate-700">
				Confirm Password
			</label>
			<input
				type="password"
				id="confirmPassword"
				bind:value={form.confirmPassword}
				placeholder="********"
				class="input-field"
				required />

			{#if errorMessage}
				<p class="text-sm text-red-500">{errorMessage}</p>
			{/if}

			<button type="submit" class="button-primary w-full" disabled={isLoading}>
				{isLoading ? 'Please wait...' : 'Register'}
			</button>
		</form>

		<p class="text-center text-sm text-slate-600">
			<a href={resolve('/admin/login')} class="font-medium text-indigo-600 hover:text-indigo-700">
				Already have an account? Login
			</a>
		</p>
	</div>
</div>
