import sys
import pytesseract
import os
import argparse
from pdf2image import convert_from_path, pdfinfo_from_path


def tess_func(path: str, page: int):
    if not os.path.exists(path):
        print(f"File not found at '{path}'")
        sys.exit(1)
    image_chunk = convert_from_path(
        path,
        first_page=page,
        last_page=page
    )[0]
    bounding_box = pytesseract.image_to_boxes(image_chunk)
    text = pytesseract.image_to_string(image_chunk, lang="eng")
    print(bounding_box)
    print(text)


def main():
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
    args = parser.parse_args()
    tess_func(args.pdf_file, int(args.page_num))

if __name__ == "__main__":
    main()
