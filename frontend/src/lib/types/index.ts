export interface Student {
	registrationNumber: number;
	name: string;
	emailID: string;
	department: string;
}

export interface MockStudent extends Student {
	password: string;
}

export interface LoginForm {
	registrationNumber: number;
	emailID: string;
	password: string;
}

export interface RegisterForm {
	registrationNumber: number;
	emailID: string;
	password: string;
	confirmPassword: string;
}

export interface AuthState {
	readonly currentUser: Student | null;
	readonly isLoggedIn: boolean;
	readonly errorMessage: string | null;
}

export interface ChatMessage {
	role: 'user' | 'assistant';
	content: string;
	timestamp: Date;
}

export interface Intent {
	tag: string;
	confidence: number;
}

export interface BotResponse {
	message: string;
	intent: Intent;
	requiresForm: boolean;
}

export interface ChatState {
	readonly messages: ChatMessage[];
	readonly isTyping: boolean;
	readonly errorMessage: string | null;
}
