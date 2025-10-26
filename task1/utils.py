from datetime import datetime, timedelta
from dateutil import parser as dateparser
import re

# Naive parsing function: tries to extract time expressions from a command.
def parse_reminder_command(text):
    """
    Examples handled:
    - set reminder to call mom at 6 pm
    - remind me to submit report tomorrow at 9 am
    - set reminder to buy milk at 18:30 on 2025-10-27
    Returns dict: {"text": "...", "time": datetime} or None
    """
    text = text.strip()
    # remove leading words
    text = re.sub(r'^(set reminder to|set a reminder to|remind me to|remind me) ', '', text, flags=re.I).strip()

    # look for ' at <time>' or ' on <date>' or ' tomorrow' or ' today' or ' in X minutes/hours'
    # in a basic order: check 'in X minutes/hours'
    m = re.search(r'in (\d+)\s*(minute|minutes|min|hour|hours|hr|hrs)', text)
    if m:
        val = int(m.group(1))
        unit = m.group(2)
        now = datetime.now()
        if 'hour' in unit:
            dt = now + timedelta(hours=val)
        else:
            dt = now + timedelta(minutes=val)
        reminder_text = re.sub(r'in \d+\s*(minute|minutes|min|hour|hours|hr|hrs)', '', text, flags=re.I).strip()
        return {"text": reminder_text, "time": dt}

    # explicit 'at' time
    m_at = re.search(r'at ([0-9:\sapmAPM]+)(?: on ([\d-\/\s\w]+))?', text)
    if m_at:
        time_part = m_at.group(1).strip()
        date_part = m_at.group(2)
        dt_str = time_part if not date_part else f"{time_part} {date_part}"
        try:
            dt = dateparser.parse(dt_str, fuzzy=True)
            reminder_text = re.sub(r'at [0-9:\sapmAPM]+(?: on [\d-\/\s\w]+)?', '', text, flags=re.I).strip()
            return {"text": reminder_text, "time": dt}
        except Exception:
            pass

    # 'tomorrow' or 'today'
    if 'tomorrow' in text:
        # try to find a time
        m_time = re.search(r'(\d{1,2}(:\d{2})?\s*(am|pm)?)', text)
        if m_time:
            t = m_time.group(1)
            try:
                dt = dateparser.parse(f"{t} tomorrow", fuzzy=True)
                reminder_text = re.sub(r'tomorrow', '', text, flags=re.I).strip()
                return {"text": reminder_text, "time": dt}
            except:
                pass
        else:
            dt = datetime.now() + timedelta(days=1)
            dt = dt.replace(hour=9, minute=0, second=0, microsecond=0)
            reminder_text = re.sub(r'tomorrow', '', text, flags=re.I).strip()
            return {"text": reminder_text, "time": dt}

    # fallback: try to parse any date/time
    try:
        dt = dateparser.parse(text, fuzzy=True, default=datetime.now())
        # if parsed dt seems to match text and is in the future
        if dt and dt > datetime.now():
            # take text minus the time part (naive)
            reminder_text = text
            return {"text": reminder_text, "time": dt}
    except Exception:
        pass

    return None
