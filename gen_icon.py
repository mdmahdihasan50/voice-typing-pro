from PIL import Image, ImageDraw, ImageFont
import os

def create_fb_icon():
    size = (64, 64)
    # Facebook Blue
    bg_color = "#1877F2"
    text_color = "white"
    
    img = Image.new('RGBA', size, (0, 0, 0, 0)) # Transparent View
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle (or just circle/square)
    draw.rounded_rectangle([(0, 0), size], radius=15, fill=bg_color)
    
    # Draw 'f' text
    # Since we might not have a bold font file handy, we'll draw a simple 'f' shape or try default font
    # Drawing a simple 'f' shape manually for better looking icon without font dependency
    
    # F vertical bar
    # draw.rectangle([(35, 15), (45, 55)], fill=text_color)
    # F top bar
    # draw.rectangle([(25, 15), (45, 25)], fill=text_color) # simplistic
    
    # Better: Use text with default font if valid, but default font size is unpredictable.
    # Let's try drawing a crude 'f' manually to be safe and recognizable.
    
    # Vertical stem
    draw.rectangle([(38, 25), (46, 58)], fill=text_color)
    
    # Cross bar
    draw.rectangle([(32, 32), (50, 40)], fill=text_color)
    
    # Top Hook (simplified)
    draw.polygon([(38, 25), (46, 25), (46, 15), (55, 15), (55, 8), (38, 8)], fill=text_color)

    # Actually, a simple text "f" usually works best if we had a font. 
    # Let's stick to a very simple "f" text using load_default if valid, otherwise manual.
    try:
        # Try to load Arial or similar
        font = ImageFont.truetype("arial.ttf", 45)
        text = "f"
        # Get text size
        # left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        # text_w = right - left
        # text_h = bottom - top
        # Pos
        # x = (size[0] - text_w) / 2
        # y = (size[1] - text_h) / 2
        
        # Manually tune pos for 'f' to look like logo (usually off-center right, bottom)
        draw.text((22, 5), text, font=font, fill=text_color)
        
    except IOError:
        # Fallback to manual drawing if arial not found
        draw.rectangle([(20, 10), (50, 50)], fill="white")

    img.save("fb_icon.png")
    print("Icon created: fb_icon.png")

if __name__ == "__main__":
    create_fb_icon()
