import re

def split_sections(pages):
    chunks = []
    current_section = "Unknown"

    for page in pages:
        lines = page["text"].split("\n")
        buffer = []

        for line in lines:
            # crude section detector (works surprisingly well)
            if line.isupper() and len(line) < 60:
                if buffer:
                    chunks.append({
                        **page,
                        "section": current_section,
                        "text": "\n".join(buffer)
                    })
                    buffer = []

                current_section = line.strip()

            buffer.append(line)

        if buffer:
            chunks.append({
                **page,
                "section": current_section,
                "text": "\n".join(buffer)
            })

    return chunks
