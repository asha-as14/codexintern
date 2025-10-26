import json
import os
import threading
import time
from datetime import datetime, timedelta
from dateutil import parser as dateparser

REMINDERS_FILE = "reminders.json"
CHECK_INTERVAL = 15  # seconds

class ReminderManager:
    def __init__(self, speak_fn):
        self.speak = speak_fn
        self._stop_event = threading.Event()
        self._thread = None
        self.reminders = self.load_reminders()

    def load_reminders(self):
        if os.path.exists(REMINDERS_FILE):
            try:
                with open(REMINDERS_FILE, "r") as f:
                    data = json.load(f)
                    # convert times back to datetime
                    for r in data:
                        r["time"] = dateparser.parse(r["time"])
                    return data
            except Exception:
                return []
        return []

    def save_reminders(self):
        data = []
        for r in self.reminders:
            data.append({"text": r["text"], "time": r["time"].isoformat(), "notified": r.get("notified", False)})
        with open(REMINDERS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def add_reminder(self, reminder):
        # reminder is dict with 'text' and 'time' (datetime)
        reminder_entry = {"text": reminder["text"], "time": reminder["time"], "notified": False}
        self.reminders.append(reminder_entry)
        self.save_reminders()

    def check_reminders_once(self):
        now = datetime.now()
        due = []
        for r in self.reminders:
            if not r.get("notified") and r["time"] <= now:
                due.append(r)
        for r in due:
            self.speak(f"Reminder: {r['text']}")
            r["notified"] = True
        if due:
            self.save_reminders()

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                self.check_reminders_once()
            except Exception as e:
                print("Reminder loop error:", e)
            self._stop_event.wait(CHECK_INTERVAL)

    def start_background_loop(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
