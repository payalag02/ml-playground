import re

def extract_financial_entities(text):
    entities = {}

    revenue = re.search(r"Revenue[s]?\s*[₹$]?\s?([\d,]+)", text, re.I)
    margin = re.search(r"Operating margin\s*([\d.]+)%", text, re.I)
    roe = re.search(r"Return on equity\s*([\d.]+)%", text, re.I)

    if revenue:
        entities["revenue"] = revenue.group(1)

    if margin:
        entities["operating_margin"] = margin.group(1)

    if roe:
        entities["roe"] = roe.group(1)

    return entities
