<script lang="ts">
	import { fade } from 'svelte/transition';
</script>

<!-- Assistant showcase -->
<div transition:fade={{ duration: 200 }} class="flex w-full flex-col">
	<!-- Three dot animation -->
	<div class="chat-bubble chat-bubble-assistant flex w-16 items-center gap-1 px-4 py-3">
		<div class="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400"></div>
		<div class="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:0.2s]"></div>
		<div class="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:0.4s]"></div>
	</div>
</div>
