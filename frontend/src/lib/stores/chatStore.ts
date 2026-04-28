import type { ChatMessage, ChatState } from '$lib/types';
import { writable } from 'svelte/store';

/** Initial chat state with no messages, not typing, and no errors. */
const initialStore: ChatState = {
	messages: [],
	isTyping: false,
	errorMessage: null,
};

const chatState = writable<ChatState>(initialStore);

/**
 * Adds a new message to the chat store.
 * Automatically attaches the current timestamp to the message.
 * Accepts a ChatMessage without the timestamp field - the store
 * generates it so callers never need to provide it manually.
 */
function addMessage(message: Omit<ChatMessage, 'timestamp'>) {
	const newMessage: ChatMessage = {
		...message,
		timestamp: new Date(),
	};

	chatState.update((state) => ({
		...state,
		messages: [...state.messages, newMessage],
	}));
}

/**
 * Removes all messages from the chat store and resets typing to false.
 * Used when the student logs out or navigates away from the chat page.
 */
function clearMessages() {
	chatState.update((state) => ({
		...state,
		messages: [],
		isTyping: false,
	}));
}

/**
 * Sets the typing indicator state.
 * Pass true when waiting for a bot response to show the loading indicator.
 * Pass false when the response has arrived or an error occurred.
 */
function setTyping(typing: boolean) {
	chatState.update((state) => ({
		...state,
		isTyping: typing,
	}));
}

/**
 * Sets an error message in the chat store.
 * Called when a sendMessage API call fails.
 * Leaves existing messages and typing state unchanged.
 */
function setError(message: string): void {
	chatState.update((state) => ({ ...state, errorMessage: message }));
}

/**
 * Svelte store for chat session state.
 * Subscribe to read messages, isTyping, and errorMessage reactively.
 * Use addMessage to append user or assistant messages.
 * Use setTyping to control the loading indicator.
 * Use setError to surface API failures to the UI.
 * Use clearMessages to reset the chat on logout.
 */
function createChatStore() {
	const { subscribe } = chatState;
	return {
		subscribe,
		addMessage,
		clearMessages,
		setTyping,
		setError,
	};
}

export const chatStore = createChatStore();
