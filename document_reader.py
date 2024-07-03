import os

import pypdf


class DocumentReader:
    SUPPORTED_EXTENSIONS = ["pdf"]

    def __init__(self, path):
        self.validate_file_extension(path)
        self.path = f"files/{path}"

    def validate_file_extension(self, path):
        file_extension = os.path.splitext(path)[1].lstrip(".")
        if file_extension not in self.SUPPORTED_EXTENSIONS:
            raise Exception(f"The file extension {file_extension} is not supported.")

    def get_chapters(self):
        toc = []
        with open(self.path, "rb") as f:
            reader = pypdf.PdfReader(f)
            outline = reader.outline
            for i, chapter in enumerate(outline):
                toc.append({"id": i, "title": chapter.title})
        return toc

    def get_chapter_content(self, chapter_id):
        text = ""
        with open(self.path, "rb") as f:
            reader = pypdf.PdfReader(f)
            outline = reader.outline
            chapter = outline[chapter_id]
            start_page = reader.get_destination_page_number(chapter)

            total_pages = len(reader.pages)

            if chapter_id < len(outline) - 1:
                # If this is not the last chapter, 'last_page' is the start page of the next chapter - 1
                next_chapter = outline[chapter_id + 1]
                last_page = reader.get_destination_page_number(next_chapter)
            else:
                # If this is the last chapter, 'last_page' is the total pages of the document
                last_page = total_pages + 1
            for i in range(start_page, last_page):
                text += "\n" + reader.get_page(i).extract_text()
        return text
