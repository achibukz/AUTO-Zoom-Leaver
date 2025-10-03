#!/usr/bin/env python3
"""
Simple script to create an app icon from text/emoji
Uses Pillow to generate a basic icon for the app
"""

import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

def create_simple_icon():
    """Create a simple text-based icon"""
    if not PILLOW_AVAILABLE:
        print("⚠️  Pillow not installed. Install with: pip install pillow")
        return False
    
    # Create 1024x1024 icon (will be scaled down by macOS)
    size = 1024
    img = Image.new('RGBA', (size, size), (70, 130, 180, 255))  # Steel blue background
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font
    try:
        # Try different font paths for macOS
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Arial.ttf"
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 200)
                break
        
        if font is None:
            font = ImageFont.load_default()
            
    except Exception:
        font = ImageFont.load_default()
    
    # Draw "ZL" text (Zoom Leaver)
    text = "ZL"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 50  # Slightly above center
    
    # Draw text with white color
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    # Draw a small subtitle
    try:
        small_font = ImageFont.truetype(font_paths[0] if font_paths and os.path.exists(font_paths[0]) else None, 60)
    except:
        small_font = font
    
    subtitle = "Auto Leaver"
    bbox2 = draw.textbbox((0, 0), subtitle, font=small_font)
    subtitle_width = bbox2[2] - bbox2[0]
    
    x2 = (size - subtitle_width) // 2
    y2 = y + text_height + 40
    
    draw.text((x2, y2), subtitle, font=small_font, fill=(255, 255, 255, 200))
    
    # Save as PNG first
    img.save("app_icon.png")
    print("✅ Created app_icon.png")
    
    # Try to convert to ICNS (macOS format)
    try:
        # Create iconset directory
        iconset_dir = "app_icon.iconset"
        if os.path.exists(iconset_dir):
            import shutil
            shutil.rmtree(iconset_dir)
        os.makedirs(iconset_dir)
        
        # Generate different sizes for iconset
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(f"{iconset_dir}/icon_{size}x{size}.png")
            if size <= 512:  # Also create @2x versions for retina
                resized.save(f"{iconset_dir}/icon_{size//2}x{size//2}@2x.png")
        
        # Convert to ICNS using iconutil (macOS command)
        result = os.system(f"iconutil -c icns {iconset_dir}")
        if result == 0:
            print("✅ Created app_icon.icns")
            # Clean up iconset
            import shutil
            shutil.rmtree(iconset_dir)
            return True
        else:
            print("⚠️  Could not create ICNS file. PNG will be used instead.")
            
    except Exception as e:
        print(f"⚠️  Error creating ICNS: {e}")
    
    return True

def create_emoji_icon():
    """Create an icon using emoji (simpler approach)"""
    if not PILLOW_AVAILABLE:
        print("⚠️  Pillow not installed for emoji icon creation")
        return False
    
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Draw a background circle
    margin = 100
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=(70, 130, 180, 255), outline=(255, 255, 255, 100), width=10)
    
    # Try to draw emoji or fallback to text
    try:
        # Use Apple Color Emoji font if available
        emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 400)
        emoji = "🏃‍♂️"  # Running person (leaving)
    except:
        emoji_font = ImageFont.load_default()
        emoji = "EXIT"
    
    # Get text size and center it
    bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), emoji, font=emoji_font, fill=(255, 255, 255, 255))
    
    img.save("app_icon_emoji.png")
    print("✅ Created app_icon_emoji.png")
    return True

def main():
    print("🎨 Creating App Icon for Zoom Auto Leaver")
    print("=" * 40)
    
    if not PILLOW_AVAILABLE:
        print("To create custom icons, install Pillow:")
        print("pip install pillow")
        print("\nAlternatively, you can:")
        print("1. Create your own icon and name it 'app_icon.icns'")
        print("2. Use the default system icon")
        return
    
    print("Choose icon type:")
    print("1. Text-based icon (ZL)")
    print("2. Emoji icon (🏃‍♂️)")
    print("3. Skip (use default)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        create_simple_icon()
    elif choice == "2":
        create_emoji_icon()
    elif choice == "3":
        print("Skipping icon creation")
    else:
        print("Invalid choice, creating text icon...")
        create_simple_icon()

if __name__ == "__main__":
    main()