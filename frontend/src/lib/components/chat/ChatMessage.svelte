<script lang="ts">
	import type { ChatMessage } from '$lib/types';

	export let message: ChatMessage;
	$: isUser = message.role === 'user';
</script>

<div class="flex w-full flex-col">
	<div class="chat-bubble {isUser ? 'chat-bubble-user' : 'chat-bubble-assistant'}">
		<p class="leading-relaxed whitespace-pre-wrap">{message.content}</p>
		{#if message.timestamp}
			<span class="mt-1 block text-[10px] opacity-70 {isUser ? 'text-right' : 'text-left'}">
				{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
			</span>
		{/if}
	</div>
</div>
