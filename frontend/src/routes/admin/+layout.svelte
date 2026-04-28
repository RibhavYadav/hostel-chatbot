<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { adminAuthStore } from '$lib/stores/adminAuthStore';
	import { logoutAdmin } from '$lib/services/adminAuthService';

	let { children } = $props();
	const publicPaths = ['/admin/login', '/admin/register'];

	/** Logs out the admin and redirects to the admin login page. */
	async function handleLogout() {
		await logoutAdmin();
		await goto(resolve('/admin/login'));
	}

	/** Returns true if the current admin team has access to the given teams list. */
	function canAccess(...teams: string[]): boolean {
		return teams.includes($adminAuthStore.currentAdmin?.adminTeam ?? '');
	}
</script>

<!-- Skip layout for login and register pages -->
{#if !$adminAuthStore.isLoggedIn || publicPaths.includes(page.url.pathname)}
	{@render children()}
{:else}
	<div class="flex min-h-screen bg-slate-50">
		<!-- Sidebar -->
		<aside
			class="flex h-screen w-56 shrink-0 flex-col overflow-y-auto border-r border-slate-200 bg-white p-4 shadow-sm">
			<!-- Brand -->
			<div class="mb-6">
				<h1 class="text-lg font-bold text-slate-900">Admin Portal</h1>
				<p class="truncate text-xs text-slate-500">{$adminAuthStore.currentAdmin?.emailID}</p>
				<span
					class="mt-1 inline-block rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-semibold text-indigo-700 uppercase">
					{$adminAuthStore.currentAdmin?.adminTeam}
				</span>
			</div>

			<!-- Navigation -->
			<nav class="flex flex-1 flex-col gap-1">
				<a
					href={resolve('/admin/dashboard')}
					class="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
					Dashboard
				</a>

				{#if canAccess('cso', 'it')}
					<a
						href={resolve('/admin/chat-logs')}
						class="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
						Chat Logs
					</a>
					<a
						href={resolve('/admin/intents')}
						class="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
						Intents
					</a>
				{/if}

				{#if canAccess('cso', 'warden')}
					<a
						href={resolve('/admin/leave')}
						class="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
						Leave Requests
					</a>
				{/if}

				{#if canAccess('cso', 'it')}
					<a
						href={resolve('/admin/documents')}
						class="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
						Documents
					</a>
				{/if}
			</nav>

			<!-- Profile -->
			<a
				href={resolve('/admin/profile')}
				class="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
				Profile
			</a>

			<!-- Logout -->
			<button
				class="mt-4 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
				onclick={handleLogout}>
				Logout
			</button>
		</aside>

		<!-- Page content -->
		<main class="flex-1 overflow-y-auto p-6">
			{@render children()}
		</main>
	</div>
{/if}
