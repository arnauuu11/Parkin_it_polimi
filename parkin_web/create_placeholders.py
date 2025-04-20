from PIL import Image, ImageDraw, ImageFont
import os

# Create static/images directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

def create_placeholder(width, height, text, filename):
    # Create a new image with a background color
    img = Image.new('RGB', (width, height), color='#e0e0e0')
    
    # Create a draw object
    draw = ImageDraw.Draw(img)
    
    # Use default font
    try:
        font = ImageFont.truetype('arial.ttf', 24)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Draw the text
    draw.text((text_x, text_y), text, fill='#666666', font=font)
    
    # Save the image
    img.save(f'static/images/{filename}')
    print(f"Created: static/images/{filename}")

# Create placeholder images
create_placeholder(1600, 900, 'Hero Background', 'hero.jpg')
create_placeholder(600, 400, 'Security System', 'security-system.jpg')
create_placeholder(600, 400, 'About Us', 'about-us.jpg')
create_placeholder(150, 150, 'Team Member 1', 'team-1.jpg')
create_placeholder(150, 150, 'Team Member 2', 'team-2.jpg')
create_placeholder(150, 150, 'Team Member 3', 'team-3.jpg')