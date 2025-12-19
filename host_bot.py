import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
import asyncio
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

# Import configuration
try:
    import config
except ImportError:
    print("CRITICAL: config.py not found. Please create it.")
    exit(1)

# --- Setup Bot & Intents ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Required to check voice states
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Global State
last_command_time = 0.0
driver = None
menu_message = None

# --- Browser Handler ---

class OmegleHandler:
    def __init__(self):
        self.driver = None

    async def initialize_driver(self):
        """Initializes the Edge WebDriver."""
        global driver
        options = Options()
        options.add_argument(f"user-data-dir={config.EDGE_USER_DATA_DIR}")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        
        print("Launching Edge Browser...")
        self.driver = await asyncio.to_thread(webdriver.Edge, options=options)
        driver = self.driver
        
        print(f"Navigating to {config.OMEGLE_VIDEO_URL}...")
        await asyncio.to_thread(self.driver.get, config.OMEGLE_VIDEO_URL)
        
        # Initial Setup
        await self.handle_setup_sequence()
        print("Browser Initialized.")

    async def handle_setup_sequence(self):
        """Runs the standard setup: Click Checkboxes -> Wait -> Relay -> Volume."""
        # 1. Click Checkboxes
        if config.CLICK_CHECKBOX:
            await asyncio.sleep(2) # Wait for load
            await self.click_checkboxes()
        
        # 2. Automation (Relay/Volume)
        await asyncio.sleep(0.5)
        await self.run_automation()

    async def click_checkboxes(self):
        """Finds and clicks checkboxes."""
        try:
            def _click():
                checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
                count = 0
                for box in checkboxes:
                    if not box.is_selected():
                        self.driver.execute_script("arguments[0].click();", box)
                        count += 1
                return count
            
            clicked = await asyncio.to_thread(_click)
            if clicked > 0:
                print(f"Clicked {clicked} checkboxes.")
        except Exception as e:
            print(f"Error clicking checkboxes: {e}")

    async def run_automation(self):
        """Handles /relay and Volume."""
        def _automate():
            # Volume
            if config.AUTO_OMEGLE_VOL:
                try:
                    script = f"var s=document.getElementById('vol-control');if(s){{s.value={config.OMEGLE_VOL};s.dispatchEvent(new Event('input',{{bubbles:true}}));}}"
                    self.driver.execute_script(script)
                except Exception:
                    pass

            # Relay
            if config.AUTO_RELAY:
                try:
                    text_area = None
                    selectors = ["textarea.chat-msg", "textarea.messageInput", "textarea"]
                    for sel in selectors:
                        try:
                            found = self.driver.find_element(By.CSS_SELECTOR, sel)
                            if found.is_displayed():
                                text_area = found
                                break
                        except:
                            continue
                    
                    if text_area:
                        text_area.clear()
                        text_area.send_keys("/relay")
                        time.sleep(0.1)
                        text_area.send_keys(Keys.RETURN)
                except Exception as e:
                    print(f"Auto-relay error: {e}")
        
        await asyncio.to_thread(_automate)

    async def skip(self):
        """Sends ESC keys to skip."""
        if not self.driver: return
        
        # Ensure we are on the video page
        if config.OMEGLE_VIDEO_URL not in self.driver.current_url:
            await asyncio.to_thread(self.driver.get, config.OMEGLE_VIDEO_URL)
            await self.handle_setup_sequence()
            await asyncio.sleep(1)

        # Run automation (Relay) before skipping to ensure it's ready for next person
        await self.run_automation()

        # Send ESC
        def _send_esc():
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(0.5)
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        
        await asyncio.to_thread(_send_esc)
        print("Skipped.")

    async def refresh(self):
        """Refreshes the page."""
        if not self.driver: return
        print("Refreshing...")
        await asyncio.to_thread(self.driver.get, config.OMEGLE_VIDEO_URL)
        await self.handle_setup_sequence()

    async def report(self):
        """Clicks the report flag and confirm button."""
        if not self.driver: return
        print("Reporting user...")
        def _do_report():
            try:
                # Try common report button selectors
                btn = self.driver.find_element(By.XPATH, "//img[@alt='Report' and contains(@class, 'reportButton')]")
                btn.click()
                time.sleep(1)
                confirm = self.driver.find_element(By.ID, "confirmBan")
                confirm.click()
                return True
            except Exception as e:
                print(f"Report failed: {e}")
                return False
        
        return await asyncio.to_thread(_do_report)

    async def close(self):
        if self.driver:
            await asyncio.to_thread(self.driver.quit)

browser = OmegleHandler()

# --- Discord Views & Commands ---

class SimpleHelpView(View):
    def __init__(self):
        super().__init__(timeout=None) # Persistent view

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Re-use the validation logic
        if not await validate_user(interaction.user, interaction):
            return False
        return True

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.success, emoji="⏭️", custom_id="host_skip")
    async def skip_btn(self, interaction: discord.Interaction, button: Button):
        await handle_command_logic(interaction, "skip")

    @discord.ui.button(label="Refresh/Pause", style=discord.ButtonStyle.danger, emoji="🔄", custom_id="host_refresh")
    async def refresh_btn(self, interaction: discord.Interaction, button: Button):
        await handle_command_logic(interaction, "refresh")

    @discord.ui.button(label="Report", style=discord.ButtonStyle.secondary, emoji="🚩", custom_id="host_report")
    async def report_btn(self, interaction: discord.Interaction, button: Button):
        await handle_command_logic(interaction, "report")

async def validate_user(user: discord.Member, ctx_or_interaction) -> bool:
    """Checks if user is in the correct VC with Camera ON."""
    
    # Helper to send response
    async def respond(msg):
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(msg, ephemeral=True)
        else:
            await ctx_or_interaction.send(msg, delete_after=5)

    # 1. Check Channel
    if not user.voice or not user.voice.channel or user.voice.channel.id != config.STREAMING_VC_ID:
        await respond(f"⛔ You must be in <#{config.STREAMING_VC_ID}> to use this.")
        return False

    # 2. Check Camera
    if not user.voice.self_video:
        await respond("⛔ You must have your **Camera ON** to use this.")
        return False

    return True

async def handle_command_logic(source, action):
    """Handles the actual logic for skip/refresh/report with cooldowns."""
    global last_command_time
    
    # Handle both Context and Interaction
    user = source.author if isinstance(source, commands.Context) else source.user
    
    # 1. Check Cooldown
    if time.time() - last_command_time < config.COMMAND_COOLDOWN:
        remaining = config.COMMAND_COOLDOWN - (time.time() - last_command_time)
        msg = f"⏳ Cooldown: Wait {remaining:.1f}s."
        if isinstance(source, discord.Interaction):
            await source.response.send_message(msg, ephemeral=True)
        else:
            await source.send(msg, delete_after=3)
        return

    # 2. Update Cooldown
    last_command_time = time.time()

    # 3. Acknowledge (if interaction)
    if isinstance(source, discord.Interaction):
        await source.response.defer()
        try:
            # Announce in channel
            await source.channel.send(f"**{user.display_name}** used `!{action}`", delete_after=5)
        except: pass
    
    # 4. Execute Action
    if action == "skip":
        await browser.skip()
    elif action == "refresh":
        await browser.refresh()
    elif action == "report":
        success = await browser.report()
        if isinstance(source, discord.Interaction):
            await source.followup.send("✅ Reported." if success else "❌ Report failed.", ephemeral=True)

# --- Discord Events ---

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
    # Initialize Browser
    await browser.initialize_driver()
    
    # Start Menu Loop
    if not menu_task.is_running():
        menu_task.start()

@bot.event
async def on_voice_state_update(member, before, after):
    """Handles AUTO_VC_START and EMPTY_VC_PAUSE."""
    if member.bot: return
    
    # Only care about the Streaming VC
    if (before.channel and before.channel.id == config.STREAMING_VC_ID) or \
       (after.channel and after.channel.id == config.STREAMING_VC_ID):
        
        guild = member.guild
        vc = guild.get_channel(config.STREAMING_VC_ID)
        if not vc: return

        # Count users with camera ON
        cam_users = [m for m in vc.members if not m.bot and m.voice.self_video]
        count = len(cam_users)

        # Logic for Auto Start
        if config.AUTO_VC_START:
            # If someone just joined/turned cam on and is the FIRST one
            if count == 1 and (after.channel and after.channel.id == config.STREAMING_VC_ID and after.self_video):
                print("Auto-Starting Stream (First camera user joined)")
                await browser.skip()

        # Logic for Auto Pause
        if config.EMPTY_VC_PAUSE:
            # If the last camera user left
            if count == 0 and (before.channel and before.channel.id == config.STREAMING_VC_ID):
                # Ensure it wasn't just a deafen toggle
                if before.self_video and (not after.self_video or after.channel.id != config.STREAMING_VC_ID):
                    print("Auto-Pausing Stream (VC Empty)")
                    await browser.refresh()

# --- Periodic Menu Task (UPDATED) ---

@tasks.loop(seconds=30)
async def menu_task():
    """Checks if the menu exists every 30s. If deleted, reposts it."""
    global menu_message
    channel = bot.get_channel(config.COMMAND_CHANNEL_ID)
    if not channel: return

    # Helper function to post the menu
    async def post_menu():
        global menu_message
        
        # Clean up previous menu messages if they exist in memory but not on Discord
        if menu_message:
            try: await menu_message.delete()
            except: pass

        # Optional: Clean up chat to keep the menu visible at bottom
        # This removes messages sent by the bot (except the new menu)
        try:
            await channel.purge(limit=5, check=lambda m: m.author == bot.user)
        except: pass

        embed = discord.Embed(
            title="🎥 Stream Controls",
            description="Must be in **Streaming VC** with **Camera ON** to use.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Commands", value="`!skip` `!refresh` `!report`", inline=False)
        
        view = SimpleHelpView()
        menu_message = await channel.send(embed=embed, view=view)

    # 1. If we have no record of a message, post it.
    if menu_message is None:
        await post_menu()
    else:
        # 2. If we have a record, check if it actually exists in Discord
        try:
            await channel.fetch_message(menu_message.id)
            # If fetch succeeds, the message exists. Do nothing.
        except discord.NotFound:
            # Message was deleted (manually or otherwise)
            print("Menu missing. Reposting...")
            await post_menu()
        except Exception as e:
            print(f"Error checking menu status: {e}")

# --- Commands ---

@bot.command()
async def skip(ctx):
    if await validate_user(ctx.author, ctx):
        await handle_command_logic(ctx, "skip")

@bot.command()
async def refresh(ctx):
    if await validate_user(ctx.author, ctx):
        await handle_command_logic(ctx, "refresh")

@bot.command()
async def report(ctx):
    if await validate_user(ctx.author, ctx):
        await handle_command_logic(ctx, "report")

# --- Run ---
if __name__ == "__main__":
    try:
        bot.run(config.BOT_TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")
    finally:
        # Cleanup browser on exit
        loop = asyncio.new_event_loop()
        loop.run_until_complete(browser.close())
