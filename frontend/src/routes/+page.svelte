<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { authStore } from '$lib/stores/authStore';

	/**
	 * On mount, redirect to chat if already logged in, otherwise to login.
	 * This runs only in the browser after the component is mounted.
	 * Checks the current auth state to avoid redirecting logged-in
	 * students back to the login page unnecessarily.
	 */
	onMount(() => {
		const auth = get(authStore);
		if (auth.isLoggedIn) {
			goto(resolve('/chat'));
		} else {
			goto(resolve('/login'));
		}
	});
</script>
