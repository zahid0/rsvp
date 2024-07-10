function rsvpApp(document_id, chapter_id) {
  return {
    document_id: document_id,
    chapter_id: chapter_id,
    readingConfig: {},
    readingProgress: {
      document_id: document_id,
      chapter_id: chapter_id,
      word_index: 0,
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
    sprint_count: 0,
    questions: [],
    answers: [],
    testSubmitted: false,
    testScore: null,

    init() {
      this.fetchReadingConfig();
      this.fetchWords();
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
      this.sprint_count++;
      this.sprint_count %= (this.readingConfig.step_ups + this.readingConfig.step_downs);
      if (this.sprint_count < this.readingConfig.step_ups) {
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
        this.next_index = data.next_index;
        this.start_index = data.start_index;
        this.setupWordDisplay();
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
      const endIdx = this.dynIndex + this.readingConfig.number_of_words;
      this.rsvpText = this.words.slice(this.dynIndex, endIdx).join(' ');
      this.dynIndex = endIdx >= this.words.length ? 0 : endIdx;

      if (this.dynIndex === 0) {
        this.pauseRsvp();
        this.saveProgress();
        this.finished = true;
      }
    },

    async fetchNextChunk() {
      this.updateSprint();
      this.fetchWords();
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
      this.saveReadingConfig();

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

    backToDoc() {
      window.location.href = '/documents/' + this.document_id;
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
        let params = this.testParams();
        let query = new URLSearchParams(params);
        const response = await fetch('/api/test/?' + query);
        if (!response.ok) {
          this.removeModal();
          return;
        }
        const data = await response.json();
        for (let i = 0; i < data.length; i++) {
          this.answers.push('');
        }
        this.questions = data;
    },

    removeModal() {
      document.getElementById('modal').remove();
      this.questions = [];
      this.answers = [];
      this.testSubmitted = false;
      this.testScore = null;
    },

    async submitTest() {
      correct = 0;
      total = this.questions.length;
      for (let i = 0; i < total; i++) {
        correct += this.questions[i].right_answer === this.answers[i];
      }
      this.testScore = Math.floor(correct * 100 / total);
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
