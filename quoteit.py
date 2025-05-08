import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import aiohttp
import traceback

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

async def fetch_image_data(session, url):
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.read()
        return None

def wrap_text(text, font, max_width):
    lines = []
    if font.getbbox(text)[2] <= max_width:
        lines.append(text)
    else:
        words = text.split(' ')
        i = 0
        while i < len(words):
            line = ''
            while i < len(words) and font.getbbox(line + words[i])[2] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line and i < len(words):
                lines.append(words[i]) 
                i += 1
                continue
            elif not line and i >= len(words):
                 break 
            lines.append(line.strip())
    return lines

async def generate_quote_image(interaction_or_message, quote_text, author_obj, bot_user):
    author_pfp_url = author_obj.display_avatar.url

    async with aiohttp.ClientSession() as session:
        pfp_data = await fetch_image_data(session, str(author_pfp_url))

    if not pfp_data:
        return None, "Could not download the profile picture."

    try:
        original_pfp_image = Image.open(io.BytesIO(pfp_data)).convert("RGBA")
        original_pfp_w, original_pfp_h = original_pfp_image.size

        processed_pfp = original_pfp_image.convert("L").convert("RGBA")
        processed_pfp = processed_pfp.filter(ImageFilter.GaussianBlur(radius=1.5))

        gradient_width = max(20, min(int(original_pfp_w * 0.25), 60))
        if gradient_width > original_pfp_w:
            gradient_width = original_pfp_w

        alpha_mask = Image.new('L', (original_pfp_w, original_pfp_h), 255)
        draw_mask = ImageDraw.Draw(alpha_mask)
        for x_coord in range(original_pfp_w - gradient_width, original_pfp_w):
            alpha_value = int(255 * ((original_pfp_w - x_coord) / float(gradient_width)))
            alpha_value = max(0, min(255, alpha_value))
            draw_mask.line([(x_coord, 0), (x_coord, original_pfp_h)], fill=alpha_value)
        processed_pfp.putalpha(alpha_mask)

        text_area_width = int(original_pfp_w * 1.65)
        if text_area_width < 350: text_area_width = 350
        if original_pfp_w > 400 and text_area_width < original_pfp_w * 0.85:
            text_area_width = int(original_pfp_w * 0.85)

        canvas_width = original_pfp_w + text_area_width
        canvas_height = original_pfp_h

        main_canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 255))

        main_canvas.paste(processed_pfp, (0, 0), processed_pfp)

        draw_on_main = ImageDraw.Draw(main_canvas)
        text_color = (255, 255, 255)

        text_block_start_x = original_pfp_w
        text_block_render_width = text_area_width
        text_block_padding = int(text_block_render_width / 12)

        font_size_main = int(canvas_height / 7.5) 
        if font_size_main * 1.5 > text_block_render_width : 
            font_size_main = int(text_block_render_width / 10) 
        if font_size_main < 14: font_size_main = 14
        
        try: main_font = ImageFont.truetype("arial.ttf", font_size_main)
        except IOError: main_font = ImageFont.load_default()

        max_content_width_for_quote = text_block_render_width - (2 * text_block_padding)
        wrapped_quote_lines = wrap_text(f'"{quote_text}"', main_font, max_content_width_for_quote)

        quote_block_total_height = 0
        line_spacing_main = int(font_size_main * 0.2)
        for i, line_content in enumerate(wrapped_quote_lines):
            quote_block_total_height += main_font.getbbox(line_content)[3] - main_font.getbbox(line_content)[1]
            if i < len(wrapped_quote_lines) - 1: quote_block_total_height += line_spacing_main
        
        current_y_main = (canvas_height - quote_block_total_height) / 2
        if current_y_main < text_block_padding : current_y_main = text_block_padding

        for line_content in wrapped_quote_lines:
            line_content_width = main_font.getbbox(line_content)[2]
            x_pos_quote_line = text_block_start_x + text_block_padding + (max_content_width_for_quote - line_content_width) / 2
            draw_on_main.text((x_pos_quote_line, current_y_main), line_content, font=main_font, fill=text_color)
            current_y_main += main_font.getbbox(line_content)[3] - main_font.getbbox(line_content)[1] + line_spacing_main

        author_display_name_text = f"- {author_obj.display_name}"
        author_username_text = f"@{author_obj.name}"
        font_size_author = int(font_size_main * 0.55)
        if font_size_author < 11: font_size_author = 11
        line_spacing_author = int(font_size_author * 0.18)
        try: author_font = ImageFont.truetype("arial.ttf", font_size_author)
        except IOError: author_font = ImageFont.load_default()
        
        author_line1_h = author_font.getbbox(author_display_name_text)[3] - author_font.getbbox(author_display_name_text)[1]
        author_line2_h = author_font.getbbox(author_username_text)[3] - author_font.getbbox(author_username_text)[1]
        author_block_total_h = author_line1_h + author_line2_h + line_spacing_author

        author_y_start = current_y_main + text_block_padding / 2 
        if author_y_start + author_block_total_h > canvas_height - text_block_padding: 
            author_y_start = canvas_height - text_block_padding - author_block_total_h

        author_line1_width = author_font.getbbox(author_display_name_text)[2]
        x_pos_author_line1 = text_block_start_x + text_block_render_width - text_block_padding - author_line1_width
        draw_on_main.text((x_pos_author_line1, author_y_start), author_display_name_text, font=author_font, fill=text_color)
        author_y_start += author_line1_h + line_spacing_author
        
        author_line2_width = author_font.getbbox(author_username_text)[2]
        x_pos_author_line2 = text_block_start_x + text_block_render_width - text_block_padding - author_line2_width
        draw_on_main.text((x_pos_author_line2, author_y_start), author_username_text, font=author_font, fill=text_color)
        
        author_block_final_y = author_y_start + author_line2_h

        watermark_text = f"{bot_user.name}#{bot_user.discriminator}"
        font_size_watermark = int(font_size_author * 0.85)
        if font_size_watermark < 10: font_size_watermark = 10
        try: watermark_font = ImageFont.truetype("arial.ttf", font_size_watermark)
        except IOError: watermark_font = ImageFont.load_default()
        
        watermark_color = (180, 180, 180)
        watermark_text_width = watermark_font.getbbox(watermark_text)[2]
        watermark_text_height = watermark_font.getbbox(watermark_text)[3] - watermark_font.getbbox(watermark_text)[1]
        
        watermark_x_pos = text_block_start_x + text_block_render_width - text_block_padding - watermark_text_width
        watermark_y_pos = canvas_height - text_block_padding - watermark_text_height

        if watermark_y_pos < author_block_final_y + line_spacing_author:
             watermark_y_pos = author_block_final_y + line_spacing_author + int(text_block_padding / 3)
             if watermark_y_pos + watermark_text_height > canvas_height - int(text_block_padding / 3):
                 watermark_y_pos = canvas_height - watermark_text_height - int(text_block_padding / 3)

        draw_on_main.text((watermark_x_pos, watermark_y_pos), watermark_text, font=watermark_font, fill=watermark_color)

        img_byte_arr = io.BytesIO()
        main_canvas.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        discord_file = discord.File(fp=img_byte_arr, filename='quote_image.png')
        return discord_file, None

    except Exception as e:
        print(f"Error during image processing: {e}")
        traceback.print_exc()
        return None, "An error occurred while creating the image."

@bot.tree.command(name="quoteimage", description="Creates an image with the previous message as a quote on the sender's PFP.")
async def quoteimage(interaction: discord.Interaction):
    await interaction.response.defer()
    target_message = None
    async for message_history_item in interaction.channel.history(limit=1):
        target_message = message_history_item
        break

    if not target_message or not target_message.content:
        await interaction.followup.send("Could not find a message with text to quote.", ephemeral=True)
        return

    discord_file, error_message = await generate_quote_image(target_message, target_message.content, target_message.author, bot.user)

    if error_message:
        await interaction.followup.send(error_message, ephemeral=True)
    else:
        await interaction.followup.send(file=discord_file)

@bot.tree.context_menu(name="Make Quote Image")
async def quote_image_context_menu(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=False)

    if not message.content:
        await interaction.followup.send("The selected message has no text content.", ephemeral=True)
        return

    discord_file, error_message = await generate_quote_image(message, message.content, message.author, bot.user)

    if error_message:
        await interaction.followup.send(error_message, ephemeral=True)
    else:
        await interaction.followup.send(file=discord_file)

BOT_TOKEN = "YOUR BOT TOKEN"
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
