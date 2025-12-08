import os
import subprocess
import pdfplumber

RAW_DIR = "data/raw/pdfs"
OUT_DIR = "data/clean/pdfs"

os.makedirs(OUT_DIR, exist_ok=True)

def run_ocr(input_pdf, output_pdf):
    try:
        subprocess.run(
            ["ocrmypdf", "--force-ocr", input_pdf, output_pdf],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except:
        return False

def extract_text(pdf_file, txt_path):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = "\n".join([(page.extract_text() or "") for page in pdf.pages])
    except:
        text = ""

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text.strip())

def main():
    pdfs = [f for f in os.listdir(RAW_DIR) if f.endswith(".pdf")]

    for pdf_name in pdfs:
        pdf_id = pdf_name[:-4]
        in_path = os.path.join(RAW_DIR, pdf_name)

        out_dir = os.path.join(OUT_DIR, pdf_id)
        os.makedirs(out_dir, exist_ok=True)

        ocr_path = os.path.join(out_dir, "ocr.pdf")
        txt_path = os.path.join(out_dir, "content.txt")

        if run_ocr(in_path, ocr_path):
            extract_text(ocr_path, txt_path)

if __name__ == "__main__":
    main()