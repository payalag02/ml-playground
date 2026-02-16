import re
from retriever import search_chunks
from llm import build_context, generate_answer


# Simple query analyzer
def detect_filters(question):

    company = None
    year = None

    # Example company detection (extend later)
    if "infosys" in question.lower():
        company = "Infosys"

    # Detect fiscal year
    year_match = re.search(r"20\d{2}", question)
    if year_match:
        year = int(year_match.group())

    return company, year


def run_query(question):

    print("Analyzing query...")
    company, year = detect_filters(question)

    print(f"Detected filters → company={company}, year={year}")

    print("Retrieving context...")
    chunks = search_chunks(
        question,
        company=company,
        year=year
    )

    context = build_context(chunks)

    print("Generating answer...")
    answer = generate_answer(question, context)

    return answer


if __name__ == "__main__":

    q = "What are future prospects for Infosys"

    result = run_query(q)

    print("\n===== ANSWER =====\n")
    print(result)
