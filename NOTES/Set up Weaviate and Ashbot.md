# 🚀 Full Guide: Setting Up Weaviate & AshBot on a Free Google Compute Engine (GCE) VM

## 📌 Overview
This guide will walk you through **setting up a free Google Compute Engine (GCE) VM** to host both **Weaviate (for memory storage)** and **AshBot (your Discord bot)** so they run 24/7, even when your computer is off.

---
## 📝 Step 1: Set Up a Google Cloud Compute Engine VM

### 1️⃣ Create a Free Google Cloud Account
1. **Go to Google Cloud Console:**  
   👉 [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. **Sign in with a Google account** (or create a new one).
3. **Start your free trial** (if eligible, you get $300 in credits, but we won’t need them).
4. **Enable billing** (Google requires a payment method but will not charge you unless you exceed the free-tier limits).
5. **Create a new project:**  
   - Click **Select a Project** → **New Project**.
   - Name it **AshBot VM** (or anything you like).
   - Click **Create**.

✅ **Checkpoint:** Your Google Cloud account is ready.

---
## 🖥️ Step 2: Create a Free Virtual Machine (VM)

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

✅ **Checkpoint:** Your Ubuntu VM is running.

---
## 🔒 Step 3: Configure the VM (Setup SSH, Install Dependencies)

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

✅ **Checkpoint:** The VM is fully configured.

---
## 📦 Step 4: Install & Run Weaviate (Vector Database)

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

✅ **Checkpoint:** Weaviate is now running.

---
## 🤖 Step 5: Deploy AshBot

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

4. **Modify AshBot’s Memory System to Use Weaviate**
   - Create `subprocesses/weaviate_memory.py` and paste:
   
   ```python
   import weaviate
   import json
   
   client = weaviate.Client("http://localhost:8080")
   
   def store_user_memory(user_id, name, memory_data):
       client.data_object.create(
           data_object={"user_id": user_id, "name": name, "memory": json.dumps(memory_data)},
           class_name="UserMemory",
       )
   
   def retrieve_user_memory(user_id):
       result = client.query.get("UserMemory", ["user_id", "name", "memory"]).do()
       if result and "data" in result and "Get" in result["data"]:
           for item in result["data"]["Get"]["UserMemory"]:
               if item["user_id"] == user_id:
                   return json.loads(item["memory"])
       return {}
   ```

✅ **AshBot now uses Weaviate for memory storage!**

---
## ♻️ Step 6: Ensure Weaviate & AshBot Auto-Restart

### **1️⃣ Weaviate Auto-Restart**
```sh
sudo nano /etc/systemd/system/weaviate.service
```
Paste:
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
Enable Weaviate:
```sh
sudo systemctl enable weaviate
sudo systemctl start weaviate
```

### **2️⃣ AshBot Auto-Restart**
```sh
sudo nano /etc/systemd/system/ashbot.service
```
Paste:
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
Enable AshBot:
```sh
sudo systemctl enable ashbot
sudo systemctl start ashbot
```

✅ **Now both services restart on boot!**

---
## 🛠️ Step 7: Test Everything
1️⃣ **Check if AshBot is running**  
```sh
sudo systemctl status ashbot
```
✅ **Should be active (running)**

2️⃣ **Check if Weaviate is running**  
```sh
sudo systemctl status weaviate
```
✅ **Should be active (running)**

3️⃣ **Send a test message to AshBot in Discord.**  
🎉 **If AshBot remembers past conversations, success!**

---
## 🎯 Next Steps
- Test **long-term memory retrieval**.
- Delete **users.json** if Weaviate works well.
- Debug if issues arise:  
  ```sh
  sudo journalctl -u ashbot -f
  ```
- Restart services if needed:  
  ```sh
  sudo systemctl restart weaviate
  ```

🎉 **AshBot now runs 24/7 with Weaviate!** 🚀
