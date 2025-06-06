# neurosync/llm/llm_initialiser.py

from threading import Thread
from queue import Queue

# Corrected imports
from ..core.livelink.livelink_init import create_socket_connection, initialize_py_face
from ..core.livelink.animations.default_animation import default_animation_loop
from ..tts.tts_bridge import tts_worker
from ..files.file_utils import initialize_directories
from .llm_utils import warm_up_llm_connection
# Note: audio_face_workers might be legacy and needs removal/relocation later
# from utils.audio_face_workers import audio_face_queue_worker # Commented out - legacy
from .chat_utils import load_full_chat_history, build_rolling_history

# Corrected config import (assuming config.py is at top level or neurosync/core)
# If it's neurosync/core/config.py:
from ..core.config import (
    DEFAULT_VOICE_NAME as VOICE_NAME,
    USE_LOCAL_AUDIO,
    USE_COMBINED_ENDPOINT,
    ENABLE_EMOTE_CALLS,
    BASE_SYSTEM_MESSAGE,
    get_llm_config,
    setup_warnings
)

# Set up warnings using the configuration helper.
setup_warnings()

# Build the LLM configuration dictionary.
llm_config = get_llm_config(system_message=BASE_SYSTEM_MESSAGE)


def initialize_system():
    """
    Encapsulates all common initialization steps for the system.

    Returns:
        dict: A dictionary containing the initialized objects:
              - py_face: the initialized face interface.
              - socket_connection: the active socket connection.
              - full_history: the full conversation history.
              - chat_history: the rolling conversation history.
              - default_animation_thread: the thread running the default animation.
              - chunk_queue: the queue for TTS chunks.
              - audio_queue: the queue for audio data.
              - tts_worker_thread: the thread running the TTS worker.
              - audio_worker_thread: the thread running the audio face worker.
    """
    # Initialize directories and hardware interfaces.
    initialize_directories()
    py_face = initialize_py_face()
    socket_connection = create_socket_connection()

    # Load conversation history.
    full_history = load_full_chat_history()
    chat_history = build_rolling_history(full_history)

    # Warm up the LLM connection.
    warm_up_llm_connection(llm_config)

    # Start the default animation thread.
    default_animation_thread = Thread(target=default_animation_loop, args=(py_face, socket_connection)) # Adjusted args
    default_animation_thread.daemon = True # Make daemon
    default_animation_thread.start()

    # Create queues for TTS and audio.
    chunk_queue = Queue()
    audio_queue = Queue()

    # Start the TTS worker thread.
    tts_worker_thread = Thread(
        target=tts_worker,
        args=(chunk_queue, audio_queue, USE_LOCAL_AUDIO, VOICE_NAME, USE_COMBINED_ENDPOINT),
        daemon=True # Make daemon
    )
    tts_worker_thread.start()

    # Start the audio face worker thread.
    # Note: audio_face_queue_worker might be legacy
    # audio_worker_thread = Thread( # Commented out - legacy
    #     target=audio_face_queue_worker,
    #     args=(audio_queue, py_face, socket_connection, default_animation_thread, ENABLE_EMOTE_CALLS),
    #     daemon=True # Make daemon
    # )
    # audio_worker_thread.start()
    audio_worker_thread = None # Set to None as it's commented out

    # Return all initialized objects.
    return {
        'py_face': py_face,
        'socket_connection': socket_connection,
        'full_history': full_history,
        'chat_history': chat_history,
        'default_animation_thread': default_animation_thread,
        'chunk_queue': chunk_queue,
        'audio_queue': audio_queue,
        'tts_worker_thread': tts_worker_thread,
        'audio_worker_thread': audio_worker_thread,
    } 