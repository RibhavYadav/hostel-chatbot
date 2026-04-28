<script lang="ts">
	import { onMount } from 'svelte';
	import {
		adminGetIntents,
		adminCreateIntent,
		adminUpdateIntent,
		adminDeleteIntent,
	} from '$lib/services/api';
	import { adminAuthStore } from '$lib/stores/adminAuthStore';
	import type { IntentEntry } from '$lib/services/api';

	let intents: IntentEntry[] = [];
	let isLoading = true;
	let errorMessage: string | null = null;
	let successMessage: string | null = null;

	// New intent form state
	let showCreateForm = false;
	let newTag = '';
	let newPatterns = '';
	let newResponses = '';
	let isCreating = false;

	// Edit form state. Only one intent editable at a time
	let editingTag: string | null = null;
	let editPatterns = '';
	let editResponses = '';
	let isSaving = false;

	/** Loads all intents on mount. */
	onMount(async () => {
		try {
			intents = await adminGetIntents();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to load intents.';
		} finally {
			isLoading = false;
		}
	});

	/**
	 * Converts a comma-separated string into a trimmed string array.
	 * Filters out empty strings that result from trailing commas.
	 */
	function parseList(input: string): string[] {
		return input
			.split(',')
			.map((s) => s.trim())
			.filter((s) => s.length > 0);
	}

	/**
	 * Submits the new intent form.
	 * Validates that tag, patterns, and responses are all provided.
	 * Appends the new intent to the local list on success.
	 */
	async function handleCreate() {
		errorMessage = null;
		successMessage = null;

		if (!newTag.trim()) {
			errorMessage = 'Please enter a tag name.';
			return;
		}
		const patterns = parseList(newPatterns);
		const responses = parseList(newResponses);

		if (patterns.length === 0) {
			errorMessage = 'Please enter at least one pattern.';
			return;
		}
		if (responses.length === 0) {
			errorMessage = 'Please enter at least one response.';
			return;
		}

		isCreating = true;
		try {
			await adminCreateIntent(newTag.trim(), patterns, responses);
			intents = [...intents, { tag: newTag.trim(), patterns, responses }];
			newTag = '';
			newPatterns = '';
			newResponses = '';
			showCreateForm = false;
			successMessage = 'Intent created successfully.';
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to create intent.';
		} finally {
			isCreating = false;
		}
	}

	/** Opens the edit form for an intent, pre-filling current values. */
	function openEdit(intent: IntentEntry) {
		editingTag = intent.tag;
		editPatterns = intent.patterns.join(', ');
		editResponses = intent.responses.join(', ');
	}

	/**
	 * Saves edits to an existing intent.
	 * Updates the local intent entry on success without a full reload.
	 */
	async function handleSave(tag: string) {
		errorMessage = null;
		successMessage = null;
		isSaving = true;

		const patterns = parseList(editPatterns);
		const responses = parseList(editResponses);

		try {
			await adminUpdateIntent(tag, patterns, responses);
			intents = intents.map((i) => (i.tag === tag ? { ...i, patterns, responses } : i));
			editingTag = null;
			successMessage = `Intent '${tag}' updated successfully.`;
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to update intent.';
		} finally {
			isSaving = false;
		}
	}

	/**
	 * Deletes an intent after confirmation.
	 * Removes the intent from the local list on success.
	 * Only available to cso team.
	 */
	async function handleDelete(tag: string) {
		if (!confirm(`Delete intent '${tag}'? This cannot be undone.`)) return;
		errorMessage = null;
		successMessage = null;

		try {
			await adminDeleteIntent(tag);
			intents = intents.filter((i) => i.tag !== tag);
			successMessage = `Intent '${tag}' deleted.`;
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to delete intent.';
		}
	}

	const isCso = $adminAuthStore.currentAdmin?.adminTeam === 'cso';
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold text-slate-900">Intents</h1>
		<button
			class="button-primary px-4 py-2 text-sm"
			onclick={() => (showCreateForm = !showCreateForm)}>
			{showCreateForm ? 'Cancel' : 'Add Intent'}
		</button>
	</div>

	{#if errorMessage}
		<p class="text-sm text-red-500">{errorMessage}</p>
	{/if}
	{#if successMessage}
		<p class="text-sm text-green-600">{successMessage}</p>
	{/if}

	<!-- Create form -->
	{#if showCreateForm}
		<div class="space-y-4 rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
			<h2 class="text-lg font-semibold text-slate-800">New Intent</h2>

			<div>
				<label for="newTag" class="mb-1 block text-sm font-medium text-slate-700">Tag</label>
				<input
					type="text"
					id="newTag"
					bind:value={newTag}
					placeholder="e.g. hostel_wifi"
					class="input-field" />
			</div>

			<div>
				<label for="newPatterns" class="mb-1 block text-sm font-medium text-slate-700">
					Patterns <span class="text-slate-400">(comma separated)</span>
				</label>
				<textarea
					id="newPatterns"
					bind:value={newPatterns}
					placeholder="wifi not working, internet issue, no internet in room"
					class="input-field resize-none"
					rows="3">
				</textarea>
			</div>

			<div>
				<label for="newResponses" class="mb-1 block text-sm font-medium text-slate-700">
					Responses <span class="text-slate-400">(comma separated)</span>
				</label>
				<textarea
					id="newResponses"
					bind:value={newResponses}
					placeholder="Please contact the IT desk., WiFi issues can be reported at the office."
					class="input-field resize-none"
					rows="3">
				</textarea>
			</div>

			<button
				class="button-primary px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
				onclick={handleCreate}
				disabled={isCreating}>
				{isCreating ? 'Creating...' : 'Create Intent'}
			</button>
		</div>
	{/if}

	<!-- Intent list -->
	{#if isLoading}
		<p class="text-sm text-slate-500">Loading intents...</p>
	{:else if intents.length === 0}
		<p class="text-sm text-slate-500">No intents found.</p>
	{:else}
		<div class="space-y-3">
			{#each intents as intent}
				<div class="space-y-3 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
					<!-- Intent header -->
					<div class="flex items-center justify-between">
						<div>
							<span class="font-semibold text-slate-800">{intent.tag}</span>
							<span class="ml-3 text-xs text-slate-400">
								{intent.patterns.length} patterns · {intent.responses.length} responses
							</span>
						</div>
						<div class="flex gap-2">
							<button
								class="rounded-lg bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-200"
								onclick={() =>
									editingTag === intent.tag ? (editingTag = null) : openEdit(intent)}>
								{editingTag === intent.tag ? 'Cancel' : 'Edit'}
							</button>
							{#if isCso}
								<button
									class="rounded-lg bg-red-50 px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-100"
									onclick={() => handleDelete(intent.tag)}>
									Delete
								</button>
							{/if}
						</div>
					</div>

					<!-- Edit form -->
					{#if editingTag === intent.tag}
						<div class="space-y-3 border-t border-slate-100 pt-3">
							<div>
								<label
									for="editPatterns-{intent.tag}"
									class="mb-1 block text-sm font-medium text-slate-700">
									Patterns <span class="text-slate-400">(comma separated)</span>
								</label>
								<textarea
									id="editPatterns-{intent.tag}"
									bind:value={editPatterns}
									class="input-field resize-none"
									rows="3">
								</textarea>
							</div>
							<div>
								<label
									for="editResponses-{intent.tag}"
									class="mb-1 block text-sm font-medium text-slate-700">
									Responses <span class="text-slate-400">(comma separated)</span>
								</label>
								<textarea
									id="editResponses-{intent.tag}"
									bind:value={editResponses}
									class="input-field resize-none"
									rows="3">
								</textarea>
							</div>
							<button
								class="button-primary px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
								onclick={() => handleSave(intent.tag)}
								disabled={isSaving}>
								{isSaving ? 'Saving...' : 'Save Changes'}
							</button>
						</div>
					{:else}
						<!-- Read only preview -->
						<div class="space-y-2 border-t border-slate-100 pt-3">
							<p class="text-xs font-medium text-slate-500">Patterns</p>
							<div class="flex flex-wrap gap-1">
								{#each intent.patterns as pattern}
									<span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
										{pattern}
									</span>
								{/each}
							</div>
							<p class="mt-2 text-xs font-medium text-slate-500">Responses</p>
							<div class="space-y-1">
								{#each intent.responses as response, i}
									<p class="text-xs text-slate-600">{i + 1}. {response}</p>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>
