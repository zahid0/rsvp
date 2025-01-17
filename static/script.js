function main() {
  return {
    documents: [],
    showAddForm: false,
    showSettings: false,
    currentTab: 'file-upload',
    title: '',
    content: '',
    chapters: [],
    doc_title: 'Doc',
    document_id: null,
    doc_title: '',
    chapter_id: null,
    readingConfig: {},
    readingProgress: {
      document_id: null,
      chapter_id: null,
      word_index: 0,
      total_words: 0,
      id: null
    },
    words: [],
    fetchingWords: false,
    dynIndex: 0,
    intervalId: null,
    playing: false,
    fullTextDisplay: '',
    rsvpText: '',
    finished: false,
    next_index: 0,
    start_index: 0,
    questions: [],
    answers: [],
    testSubmitted: false,
    testScore: null,
    testScoreText: '',
    progress_bar_percentage: 0,
    progressDone: 0,
    fetchingQuestionFailed: false,

    init: async function(){
      this.fetchDocuments();
      this.fetchReadingConfig();
    },

    fetchDocuments: async function() {
      let response = await fetch('/api/documents');
      this.documents = await response.json();
    },

    addDocument: async function() {
      const file = document.getElementById('new-file').files[0];
      this.uploadFile(file);
    },
    addTextDocument: async function() {
      const blob = new Blob([this.content], { type: 'text/plain' });
      const file = new File([blob], `${this.title}.txt`, {type: 'text/plain'});
      this.uploadFile(file);
    },
    uploadFile: async function(file) {
      const formData = new FormData();
      formData.append('file', file);
      let response = await fetch('/api/documents', {
        method: 'POST',
        body: formData
      });
      if (response.ok) {
        this.showAddForm = false;
        this.fetchDocuments();
      }
    },
    confirmReset: function (docId) {
      if (confirm('Are you sure you want to reset all progress for this document?')) {
        this.resetDocProgress(docId);
      }
    },
    resetDocProgress: async function(docId) {
      let response = await fetch('/api/documents/' + docId + '/reading_progress', {method: 'DELETE'});
      if (response.ok && this.document_id === docId) {
        this.selectDocument(docId);
      }
    },
    confirmDelete: function (docId) {
      if (confirm('Are you sure you want to delete this document?')) {
        this.deleteDocument(docId); // Call the delete API or function
      }
    },
    deleteDocument: async function(docId) {
      let response = await fetch('/api/documents/' + docId, {method: 'DELETE'});
      if (response.ok) {
        this.fetchDocuments();
      }
    },

    selectDocument (document_id) {
      this.fetchDocument(document_id);
    },

    selectChapter(chapter_id) {
      this.chapter_id = chapter_id;
      this.readingProgress.document_id = this.document_id;
      this.readingProgress.chapter_id = this.chapter_id;
      this.fetchWords();
    },

    async fetchDocument(document_id) {
      const response = await fetch('/api/documents/' + document_id);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      this.document_id = document_id;
      const data = await response.json();
      this.chapters = data.chapters;
      this.doc_title = data.path;
      if (this.chapters.length === 0) {
        return this.selectChapter(null);
      }
      let inProgressChapters = this.chapters.filter(chapter => chapter.progress !== 100);
      if (inProgressChapters.length === 0) {
        return this.selectChapter(this.chapters[0].id);
      }
      let updatedChapters = inProgressChapters.filter(chapter => chapter.updated_at !== null).sort((a, b) => (new Date(b.updated_at) - new Date(a.updated_at)));
      if (updatedChapters.length > 0) {
        return this.selectChapter(updatedChapters[0].id);
      }
      return this.selectChapter(inProgressChapters[0].id);
    },

    async fetchReadingConfig() {
      try {
        const response = await fetch('/api/reading_config');
        const data = await response.json();
        this.readingConfig = data;
      } catch (error) {
        console.error('Error fetching reading config:', error);
      }
    },

    updateSprint() {
      this.readingConfig.sprint_count %= (this.readingConfig.step_ups + this.readingConfig.step_downs);
      this.readingConfig.sprint_count++;
      if (this.readingConfig.sprint_count <= this.readingConfig.step_ups) {
        this.readingConfig.words_per_minute += this.readingConfig.ramp_step;
      } else {
        this.readingConfig.words_per_minute -= this.readingConfig.ramp_step;
      }
      this.saveReadingConfig();
    },

    async saveReadingConfig() {
      try {
        const response = await fetch('/api/reading_configs/' + this.readingConfig.id, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.readingConfig),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } catch (error) {
        console.error('Error saving reading config:', error);
      }
      this.showSettings = false;
    },

    async resetProgress() {
      this.next_index = null;
      await this.saveProgress();
      this.fetchWords();
    },

    async saveProgress() {
      try {
        this.readingProgress.word_index = this.next_index;
        const response = await fetch('/api/reading_progress/', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.readingProgress),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (this.chapter_id) {
          let current_chapter = this.chapters.filter(chapter => chapter.id === this.chapter_id)[0];
          current_chapter.progress = Math.floor(this.progressDone);
        }
      } catch (error) {
        console.error('Error saving reading config:', error);
      }
    },

    async fetchWords() {
      try {
        this.fetchingWords = true;
        this.finished = false;
        while (typeof this.readingConfig.words_per_minute === 'undefined') {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
        let params = {
          'words_per_minute': this.readingConfig.words_per_minute,
          'sprint_minutes': this.readingConfig.sprint_minutes
        };
        if (this.chapter_id !== null) {
          params['chapter_id'] = this.chapter_id;
        }
        let query = new URLSearchParams(params);
        let url = '/api/documents/' + this.document_id + '/content/?' + query;
        const response = await fetch(url);
        const data = await response.json();
        this.words = data.content;
        this.doc_title = data.title;
        this.next_index = data.next_index;
        this.start_index = data.start_index;
        this.setupWordDisplay();
        this.readingProgress.total_words = data.total_words;
        if (data.next_index === null) {
          this.progress_bar_percentage = 100;
        } else {
          this.progress_bar_percentage = 100 * data.next_index / data.total_words;
        }
        this.progressDone = 100 * this.start_index / data.total_words;
        this.fetchingWords = false;
      } catch (error) {
        console.error('Error fetching content:', error);
      }
    },

    setupWordDisplay() {
      let fulltextdisplay = '';
      for (let i = 0; i < this.words.length; i++) {
        if (this.words[i] === "<br>") {
          fulltextdisplay += '<br>';
        } else {
          let span = `<span style="margin-right: 5px;" @click="highlightWord(${i})" class="${i === this.dynIndex ? 'highlight' : ''}">${this.words[i]}</span>`;
          fulltextdisplay += span;
        }
      }
      this.fullTextDisplay = fulltextdisplay;
    },

    highlightWord(index) {
      this.dynIndex = index;
      this.setupWordDisplay();
    },

    displayWords() {
      if (this.dynIndex >= this.words.length) {
        this.dynIndex = 0;
        this.pauseRsvp();
        this.saveProgress();
        this.finished = true;
      } else {
        let endIdx = this.dynIndex + this.readingConfig.number_of_words;
        let endIdxOffset = 0;
        for (let i = this.dynIndex; i <= endIdx; i++) {
          if (this.words[i] === "<br>") {
            endIdx = i;
            endIdxOffset = 1;
            break;
          }
        }
        this.rsvpText = this.words.slice(this.dynIndex, endIdx).join(' ');
        this.dynIndex = endIdx + endIdxOffset;
        this.progressDone = 100 * (this.start_index + this.dynIndex) / this.readingProgress.total_words;
      }
    },

    async fetchNextChunk() {
      this.updateSprint();
      if (this.next_index === null) {
        this.selectDocument(this.document_id);
      } else {
        this.fetchWords();
      }
    },

    initRsvp() {
      const wordsPerSecond = this.readingConfig.words_per_minute / 60;
      const interval = 1000 / wordsPerSecond * this.readingConfig.number_of_words;
      document.getElementById('rsvp').style.fontSize = `${this.readingConfig.font_size}px`;
      this.intervalId = setInterval(() => this.displayWords(), interval);
    },

    togglePlayPause() {
      if (this.playing) {
        this.pauseRsvp();
      } else {
        this.playRsvp();
      }
    },

    playRsvp() {
      this.initRsvp();
      this.playing = true;
      this.finished = false;
    },

    pauseRsvp() {
      clearInterval(this.intervalId);
      this.intervalId = null;
      this.playing = false;
      this.rsvpText = "";
      this.setupWordDisplay();
    },


    async loadTest() {
      fetch('/static/views/test.html')
        .then(response => response.text())
        .then(html => {
          const rsvpElement = document.querySelector('#main');
          rsvpElement.insertAdjacentHTML('beforeend', html);
        });
    },

    testParams() {
      let params = {
        'document_id': this.document_id,
        'start_index': this.start_index
      };

      if (this.chapter_id !== null) {
        params['chapter_id'] = this.chapter_id;
      }
      if (this.next_index !== null) {
        params['end_index'] = this.next_index;
      }
      return params
    },

    async fetchQuestions() {
      this.fetchingQuestions = true;
      let params = this.testParams();
      let query = new URLSearchParams(params);
      const response = await fetch('/api/test/?' + query);
      if (!response.ok) {
        this.fetchingQuestions = false;
        this.fetchingQuestionFailed = true;
        return;
      }
      const data = await response.json();
      for (let i = 0; i < data.length; i++) {
        this.answers.push('');
      }
      this.questions = data;
      this.fetchingQuestions = false;
    },

    removeModal() {
      document.getElementById('modal').remove();
      this.questions = [];
      this.answers = [];
      this.testSubmitted = false;
      this.testScore = null;
      this.fetchingQuestionFailed = false;
      this.testScoreText = '';
    },

    async submitTest() {
      correct = 0;
      total = this.questions.length;
      for (let i = 0; i < total; i++) {
        correct += this.questions[i].right_answer === this.answers[i];
      }
      this.testScore = Math.floor(correct * 100 / total);
      this.testScoreText = correct + '/' + total;
      let params = {
        "score": this.testScore,
        "words_per_minute": this.readingConfig.words_per_minute
      };
      const response = await fetch('/api/test_score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      this.testSubmitted = true;
    }
  }
}
