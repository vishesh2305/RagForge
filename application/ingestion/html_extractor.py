# from pathlib import Path

# from bs4 import BeautifulSoup


# doc_path = Path("../../data/raw/python/document_1.html")

# if doc_path.is_file():
#     print(f"File Found at : {doc_path}")
# else:
#     print("File Not Found !..")

# # Read the file

# with open(doc_path, "r") as file:
#     html_content = file.read()
#     soup = BeautifulSoup(html_content, 'html.parser')
#     content_section=soup.find('section', id='more-control-flow-tools')
#     # nested_elements = content_section.find_all()
#     # all_tags = {tag.name for tag in content_section.find_all()}
#     # has_script = content_section.find('script') is not None
#     # has_style = content_section.find('style') is not None
#     # has_code = content_section.find(['code', 'pre']) is not None
#     # has_nav = content_section.find(['a', 'li', 'nav']) is not None
#     # links = content_section.find_all('a')
#     # print(f"Has script: {has_script}, has style : {has_style}, has Code : {has_code}, has navigation: {has_nav}")
#     # print("Total Links : ", len(links))

#     # for link in links:
#     #     print(link.get('href'))
#     # print(content_section.get_text())
#     # for tag in content_section(['script', 'style']):
#     #     tag.decompose()

#     # for tag in content_section.find_all("a"):
#     #     tag.unwrap()

#     # # print(content_section.get_text(separator=" "))

#     # heading_element = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
#     # paragraph_element = soup.find('p')
#     # code_element = soup.find('code')

#     # head_tag = heading_element.name if heading_element else "Not found"
#     # para_tag = paragraph_element.name if paragraph_element else "Not found"
#     # code_tag = code_element.name if code_element else "Not found"

#     # print(f"heading -> {head_tag}")
#     # print(f"paragraph -> {para_tag}")
#     # print(f"code -> {code_tag}")

#     TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre']
#     sequence = []

#     for el in content_section.find_all(TAGS):
#         text = el.get_text().strip() if el.name =='pre' else el.get_text(" ", strip=True)
#         if not text:
#             continue
#         kind = 'heading' if el.name.startswith('h') else 'code' if el.name.startswith('pre') else 'paragraph'
#         sequence.append((kind, text))


#     document_content = "\n\n".join(item[1] for item in sequence)

#     document_title = soup.title.text if soup.title.text else soup.h1.text if soup.h1.text else doc_path.name


from pathlib import Path
from bs4 import BeautifulSoup


# Load HTML File

def load_html(file_path : Path) -> str:

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found : {file_path}")

    return file_path.read_text(encoding="utf-8")



# Parse Html

def parse_html(html:str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")



# Extract document title

def extract_title(soup: BeautifulSoup, file_path: Path) -> str:

    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(strip=True)

    h1 = soup.find("h1")

    if h1 and h1.get_text(strip=True):
        return h1.get_text(" ", strip=True)


    return file_path.stem



# Find the main Content

def find_main_content(soup: BeautifulSoup):
    content = soup.find("article", class_="md-content__inner")

    if content:
        return content
    # Generic Article
    content = soup.find("article")
    if content:
        return content

    # Python documentation Style
    content = soup.find("main")

    if content:
        return content

    # Generic <Section>

    content = soup.find("section")
    if content:
        return content

    raise ValueError("Could not find a suitable main Content container")



# Clean Unwanted HTML

def clean_content(content) -> None:

    for tag in content.find_all(["script", "style"]):
        tag.decompose()

    for tag in content.find_all("a"):
        tag.unwrap()


# Extract Structured Text

def extract_content(content) -> str:

    elements = content.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6",
        "p",
        "ul", "ol",
        "pre"]
    )

    sequence = []

    for element in elements:
        if element.name.startswith("h"):
            text = element.get_text(" ", strip = True)

            if text:
                sequence.append(("heading", text))

        elif element.name == "p":
            text = element.get_text(" ", strip=True)

            if text:
                sequence.append(("paragraph", text))

        elif element.name == "pre":
            text = element.get_text("", strip=False).strip()

            if text:
                sequence.append(("code", text))


        elif element.name in ["ul", "ol"]:

            if element.find_parent(["ul", "ol"]):
                continue

            items = []

            for li in element.find_all("li", recursive=False):
                item_text = li.get_text(" ", strip=True)

                if item_text:
                    items.append(f"- {item_text}")

            if items:
                sequence.append(("list", "\n".join(items)))
    return "\n\n".join(text for _, text in sequence)



# Document Representation


def create_document(
        file_path : Path,
        title: str,
        content: str,
        source : str
) -> dict :
    if not content.strip():
        raise ValueError(
            f"No usable content extracted from file {file_path}"
        )


    return {
        "id" : file_path.stem,
        "title": title,
        "source": source,
        "filename": file_path.name,
        "content": content
    }


def extract_document(file_path : Path, source: str) -> dict:

    html = load_html(file_path)

    soup = parse_html(html)


    title = extract_title(soup , file_path)

    content = find_main_content(soup)

    clean_content(content)

    document_content = extract_content(content)

    document = create_document(
        file_path = file_path,
        title=title,
        content=document_content,
        source=source
    )

    return document


# testing extractor


if __name__ == "__main__":
    file_path = Path("../../data/raw/python/document_1.html")

    document = extract_document(
        file_path = file_path,
        source = "python"
    )

    print(" \n Document \n")

    print("ID:")
    print(document["id"])

    print("\nTITLE:")
    print(document["title"])

    print("\nSOURCE:")
    print(document["source"])

    print("\nFILENAME:")
    print(document["filename"])

    print("\nCONTENT PREVIEW:")
    print(document["content"][:3000])