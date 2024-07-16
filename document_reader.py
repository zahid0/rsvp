import os

import pypdf
from bs4 import BeautifulSoup
from ebooklib import ITEM_NAVIGATION, epub


class DocumentReader:
    SUPPORTED_EXTENSIONS = ["pdf", "txt", "epub"]

    def __init__(self, path):
        self.path = f"files/{path}"
        self.extension = os.path.splitext(path)[1].lstrip(".")
        self.validate_file_extension(path)

    def validate_file_extension(self, path):
        if self.extension not in self.SUPPORTED_EXTENSIONS:
            raise Exception(f"The file extension {self.extension} is not supported.")

    def process_pdf_outline(self, outline):
        toc = []
        for chapter in outline:
            if isinstance(chapter, list):
                toc += self.process_pdf_outline(chapter)
            else:
                toc.append(chapter)
        return toc

    def get_chapters(self):
        toc = []
        if self.extension == "pdf":
            with open(self.path, "rb") as f:
                reader = pypdf.PdfReader(f)
                outline = reader.outline
                toc = self.process_pdf_outline(outline)
        elif self.extension == "txt":
            toc = []
        elif self.extension == "epub":
            book = epub.read_epub(self.path)
            nav_items = [
                item for item in book.get_items() if item.get_type() == ITEM_NAVIGATION
            ]
            if nav_items:
                nav_item = nav_items[0]
            else:
                return []
            soup = BeautifulSoup(nav_item.get_content(), features="xml")
            nav_points = soup.navMap.find_all("navPoint")
            for np in nav_points:
                link = np.content.attrs["src"]
                title = np.navLabel.get_text().strip()
                chapter = book.get_item_with_href(link)
                if title and chapter:
                    toc.append({"title": title, "chapter": chapter})
        return toc

    def get_chapter_titles(self):
        chapters = self.get_chapters()
        titles = []
        if self.extension == "pdf":
            for i, chapter in enumerate(chapters):
                titles.append({"id": i, "title": chapter.title})
        elif self.extension == "txt":
            return []
        elif self.extension == "epub":
            for i, chapter in enumerate(chapters):
                titles.append({"id": i, "title": chapter["title"]})
        return titles

    async def get_chapter_content(self, chapter_id):
        text = ""
        if self.extension == "pdf":
            with open(self.path, "rb") as f:
                reader = pypdf.PdfReader(f)
                chapters = self.process_pdf_outline(reader.outline)
                chapter = chapters[chapter_id]
                start_page = reader.get_destination_page_number(chapter)

                total_pages = len(reader.pages)

                if chapter_id < len(chapters) - 1:
                    # If this is not the last chapter, 'last_page' is the start page of the next chapter - 1
                    next_chapter = chapters[chapter_id + 1]
                    last_page = reader.get_destination_page_number(next_chapter)
                else:
                    # If this is the last chapter, 'last_page' is the total pages of the document
                    last_page = total_pages
                for i in range(start_page, last_page):
                    text += "\n" + reader.get_page(i).extract_text()
        elif self.extension == "txt":
            with open(self.path, "r") as f:
                return f.read()
        elif self.extension == "epub":
            chapter = self.get_chapters()[chapter_id]["chapter"]
            return BeautifulSoup(chapter.get_content()).get_text()
        return text

    async def get_content(self):
        text = ""
        if self.extension == "pdf":
            with open(self.path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text += "\n" + page.extract_text()
        elif self.extension == "txt":
            with open(self.path, "r") as f:
                return f.read()
        return text
