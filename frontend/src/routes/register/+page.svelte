<script lang="ts">
	import { register } from '$lib/services/authService';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { authStore } from '$lib/stores/authStore';
	import type { RegisterForm } from '$lib/types';

	// Template section variables
	let isLoading: boolean = false;
	let errorMessage: string | null = null;
	let form: RegisterForm = {
		registrationNumber: 0,
		emailID: '',
		password: '',
		confirmPassword: '',
	};

	async function handleRegister(): Promise<void> {
		// Register form value checking and raising errors if needed
		errorMessage = null;
		if (form.registrationNumber === 0) {
			errorMessage = 'Please enter a registration number';
			return;
		} else if (form.emailID === '') {
			errorMessage = 'Please enter a registration email address';
			return;
		} else if (form.password === '') {
			errorMessage = 'Please enter a valid password';
			return;
		} else if (form.password !== form.confirmPassword) {
			errorMessage = 'Please match the password';
			return;
		}

		// Register if values follow basic format
		isLoading = true;
		await register(form);
		if ($authStore.errorMessage === null) {
			isLoading = false;
			await goto(resolve('/login'));
		} else {
			errorMessage = $authStore.errorMessage;
			isLoading = false;
		}
	}
</script>

<!-- Register form -->
<div class="flex min-h-screen items-center justify-center bg-slate-50 p-4">
	<div class="auth-card">
		<div class="text-center">
			<h1 class="text-3xl font-bold text-slate-900">Register</h1>
		</div>

		<!-- Main register form data entry -->
		<form on:submit|preventDefault={handleRegister} class="space-y-4">
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

			<!-- Confirm password-->
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

			<!-- Error display -->
			{#if errorMessage}
				<p class="text-sm text-red-500">{errorMessage}</p>
			{/if}

			<!-- Register -->
			<button type="submit" class="button-primary w-full" disabled={isLoading}>
				{isLoading ? 'Please wait...' : 'Register'}
			</button>
		</form>

		<!-- Login -->
		<p class="text-center text-sm text-slate-600">
			<a href={resolve('/login')} class="font-medium text-indigo-600 hover:text-indigo-700">
				Already have an account ? Login
			</a>
		</p>
	</div>
</div>
