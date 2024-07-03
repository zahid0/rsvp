function documentData(document_id) {
  return {
    document_id: document_id,
    chapters: [],

    async fetchChapters() {
      try {
        const response = await fetch('/api/documents/' + this.document_id + '/chapters');
        this.chapters = response.json();
      } catch (error) {
        console.error('Error fetching content:', error);
      }
    }
  }
}
