<script lang="ts">
	import { onMount } from 'svelte';
	import {
		adminListDocuments,
		adminUploadDocument,
		adminDeleteDocument,
		adminAnalyzeDocument,
		adminApplySuggestions,
	} from '$lib/services/api';
	import { adminAuthStore } from '$lib/stores/adminAuthStore';
	import type { DocumentInfo, IntentSuggestion, SuggestionResult } from '$lib/services/api';

	// State
	let documents: DocumentInfo[] = [];
	let isLoadingDocs = true;
	let isUploading = false;
	let isAnalyzing = false;
	let isApplying = false;
	let openSuggestionTag: string | null = null;

	let selectedFile: File | null = null;
	let analyzingFilename: string | null = null;
	let suggestionResult: SuggestionResult | null = null;
	let editableSuggestions: Record<string, IntentSuggestion[]> = {};

	let errorMessage: string | null = null;
	let successMessage: string | null = null;

	// Available intent tags for the dropdown
	$: availableTags = suggestionResult ? Object.keys(suggestionResult.intents) : [];

	// Load documents

	/** Loads the list of uploaded PDF documents on mount. */
	onMount(async () => {
		await loadDocuments();
	});

	async function loadDocuments() {
		try {
			documents = await adminListDocuments();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to load documents.';
		} finally {
			isLoadingDocs = false;
		}
	}

	// Upload

	/** Handles PDF file selection from the file input. */
	function handleFileSelect(event: Event) {
		const input = event.target as HTMLInputElement;
		selectedFile = input.files?.[0] ?? null;
	}

	/** Uploads the selected PDF file to the documents directory. */
	async function handleUpload() {
		if (!selectedFile) return;
		errorMessage = null;
		successMessage = null;
		isUploading = true;

		try {
			await adminUploadDocument(selectedFile);
			successMessage = `${selectedFile.name} uploaded successfully.`;
			selectedFile = null;
			await loadDocuments();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Upload failed.';
		} finally {
			isUploading = false;
		}
	}

	// Delete

	/** Deletes a PDF after confirmation. */
	async function handleDelete(filename: string) {
		if (!confirm(`Delete ${filename}? This cannot be undone.`)) return;
		errorMessage = null;
		successMessage = null;

		try {
			await adminDeleteDocument(filename);
			successMessage = `${filename} deleted.`;
			await loadDocuments();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Delete failed.';
		}
	}

	// Analyze

	/**
	 * Runs the intent suggestion pipeline on the selected PDF.
	 * Populates editableSuggestions for review after completion.
	 */
	async function handleAnalyze(filename: string) {
		errorMessage = null;
		successMessage = null;
		isAnalyzing = true;
		analyzingFilename = filename;
		suggestionResult = null;
		editableSuggestions = {};

		try {
			const result = await adminAnalyzeDocument(filename);
			suggestionResult = result;
			// Deep copy to not mutate the original result
			editableSuggestions = JSON.parse(JSON.stringify(result.intents));
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Analysis failed.';
		} finally {
			isAnalyzing = false;
		}
	}

	// Apply

	/**
	 * Flattens all editable suggestions into a single list and sends
	 * accepted ones to the backend for writing to intents.json.
	 */
	async function handleApply() {
		errorMessage = null;
		successMessage = null;
		isApplying = true;

		const allSuggestions: IntentSuggestion[] = Object.values(editableSuggestions).flat();

		try {
			const result = await adminApplySuggestions(allSuggestions);
			successMessage = `${result.patternsAdded} patterns and ${result.responsesAdded} responses added. ${result.skipped} duplicates skipped.`;
			suggestionResult = null;
			editableSuggestions = {};
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to apply suggestions.';
		} finally {
			isApplying = false;
		}
	}

	/** Returns the count of accepted suggestions across all intents. */
	function acceptedCount(): number {
		return Object.values(editableSuggestions)
			.flat()
			.filter((s) => s.accepted).length;
	}

	/** Formats file size in KB or MB for display. */
	function formatSize(bytes: number): string {
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}

	/** Toggles the suggestion accordion for an intent group. */
	function toggleSuggestionTag(tag: string) {
		openSuggestionTag = openSuggestionTag === tag ? null : tag;
	}

	/** Returns accepted count for a specific intent tag. */
	function acceptedCountForTag(tag: string): number {
		return (editableSuggestions[tag] ?? []).filter((s) => s.accepted).length;
	}
</script>

<div class="space-y-8">
	<h1 class="text-2xl font-bold text-slate-900">Documents</h1>

	{#if errorMessage}
		<p class="text-sm text-red-500">{errorMessage}</p>
	{/if}
	{#if successMessage}
		<p class="text-sm text-green-600">{successMessage}</p>
	{/if}

	<!-- Document List -->
	<div class="space-y-4 rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
		<div class="flex items-center justify-between">
			<h2 class="text-lg font-semibold text-slate-800">Uploaded Documents</h2>
		</div>

		<!-- Upload -->
		<div class="flex items-center gap-3">
			<input type="file" accept=".pdf" id="fileInput" class="hidden" onchange={handleFileSelect} />
			<label
				for="fileInput"
				class="cursor-pointer rounded-lg border border-dashed border-slate-300 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50">
				{selectedFile ? selectedFile.name : 'Choose PDF file'}
			</label>
			{#if selectedFile}
				<button
					class="button-primary px-4 py-2 text-sm disabled:opacity-50"
					onclick={handleUpload}
					disabled={isUploading}>
					{isUploading ? 'Uploading...' : 'Upload'}
				</button>
			{/if}
		</div>

		<!-- Document list -->
		{#if isLoadingDocs}
			<p class="text-sm text-slate-500">Loading documents...</p>
		{:else if documents.length === 0}
			<p class="text-sm text-slate-500">No documents uploaded yet.</p>
		{:else}
			<div class="space-y-2">
				{#each documents as doc}
					<div
						class="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3">
						<div>
							<p class="text-sm font-medium text-slate-800">{doc.filename}</p>
							<p class="text-xs text-slate-400">{formatSize(doc.size)}</p>
						</div>
						<div class="flex gap-2">
							<button
								class="rounded-lg bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 disabled:opacity-50"
								onclick={() => handleAnalyze(doc.filename)}
								disabled={isAnalyzing}>
								{isAnalyzing && analyzingFilename === doc.filename ? 'Analyzing...' : 'Analyze'}
							</button>
							<button
								class="rounded-lg bg-red-50 px-3 py-1 text-xs font-semibold text-red-700 hover:bg-red-100"
								onclick={() => handleDelete(doc.filename)}>
								Delete
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Suggestions Review -->
	{#if suggestionResult !== null}
		<div class="space-y-4 rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
			<div class="flex items-center justify-between">
				<div>
					<h2 class="text-lg font-semibold text-slate-800">
						Suggestions from {analyzingFilename}
					</h2>
					<p class="text-sm text-slate-500">
						{suggestionResult.totalSuggestions} suggestions found.
						{acceptedCount()} selected.
					</p>
				</div>
				<button
					class="button-primary px-4 py-2 text-sm disabled:opacity-50"
					onclick={handleApply}
					disabled={isApplying || acceptedCount() === 0}>
					{isApplying ? 'Applying...' : `Apply ${acceptedCount()} Selected`}
				</button>
			</div>

			<!-- Suggestions grouped by intent -->
			{#each Object.entries(editableSuggestions) as [tag, suggestions]}
				<div class="rounded-xl border border-slate-200">
					<!-- Accordion header -->
					<button
						class="flex w-full items-center justify-between px-4 py-3 text-left"
						onclick={() => toggleSuggestionTag(tag)}>
						<div class="flex items-center gap-3">
							<span class="text-sm font-semibold tracking-wide text-indigo-700 uppercase">
								{tag}
							</span>
							<span class="text-xs text-slate-400">{suggestions.length} suggestions</span>
							{#if acceptedCountForTag(tag) > 0}
								<span
									class="rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-semibold text-indigo-700">
									{acceptedCountForTag(tag)} selected
								</span>
							{/if}
						</div>
						<span class="text-sm text-slate-400">
							{openSuggestionTag === tag ? '▲' : '▼'}
						</span>
					</button>

					<!-- Accordion body -->
					{#if openSuggestionTag === tag}
						<div class="space-y-2 border-t border-slate-100 px-4 py-3">
							{#each suggestions as suggestion, i}
								<div
									class="flex items-start gap-3 rounded-lg border border-slate-200 p-3
                        {suggestion.accepted ? 'border-indigo-200 bg-indigo-50' : ''}">
									<input
										type="checkbox"
										id="accept-{tag}-{i}"
										bind:checked={suggestion.accepted}
										class="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600" />
									<div class="flex-1 space-y-2">
										<p class="text-sm text-slate-800">{suggestion.sentence}</p>
										<div class="flex flex-wrap items-center gap-3">
											<span class="text-xs text-slate-400">
												{(suggestion.similarity * 100).toFixed(1)}% match
											</span>
											<div class="flex items-center gap-1">
												<label for="intent-{tag}-{i}" class="text-xs text-slate-500">Intent:</label>
												<select
													id="intent-{tag}-{i}"
													bind:value={suggestion.suggestedIntent}
													class="rounded border border-slate-200 px-2 py-0.5 text-xs text-slate-700">
													{#each Object.keys(editableSuggestions) as t}
														<option value={t}>{t}</option>
													{/each}
												</select>
											</div>
											<div class="flex items-center gap-1">
												<label for="type-{tag}-{i}" class="text-xs text-slate-500">Type:</label>
												<select
													id="type-{tag}-{i}"
													bind:value={suggestion.type}
													class="rounded border border-slate-200 px-2 py-0.5 text-xs text-slate-700">
													<option value="pattern">Pattern</option>
													<option value="response">Response</option>
												</select>
											</div>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>
