# pdf2epub_efficient.py

import sys
import os
import argparse
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from ebooklib import epub
from tqdm import tqdm

def ocr_pdf_to_epub(pdf_path: str, chunk_size: int = 10):
    """
    Converts a PDF file to an EPUB file using OCR, processing the PDF in chunks
    to conserve memory.

    Args:
        pdf_path (str): The full path to the input PDF file.
        chunk_size (int): The number of pages to process in each batch.
    """
    # 1. Validate input and set up paths
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found at '{pdf_path}'")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    epub_path = os.path.join(os.path.dirname(pdf_path), f"{base_name}.epub")
    
    print(f"🚀 Starting conversion of '{os.path.basename(pdf_path)}'...")

    # 2. Get total number of pages without loading the whole file
    try:
        total_pages = pdfinfo_from_path(pdf_path)['Pages']
        print(f"📄 Found {total_pages} pages in the PDF.")
    except Exception as e:
        print(f"\n❌ Error getting PDF info: {e}")
        print("Please ensure Poppler is installed and accessible in your system's PATH.")
        sys.exit(1)

    # 3. Initialize EPUB book
    book = epub.EpubBook()
    book.set_identifier(f"urn:uuid:{base_name}")
    book.set_title(base_name)
    book.set_language("en")

    chapters = []
    
    # 4. Process the PDF in chunks
    print("Performing OCR on all pages (in batches)...")
    with tqdm(total=total_pages, desc="OCR Progress", unit="page") as pbar:
        for start_page in range(1, total_pages + 1, chunk_size):
            end_page = min(start_page + chunk_size - 1, total_pages)
            
            # Convert only the current chunk of pages to images
            images_chunk = convert_from_path(
                pdf_path,
                first_page=start_page,
                last_page=end_page
            )

            # Process each image in the current chunk
            for i, image in enumerate(images_chunk):
                current_page_num = start_page + i
                
                try:
                    text = pytesseract.image_to_string(image)
                except pytesseract.TesseractNotFoundError:
                    print("\n❌ Error: Tesseract is not installed or not in your system's PATH.")
                    sys.exit(1)

                # Create and add the chapter
                chapter_title = f'Page {current_page_num}'
                chapter_file_name = f'page_{current_page_num}.xhtml'
                chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_file_name, lang='en')
                
                html_content = f"<h1>{chapter_title}</h1><p>{text.replace(chr(12), '').replace('\n', '<br />')}</p>"
                chapter.content = html_content
                
                book.add_item(chapter)
                chapters.append(chapter)
                pbar.update(1) # Manually update the progress bar

    # 5. Define final book structure
    print("Assembling the EPUB file...")
    book.toc = chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + chapters

    # 6. Write the final EPUB file
    epub.write_epub(epub_path, book, {})
    print(f"\n✅ Conversion complete! ✨ EPUB saved to '{epub_path}'")


def main():
    """
    Parses command-line arguments and initiates the conversion.
    """
    parser = argparse.ArgumentParser(
        description="Convert a PDF to an EPUB using OCR, processing in chunks for efficiency.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("pdf_file", help="The path to the input PDF file.")
    parser.add_argument(
        "-c", "--chunk_size",
        type=int,
        default=10,
        help="Number of pages to process at a time (default: 10)."
    )
    
    args = parser.parse_args()
    ocr_pdf_to_epub(args.pdf_file, args.chunk_size)


if __name__ == "__main__":
    main()
