<script lang="ts">
	import { sendMessage } from '$lib/services/api';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { chatStore } from '$lib/stores/chatStore';

	let messageText = '';
	let textAreaElement: HTMLTextAreaElement;

	/**
	 * Svelte action that makes the textarea grow with its content.
	 * Resets height to auto before measuring scrollHeight so shrinking
	 * works correctly when the student deletes text.
	 * Cleans up the event listener when the element is destroyed.
	 */
	function autoResize(area: HTMLTextAreaElement) {
		const updateHeight = () => {
			area.style.height = 'auto';
			area.style.height = `${area.scrollHeight}px`;
		};

		area.addEventListener('input', updateHeight);
		updateHeight();
		textAreaElement = area;

		return {
			destroy: () => area.removeEventListener('input', updateHeight),
		};
	}

	/**
	 * Submits the message when Enter is pressed without Shift.
	 * Shift+Enter inserts a newline instead of submitting.
	 */
	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSending();
		}
	}

	/**
	 * Handles the full message submission flow.
	 * Trims the input and returns early if empty.
	 * Adds the user message to the store, clears the input,
	 * shows the typing indicator, then calls botResponse.
	 * Always hides the typing indicator in the finally block
	 * regardless of whether botResponse succeeded or failed.
	 */
	async function handleSending() {
		const content = messageText.trim();
		if (!content) return;

		chatStore.addMessage({ role: 'user', content: content });
		messageText = '';
		chatStore.setTyping(true);

		if (textAreaElement) {
			textAreaElement.style.height = 'auto';
		}

		try {
			await botResponse(content);
		} finally {
			chatStore.setTyping(false);
		}
	}

	/**
	 * Sends the student message to the backend NLP model.
	 * Calls sendMessage from api.ts which attaches the JWT token automatically.
	 * Adds the bot response text to the chat store on success.
	 * If requiresForm is true the model detected a leave request intent -
	 * the student is redirected to the leave form page automatically.
	 * On failure sets a chat store error and adds a visible fallback message
	 * so the student knows something went wrong.
	 */
	async function botResponse(query: string) {
		try {
			const response = await sendMessage(query);
			chatStore.addMessage({
				role: 'assistant',
				content: response.message,
			});

			if (response.requiresForm) {
				await goto(resolve('/leave'));
			}
		} catch (error) {
			const message = error instanceof Error ? error.message : 'Something went wrong.';
			chatStore.setError(message);

			chatStore.addMessage({
				role: 'assistant',
				content: 'Sorry, I could not process your request. Please try again.',
			});
		}
	}
</script>

<!-- Message input footer -->
<form on:submit|preventDefault={handleSending} class="mx-auto flex max-w-4xl items-center gap-3">
	<!-- Message input -->
	<textarea
		use:autoResize
		bind:value={messageText}
		on:keydown={handleKeyDown}
		placeholder="Enter queries"
		class="input-field max-h-48 flex-1 resize-none overflow-y-auto py-3"
		rows="1"
		autocomplete="off"></textarea>

	<!-- Submit button -->
	<button
		type="submit"
		class="button-primary h-12 shrink-0 px-6 transition-all disabled:cursor-not-allowed disabled:opacity-50"
		disabled={!messageText.trim()}>
		Send
	</button>
</form>
