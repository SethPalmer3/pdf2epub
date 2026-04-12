import sys
from PIL import Image, ImageDraw
import pytesseract
import os
import argparse
from page_structures import Character, CharacterConverter, Line, LineGenerator
from pdf2image import convert_from_path, pdfinfo_from_path


def tess_func(path: str, page: int, min_space_threshold, max_space_threshold):
    if not os.path.exists(os.path.expanduser(path)):
        print(f"File not found at '{path}'")
        sys.exit(1)

    # Get the image of a single page
    path = os.path.expanduser(path)
    image_chunks: list[Image.Image] = convert_from_path(
        path, first_page=61, last_page=71
    )
    # image_chunk = image_chunks[0]
    # draw: ImageDraw.ImageDraw = ImageDraw.Draw(image_chunk)
    # text = pytesseract.image_to_string(image_chunk, lang="eng", output_type="dict")

    for image_chunk in image_chunks:
        bounding_boxes: str = pytesseract.image_to_boxes(
            image_chunk, config="--oem 1 --psm 1 -l eng --tessdata-dir ./tessdata/"
        )
        char_iter = CharacterConverter(
            bounding_boxes, min_space_threshold, max_space_threshold
        )
        line_iter = LineGenerator(char_iter, False)
        for line in line_iter:
            flipped_top_coord = image_chunk.height - line.top_side
            flipped_bottom_coord = image_chunk.height - line.bottom_side
            box = (
                line.left_side,
                flipped_top_coord,
                line.right_side,
                flipped_bottom_coord,
            )
            print(line)
            # try:
            #     if (
            #         line.width < line.height
            #         or 0.6 <= (line.height / line.width)
            #         or line.height < 5
            #     ):
            #         outline_color = "blue"
            #     else:
            #         outline_color = "red"
            #     # draw.rectangle(box, outline=outline_color, width=2)
            # except ValueError as e:
            #     error_value = (
            #         line.character if isinstance(line, Character) else line.characters
            #     )
            #     print(f"box: {box} char: '{error_value}'\n{e}")

    # image_chunk.show()


def main(
    accept_commandline_args,
    path="",
    page=1,
    min_space_threshold=7,
    max_space_threshold=20,
):
    if accept_commandline_args:
        parser = argparse.ArgumentParser(
            description="A test of the tesseract library",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument("pdf_file", help="The path to the input PDF file.")
        parser.add_argument(
            "page_num", help="The page number to parse (default=1)", default=1
        )
        parser.add_argument(
            "min_page_threshold",
            help="The number of pixels between characters to evaluate a space character",
            default=5,
        )
        parser.add_argument(
            "max_page_threshold",
            help="The number of pixels between characters to evaluate a space character",
            default=5,
        )
        args = parser.parse_args()
        tess_func(
            args.pdf_file,
            int(args.page_num),
            args.min_space_threshold,
            args.max_space_threshold,
        )
    else:
        tess_func(path, page, min_space_threshold, max_space_threshold)


if __name__ == "__main__":
    main(False, "~/Downloads/Basic-Electronics.pdf", 11)
