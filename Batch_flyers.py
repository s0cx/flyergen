import os
import random
from PIL import Image, ImageDraw, ImageFont

def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def create_flyer(qr_code, save_path, flyer_width=850, flyer_height=1100):
    flyer = Image.new("L", (flyer_width, flyer_height), color=255)  # white background
    draw = ImageDraw.Draw(flyer)

    title_text = "■■■ SIGNAL FOUND ■■■"
    subtitle_text = "Whisper to the void."
    info_lines = [
        "xmr only: [scan code]",
        "no logs. no names. no memory."
    ]

    # subtle background noise
    try:
        import numpy as np
        arr = (np.random.rand(flyer_height, flyer_width) * 15).astype('uint8')  # light noise
        noise_img = Image.fromarray(arr, mode='L')
        flyer = Image.composite(noise_img, flyer, mask=noise_img)
        draw = ImageDraw.Draw(flyer)
    except ImportError:
        pass  # no numpy, skip noise

    # fonts, fallback to default if DejaVu not found
    try:
        title_font_size = random.randint(28, 38)
        body_font_size = random.randint(14, 22)
        title_font = ImageFont.truetype("DejaVuSansMono.ttf", title_font_size)
        body_font = ImageFont.truetype("DejaVuSansMono.ttf", body_font_size)
    except IOError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # glitch offset for title
    glitch_offset = random.choice([0,1,2,3])

    x_title = (flyer_width - text_width(draw, title_text, title_font)) / 2
    y_title = 80
    # glitch effect layers
    if glitch_offset > 0:
        for dx, dy, fill in [(0,0,0), (glitch_offset,0, 100), (-glitch_offset, glitch_offset, 150)]:
            draw.text((x_title + dx, y_title + dy), title_text, font=title_font, fill=fill)
    else:
        draw.text((x_title, y_title), title_text, font=title_font, fill=0)

    # subtitle
    x_sub = (flyer_width - text_width(draw, subtitle_text, body_font)) / 2
    y_sub = 140 + random.randint(-2,2)
    draw.text((x_sub, y_sub), subtitle_text, font=body_font, fill=0)

    # QR code placement, subtle random rotation and offset
    qr_size = 300
    qr_resized = qr_code.resize((qr_size, qr_size))
    qr_rotation = random.uniform(-5, 5)  # small rotation max ±5 degrees
    qr_rotated = qr_resized.rotate(qr_rotation, expand=True, fillcolor=255)

    qr_offset_x = random.randint(-10, 10)
    qr_offset_y = random.randint(-10, 10)

    qr_x = (flyer_width - qr_rotated.width) // 2 + qr_offset_x
    qr_y = 200 + qr_offset_y

    flyer.paste(qr_rotated, (qr_x, qr_y))

    # info lines
    y = 520
    for line in info_lines:
        x = (flyer_width - text_width(draw, line, body_font)) / 2 + random.randint(-3,3)
        draw.text((x, y), line, font=body_font, fill=0)
        y += 30

    flyer.save(save_path)
    print(f"Saved flyer: {save_path}")

def main():
    import tkinter as tk
    from tkinter import filedialog

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

    flyers_per_qr = 5  # fixed number of flyer variations per QR code

    for file in files:
        qr_path = os.path.join(input_folder, file)
        qr_img = Image.open(qr_path).convert("L")

        for i in range(flyers_per_qr):
            flyer_name = f"flyer_{os.path.splitext(file)[0]}_{i+1}.png"
            flyer_path = os.path.join(output_folder, flyer_name)

            create_flyer(qr_img, flyer_path)

    print(f"\nAll flyers created in folder:\n{output_folder}")

if __name__ == "__main__":
    main()
