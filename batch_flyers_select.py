import os
import random
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog, simpledialog

def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def create_flyer(qr_code, save_path, flyer_width=850, flyer_height=1100,
                 title_font_size=36, body_font_size=18,
                 qr_offset=(0,0), qr_rotation=0,
                 glitch_offset=3,
                 bg_noise=False,
                 title_style='normal'):
    flyer = Image.new("L", (flyer_width, flyer_height), color=255)  # white background
    draw = ImageDraw.Draw(flyer)

    title_text = "■ SIGNAL FOUND ■"
    subtitle_text = "tip the ghost"
    info_lines = [
        "xmr: [scan code]",
        "no logs. no names. no memory."
    ]

    # Optional: add Y2K-style subtle noise background if selected
    if bg_noise:
        import numpy as np
        arr = (np.random.rand(flyer_height, flyer_width) * 30).astype('uint8')
        noise_img = Image.fromarray(arr, mode='L')
        flyer = Image.composite(noise_img, flyer, mask=noise_img)
        draw = ImageDraw.Draw(flyer)

    try:
        title_font = ImageFont.truetype("DejaVuSansMono.ttf", title_font_size)
        body_font = ImageFont.truetype("DejaVuSansMono.ttf", body_font_size)
    except IOError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Title styling variants
    x_title = (flyer_width - text_width(draw, title_text, title_font)) / 2
    y_title = 80
    if title_style == 'glitch':
        for dx, dy in [(0,0), (glitch_offset,0), (-glitch_offset, glitch_offset)]:
            draw.text((x_title + dx, y_title + dy), title_text, font=title_font, fill=0)
    elif title_style == 'shadow':
        draw.text((x_title + 2, y_title + 2), title_text, font=title_font, fill=150)
        draw.text((x_title, y_title), title_text, font=title_font, fill=0)
    else:
        draw.text((x_title, y_title), title_text, font=title_font, fill=0)

    # Subtitle with slight random offset
    x_sub = (flyer_width - text_width(draw, subtitle_text, body_font)) / 2
    y_sub = 140 + random.randint(-2,2)
    draw.text((x_sub, y_sub), subtitle_text, font=body_font, fill=0)

    # Prep QR code with rotation and offset
    qr_size = 300
    qr_resized = qr_code.resize((qr_size, qr_size))
    qr_rotated = qr_resized.rotate(qr_rotation, expand=True, fillcolor=255)

    qr_x = (flyer_width - qr_rotated.width) // 2 + qr_offset[0]
    qr_y = 200 + qr_offset[1]

    flyer.paste(qr_rotated, (qr_x, qr_y))

    # Draw info lines with kinda random horizontal shifts
    y = 520
    for line in info_lines:
        x = (flyer_width - text_width(draw, line, body_font)) / 2 + random.randint(-3,3)
        draw.text((x, y), line, font=body_font, fill=0)
        y += 30

    flyer.save(save_path)
    print(f"Saved flyer: {save_path}")

def prompt_int(title, prompt, min_val, max_val, default):
    root = tk.Tk()
    root.withdraw()
    val = simpledialog.askinteger(title, prompt, minvalue=min_val, maxvalue=max_val, initialvalue=default)
    root.destroy()
    return val

def prompt_choice(title, prompt, options, default):
    root = tk.Tk()
    root.withdraw()
    val = simpledialog.askstring(title, f"{prompt}\nOptions: {', '.join(options)}", initialvalue=default)
    root.destroy()
    if val and val.lower() in options:
        return val.lower()
    return default

def main():
    root = tk.Tk()
    root.withdraw()

    input_folder = filedialog.askdirectory(title="Select folder with QR codes")
    if not input_folder:
        print("No folder selected, exiting.")
        return

    output_folder = os.path.join(input_folder, "flyers_out")
    os.makedirs(output_folder, exist_ok=True)

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(".png")]

    if not files:
        print(f"No PNG files found in {input_folder}.")
        return

    # Prompt style options
    num_variations = prompt_int("Flyers per QR",
                                "How many flyer variations per QR code?",
                                1, 50, 5)
    title_font_min = prompt_int("Title Font Size",
                                "Minimum title font size?",
                                24, 72, 30)
    title_font_max = prompt_int("Title Font Size",
                                "Maximum title font size?",
                                title_font_min, 72, 42)
    body_font_min = prompt_int("Body Font Size",
                               "Minimum body font size?",
                               12, 36, 16)
    body_font_max = prompt_int("Body Font Size",
                               "Maximum body font size?",
                               body_font_min, 36, 20)
    max_qr_rotation = prompt_int("Max QR Rotation",
                                 "Maximum rotation of QR code (degrees)?",
                                 0, 20, 5)
    max_qr_offset = prompt_int("Max QR Offset",
                               "Maximum pixel offset of QR code (X and Y)?",
                               0, 30, 15)

    glitch_level = prompt_choice("Glitch Intensity",
                                 "Choose glitch intensity",
                                 ['none', 'low', 'medium', 'high'],
                                 'medium')

    # Map glitch level to glitch offset pixels
    glitch_map = {'none': 0, 'low': 1, 'medium': 3, 'high': 6}
    glitch_offset = glitch_map.get(glitch_level, 3)

    # Title style choice (normal, glitch, shadow)
    title_style = prompt_choice("Title Style",
                                "Choose title style",
                                ['normal', 'glitch', 'shadow'],
                                'glitch')

    print("\nStarting flyer generation...\n")

    for file in files:
        qr_path = os.path.join(input_folder, file)
        qr_code = Image.open(qr_path).convert("L")

        for i in range(1, num_variations + 1):
            title_font_size = random.randint(title_font_min, title_font_max)
            body_font_size = random.randint(body_font_min, body_font_max)
            qr_offset = (random.randint(-max_qr_offset, max_qr_offset),
                         random.randint(-max_qr_offset, max_qr_offset))
            qr_rotation = random.randint(-max_qr_rotation, max_qr_rotation)

            flyer_name = f"flyer_{os.path.splitext(file)[0]}_{i}.png"
            save_path = os.path.join(output_folder, flyer_name)

            create_flyer(qr_code, save_path,
                         title_font_size=title_font_size,
                         body_font_size=body_font_size,
                         qr_offset=qr_offset,
                         qr_rotation=qr_rotation,
                         glitch_offset=glitch_offset,
                         title_style=title_style)

    print("\nDone generating flyers! Check your 'flyers_out' folder.")

if __name__ == "__main__":
    main()
