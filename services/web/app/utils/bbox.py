from PIL.ImageDraw import ImageDraw

PAGE_HEIGHT = 1000
PAGE_WIDTH = 1000


# TODO create type aliases everywhere
# bbox = [x0, y0, x1, y1] describes corner points, top left as zero, normalized to 1000*1000


def normalize_bbox(bbox: tuple[float, float, float, float], page_height: int, page_width: int) -> \
        tuple[int, int, int, int]:
    return (
        int(bbox[0] * PAGE_WIDTH / page_width),
        int(bbox[1] * PAGE_HEIGHT / page_height),
        int(bbox[2] * PAGE_WIDTH / page_width),
        int(bbox[3] * PAGE_HEIGHT / page_height),
    )


def bbox_bottom_left_to_top_left(bbox: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return (
        bbox[0],
        PAGE_HEIGHT - bbox[3],
        bbox[2],
        PAGE_HEIGHT - bbox[1]
    )


def bbox_split_on_line(text_line, bbox_line) -> list[tuple[str, tuple[int, int, int, int]]]:
    bbox_line_width = bbox_line[2] - bbox_line[0]
    text_by_word = text_line.split(' ')  # space character as indicator of new word
    word_list = []
    for i_word, text_word in enumerate(text_by_word, start=0):
        if text_word.strip() == '':
            continue
        previous_text_in_line = ' '.join(text_by_word[:i_word])
        bbox_x0 = bbox_line[0] + bbox_line_width * (len(previous_text_in_line) / len(text_line))
        bbox_word_width = bbox_line_width * (len(text_word) / len(text_line))
        bbox_word = (
            int(bbox_x0),
            int(bbox_line[1]),
            int(bbox_x0 + bbox_word_width),
            int(bbox_line[3])
        )
        word_list.append((text_word, bbox_word))

    return word_list


def bbox_split_on_paragraph(text_paragraph, bbox_all) -> list[str, tuple]:
    text_by_line = text_paragraph.split('\n')
    line_height = (bbox_all[3] - bbox_all[1]) / len(text_by_line)
    word_list = []
    for i_line, text_line in enumerate(text_by_line, start=1):
        bbox_line = (bbox_all[0], bbox_all[1], bbox_all[2], bbox_all[1] + line_height * i_line)
        word_list.extend(bbox_split_on_line(text_line, bbox_line))

    return word_list


def draw_boxes(image, boxes, color='red'):
    image = image.convert('RGB')
    draw = ImageDraw.Draw(image, mode='RGB')
    for box in boxes:
        draw.rectangle(box, outline=color)
    return image
