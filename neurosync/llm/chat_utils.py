# neurosync/llm/chat_utils.py
# This software is licensed under a **dual-license model**
# For individuals and businesses earning **under $1M per year**, this software is licensed under the **MIT License**
# Businesses or organizations with **annual revenue of $1,000,000 or more** must obtain permission to use this software commercially.

import os
import json

# -------------------------------------------------------------------
# Existing configuration and functions
CHAT_LOGS_DIR = "chat_logs"
MAX_CONTEXT_LENGTH = 4000
ROLLING_LOG_FILE = os.path.join(CHAT_LOGS_DIR, "chat_history.json")
FULL_LOG_FILE = os.path.join(CHAT_LOGS_DIR, "chat_history_full.json")

# Ensure the directory exists
os.makedirs(CHAT_LOGS_DIR, exist_ok=True)


def load_full_chat_history():
    """
    Loads the never-ending chat history from a JSON file,
    or returns an empty list if none found.
    """
    if os.path.exists(FULL_LOG_FILE):
        try:
            with open(FULL_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
             print(f"Warning: Could not decode JSON from {FULL_LOG_FILE}")
             return [] # Return empty list on decode error
    return []


def save_full_chat_history(full_history):
    """
    Saves the never-ending chat history to disk (no truncation).
    """
    try:
        with open(FULL_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(full_history, f, indent=4)
    except IOError as e:
        print(f"Error saving full chat history to {FULL_LOG_FILE}: {e}")


def build_rolling_history(full_history):
    """
    Builds a rolling context from the end of the full_history,
    ensuring we don't exceed the MAX_CONTEXT_LENGTH in total JSON size.

    Returns a truncated list that is <= MAX_CONTEXT_LENGTH in size.
    """
    rolling = []
    total_size = 0

    # We'll iterate backwards (most recent first), then insert at the front.
    for entry in reversed(full_history):
        try:
            entry_str = json.dumps(entry)
            entry_size = len(entry_str)
            if total_size + entry_size <= MAX_CONTEXT_LENGTH:
                rolling.insert(0, entry)
                total_size += entry_size
            else:
                break
        except TypeError as e:
             print(f"Warning: Could not serialize entry for rolling history: {e} - Entry: {entry}")
             continue # Skip unserializable entries

    return rolling


def save_rolling_history(rolling_history):
    """
    Saves the rolling history to 'chat_history.json'.
    """
    try:
        with open(ROLLING_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(rolling_history, f, indent=4)
    except IOError as e:
        print(f"Error saving rolling chat history to {ROLLING_LOG_FILE}: {e}")


def load_rolling_history():
    """
    Loads the truncated (rolling) chat history from the log file.
    If it doesn't exist, returns an empty list.
    """
    if os.path.exists(ROLLING_LOG_FILE):
        try:
            with open(ROLLING_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
             print(f"Warning: Could not decode JSON from {ROLLING_LOG_FILE}")
             return []
    return []

# Note: These seem redundant with the rolling/full logic, consider removing
def load_chat_history():
    """Loads chat history from the log file."""
    log_file = os.path.join(CHAT_LOGS_DIR, "chat_history_small.json")
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {log_file}")
                return []
    return []

def save_chat_log(chat_history):
    """Saves the chat history, ensuring it stays within context length."""
    log_file = os.path.join(CHAT_LOGS_DIR, "chat_history_small.json")
    total_length = sum(len(json.dumps(entry)) for entry in chat_history)
    while total_length > MAX_CONTEXT_LENGTH and chat_history:
        chat_history.pop(0)
        total_length = sum(len(json.dumps(entry)) for entry in chat_history)
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, indent=4)
    except IOError as e:
        print(f"Error saving chat log to {log_file}: {e}")


# -------------------------------------------------------------------
# NEW: Functions for AI-specific logs (ai_1 and ai_2)

def get_ai_log_files(ai_id):
    """
    Returns the rolling and full log file paths for a given AI.
    ai_id should be either 1 or 2.
    """
    if ai_id not in (1, 2):
        raise ValueError("ai_id must be 1 or 2")
    rolling_file = os.path.join(CHAT_LOGS_DIR, f"chat_history_ai_{ai_id}.json")
    full_file = os.path.join(CHAT_LOGS_DIR, f"chat_history_full_ai_{ai_id}.json")
    return rolling_file, full_file


def load_full_chat_history_ai(ai_id):
    """
    Loads the full chat history for the specified AI.
    """
    _, full_log_file = get_ai_log_files(ai_id)
    if os.path.exists(full_log_file):
        try:
            with open(full_log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
             print(f"Warning: Could not decode JSON from {full_log_file}")
             return []
    return []


def save_full_chat_history_ai(ai_id, full_history):
    """
    Saves the full chat history for the specified AI.
    """
    _, full_log_file = get_ai_log_files(ai_id)
    try:
        with open(full_log_file, "w", encoding="utf-8") as f:
            json.dump(full_history, f, indent=4)
    except IOError as e:
        print(f"Error saving full AI chat history to {full_log_file}: {e}")


def load_rolling_history_ai(ai_id):
    """
    Loads the rolling (truncated) chat history for the specified AI.
    """
    rolling_log_file, _ = get_ai_log_files(ai_id)
    if os.path.exists(rolling_log_file):
        try:
            with open(rolling_log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
             print(f"Warning: Could not decode JSON from {rolling_log_file}")
             return []
    return []


def save_rolling_history_ai(ai_id, rolling_history):
    """
    Saves the rolling chat history for the specified AI.
    """
    rolling_log_file, _ = get_ai_log_files(ai_id)
    try:
        with open(rolling_log_file, "w", encoding="utf-8") as f:
            json.dump(rolling_history, f, indent=4)
    except IOError as e:
        print(f"Error saving rolling AI chat history to {rolling_log_file}: {e}")


def build_rolling_history_ai(ai_id, full_history, max_context_length=MAX_CONTEXT_LENGTH):
    """ Calls build_rolling_history - specific function not needed unless logic differs. """
    # Assuming the logic is the same as the general rolling history builder
    return build_rolling_history(full_history)

# Note: These seem redundant, consider removing
def load_chat_history_ai(ai_id):
    """Loads the small (truncated) chat history for the specified AI."""
    log_file = os.path.join(CHAT_LOGS_DIR, f"chat_history_small_ai_{ai_id}.json")
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                 print(f"Warning: Could not decode JSON from {log_file}")
                 return []
    return []

def save_chat_log_ai(ai_id, chat_history):
    """Saves the chat history for the specified AI, ensuring it stays within context length."""
    log_file = os.path.join(CHAT_LOGS_DIR, f"chat_history_small_ai_{ai_id}.json")
    total_length = sum(len(json.dumps(entry)) for entry in chat_history)
    while total_length > MAX_CONTEXT_LENGTH and chat_history:
        chat_history.pop(0)
        total_length = sum(len(json.dumps(entry)) for entry in chat_history)
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, indent=4)
    except IOError as e:
        print(f"Error saving small AI chat log to {log_file}: {e}") 