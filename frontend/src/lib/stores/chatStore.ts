import { writable } from 'svelte/store';
import type { ChatMessage, ChatState } from '$lib/types';

// Initial chat data
const initialStore: ChatState = {
	messages: [],
	isTyping: false,
	errorMessage: null,
};

// Writable store
const chatState = writable<ChatState>(initialStore);

// Add new messages
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

// Remove messages
function clearMessages() {
	chatState.update((state) => ({
		...state,
		messages: [],
		isTyping: false,
	}));
}

// Set typing boolean
function setTyping(typing: boolean) {
	chatState.update((state) => ({
		...state,
		isTyping: typing,
	}));
}

// Chat store function
function createChatStore() {
	const { subscribe } = chatState;
	return {
		subscribe,
		addMessage,
		clearMessages,
		setTyping,
	};
}

export const chatStore = createChatStore();
