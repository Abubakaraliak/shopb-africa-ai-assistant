
from pathlib import Path
import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 1. Locate the company knowledge-base file
document_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "shopb_company_docs.txt"
)

# 2. Read the document
with open(document_path, "r", encoding="utf-8") as file:
    content = file.read()


# 3. Detect numbered headings such as:
# SECTION 1: COMPANY OVERVIEW
# SECTION 2: PRODUCTS AND CATEGORIES
#
# Also supports Markdown headings such as:
# ## Company Overview

heading_pattern = re.compile(
    r"(?im)^\s*(?:"
    r"SECTION\s+\d+\s*:\s*(.+?)"
    r"|#{1,3}\s+(.+?)"
    r")\s*$"
)

matches = list(heading_pattern.finditer(content))

sections = []

# 4. Extract the sections
if not matches:
    sections.append({
        "section": "General Information",
        "text": content.strip()
    })
else:
    # Preserve any introductory text before the first heading
    intro = content[:matches[0].start()].strip()

    if intro:
        sections.append({
            "section": "General Information",
            "text": intro
        })

    for i, match in enumerate(matches):
        section_name = (
            match.group(1) or match.group(2)
        ).strip()

        start = match.end()

        end = (
            matches[i + 1].start()
            if i + 1 < len(matches)
            else len(content)
        )

        section_text = content[start:end].strip()

        if section_text:
            sections.append({
                "section": section_name,
                "text": section_text
            })


# 5. Split each section into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)

chunks = []

for section in sections:
    document = Document(
        page_content=section["text"],
        metadata={
            "source": "shopb_company_docs.txt",
            "company": "ShopB.Africa",
            "section": section["section"]
        }
    )

    section_chunks = text_splitter.split_documents(
        [document]
    )

    chunks.extend(section_chunks)


# 6. Display processing results
print("\n===================================")
print("SHOPB.AFRICA DOCUMENT PROCESSOR")
print("===================================")

print(f"\nTotal sections: {len(sections)}")
print(f"Total chunks: {len(chunks)}")

print("\nSections found:")

for section in sections:
    print(f"- {section['section']}")

print("\n===================================")
print("FIRST CHUNK")
print("===================================")

if chunks:
    print(chunks[0].page_content)
    print("\nMetadata:")
    print(chunks[0].metadata)