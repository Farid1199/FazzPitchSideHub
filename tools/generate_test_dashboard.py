from PIL import Image, ImageDraw, ImageFont
import os

OUT_DIR = 'media/test_assets'
os.makedirs(OUT_DIR, exist_ok=True)
path = os.path.join(OUT_DIR, 'test_fa_dashboard.png')

# Image size
W, H = 1000, 500
bg = (255, 255, 255)
fg = (24, 24, 24)
accent = (0, 84, 166)

img = Image.new('RGB', (W, H), color=bg)
d = ImageDraw.Draw(img)

# Try to load a TTF if available, otherwise use default
try:
    font_bold = ImageFont.truetype('arialbd.ttf', 28)
    font = ImageFont.truetype('arial.ttf', 20)
except Exception:
    font_bold = ImageFont.load_default()
    font = ImageFont.load_default()

# Header bar
d.rectangle([0,0,W,70], fill=accent)
d.text((24, 18), 'England Football Learning', fill=(255,255,255), font=font_bold)

# Profile box
d.rectangle([40, 100, W-40, H-40], outline=(220,220,220), width=2)

# Sample fields
name = 'Alex Coach'
fan = 'FAN1234567'
licence = 'UEFA C Licence (Level 2)'

d.text((70, 130), 'Name:', fill=fg, font=font_bold)
d.text((180, 130), name, fill=fg, font=font)

d.text((70, 170), 'FAN Number:', fill=fg, font=font_bold)
d.text((220, 170), fan, fill=fg, font=font)

d.text((70, 210), 'Licence:', fill=fg, font=font_bold)
d.text((180, 210), licence, fill=fg, font=font)

# Add a fake verification badge area
d.ellipse((W-220, 120, W-120, 220), fill=(245,245,245), outline=(200,200,200))
d.text((W-210, 155), 'Verified', fill=(34,197,94), font=font_bold)

# Footer note
d.text((70, H-80), 'This is a test image for local development only.', fill=(120,120,120), font=font)

img.save(path)
print(path)
