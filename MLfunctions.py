# from PaddleOCR import paddleocr
from PaddleOCR.paddleocr import PaddleOCR, draw_ocr # main OCR dependencies
from matplotlib import pyplot as plt # plot images
import cv2 #opencv
import os # folder directory navigation
import pandas as pd
import units_dict
import re

ocr_model = PaddleOCR(lang='en', use_gpu=False)

def extract_ocr(img_path):
    try:
        # Run OCR on the image
        result = ocr_model.ocr(img_path)
        # Combine the detected text into a single string
        ocr_text = ' '.join([line[1][0] for line in result[0]])
        ocr_text = ocr_text.lower()
        return ocr_text
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return None

SYMBOLS = r"[ !@#%^&*()$_\-\+\{\}\[\]\'\|:;<>,/~?`=\©™°®¢»«¥""§—''é€]"
PATTERN = r"(\d+(\.\d+)?[a-zA-Z]{0,2})"  # Match numeric values with any suffix length

def postprocessing(text: str) -> list:
    if isinstance(text, str):
        no_spaces = re.sub(r"\s+", "", text)
        lower_case = no_spaces.lower()
        cleaned_symbol = re.sub(SYMBOLS, " ", lower_case)
        cleaned_symbol = cleaned_symbol.replace('"', "inch")

        matches = re.findall(PATTERN, cleaned_symbol)

        results = []
        for match in matches:
            full_match = match[0] 
            numeric_part = re.match(r"\d+(\.\d+)?", full_match).group()
            suffix = full_match[len(numeric_part):]

            if numeric_part:
                results.append(numeric_part)

            if suffix:
                current_suffix = ""
                for char in suffix:
                    current_suffix += char
                    results.append(f"{numeric_part}{current_suffix}")

        seen = set()
        return [x for x in results if not (x in seen or seen.add(x))]
    else:
        return []
    
def match_units(input_list, units_dict, entity_name):
    # Match units from input_list using the provided units_dict and entity_name.
    # input_list = input_list.split('\'')
    abb_dict = {
        key: value
        for category, sub_dict in units_dict.items()
        if category == entity_name
        for key, value in sub_dict.items()
    }

    results = []
    for item in input_list:
        if len(item) >= 2:
            # Check for matches up to three characters from the end of the string
            for length in range(3, 0, -1):  # Check lengths 1, 2, and 3
                suffix = item[-length:]  # Get the last `length` characters
                # print(suffix)
                result = abb_dict.get(suffix)
                if result:
                    results.append(f"{item[:-length]} {result}")
                    break  # Stop checking further lengths if a match is found

    return results


def get_max(units_list):
    # units_list = units_list.split('\'')
    if not units_list or not isinstance(units_list, list) or not units_list[0]: # handle empty list or empty string
        return ""
    
    max_val = -10000000
    # Check if the first element has at least 2 parts after splitting
    parts = units_list[0].split(" ")
    if len(parts) >= 2:
        max_val_unit = parts[1]  # Assign if it has at least 2 parts
    else:
        max_val_unit = parts[0] if parts else ""  # Assign first if only one part, otherwise empty string
    
    for u in units_list:
        if(u == '[]' or u == '[' or u == ']' or u == ', '):
            continue
        print(u)
        parts = u.split(" ")
        # Extract the numeric part using regular expression
        match = re.match(r"(\d+(\.\d+)?)", parts[0])
        if match:
            num_str = match.group(1)
            if "." in num_str:
                num = float(num_str)
            else:
                num = int(num_str)

            unit = " ".join(parts[1:])
            if num > max_val:
                max_val = num
                max_val_unit = unit

    return f"{max_val} {max_val_unit}"