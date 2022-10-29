import datetime
import io
import itertools
import json
import os
import re

from PIL import Image, ImageFont, ImageDraw
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.files.storage import default_storage
from pyarabic import araby


def base_split_words(text, arabic):
    if arabic:
        return araby.tokenize(text)
    return text.split(" ")


def save_page_data(file_name, dimen_name, page_data):
    response = {"page_data": []}
    for word, bboxes in page_data:
        word_resp = {"text": word, "bboxes": []}
        for bbox in bboxes:
            left, top, right, bottom = bbox
            word_resp["bboxes"].append({
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom
            })
        response["page_data"].append(word_resp)

    byteio = io.StringIO()
    json.dump(response, byteio)
    final_path = f"book_image_metadata/{file_name}-{dimen_name}.json"
    if default_storage.exists(final_path):
        default_storage.delete(final_path)
    default_storage.save(final_path, byteio)
    byteio.close()


def fix_non_arabic_page_data(text, page_data):
    split_text = split_words(settings.BOOK_SPECIAL_WORDS, text)
    final = [(word, []) for word in split_text]

    words_and_index = []
    for index, line in enumerate(split_text):
        for word in line.split(" "):
            words_and_index.append((word, index))

    for data, word_and_index in zip(page_data, words_and_index):
        word, left, top, right, bottom = data
        word_1, index = word_and_index
        final[index][1].append([left, top, right, bottom])

    return final


def normalize_lines(page_data):
    """
    Merge one line words to one bbox

    :param page_data:
    :return: page_data
    """
    lines = []
    for word, bboxes in page_data:
        if len(bboxes) == 1:
            lines.append((word, bboxes))
            continue

        final_bboxes = []
        line_groups = itertools.groupby(bboxes, key=lambda bbox: bbox[1])
        for _, g_bboxes in line_groups:
            g_bboxes = list(g_bboxes)
            if len(g_bboxes) == 1:
                final_bboxes += g_bboxes
                continue

            left = min([b[0] for b in g_bboxes])
            right = max([b[2] for b in g_bboxes])
            top = g_bboxes[0][1]
            bottom = g_bboxes[0][3]
            final_bboxes.append([left, top, right, bottom])
        lines.append((word, final_bboxes))

    return lines


def fix_arabic_page_data(page_data):
    """
    Because aur arabic page is one data, then we need to make all lines in the one text
    :param page_data:
    :return:
    """
    text = page_data[0][0]
    bboxes = []
    for _, left, top, right, bottom in page_data:
        bboxes.append((left, top, right, bottom))

    return [[text, bboxes]]


def process_page_image(text, file_name, arabic=False):
    """
    the main function used for generating image from the text

    :param text: text we want to render it into image
    :param file_name: base file name used to save image, and it's bounding boxes
    :param arabic: check is the text arabic or not
    :return: Nothing
    """

    # we replace new lines
    text = text.replace("\n", " ").strip()

    sizes = settings.BOOK_IMAGE_SIZES
    for image_size, font_size, dimen_name in sizes:
        font = initialize_font(font_size, arabic)
        space_box = font.getbbox(" ")

        image = Image.new("RGBA", image_size, (0, 0, 0, 0))
        canvas = ImageDraw.Draw(image)
        words = base_split_words(text, arabic)
        lines = wrap_text(words, font, image.width * 0.8)
        y, line_heights = get_y_and_heights(lines, image.size, 0, font)

        page_data = []

        for idx, line in enumerate(lines):
            x = image.width // 2

            canvas.text((x + 1, y + 1), line, font=font, anchor="ma", fill="grey")
            canvas.text((x, y), line, font=font, anchor="ma", fill="black")

            box_line = canvas.textbbox((x, y), line, font=font, anchor="ma")

            if arabic:
                page_data.append([text] + list(box_line))
                y += line_heights[idx]
                continue

            box_left, box_top, box_right, box_bottom = box_line

            word_x = box_left
            for word in base_split_words(line, arabic):
                word_left, word_top, word_right, word_bottom = font.getbbox(word)

                word_final_box = (word_left + word_x, box_top, word_right + word_x, box_bottom)

                # increase x
                word_x += word_right + space_box[2]

                page_data.append([word] + list(word_final_box))

            y += line_heights[idx]

        # finalize data
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        final_fname = f"books_image/{file_name}-{dimen_name}.png"
        if default_storage.exists(final_fname):
            default_storage.delete(final_fname)
        default_storage.save(final_fname, img_byte_arr)
        img_byte_arr.close()
        image.close()

        if arabic:
            page_data = fix_arabic_page_data(page_data)
            save_page_data(file_name, dimen_name, page_data)
            continue

        page_data = fix_non_arabic_page_data(text, page_data)
        page_data = normalize_lines(page_data)
        save_page_data(file_name, dimen_name, page_data)


def wrap_text(words, font, max_width):
    # simpan list
    lines = []
    # simpan current_line
    current_line = ""
    # untuk setiap word:
    for word in words:
    # temp_line = current + word + " " // temp_line = " ".join(current, word)
        temp_line = " ".join([current_line, word])
    # hitung >= max_width -> menambahkan ke list + current line == word ?: current line = temp line
        width = font.getbbox(temp_line)[2]  # x,y,x,y
        if width >= max_width:
            lines.append(current_line.strip())
            current_line = word
        else:
            current_line = temp_line

    # keluar dari loop -> jangan lupa tambahkan current line
    lines.append(current_line.strip())

    # lines
    return lines


def get_y_and_heights(text_wrapped, dimensions, margin, font):
    """Get the first vertical coordinate at which to draw text and the height of each line of text"""
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    # Calculate the height needed to draw each line of text (including its bottom margin)
    line_heights = []

    for _ in text_wrapped:
        line_heights.append(
            ascent + descent
        )

    line_heights[-1] -= margin

    # Total height needed
    height_text = sum(line_heights)

    # Calculate the Y coordinate at which to draw the first line of text
    y = (dimensions[1] - height_text) // 2

    # Return the first Y coordinate and a list with the height of each line
    return y, line_heights


def split_words(special_words, text):
    special_words_pattern = "|".join(special_words)
    separators = "[,.?!]?"
    text_pattern = f"(?P<final>({special_words_pattern}|[\w\-\'\`’]+){separators})"
    pattern = re.compile(text_pattern)

    final_words = []
    for match in re.finditer(pattern, text):
        res = match.groupdict().get("final")
        if res:
            final_words.append(res)
    return final_words


def initialize_font(font_size, arabic=False):
    if arabic:
        font_name = "uthman-toha.ttf"
    else:
        font_name = "BookWorm.ttf"

    abs_font_path = os.path.join(settings.FONTS_DIRECTORY, font_name)
    return ImageFont.truetype(abs_font_path, font_size)


def is_arabic(text):
    """
    check the text is arabic or not. Just check if any arabic character
    :param text:
    :return: True if any arabic character found else False
    """

    pattern = r"[\u0600-\u06FF]"
    resp = re.search(pattern, text)
    return resp is not None


def stamp_book(f_name):
    final_f_name = f"books_image/{f_name}"
    if default_storage.exists(final_f_name):
        default_storage.delete(final_f_name)

    timestamp = io.StringIO(str(datetime.datetime.now().timestamp()))
    default_storage.save(final_f_name, timestamp)
    timestamp.close()
