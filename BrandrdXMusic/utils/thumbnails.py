import os
import re
import random
import aiofiles
import aiohttp

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from BrandrdXMusic import app
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


def clear(text):
    parts = text.split(" ")
    title = ""
    for i in parts:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()


async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
            duration = result.get("duration", "Unknown Mins")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            views = result.get("viewCount", {}).get("short", "Unknown Views")
            channel = result.get("channel", {}).get("name", "Unknown Channel")

        # Download YouTube thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # Random border color
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFD700", "#FF69B4", "#00FFFF"]
        border = random.choice(colors)

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)

        # Enhance image
        bg_bright = ImageEnhance.Brightness(image1).enhance(1.15)
        bg_contra = ImageEnhance.Contrast(bg_bright).enhance(1.1)
        logox = ImageOps.expand(bg_contra, border=8, fill=border)
        background = changeImageSize(1280, 720, logox)

        # Draw text
        draw = ImageDraw.Draw(background)
        font_big = ImageFont.truetype("BrandrdXMusic/assets/font2.ttf", 40)
        font_small = ImageFont.truetype("BrandrdXMusic/assets/font.ttf", 28)

        # Title
        draw.text((30, 600), clear(title), fill="white", font=font_big)

        # Channel + Views
        draw.text((30, 650), f"{channel} • {views}", fill="white", font=font_small)

        # Duration
        draw.text((1100, 650), f"⏱ {duration}", fill="white", font=font_small)

        # Footer branding
        footer_text = f"Provided by {unidecode(app.name)}"
        draw.text((30, 20), footer_text, fill=border, font=font_small)

        # Save final
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(f"[Thumbnail Error]: {e}")
        return YOUTUBE_IMG_URL