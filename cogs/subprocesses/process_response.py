async def process_response(interaction, username, query, ash_reply, debug_channel):
    """Formats and sends the final response."""
    
    # ✅ Remove NEW INFO lines
    cleaned_response = []
    for line in ash_reply.split("\n"):
        if not line.startswith("NEW INFO:"):
            cleaned_response.append(line)
    
    ash_reply = "\n".join(cleaned_response).strip()

    final_response = f"**{username}:**\n{query}\n──────────────────────────\n{ash_reply}"

    if debug_channel:
        await debug_channel.send(f"📜 **DEBUG:** Final response being sent:\n```\n{final_response}\n```")

    return final_response
