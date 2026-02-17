import fitz  # PyMuPDF

def parse_pdf(path, company, year):
    doc = fitz.open(path)
    pages = []

    for i, page in enumerate(doc):
        text = page.get_text("text")

        pages.append({
            "company": company,
            "year": year,
            "page": i + 1,
            "text": text
        })

    return pages
