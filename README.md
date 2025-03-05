# **AshBot: A Mischievous Fae-Witch Discord Bot**

![AshBot]
*A lively, mischievous, queer fae-witch powered by AI & Weaviate memory storage.*

---

## **📌 Overview**
AshBot is a **Discord bot** designed to be an immersive AI companion. She remembers users, responds with personality, and interacts in a **playful, goblin-core, tea-loving** style. **Memory is now stored in Weaviate**, allowing AshBot to recall past conversations across multiple interactions.

---

## **⚡ Features**
- **Weaviate-Powered Memory** → Remembers user details and past interactions.
- **OpenAI GPT-4 Chat** → Provides responses based on memory & recent messages.
- **Role Management** → Can assign or deny roles playfully.
- **Debugging Integration** → Sends logs to a dedicated Discord debug channel.
- **Batch Script Startups** → Easy launching via `START.bat` & `STARTwWatchdog.bat`.

---

## **🛠️ Setup Instructions**

### **1️⃣ Install Required Software**
Ensure you have the following installed:

- **[Python 3.12+](https://www.python.org/downloads/)**
- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**
- **[Git](https://git-scm.com/downloads)**
- **Weaviate Docker Image** (for long-term memory storage)

---

### **2️⃣ Clone the Repository**
```sh
git clone https://github.com/yourusername/AshBot.git
cd AshBot
```

---

### **3️⃣ Set Up the Virtual Environment**
```sh
python -m venv .venv
source .venv/bin/activate  # For macOS/Linux
.\.venv\Scripts\activate   # For Windows
```
Then install dependencies:
```sh
pip install -r requirements.txt
```

---

### **4️⃣ Run Weaviate in Docker**
1. **Open Docker Desktop.**
2. **Pull & Run Weaviate Image:**
   ```sh
   docker run -d --restart=always --name weaviate -p 8080:8080 semitechnologies/weaviate:latest
   ```
3. **Verify Weaviate is Running:**
   ```sh
   docker ps
   ```

---

### **5️⃣ Start AshBot**

**Option 1: Basic Startup**
```sh
./START.bat
```

**Option 2: Auto-Restart with Watchdog**
```sh
./STARTwWatchdog.bat
```
🚀 **AshBot will now run in your Discord server!** 🎉

---

## **🛠️ Configuration**

### **🔹 Environment Variables (`.env`)**
Before running, ensure you set up your `.env` file:
```
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
ASSISTANT_ID=your_openai_assistant_id
WEAVIATE_URL=http://localhost:8080
DEBUG_CHANNEL_ID=1346181778464964760
```

---

## **🔍 Debugging & Logs**

### **🔹 View Logs in Discord Debug Channel**
AshBot sends logs to a **dedicated debug channel**. To check logs:
1. Open your Discord server.
2. Go to the **debug channel** (set in `.env`).
3. Look for messages like:
   ```
   🚀 DEBUG: Ash command received from <username>: <message>
   ✅ Memory saved for user <user_id>.
   ```

### **🔹 Check Weaviate Logs**
To view Weaviate logs, use:
```sh
docker logs weaviate --follow
```

---

## **🛠️ Troubleshooting**

| Issue                           | Solution |
|---------------------------------|----------|
| **Bot is not responding** | Ensure the bot is running (`./START.bat`) and Weaviate is active (`docker ps`). |
| **Memory is not saving** | Check debug logs for errors related to `weaviate_memory.py`. |
| **400 Bad Request (OpenAI)** | Message too long; truncation may need adjustment in `send_to_openai.py`. |

---

## **🤝 Contributing**
Want to improve AshBot? Fork the repo & submit a pull request!

```sh
git checkout -b feature-branch
git add .
git commit -m "Added new feature"
git push origin feature-branch
```

---

## **📜 License**
This project is open-source under the **MIT License**.

---

