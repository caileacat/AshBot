# **🚀 Full Guide: Setting Up Weaviate & AshBot on a Free Google Compute Engine (GCE) VM**

## **📌 Overview**
This guide will walk you through **setting up a free Google Compute Engine (GCE) VM** to host both **Weaviate (for memory storage)** and **AshBot (your Discord bot)** so they run 24/7, even when your computer is off.

---
## **📝 Step 1: Set Up a Google Cloud Account**
1. **Go to Google Cloud Console:**  
   👉 [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. **Sign in with a Google account** (or create a new one).
3. **Start your free trial** (if eligible, you get $300 in credits, but we won’t need them).
4. **Enable billing** (Google requires a payment method but will not charge you unless you exceed the free-tier limits).
5. **Create a new project:**  
   - Click **Select a Project** → **New Project**.
   - Name it **AshBot VM** (or anything you like).
   - Click **Create**.

🔹 **Checkpoint:** You now have a working Google Cloud account.

---
## **🖥️ Step 2: Create a Free Virtual Machine (VM)**
1. **Go to Compute Engine:**  
   👉 [https://console.cloud.google.com/compute](https://console.cloud.google.com/compute)
2. **Click "Create Instance."**
3. **Configure the VM:**
   - **Name:** `ashbot-vm`
   - **Region:** Select a free-tier region (e.g., `us-east1` or `us-west1`).
   - **Machine Type:** `e2-micro` (always free-tier eligible).
   - **Boot Disk:**
     - Click **Change** → Select **Ubuntu 22.04 LTS**.
     - Click **Select**.
   - **Firewall:** Check both **Allow HTTP** and **Allow HTTPS**.
4. **Click Create** and wait for the VM to start.

🔹 **Checkpoint:** Your Ubuntu VM is running and ready for setup.

---
## **🔒 Step 3: Configure the VM (Setup SSH, Install Dependencies)**
1. **Connect to the VM via SSH:**
   - In the Google Cloud Console, go to **Compute Engine**.
   - Click **SSH** next to `ashbot-vm`.

2. **Update the System:**  
   ```sh
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install Required Packages:**  
   ```sh
   sudo apt install -y python3 python3-venv python3-pip docker.io git
   ```

4. **Enable Docker to Start on Boot:**  
   ```sh
   sudo systemctl enable --now docker
   ```

🔹 **Checkpoint:** The VM is fully configured and ready for Weaviate.

---
## **📦 Step 4: Install & Run Weaviate (Vector Database)**

1. **Pull the Weaviate Docker Image:**  
   ```sh
   sudo docker pull semitechnologies/weaviate:latest
   ```

2. **Run Weaviate:**  
   ```sh
   sudo docker run -d --restart=always --name weaviate -p 8080:8080 semitechnologies/weaviate:latest
   ```

3. **Check If Weaviate Is Running:**  
   ```sh
   sudo docker ps
   ```
   You should see a running container named **weaviate**.

🔹 **Checkpoint:** Weaviate is now running and ready for use.

---
## **🤖 Step 5: Deploy AshBot**

1. **Clone the AshBot Repository (or Upload Your Code):**  
   ```sh
   git clone https://github.com/yourusername/ashbot.git
   cd ashbot
   ```

2. **Set Up a Python Virtual Environment:**  
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**  
   ```sh
   pip install -r requirements.txt
   ```

4. **Modify `chat.py` to Use Weaviate Instead of JSON:**
   - Update AshBot’s memory system to store & retrieve data from Weaviate instead of `users.json`.
   - Use Weaviate’s API for semantic memory retrieval.

5. **Run AshBot:**  
   ```sh
   python ashBot.py
   ```

🔹 **Checkpoint:** AshBot is now running and connected to Weaviate.

---
## **♻️ Step 6: Keep Everything Running (Auto-Restart on Boot)**
1. **Create a systemd service for Weaviate:**  
   ```sh
   sudo nano /etc/systemd/system/weaviate.service
   ```

   Paste the following:
   ```ini
   [Unit]
   Description=Weaviate Vector Database
   After=network.target

   [Service]
   ExecStart=/usr/bin/docker start weaviate
   ExecStop=/usr/bin/docker stop weaviate
   Restart=always
   User=root

   [Install]
   WantedBy=multi-user.target
   ```
   **Save and exit** (`CTRL + X`, then `Y`, then `Enter`).

2. **Enable the Weaviate Service:**  
   ```sh
   sudo systemctl enable weaviate
   sudo systemctl start weaviate
   ```

3. **Create a systemd service for AshBot:**  
   ```sh
   sudo nano /etc/systemd/system/ashbot.service
   ```

   Paste the following:
   ```ini
   [Unit]
   Description=AshBot Discord Bot
   After=network.target

   [Service]
   WorkingDirectory=/home/YOUR_USER/ashbot
   ExecStart=/home/YOUR_USER/ashbot/.venv/bin/python ashBot.py
   Restart=always
   User=YOUR_USER

   [Install]
   WantedBy=multi-user.target
   ```
   **Save and exit** (`CTRL + X`, then `Y`, then `Enter`).

4. **Enable the AshBot Service:**  
   ```sh
   sudo systemctl enable ashbot
   sudo systemctl start ashbot
   ```

🔹 **Checkpoint:** Both Weaviate & AshBot now **auto-restart if the server reboots!**

---
## **🛠️ Step 7: Test Everything**
1. **Check if AshBot is running:**  
   ```sh
   sudo systemctl status ashbot
   ```
   ✅ You should see **active (running)**.

2. **Check if Weaviate is running:**  
   ```sh
   sudo systemctl status weaviate
   ```
   ✅ You should see **active (running)**.

3. **Send a test message to AshBot in Discord.**

🎉 **Congratulations! AshBot & Weaviate are now running 24/7 on Google Cloud!** 🚀

