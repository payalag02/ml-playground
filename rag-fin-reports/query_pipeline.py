import re
from retriever import search_chunks
from llm import build_context, generate_answer
import re

# Maintain a known company list (expand as you add reports)
KNOWN_COMPANIES = [
    "Infosys",
    "TCS",
    "Wipro",
    "HCL",
    "Tech Mahindra"
]


def detect_filters(question):

    question_lower = question.lower()

    companies = []
    year = None

    # Detect companies
    for c in KNOWN_COMPANIES:
        if c.lower() in question_lower:
            companies.append(c)

    # Detect year
    year_match = re.search(r"20\d{2}", question)
    if year_match:
        year = int(year_match.group())

    return companies, year


# Simple query analyzer


def run_query(question):

    print("Analyzing query...")
    companies, year = detect_filters(question)

    print(f"Detected filters → company={companies}, year={year}")

    print("Retrieving context...")
    chunks = search_chunks(
        question,
        companies=companies,
        year=year
    )

    print(f"\n--- Retrieved {len(chunks)} chunks ---")
    context = build_context(chunks)

    print("Generating answer...")
    answer = generate_answer(question, context)

    return answer


if __name__ == "__main__":

    q = "Compare operational expenses of Wipro with Infosys ended March 31, 2024:?"
    # q = "Summary of acquisition of Wipro compared to Infosys ended March 31, 2024:?"

    result = run_query(q)

    print("\n===== ANSWER =====\n")
    print(result)
