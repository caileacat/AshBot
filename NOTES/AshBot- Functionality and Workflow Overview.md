# **AshBot: Functionality & Workflow Overview**

## **1. User Interaction & Context Gathering**
When a user messages Ash, the bot gathers the necessary data and sends it to Ash for processing. This includes:

- **Who sent the message** (username and user ID).
- **The past 20 messages in the channel** (to maintain conversation context).
- **Ash's memory (`users.json`)**, which contains stored user information.

This allows Ash to recall relevant details about users and actively participate in conversations instead of responding in isolation.

---

## **2. Ash's Response Structure**
AshBot expects Ash’s response to contain up to three key components:

1. **Natural User Response**: A message back to the user that continues the conversation.
2. **Bot Commands**: If Ash determines an admin action needs to happen (e.g., adding/removing a role, banning a user), she includes a formatted command for the bot.
3. **Memory Updates**: Any new information Ash learns about a user is sent back to be stored in `users.json`.

---

## **3. Memory Handling & Updating (`users.json`)**
- AshBot keeps a structured memory in `users.json`.
- New information is **appended at the front** (most recent first).
- **Timestamps** are included to determine if the information is still relevant.
- If old data is no longer relevant, the bot **marks it as outdated** but retains it for reference.
- This system ensures that Ash has an evolving memory of users over time.

---

## **4. Executing Admin Commands**
If Ash includes a command in her response, the bot:

1. **Checks if the user has permission** to perform the action.
2. **Executes the command** if allowed (e.g., adding a role, banning a user).
3. Uses **predefined admin functions** for common tasks (so the bot understands how to handle standard admin actions).
4. Communicates clearly with Ash about **what was performed and what wasn’t**.

---

## **5. Sending the Final Message in the Channel**
The bot structures the message clearly for readability:

- **User’s message to Ash** is shown first.
- A **separator** (`──────────`).
- **Ash’s response** follows.
- If an admin action was performed, a confirmation is included.

---

## **6. Ash's Conversation Awareness**
When receiving conversation history, Ash:
- Recognizes past user messages.
- Understands when an admin action was performed.
- Can follow up naturally based on previous exchanges.

This ensures that Ash feels more like an active presence rather than a disconnected chatbot.

