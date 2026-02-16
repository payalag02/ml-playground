from parser import parse_pdf
from chunker import split_sections
from entities import extract_financial_entities
from embedder import init_collection, upsert_chunks


def run_pipeline(pdf_path, company, year):

    print("Parsing PDF...")
    pages = parse_pdf(pdf_path, company, year)

    print("Chunking sections...")
    chunks = split_sections(pages)

    print("Extracting financial entities...")
    for c in chunks:
        c["entities"] = extract_financial_entities(c["text"])

    print("Embedding + Indexing...")
    upsert_chunks(chunks)

    print("DONE ✅")


if __name__ == "__main__":
    init_collection()

    folder = "fin_report_analysis"

    run_pipeline(
        "fin_report_analysis/AR_24073_INFY_2023_2024_03062024153021.pdf",
        company="Infosys",
        year=2024
    )
