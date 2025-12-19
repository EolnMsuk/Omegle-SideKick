# 🤖 Discord Omegle Host Bot – Setup Guide

This bot allows you to host an automated Omegle stream control bot on your own computer. It connects to a Discord server and allows users in a specific voice channel (with their camera on) to control the browser remotely.

## 📋 Prerequisites

Before starting, ensure you have the following installed on your Windows computer:

1.  **Python 3.10 or newer**
    * [Download Here](https://www.python.org/downloads/)
    * **⚠️ IMPORTANT:** When installing, check the box **"Add Python to PATH"** at the bottom of the installer.
2.  **Microsoft Edge Browser**
    * (This is usually pre-installed on Windows).

---

## 🛠️ Part 1: Get the Discord Token from the Server Owner

You only need to get the TOKEN from the server owner, the owner will create a bot for you with limited access.

1.  Ask the owner to provide you with the TOKEN, do not share it with anyone.
2.  Save this token in a text file somewhere safe, you will use it later in your config.py file.

---

## 💻 Part 2: Installation on Your Computer

1.  Create a folder on your Desktop (e.g., `OmegleBot`).
2.  Place the provided files (`host_bot.py` and `config.py`) inside this folder.
3.  Open the folder, click the address bar at the top, type `cmd`, and press **Enter**.
4.  In the black window that appears, run this command to install dependencies:
    ```bash
    pip install discord.py selenium webdriver-manager
    ```

---

## ⚙️ Part 3: Configuration

You must edit the `config.py` file to link the bot to your account and browser.

1.  Right-click `config.py` and open it with Notepad.
2.  **Paste your Bot Token:**
    * Replace `PASTE_YOUR_BOT_TOKEN_HERE` with the token you copied in Part 1.
3.  **Get your Edge Profile Path:**
    * Open Microsoft Edge.
    * Type `edge://version` in the address bar.
    * Copy the **"Profile path"** (e.g., `C:\Users\User\AppData\Local\Microsoft\Edge\User Data\Default`).
4.  **Update the Config:**
    * Paste that path into `EDGE_USER_DATA_DIR`.
    * **⚠️ CRITICAL:** You must use double backslashes (`\\`) instead of single ones (`\`).
    * *Example:* `"C:\\Users\\User\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default"`
5.  **Set IDs:**
    * Update `GUILD_ID`, `COMMAND_CHANNEL_ID`, and `STREAMING_VC_ID` with the correct IDs from your Discord server. (You can get these by enabling "Developer Mode" in Discord settings and right-clicking channels/servers).

---

## 🚀 Part 4: Running the Bot

1.  **Login first:** Open Edge manually and log in to the site (Omegle/Umingle) to save your cookies/settings.
2.  **Close Edge:** Completely close all Edge windows.
3.  Open your Command Prompt (from Part 2) and run:
    ```bash
    python host_bot.py
    ```
4.  The bot will launch a browser window controlled by the script. **Do not close this window.**

---

## 🎮 Usage

Users must be in the **Streaming Voice Channel** with their **Camera ON** to use commands.

* **!skip** - Skips the current stranger.
* **!refresh** - Refreshes the page (useful if stuck).
* **!report** - Reports the current stranger.

The bot will also post a menu with buttons in the `COMMAND_CHANNEL_ID` every 30 minutes.

---

## ❓ Troubleshooting

* **"Private application cannot have a default authorization link"**:
    * Go to the Developer Portal -> Installation Tab -> Set "Install Link" to "None".
* **Browser opens and closes immediately**:
    * Your `EDGE_USER_DATA_DIR` path in `config.py` is likely wrong or missing double backslashes (`\\`).
* **Bot ignores commands**:
    * Make sure "Message Content Intent" is enabled in the Discord Developer Portal -> Bot tab.
    * Ensure the user trying to command is in the correct Voice Channel with their Camera enabled.
