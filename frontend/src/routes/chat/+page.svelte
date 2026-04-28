<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { authStore } from '$lib/stores/authStore';
	import { chatStore } from '$lib/stores/chatStore';
	import ChatMessageComponent from '$lib/components/ChatMessage.svelte';
	import LoadingIndicator from '$lib/components/LoadingIndicator.svelte';
	import MessageInput from '$lib/components/MessageInput.svelte';

	// Logout handling
	async function handleLogout(): Promise<void> {
		authStore.logout();
		await goto(resolve('/login'));
	}

	// Message scrolling
	let messageContainer: HTMLElement | null = null;
	$effect(() => {
		void $chatStore.messages.length;
		if (messageContainer) {
			messageContainer.scrollTo({
				top: messageContainer.scrollHeight,
				behavior: 'smooth',
			});
		}
	});
</script>

<div class="flex h-screen flex-col bg-slate-50">
	<header
		class="z-10 flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6">
		<div class="flex items-center gap-6">
			<h1 class="text-lg font-bold text-slate-900">MAHE Chat</h1>
		</div>

		<nav class="flex items-center gap-3">
			<a
				href={resolve('/profile')}
				class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100">
				Profile
			</a>
			<a
				href={resolve('/leave')}
				class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium whitespace-nowrap text-slate-600 hover:bg-slate-100">
				Leave Request
			</a>
			<button class="button-primary w-full px-8" type="button" onclick={handleLogout}>
				Logout
			</button>
		</nav>
	</header>

	<!-- Message display -->
	<main bind:this={messageContainer} class="flex flex-1 flex-col gap-4 overflow-y-auto p-4 md:p-8">
		<div class="mx-auto flex w-full max-w-3xl flex-col gap-4">
			{#each $chatStore.messages as msg}
				<ChatMessageComponent message={msg} />
			{/each}

			{#if $chatStore.isTyping}
				<LoadingIndicator />
			{/if}
		</div>
	</main>

	<!-- Message input and submission -->
	<footer class="border-t border-slate-200 bg-white p-4">
		<MessageInput />
	</footer>
</div>
