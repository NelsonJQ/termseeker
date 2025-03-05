import re

def find_paragraphs_with_merge(text, search_string, max_paragraphs=1) -> list:
    paragraphs = text.split('\n\n')
    matched_paragraphs = []
    found_count = 0

    for i, paragraph in enumerate(paragraphs):
        if search_string in paragraph:
            matched_paragraph = paragraph

            if i < len(paragraphs) - 1:
                next_paragraph = paragraphs[i + 1]
                is_page_number = re.match(r'\s*\*\*\d+\*\*\s*', next_paragraph)
                is_footnote = re.match(r'\s*K\d{7}\s\d{6}\s*', next_paragraph)

                if (is_page_number or is_footnote) and i < len(paragraphs) - 2:
                    separator_index = i + 2
                    if separator_index < len(paragraphs) and re.match(r'\s*-+\s*', paragraphs[separator_index]):
                        separator_index += 1

                    if separator_index < len(paragraphs):
                        continuation = paragraphs[separator_index]
                        if not re.match(r'\s*\d+\.\s', continuation):
                            matched_paragraph = matched_paragraph + " " + continuation

            matched_paragraphs.append(matched_paragraph)
            found_count += 1

            if found_count >= max_paragraphs:
                break

    if max_paragraphs == 1:
        return matched_paragraphs[0] if matched_paragraphs else None

    return matched_paragraphs