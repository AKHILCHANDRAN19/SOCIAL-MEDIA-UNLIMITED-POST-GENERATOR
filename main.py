from PIL import Image, ImageDraw, ImageFont
import os
import re

# Define paths
input_folder = '/storage/emulated/0/input'
fonts_folder = '/storage/emulated/0/fonts'
output_folder = '/storage/emulated/0/output'

# Ensure output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def list_fonts(fonts_folder):
    return [f for f in os.listdir(fonts_folder) if f.endswith('.ttf')]

def select_font(fonts_folder):
    fonts = list_fonts(fonts_folder)
    if not fonts:
        raise ValueError("No fonts found in the fonts folder.")
    print("Select a font:")
    for i, font in enumerate(fonts):
        print(f"{i}: {font}")
    choice = int(input("Enter the number of your choice: "))
    if choice < 0 or choice >= len(fonts):
        raise ValueError("Invalid choice.")
    return os.path.join(fonts_folder, fonts[choice])

def gradient_color(start_color, end_color, steps):
    """Generate a list of gradient colors."""
    return [
        (
            int(start_color[0] + (end_color[0] - start_color[0]) * i / steps),
            int(start_color[1] + (end_color[1] - start_color[1]) * i / steps),
            int(start_color[2] + (end_color[2] - start_color[2]) * i / steps)
        )
        for i in range(steps + 1)
    ]

def get_gradient_colors(choice):
    """Return the gradient colors based on user choice."""
    if choice == 1:
        # Silver to Gold gradient
        return gradient_color((192, 192, 192), (255, 215, 0), 10)
    elif choice == 2:
        # Magenta to Green gradient
        return gradient_color((255, 0, 255), (0, 255, 0), 10)
    elif choice == 3:
        # Yellow to Purple gradient
        return gradient_color((255, 255, 0), (128, 0, 128), 10)
    elif choice == 4:
        # Black and White gradient
        return gradient_color((0, 0, 0), (255, 255, 255), 10)
    elif choice == 5:
        # Black color only
        return [(0, 0, 0)]
    elif choice == 6:
        # White color only
        return [(255, 255, 255)]
    elif choice == 7:
        # Black and White combination
        return [(0, 0, 0), (255, 255, 255)]
    elif choice == 8:
        # Silver color only
        return [(192, 192, 192)]
    elif choice == 9:
        # Gold color only
        return [(255, 215, 0)]
    elif choice == 10:
        # Silver and Gold combination
        return [(192, 192, 192), (255, 215, 0)]
    else:
        raise ValueError("Invalid color choice.")

def wrap_text(draw, text, font, max_width):
    """Wrap the text into multiple lines to fit the specified width."""
    lines = []
    words = text.split()
    line = ''
    for word in words:
        test_line = f'{line} {word}'.strip()
        text_width, _ = draw.textbbox((0, 0), test_line, font=font)[2:4]
        if text_width <= max_width:
            line = test_line
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def sanitize_text(text):
    """Remove any unexpected characters or symbols from the text, and remove numeric prefixes."""
    text = re.sub(r'^\d+\.\s*', '', text).strip()
    sanitized_text = re.sub(r'[^\w\s.,?!\'-]', '', text)
    return sanitized_text.strip()

def add_text_to_image(image_path, text, font_path, font_size, output_path, gradient_colors, placement):
    try:
        image = Image.open(image_path)
    except IOError:
        raise ValueError("Error opening image file.")
    
    draw = ImageDraw.Draw(image)
    width, height = image.size

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        raise ValueError("Error loading font file.")
    
    max_width = width - 40
    text = sanitize_text(text)
    lines = wrap_text(draw, text, font, max_width)
    
    line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
    total_height = line_height * len(lines) + 10 * (len(lines) - 1)

    if placement == 'top':
        y = 20
    elif placement == 'middle':
        y = (height - total_height) / 2
    elif placement == 'bottom':
        margin_from_bottom = 50
        y = height - total_height - margin_from_bottom
    else:
        raise ValueError("Invalid placement option.")

    if y < 0:
        raise ValueError("Text is too large to fit within the image with the specified margin.")

    if len(lines) > 1:
        gap = 10
    else:
        gap = 0

    for line in lines:
        words = line.split()
        x = (width - sum(draw.textbbox((0, 0), word, font=font)[2] for word in words) - 10 * (len(words) - 1)) / 2
        for i, word in enumerate(words):
            text_width, _ = draw.textbbox((0, 0), word, font=font)[2:4]
            color = gradient_colors[i % len(gradient_colors)]
            draw.text((x, y), word, font=font, fill=color)
            x += text_width + 10
        y += line_height + gap

    image.save(output_path)
    print(f"Image saved as {output_path}")

def process_images_with_quotes(input_folder, quotes, font_path, font_size, gradient_colors, placement):
    images = [f for f in os.listdir(input_folder) if f.endswith(('jpg', 'jpeg', 'png'))]
    if not images:
        raise ValueError("No images found in the input folder.")
    
    for i, image_name in enumerate(images, start=1):
        image_path = os.path.join(input_folder, image_name)
        for j, quote in enumerate(quotes, start=1):
            output_path = os.path.join(output_folder, f"{i}_{j}.jpg")
            add_text_to_image(image_path, quote, font_path, font_size, output_path, gradient_colors, placement)

def main():
    try:
        print("Enter the quotes (type 'done' when finished):")
        quotes = []
        while True:
            quote = input()
            if quote.lower() == 'done':
                break
            sanitized_quote = sanitize_text(quote)
            if sanitized_quote:
                quotes.append(sanitized_quote)

        if not quotes:
            raise ValueError("No valid quotes provided.")

        print("Select a color scheme:")
        print("1: Silver to Gold gradient")
        print("2: Magenta to Green gradient")
        print("3: Yellow to Purple gradient")
        print("4: Black and White gradient")
        print("5: Black color only")
        print("6: White color only")
        print("7: Black and White combination")
        print("8: Silver color only")
        print("9: Gold color only")
        print("10: Silver and Gold combination")
        color_choice = int(input("Enter the number of your choice: "))
        gradient_colors = get_gradient_colors(color_choice)

        print("Select text placement:")
        print("1: Top")
        print("2: Middle")
        print("3: Bottom")
        placement_choice = int(input("Enter the number of your choice: "))
        placement_options = {1: 'top', 2: 'middle', 3: 'bottom'}
        placement = placement_options.get(placement_choice, 'bottom')

        font_path = select_font(fonts_folder)
        font_size = int(input("Enter the font size (e.g., 40): "))
        process_images_with_quotes(input_folder, quotes, font_path, font_size, gradient_colors, placement)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
