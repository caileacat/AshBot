async def process_response(interaction, username, query, ash_reply, debug_channel):
    """Formats and sends the final response while respecting Discord’s message limits."""
    if not ash_reply:
        return "❌ Oops, I seem to have lost my words! Try again?"

    max_discord_length = 4000  # Ensure we respect Discord’s character limit

    # Ensure response is within limits
    formatted_response = f"**{username}:**\n{query}\n──────────────────────────\n{ash_reply}"
    if len(formatted_response) > max_discord_length:
        formatted_response = formatted_response[:max_discord_length - 50] + "\n...(truncated for length)"

    if debug_channel:
        await debug_channel.send(f"📜 **DEBUG:** Final response being sent:\n```\n{formatted_response}\n```")

    await interaction.followup.send(formatted_response)  # Ensure it's awaited

    return formatted_response
