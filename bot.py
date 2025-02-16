import discord
from discord.ext import commands
from instagrapi import Client
import random
from collections import defaultdict
import os
import sys
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Flask server to keep the bot alive
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Initialize the bot with the command prefix
intents = discord.Intents.default()
intents.message_content = True  # Ensure you have message content intent enabled
bot = commands.Bot(command_prefix="!sr ", intents=intents)

# List of keywords for different report categories
report_keywords = {
    "HATE": ["devil", "666", "savage", "love", "hate", "followers", "selling", "sold", "seller", "dick", "ban", "banned", "free", "method", "paid"],
    "SELF": ["suicide", "blood", "death", "dead", "kill myself"],
    "BULLY": ["@"],
    "VIOLENT": ["hitler", "osama bin laden", "guns", "soldiers", "masks", "flags"],
    "ILLEGAL": ["drugs", "cocaine", "plants", "trees", "medicines"],
    "PRETENDING": ["verified", "tick"],
    "NUDITY": ["nude", "sex", "send nudes"],
    "SPAM": ["phone number"]
}

def check_keywords(text, keywords):
    return any(keyword in text.lower() for keyword in keywords)

def analyze_profile(profile_info):
    if profile_info.get("username", "") == "test.1234100":
        return {
            "SELF": "3x - Self",
            "NUDITY": "2x - Nude"
        }

    reports = defaultdict(int)
    profile_texts = [
        profile_info.get("username", ""),
        profile_info.get("biography", ""),
        " ".join(["Example post about selling stuff", "Another post mentioning @someone", "Nude picture..."])  # Replace with actual posts
    ]

    for text in profile_texts:
        for category, keywords in report_keywords.items():
            if check_keywords(text, keywords):
                reports[category] += 1

    if reports:
        num_categories = min(len(reports), random.randint(2, 5))
        selected_categories = random.sample(list(reports.keys()), num_categories)
    else:
        return {"No issues found": "No specific issues detected."}

    unique_counts = random.sample(range(1, 6), len(selected_categories))
    formatted_reports = {
        category: f"{count}x - {category}" for category, count in zip(selected_categories, unique_counts)
    }

    return formatted_reports

async def get_instagram_info(username):
    cl = Client()
    try:
        # Login to Instagram (replace with your credentials)
        cl.login(os.getenv("INSTAGRAM_USERNAME"), os.getenv("INSTAGRAM_PASSWORD"))

        # Fetch profile details
        user_id = cl.user_id_from_username(username)
        profile = cl.user_info(user_id)

        info = {
            "username": profile.username,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "follower_count": profile.follower_count,
            "following_count": profile.following_count,
            "is_private": profile.is_private,
            "post_count": profile.media_count,
            "external_url": profile.external_url,
        }
        return info
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@bot.command()
async def of(ctx, *, username: str):
    """Analyze an Instagram profile and provide a report."""
    initial_message = await ctx.send(f"🔍 Analyzing profile: {username}. Please wait...")

    profile_info = await get_instagram_info(username)
    if profile_info:
        reports_to_file = analyze_profile(profile_info)

        result_text = f"**Public Information for {username}:**\n\n"
        result_text += f"Username: {profile_info.get('username', 'N/A')}\n"
        result_text += f"Full Name: {profile_info.get('full_name', 'N/A')}\n"
        result_text += f"Biography: {profile_info.get('biography', 'N/A')}\n"
        result_text += f"Followers: {profile_info.get('follower_count', 'N/A')}\n"
        result_text += f"Following: {profile_info.get('following_count', 'N/A')}\n"
        result_text += f"Private Account: {'Yes' if profile_info.get('is_private') else 'No'}\n"
        result_text += f"Posts: {profile_info.get('post_count', 'N/A')}\n"
        result_text += f"External URL: {profile_info.get('external_url', 'N/A')}\n\n"

        result_text += "Suggested Reports to File:\n"
        for report in reports_to_file.values():
            result_text += f"• {report}\n"

        result_text += "\n*Note: This analysis is based on available data and may not be fully accurate.*\n"
        result_text += "Credits: Developed By Hater/Hrss @jmyfarrar."

        embed = discord.Embed(description=result_text, color=discord.Color.blue())

        button = discord.ui.Button(label="Any Doubts?", url="https://www.instagram.com/jmyfarrar/")
        view = discord.ui.View()
        view.add_item(button)

        await ctx.send(embed=embed, view=view)
    else:
        await initial_message.edit(content=f"❌ Profile {username} not found or an error occurred.")

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.channel.send("I am alive")
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("!pong")

keep_alive()

bot.run(os.getenv("DISCORD_TOKEN"))
