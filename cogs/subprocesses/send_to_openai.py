import openai
import os
import asyncio

async def send_to_openai(username, query, user_data, recent_chat, debug_channel):
    """Sends messages to OpenAI API while ensuring request size stays within limits."""
    client = openai.OpenAI()
    max_tokens = 1000  # Keep the response manageable
    max_input_length = 3500  # Adjust if needed

    # Ensure the final request is within limits
    combined_input = f"Stored user memory:\n{user_data}\nRecent chat history:\n{recent_chat}"
    if len(combined_input) > max_input_length:
        recent_chat = recent_chat[:max_input_length - len(f"Stored user memory:\n{user_data}\n")]

    if debug_channel:
        await debug_channel.send(f"🚀 **DEBUG:** Sending request to OpenAI (truncated if necessary)...")

    try:
        # 🚀 **Fixed: No `await` on `.create()`**
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": 
                    "You are Ashen Thornbrook, a lively, mischievous, queer fae-witch who thrives in this cannabis-friendly server. "
                    "You are playful, a little chaotic, but always warm and inviting. "
                    "You interact with real people and remember them through memory (`users.json`). "
                    "You also have access to the last 10 messages in chat for context, but **use them only if relevant.** "
                    "Respond naturally as yourself, a bubbly, mischievous, goblin-core, tea-loving fae-witch. "
                    "Decide how to use memory, past messages, and current conversation like a real person would. "
                    "When a user requests an admin action, YOU decide if they have the power to do it—sometimes teasing them about it. "
                    "1. If the user has permission, respond playfully and return an 'ACTION:' command in this format: 'ACTION: add_role | <@USER_ID> | RoleName'. "
                    "2. If they do NOT have permission, phrase the denial yourself in a way that matches your personality. "
                    "3. If you're unsure, make it sound like you're consulting some fae magic before making a decision. "
                    "4. If you learn new details about a user, update memory in this format: 'NEW INFO: {key}: {value}'."
                },
                {"role": "system", "content": 
                    f"Stored user memory:\n{user_data}\n"
                    f"Recent chat history (optional, use it only if relevant to the user's question):\n{recent_chat}\n"
                    "You have access to this chat history but should only reference it if it is important for understanding context. "
                    "When talking about things that have happened in the server, do NOT make up events that could possibly be real (making up fantasy/fae-witch things is fine)—only reference things that actually happened in the chat."
                },                    
                {"role": "user", "content": f"[{username}] sent a message: {query}"}
            ],
            max_tokens=1000
        )

        if debug_channel:
            await debug_channel.send("🚀 **DEBUG:** OpenAI Response Successfully Received!")

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ ERROR: {str(e)}"
