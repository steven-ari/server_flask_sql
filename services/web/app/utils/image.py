from collections import defaultdict
from pytesseract import pytesseract


from pathlib import Path

import cv2
import numpy as np
import pytesseract

from utils.pdf import normalize_bbox, create_metadata_from_pages_data


def extract_metadata_from_images(image_paths: list[Path]) -> dict:
    pages_data = []
    for image_path in image_paths:
        page_data = []
        page_shape = cv2.imread(str(image_path)).shape[:2]
        # TODO enlarge image before OCR to improve result
        ocr_results = pytesseract.image_to_data(str(image_path), output_type=pytesseract.Output.DICT)
        for i, word in enumerate(ocr_results["text"]):
            if word not in ["", " "]:
                bbox_word = (
                    ocr_results["left"][i],
                    ocr_results["top"][i],
                    ocr_results["left"][i] + ocr_results["width"][i],
                    ocr_results["top"][i] + ocr_results["height"][i],
                )
                bbox_word_normalized = normalize_bbox(bbox_word, page_shape[0], page_shape[1])
                page_data.append((word, bbox_word_normalized))
        pages_data.append((page_data, page_shape))

    return create_metadata_from_pages_data(pages_data)


# TODO refactor by prioritizing this one, over the one in bbox, since this one accommodates multiple boxes
def normalize_boxes(boxes: np.array, width: int, height: int) -> np.array:
    return np.array(
        [
            1000 * (boxes[0] / width),
            1000 * (boxes[1] / height),
            1000 * (boxes[2] / width),
            1000 * (boxes[3] / height),
        ],
        dtype=int
    )
