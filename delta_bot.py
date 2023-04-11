import os
import delta_helpers
import discord
import openai
import requests
from io import BytesIO
import asyncio
import banana_dev as banana
import base64

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BANANA_API_KEY = os.getenv("BANANA_API_KEY")
DEBUG = os.getenv("DEBUG")
SD_KEY = os.getenv("SD_KEY")
PASTEL_MIX_KEY = os.getenv("PASTEL_MIX_KEY")
SYSTEM_DETAILS = os.getenv("SYSTEM_DETAILS")

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!",intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.event
async def on_message(message):
    if DEBUG != "1" or message.author.id == 228941994259513344:
        if message.author == bot.user:
            return

        if bot.user.mentioned_in(message):
            asyncio.create_task(generate_reply(message))

        if message.content.startswith("!delta-imagegen"):
            asyncio.create_task(generate_image(message))

        if message.content.startswith("!delta-dalle"):
            asyncio.create_task(generate_dalle(message))

        if message.content.startswith("!delta-pastelgen"):
            asyncio.create_task(generate_pastel_mix(message))

        await bot.process_commands(message)

async def generate_reply(message):
    reply_chain = [
        {"role": "system", "content": f"{SYSTEM_DETAILS} You are a cheerful android that responds to the name Delta, you care very much for your creator and do a lot of errands around your local town for them. She is also fond of using emotes in her replies. Your replies are short and rather to the point. If someone asks you a question then you do your best to reply!"},
        {"role": "user", "content": "Keep your replies short, do not start any reply with 'Delta:', 'Delta Bot:' or anything similar. If you wish to mention someone, you can use <@[USER ID]>, user messages start with [USER NAME]|[USER ID] and the ID for the mention can be pulled from there"}
    ]
    message_channel = message.channel
    current_message = message
    chat_response = ""
    current_chain_length = 3
    async with message_channel.typing():
        try:
            while current_message.reference is not None:
                if current_chain_length % 2 == 1:
                    reply_chain.insert(2, {"role": "user", "content": f"{current_message.author.name}|{current_message.author.id}: {current_message.clean_content}"})
                else:
                    reply_chain.insert(2, {"role": "assistant", "content": f"{current_message.clean_content}"})
                current_message = await message_channel.fetch_message(current_message.reference.message_id)
                current_chain_length = current_chain_length + 1

            if current_chain_length % 2 == 1:
                reply_chain.insert(2, {"role": "user", "content": f"{current_message.author.name}|{current_message.author.id}: {current_message.clean_content}"})
            else:
                reply_chain.insert(2, {"role": "assistant", "content": f"{current_message.clean_content}"})

            input_message = message.content.replace(f"<@!{bot.user.id}>", "").strip()
            chat_output = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=reply_chain,
                temperature=0.7
            )
            chat_response = chat_output.choices[0].message.content.replace("Delta: ", "").replace("Delta Bot: ", "")
        except Exception as ex:
            chat_response = f"I'm sorry but there is an issue with processing a reply\nException Message:\n```{str(ex)}```"
            pass
        if len(chat_response) > 2000:
            chunk_size = 1980
            chunks = [chat_response[i:i+chunk_size] for i in range(0, len(chat_response), chunk_size)]
            chunks_processed = chunks.copy()
            i = 0
            while i < len(chunks):
                chunk = chunks[i]
                if i > 0 and delta_helpers.check_unclosed_formatting(chunks[i - 1]):
                    chunk = f"```\n{chunk}"
                    chunks[i] = chunk

                if delta_helpers.check_unclosed_formatting(chunk):
                    chunk = f"{chunk}```"

                chunks_processed[i] = chunk
                i += 1

            num_chunks = len(chunks)
            chunks_with_id = [f"{i+1}/{num_chunks}\n{chunk}" for i, chunk in enumerate(chunks_processed)]

            current_reply = await message.reply(chunks_with_id[0])
            for string_chunk in chunks_with_id:
                if string_chunk != chunks_with_id[0]:
                    current_reply = await current_reply.reply(string_chunk)
        else:
            await message.reply(chat_response)

async def generate_image(message):
    async with message.channel.typing():
        await generate_banana(message, SD_KEY)

async def generate_pastel_mix(message):
    async with message.channel.typing():
        await generate_banana(message, PASTEL_MIX_KEY)

async def generate_banana(message, model_id, width = 768, height = 768):
    try:
        input_message = message.clean_content.replace("!delta-imagegen", "").strip()
        model_inputs = {
        "endpoint": "txt2img",
        "params": {
            "prompt": input_message,
            "steps": 40,
            "sampler_name": "Euler a",
            "cfg_scale": 7.5,
            "seed": None,
            "batch_size": 1,
            "n_iter": 1,
            "width": width,
            "height": height
            }
        }

        api_key = BANANA_API_KEY
        model_key = model_id

        # Run the model
        out = banana.run(api_key, model_key, model_inputs)
        image_base64 = out["modelOutputs"][0]["images"][0]
        image_data = base64.b64decode(image_base64)
        file = discord.File(BytesIO(image_data), filename='image.png')
        await message.reply(file=file)
    except Exception as ex:
        await message.reply(f"Sorry, but your image request could not be completed. This may be due to the image generation returning possibly adult content or an error with my programming.\nException Message:\n```{str(ex)}```")

async def generate_dalle(message):
    async with message.channel.typing():
        try:
            input_message = message.clean_content.replace("!delta-dalle", "").strip()
            response = openai.Image.create(
                prompt=input_message,
                n=1,
                size='1024x1024',
            )
            image_url = response['data'][0]['url']
            image_data = requests.get(image_url).content
            file = discord.File(BytesIO(image_data), filename='image.png')
            await message.reply(file=file)
        except Exception as ex:
            await message.reply(f"Sorry, but your image request could not be completed. This may be due to the image generation returning possibly adult content or an error with my programming.\nException Message:\n```{str(ex)}```")

bot.run(DISCORD_TOKEN)
