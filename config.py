# config.py

# --- Discord Configuration ---
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

GUILD_ID = 1131770315740024966  # PASTE YOUR SERVER'S ID HERE

# The text channel where the menu will appear and commands are allowed
COMMAND_CHANNEL_ID = 1131770315740024966

# The voice channel where users MUST be (with camera ON) to use commands
STREAMING_VC_ID = 1131770315740024966

# --- Omegle / Browser Configuration ---
OMEGLE_VIDEO_URL = "https://umingle.com/video"

# Path to the Edge User Data directory (preserves login/settings)
# Note: Ensure all backslashes are doubled (\\) as shown below
EDGE_USER_DATA_DIR = "C:\\Users\\owner\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 3"

# Global cooldown (seconds) between commands to prevent spam
COMMAND_COOLDOWN = 5

# --- Automation Settings ---

# If True, automatically pauses (refreshes) when the last camera-user leaves VC
EMPTY_VC_PAUSE = True

# If True, automatically starts (skips) when the first camera-user joins VC
AUTO_VC_START = False

# If True, automatically clicks checkboxes on refresh/load
CLICK_CHECKBOX = True

# If True, automatically types /relay into the chat box
AUTO_RELAY = True

# If True, automatically sets the volume slider
AUTO_OMEGLE_VOL = True

OMEGLE_VOL = 40
