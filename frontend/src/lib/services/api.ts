import axios from 'axios';
import type { BotResponse, LeaveRequest } from '$lib/types';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const client = axios.create({
	baseURL: BASE_URL,
	headers: { 'Content-Type': 'application/json' }
});

export async function sendMessage(message: string): Promise<BotResponse> {
	const response = await client.post('/chat', { message });
	return response.data;
}

export async function submitLeaveRequest(request: LeaveRequest): Promise<void> {
	await client.post('/leave', request);
}
