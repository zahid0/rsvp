function documentData(document_id) {
  return {
    document_id: document_id,
    chapters: [],
    doc_title: '',

    async fetchDocument() {
        const response = await fetch('/api/documents/' + this.document_id);
        const data = await response.json();
        this.chapters = data.chapters;
        this.doc_title = data.path;
    }
  }
}
