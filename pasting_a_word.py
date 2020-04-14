from PIL import Image, ImageDraw, ImageFont
from random import randint
import os

def draw_a_word(file_path, path_to_wordlist='./database/russian.txt',
                fonts_dir='./database/fonts'):
    stroke_color = (0, 0, 0)
    font_color = 'white'

    random_line = randint(0, 1531463)
    with open(path_to_wordlist, encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx == random_line:
                random_word = line

    _, _, files = next(os.walk(fonts_dir))
    file_count = len(files)
    random_font_number = randint(0, file_count - 1)

    img = Image.open(file_path)

    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    font_size = (height + width) // 18

    random_font = ImageFont.truetype(f'./database/fonts/{random_font_number}.otf', font_size)
    word_width, word_height = draw.textsize(random_word, font=random_font)


    draw.text(((width - word_width) / 2, height - word_height + 10),
              text=random_word,
              font=random_font,
              fill=font_color,
              stroke_width=1,
              stroke_fill=stroke_color)

    img.save(file_path)
