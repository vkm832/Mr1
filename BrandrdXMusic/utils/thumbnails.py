import os
import re
import random

import aiofiles
import aiohttp

from PIL import Image, ImageDraw, ImageEnhance
from PIL import ImageFont, ImageOps

from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from BrandrdXMusic import app
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
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
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # 🎨 Professional Styling Start
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#00FFFF", "#FFA500"]
        border = random.choice(colors)

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)

        # Brightness + Contrast adjust
        bg_bright = ImageEnhance.Brightness(image1).enhance(1.1)
        bg_logo = ImageEnhance.Contrast(bg_bright).enhance(1.1)

        # Add border
        background = ImageOps.expand(bg_logo, border=8, fill=border)

        # Draw text
        draw = ImageDraw.Draw(background)
        title_font = ImageFont.truetype("BrandrdXMusic/assets/font.ttf", 50)
        info_font = ImageFont.truetype("BrandrdXMusic/assets/font2.ttf", 35)
        brand_font = ImageFont.truetype("BrandrdXMusic/assets/font2.ttf", 32)

        # Song Title
        song_title = clear(title)
        if len(song_title) > 45:
            song_title = song_title[:45] + "..."

        draw.text((50, 50), f"🎶 {song_title}", fill="white", font=title_font)
        draw.text((50, 130), f"⏱ Duration: {duration}", fill="#00FFFF", font=info_font)
        draw.text((50, 180), f"📺 {channel}", fill="#FFD700", font=info_font)

        # Branding bottom center
        brand_text = f"Provided by {app.name}"
        w, h = draw.textsize(brand_text, font=brand_font)
        draw.text(((1280 - w) // 2, 660), brand_text, fill="#FF5733", font=brand_font)
        # 🎨 Professional Styling End

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL