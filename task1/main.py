import time
import threading
from assistant import Assistant
from reminders import ReminderManager

def main():
    print("Starting Voice Assistant...")
    assistant = Assistant()
    reminder_manager = ReminderManager(assistant.speak)
    reminder_manager.start_background_loop()

    try:
        assistant.run(reminder_manager)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        reminder_manager.stop()

if __name__ == "__main__":
    main()
