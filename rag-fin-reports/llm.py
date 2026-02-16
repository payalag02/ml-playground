from openai import OpenAI
from config import *

client = OpenAI(api_key=OPENAI_API_KEY)


def build_context(chunks):

    context_blocks = []

    for c in chunks:
        block = f"""
[Company: {c['company']} | Year: {c['year']} | Section: {c['section']} | Page: {c['page']}]
{c['text']}
"""
        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def generate_answer(question, context):

    system_prompt = """
You are a financial analyst assistant.

Rules:
- Use ONLY the provided annual report context.
- Cite company and page numbers in answers.
- If financial numbers appear, quote exact values.
- If unsure, say the report does not mention it.
"""

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
Question:
{question}

Context:
{context}
"""}
        ]
    )

    return completion.choices[0].message.content
