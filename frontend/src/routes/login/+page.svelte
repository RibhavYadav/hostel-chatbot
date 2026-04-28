<script lang="ts">
	import { login } from '$lib/services/authService';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { authStore } from '$lib/stores/authStore';
	import type { LoginForm } from '$lib/services/api';

	// Template section variables
	let isLoading: boolean = false;
	let errorMessage: string | null = null;
	let form: LoginForm = {
		registrationNumber: 0,
		emailID: '',
		password: '',
	};

	async function handleSubmit(): Promise<void> {
		// Login form value checking and raising errors if needed
		errorMessage = null;
		if (form.registrationNumber === 0) {
			errorMessage = 'Please enter a registration number';
			return;
		} else if (form.emailID === '') {
			errorMessage = 'Please enter a valid email';
			return;
		} else if (form.password === '') {
			errorMessage = 'Please enter a valid password';
			return;
		}

		// Login if values follow basic format
		isLoading = true;
		await login(form);
		if ($authStore.errorMessage === null) {
			isLoading = false;
			await goto(resolve('/chat'));
		} else {
			errorMessage = $authStore.errorMessage;
			isLoading = false;
		}
	}
</script>

<!-- Login form -->
<div class="flex min-h-screen items-center justify-center bg-slate-50 p-4">
	<div class="auth-card">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-slate-900">Login</h1>
		</div>

		<!-- Main login form data entry -->
		<form on:submit|preventDefault={handleSubmit} class="space-y-4">
			<!-- Registration number -->
			<label for="registrationNumber" class="mb-1 block text-sm font-medium text-slate-700">
				Registration Number
			</label>
			<input
				type="text"
				inputmode="numeric"
				id="registrationNumber"
				bind:value={form.registrationNumber}
				placeholder="Enter Student ID"
				class="input-field"
				required />

			<!-- Student email ID -->
			<label for="emailID" class="mb-1 block text-sm font-medium text-slate-700">
				Student Email ID
			</label>
			<input
				type="email"
				id="emailID"
				bind:value={form.emailID}
				placeholder="student.mitblr2022@learner.manipal.edu"
				class="input-field"
				required />

			<!-- Login password -->
			<label for="password" class="block text-sm font-medium text-slate-700"> Password </label>
			<input
				type="password"
				id="password"
				bind:value={form.password}
				placeholder="********"
				class="input-field"
				required />

			<!-- Error display-->
			{#if errorMessage}
				<p class="text-sm text-red-500">{errorMessage}</p>
			{/if}

			<!-- Sign in -->
			<button type="submit" class="button-primary w-full" disabled={isLoading}>
				{isLoading ? 'Please wait...' : 'Sign In'}
			</button>
		</form>

		<!-- Registration -->
		<p class="text-center text-sm text-slate-600">
			<a href={resolve('/register')} class="font-medium text-indigo-600 hover:text-indigo-700">
				No account ? Register
			</a>
		</p>
	</div>
</div>
