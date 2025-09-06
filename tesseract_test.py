import sys
from tqdm import tqdm
from PIL import Image, ImageDraw
import pytesseract
import os
import argparse
from page_structures import Character, CharacterConverter, Line, LineGenerator
from pdf2image import convert_from_path, pdfinfo_from_path


def tess_func(path: str, page: int, min_space_thresh, max_space_thresh):
    if not os.path.exists(os.path.expanduser(path)):
        print(f"File not found at '{path}'")
        sys.exit(1)

    path = os.path.expanduser(path)
    image_chunks: list[Image.Image] = convert_from_path(
        path,
        first_page=page,
        last_page=page
    )
    image_chunk = image_chunks[0]
    bounding_box: str = pytesseract.image_to_boxes(image_chunk, config='--oem 1')
    draw = ImageDraw.Draw(image_chunk)
    # text = pytesseract.image_to_string(image_chunk, lang="eng", output_type="dict")
    
    char_iter = CharacterConverter(bounding_box, min_space_thresh, max_space_thresh)
    line_iter = LineGenerator(char_iter, False)
    for line in char_iter:
        # print(line)
        pillow_top = image_chunk.height - line.top_side
        pillow_bottom = image_chunk.height - line.bottom_side
        if line.height < 5:
            continue 
        box = (line.left_side, pillow_top, line.right_side, pillow_bottom)
        print(line)
        try:
            if line.width < line.height or .6 <= (line.height / line.width) or line.height < 5: 
                outline_color = "blue"
            else:
                outline_color = "red"
            draw.rectangle(box, outline=outline_color, width=2)
        except ValueError as e:
            print(f"box: {box}\n{e}")

        # print(f"H: {line.height}, W: {line.width}")
        # if line.width < line.height or .6 <= (line.height / line.width) or line.height < 5: 
        #     print('-'*10)
        #     print(line)
        #     for c in line.characters:
        #         print(c)
        #     print('-'*10)
    image_chunk.show()

    # print(text)

def main(accept_commandline_args, path="", page=1, min_space_threshold=0.6, max_space_threshold=1.3):
    if accept_commandline_args:
        parser = argparse.ArgumentParser(
            description="A test of the tesseract library",
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument("pdf_file", help="The path to the input PDF file.")
        parser.add_argument(
            "page_num",
            help="The page number to parse (default=1)",
            default=1
        )
        parser.add_argument(
            "min_page_threshold",
            help="The number of pixels between characters to evaluate a space character",
            default=5
        )
        parser.add_argument(
            "max_page_threshold",
            help="The number of pixels between characters to evaluate a space character",
            default=5
        )
        args = parser.parse_args()
        tess_func(args.pdf_file, int(args.page_num), args.min_space_threshold, args.max_space_threshold)
    else:
        tess_func(path, page, min_space_threshold, max_space_threshold)

if __name__ == "__main__":
    main(False, "~/Downloads/Silicon_Wafer_breakage_Analysis.pdf", 1)
