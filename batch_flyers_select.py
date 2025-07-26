import os
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog

# Function to get folder path from user
def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide main window
    folder_selected = filedialog.askdirectory(title="Select folder with QR codes")
    root.destroy()
    return folder_selected

def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def create_flyer(qr_path, save_path, flyer_width=850, flyer_height=1100):
    qr_code = Image.open(qr_path).convert("L")

    flyer = Image.new("L", (flyer_width, flyer_height), color=255)  # white background
    draw = ImageDraw.Draw(flyer)

    title_text = "■ SIGNAL FOUND ■"
    subtitle_text = "tip the ghost"
    info_lines = [
        "xmr: [scan code]",
        "no logs. no names. no memory."
    ]

    try:
        title_font = ImageFont.truetype("DejaVuSansMono.ttf", 36)
        body_font = ImageFont.truetype("DejaVuSansMono.ttf", 18)
    except IOError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Draw title + subtitle
    draw.text(((flyer_width - text_width(draw, title_text, title_font)) / 2, 80),
              title_text, font=title_font, fill=0)
    draw.text(((flyer_width - text_width(draw, subtitle_text, body_font)) / 2, 140),
              subtitle_text, font=body_font, fill=0)

    # Resize and paste QR code
    qr_size = 300
    qr_code = qr_code.resize((qr_size, qr_size))
    flyer.paste(qr_code, ((flyer_width - qr_size) // 2, 200))

    # Draw bottom info lines
    y = 520
    for line in info_lines:
        draw.text(((flyer_width - text_width(draw, line, body_font)) / 2, y),
                  line, font=body_font, fill=0)
        y += 30

    flyer.save(save_path)
    print(f"Saved flyer: {save_path}")

def main():
    input_folder = select_folder()
    if not input_folder:
        print("No folder selected, exiting.")
        return

    output_folder = os.path.join(input_folder, "flyers_out")
    os.makedirs(output_folder, exist_ok=True)

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(".png")]

    if not files:
        print(f"No PNG files found in {input_folder}.")
        return

    for file in files:
        qr_path = os.path.join(input_folder, file)
        flyer_name = f"flyer_{os.path.splitext(file)[0]}.png"
        save_path = os.path.join(output_folder, flyer_name)
        create_flyer(qr_path, save_path)

if __name__ == "__main__":
    main()
