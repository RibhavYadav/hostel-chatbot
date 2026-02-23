export interface Student {
	id: string;
	name: string;
	roomNumber: string;
	department: string;
}

export interface ChatMessage {
	role: 'user' | 'assistant';
	content: string;
	timestamp: Date;
}

export interface LeaveRequest {
	studentId: string;
	startDate: string;
	endDate: string;
	reason: string;
	status: 'pending' | 'approved' | 'rejected';
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
