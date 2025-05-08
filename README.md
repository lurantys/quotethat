# Quote Image Discord Bot

A Discord bot that generates stylish quote images from messages in your server!
It takes the text of a message, overlays it on the sender's profile picture, and returns a beautiful, shareable image.

## Features

- **Slash Command `/quoteimage`**: Instantly create a quote image from the latest message in a channel.
- **Context Menu "Make Quote Image"**: Right-click any message and turn it into a quote image.
- **Automatic Profile Picture Integration**: The sender's profile picture is used as the background, with a smooth gradient effect.
- **Custom Watermark**: The bot's name and discriminator are added as a subtle watermark.
- **Text Wrapping**: Long quotes are automatically wrapped for a clean look.
- **No External Storage Needed**: Images are generated in-memory and sent directly to Discord.

## Example

![Example Quote Image](https://media.discordapp.net/attachments/1266372345761890348/1370105243911589960/quote_image.png?ex=681e4971&is=681cf7f1&hm=9e0b41277b5262cd7c7dceaac98779a73d9c8e8af91a6a763ca7c5db3abdce7a&=&format=webp&quality=lossless)

## Installation

### Prerequisites

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-%3E%3D2.0-blueviolet?logo=python)
![Pillow](https://img.shields.io/badge/Pillow-%3E%3D8.0-yellow?logo=pillow)
![aiohttp](https://img.shields.io/badge/aiohttp-%3E%3D3.7-blue?logo=python)

- A Discord bot token ([How to get one](https://discord.com/developers/applications))

### Setup

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/quote-image-bot.git
   cd quote-image-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   If you don't have a `requirements.txt`, use:
   ```bash
   pip install discord.py Pillow aiohttp
   ```

3. **Configure your bot token:**
   - Open `discordbots/quoteit.py`
   - Replace `YOUR BOT TOKEN` with your actual Discord bot token.

4. **(Optional) Install Arial Font:**
   - The bot uses `arial.ttf` for text rendering. If you get font errors, either install Arial or adjust the font in the code.

5. **Run the bot:**
   ```bash
   python discordbots/quoteit.py
   ```

## Usage

### Slash Command

Type `/quoteimage` in any channel. The bot will create a quote image from the most recent message.

### Context Menu

Right-click any message, select **Apps → Make Quote Image**. The bot will reply with a quote image of that message.

## Permissions

The bot needs the following permissions:

- Read Messages/View Channels
- Send Messages
- Attach Files
- Use Slash Commands

## Troubleshooting

- **Font errors**: Make sure `arial.ttf` is available, or change the font in the code.
- **No image generated**: Ensure the bot has permission to read messages and attach files.
- **Bot not responding**: Check your bot token and that the bot is invited with the correct permissions.

## License

MIT License

---
