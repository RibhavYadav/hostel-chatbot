<script lang="ts">
	import { chatStore } from '$lib/stores/chatStore';

	let messageText = '';
	let textAreaElement: HTMLTextAreaElement;

	// Input area resize
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

	// Text sending
	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSending();
		}
	}

	// User message handling and sending
	async function handleSending() {
		// Message trimming and returning if the message is empty
		const content = messageText.trim();
		if (!content) return;

		// Adding user message to the chat store
		chatStore.addMessage({
			role: 'user',
			content: content,
		});

		// Message set to empty
		messageText = '';
		chatStore.setTyping(true);

		// Reset height after clearing text
		if (textAreaElement) {
			textAreaElement.style.height = 'auto';
		}

		// Message sent to the bot for response
		try {
			await botResponse(content);
		} finally {
			// Indicator turned off after the bot response
			chatStore.setTyping(false);
		}
	}

	// Bot response to the user query
	async function botResponse(query: string) {
		// 1.5 seconds delay
		await new Promise((done) => setTimeout(done, 1500));

		// Adding bot response to the chat store
		chatStore.addMessage({
			role: 'assistant',
			content: `Response to "${query}"`,
		});
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
