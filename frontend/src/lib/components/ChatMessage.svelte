<script lang="ts">
	import type { ChatMessage } from '$lib/types';

	// User and assistant message
	export let message: ChatMessage;
	$: isUser = message.role === 'user';
</script>

<!-- Chat showcase -->
<div class="flex w-full flex-col">
	<!-- Message alignment based on the sender -->
	<div class="chat-bubble {isUser ? 'chat-bubble-user' : 'chat-bubble-assistant'}">
		<p class="leading-relaxed whitespace-pre-wrap">
			{message.content}
		</p>

		<!-- Message timestamp showcase -->
		{#if message.timestamp}
			<span class="mt-1 block text-[10px] opacity-70 {isUser ? 'text-right' : 'text-left'}">
				{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
			</span>
		{/if}
	</div>
</div>
