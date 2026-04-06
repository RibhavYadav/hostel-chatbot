export interface Student {
	registrationNumber: number;
	name: string;
	emailID: string;
	department: string;
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

export interface ChatState {
	readonly messages: ChatMessage[];
	readonly isTyping: boolean;
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

export interface TokenResponse {
	access_token: string;
	token_type: string;
	student: Student;
}

export interface LeaveRequest {
	departureDate: string;
	returnDate: string;
	reason: string;
}

export interface LeaveResponse {
	id: number;
	studentId: number;
	departureDate: string;
	returnDate: string;
	reason: string;
	status: 'pending' | 'approved' | 'rejected';
	submittedAt: string;
}

export interface Admin {
	emailID: string;
	adminTeam: 'cso' | 'warden' | 'it';
}

export interface AdminTokenResponse {
	access_token: string;
	token_type: string;
	admin: Admin;
}

export interface AdminAuthState {
	readonly currentAdmin: Admin | null;
	readonly isLoggedIn: boolean;
	readonly errorMessage: string | null;
}

export interface AdminRegisterForm {
	emailID: string;
	adminTeam: string;
	password: string;
	confirmPassword: string;
}

export interface AdminLoginForm {
	emailID: string;
	password: string;
}

export interface ChatLogEntry {
	id: number;
	studentId: number;
	message: string;
	predictedTag: string;
	confidence: number;
	botResponse: string;
	timestamp: string;
	promoted: boolean;
}

export interface IntentEntry {
	tag: string;
	patterns: string[];
	responses: string[];
}
