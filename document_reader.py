import os

import pypdf


class DocumentReader:
    SUPPORTED_EXTENSIONS = ["pdf", "txt"]

    def __init__(self, path):
        self.path = f"files/{path}"
        self.extension = os.path.splitext(path)[1].lstrip(".")
        self.validate_file_extension(path)

    def validate_file_extension(self, path):
        if self.extension not in self.SUPPORTED_EXTENSIONS:
            raise Exception(f"The file extension {extension} is not supported.")

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
            # Logic here to extract chapters based on structure
            pass  # Custom logic required here
        return toc

    def get_chapter_titles(self):
        chapters = self.get_chapters()
        titles = []
        if self.extension == "pdf":
            for i, chapter in enumerate(chapters):
                titles.append({"id": i, "title": chapter.title})
        elif self.extension == "txt":
            # Logic here to extract chapters based on structure
            pass  # Custom logic required here
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
                    last_page = total_pages + 1
                for i in range(start_page, last_page):
                    text += "\n" + reader.get_page(i).extract_text()
        elif self.extension == "txt":
            # Add logic here to extract the content of a specific chapter for txt files
            pass  # This section needs to be updated with the proper parsing
        return text

    async def get_content(self):
        text = ""
        if self.extension == "pdf":
            with open(self.path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text += "\n" + page.extract_text()
        return text
