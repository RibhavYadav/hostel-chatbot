import { requireStudentAuth } from '$lib/guards';

export const ssr = false;
export function load() { requireStudentAuth(); }