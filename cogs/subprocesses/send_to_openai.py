import openai
import os
import json
import textwrap

async def send_to_openai(username, query, user_memory, recent_chat, debug_channel):
    """Sends messages to OpenAI API while ensuring request size stays within limits."""
    client = openai.OpenAI()
    max_tokens = 1000  # ✅ Keep response manageable
    max_input_length = 1800  # ✅ Ensure message stays within Discord's 2000-character limit

    # ✅ Convert memory to JSON format and truncate properly
    user_memory_json = json.dumps(user_memory, ensure_ascii=False)
    
    # ✅ Ensure recent_chat is a string and truncate correctly
    chat_lines = recent_chat.split("\n")[-10:]  # ✅ Keep only the last 10 messages
    chat_history_str = "\n".join(chat_lines)

    # ✅ Ensure the combined input fits within limits
    combined_input = f"Stored user memory:\n{user_memory_json}\nRecent chat history:\n{chat_history_str}"
    if len(combined_input) > max_input_length:
        excess = len(combined_input) - max_input_length
        chat_history_str = textwrap.shorten(chat_history_str, width=len(chat_history_str) - excess, placeholder="...")
        debug_truncation = f"⚠️ **Truncated chat history to fit within {max_input_length} characters.**"
        print(debug_truncation)
        if debug_channel:
            await debug_channel.send(debug_truncation)

    if debug_channel:
        await debug_channel.send("🚀 **DEBUG:** Sending request to OpenAI (truncated if necessary)...")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": 
                    "You are Ashen Thornbrook, a lively, mischievous, queer fae-witch who thrives in this cannabis-friendly server. "
                    "You are playful, a little chaotic, but always warm and inviting. "
                    "You interact with real people and remember them through Weaviate. "
                    "You also have access to the last 10 messages in chat for context, but **use them only if relevant.** "
                    "Respond naturally as yourself, a bubbly, mischievous, goblin-core, tea-loving fae-witch."
                    "Decide how to use memory, past messages, and current conversation like a real person would. "
                    "When a user requests an admin action, YOU decide if they have the power to do it—sometimes teasing them about it. "
                    "1. If the user has permission, respond playfully and return an 'ACTION:' command in this format: 'ACTION: add_role | <@USER_ID> | RoleName'. "
                    "2. If they do NOT have permission, phrase the denial yourself in a way that matches your personality. "
                    "3. If you're unsure, make it sound like you're consulting some fae magic before making a decision. "
                    "4. If you learn new details about a user, update memory in this format: 'NEW INFO: {key}: {value}'."
                },
                {"role": "system", "content": 
                    f"Stored user memory:\n{user_memory_json}\n"
                    f"Recent chat history (truncated if needed):\n{chat_history_str}\n"
                },
                {"role": "user", "content": f"[{username}] sent a message: {query}"}
            ],
            max_tokens=1000
        )

        if debug_channel:
            await debug_channel.send("🚀 **DEBUG:** OpenAI Response Successfully Received!")

        return response.choices[0].message.content.strip()
    except Exception as e:
        error_msg = f"❌ ERROR: {str(e)}"
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)
        return error_msg
