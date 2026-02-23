import { writable } from 'svelte/store';
import type { ChatMessage, LeaveRequest } from '$lib/types';

export const messages = writable<ChatMessage[]>([]);
export const leaveRequest = writable<LeaveRequest | null>(null);
export const isLoading = writable<boolean>(false);
