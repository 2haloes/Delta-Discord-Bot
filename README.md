# Delta-Discord-Bot
A bot for Discord that utilises AI technologies to respond to text and generate images

# This is a work in progress so only basic details are provided

This is a basic Discord bot that can use ChatGPT, DALL-E and Stable Diffusion to converse and entertain users  
Delta uses OpenAI for chat replies and DALL-E image generations and uses Banana.dev for other image generation options  
DALL-E images generate at 1024x1024 while other image generators generage images at 768x768

# Commands
- Mention/Reply bot - Uses ChatGPT to reply
- !delta-dalle - Uses OpenAI's DALL-E preview to generate images, it is setup to generate 1024x1024 images
- !delta-imagegen - Uses Stable Diffusion 2.1 running on Banana's Serverless GPU to generate an image
- !delta-pastelgen - Uses Pastel Mix running on Banana's Serverless GPU to generate an image

# Environmenet Variables
- BANANA_API_KEY - The API key for Banana.dev to generate images outside of DALL-E
- OPENAI_API_KEY - The API key for OpenAI to generate ChatGPT replies and DALL-E images
- DISCORD_TOKEN - The API key for Discord
- DEBUG (optional) - Set this to 1 to allow the bot to only reply to the USER_ID defined below
- SD_KEY - Model Id for the Stable Diffusion instance
- PASTEL_MIX_KEY - Model Id for the Pastel Mix instance
- SYSTEM_DETAILS (optional) - Extra details that can be used to define the ChatGPT personality beyond what is provided in the script 
- USER_ID (optonal) - The Id of the user for the bot to only reply to when DEBUG is set to 1
