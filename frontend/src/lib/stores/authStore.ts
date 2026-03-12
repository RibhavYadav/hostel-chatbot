import { writable } from 'svelte/store';
import type { MockStudent, LoginForm, RegisterForm, AuthState } from '$lib/types';

// Initial user state data
const initialState: AuthState = {
	currentUser: null,
	isLoggedIn: false,
	errorMessage: null,
};

// Mock student test data
const mockStudents: MockStudent[] = [
	{
		registrationNumber: 225890001,
		name: 'Test',
		emailID: 'test.mitblr2022@learner.manipal.edu',
		department: 'Test',
		password: 'test',
	},
];

// Writable store
const authState = writable<AuthState>(initialState);

// Login function
function login(form: LoginForm) {
	// Student identity check through registration number and email ID
	const student = mockStudents.find(
		(s) =>
			s.registrationNumber === form.registrationNumber &&
			s.emailID === form.emailID &&
			s.password === form.password
	);

	// Error message set if the student is not found and login stopped
	if (!student) {
		authState.update((state) => ({
			...state,
			errorMessage: 'Invalid registration number or email ID',
		}));
		return;
	}

	// If found, store is updated with the student data
	const { password: _, ...studentData } = student;
	authState.update((state) => ({
		...state,
		currentUser: studentData,
		isLoggedIn: true,
		errorMessage: null,
	}));
}

// Register function - temporary until backend is connected via API
function register(form: RegisterForm) {
	authState.update((state) => ({
		...state,
		errorMessage: null,
	}));
}

// Logout function
function logout() {
	authState.set(initialState);
}

// Auth store function and export
function createAuthStore() {
	// Only subscribe allows to read the store data
	const { subscribe } = authState;
	return {
		subscribe,
		login,
		register,
		logout,
	};
}

export const authStore = createAuthStore();
