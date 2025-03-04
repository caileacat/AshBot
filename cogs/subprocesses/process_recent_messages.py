async def process_recent_messages(interaction, debug_channel):
    """Retrieve and format the last 10 messages from the channel while keeping them under the 4000-character limit."""
    channel_messages = []
    max_length = 3500  # Leave space for system messages and user query

    try:
        async for message in interaction.channel.history(limit=10):
            author_name = "Ash Thornbrook (YOU)" if message.author == interaction.client.user else message.author.display_name
            message_content = f"{author_name}: {message.content}"

            # Ensure we don't exceed max length
            if len("\n".join(channel_messages)) + len(message_content) > max_length:
                break

            channel_messages.append(message_content)

        processed_chat = "\n".join(reversed(channel_messages)) if channel_messages else "No messages retrieved."

        if debug_channel:
            await debug_channel.send(f"📜 **DEBUG:** Retrieved and processed messages (truncated if necessary):\n```\n{processed_chat}\n```")

        return processed_chat
    except Exception as e:
        error_msg = f"❌ ERROR: Failed to retrieve messages: {str(e)}"
        if debug_channel:
            await debug_channel.send(error_msg)
        return error_msg
