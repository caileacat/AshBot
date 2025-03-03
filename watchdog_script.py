import os
import time
import signal
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartBotHandler(FileSystemEventHandler):
    """Watches for file changes and restarts the bot when detected."""
    def __init__(self, bot_process):
        self.bot_process = bot_process

    def on_any_event(self, event):
        """Triggers on any file change and restarts the bot."""
        if event.event_type in ['modified', 'created', 'deleted'] and event.src_path.endswith(".py"):
            print(f"🔄 Detected changes in {event.src_path}. Restarting bot...")
            self.restart_bot()

    def restart_bot(self):
        """Terminates the bot and restarts it."""
        self.bot_process.terminate()
        self.bot_process.wait()
        time.sleep(1)  # Small delay to prevent race conditions
        self.bot_process = subprocess.Popen(["python", "ashBot.py"])

if __name__ == "__main__":
    print("👀 Watching for changes... Starting AshBot.")
    bot_process = subprocess.Popen(["python", "ashBot.py"])  # Start the bot

    event_handler = RestartBotHandler(bot_process)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)  # Watches all files in the bot directory
    observer.start()

    try:
        while True:
            time.sleep(1)  # Keeps the script running
    except KeyboardInterrupt:
        observer.stop()
        bot_process.terminate()  # Stop the bot when exiting
    observer.join()
