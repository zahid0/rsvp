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
    dynIndex: 0,
    intervalId: null,
    playing: false,
    fullTextDisplay: '',
    rsvpText: '',
    finished: false,
    next_index: 0,
    sprint_count: 0,

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

    async updateSprint() {
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
        this.finished = false;
        const response = await fetch('/api/documents/' + this.document_id + '/chapters/' + this.chapter_id);
        const data = await response.json();
        this.words = data.content;
        this.next_index = data.next_index;
        this.setupWordDisplay();
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
        this.updateSprint();
      }
    },

    initRsvp() {
      const wordsPerSecond = this.readingConfig.words_per_minute / 60;
      const interval = 1000 / wordsPerSecond * this.readingConfig.number_of_words;
      document.getElementById('rsvp').style.fontSize = `${this.readingConfig.font_size}px`;
      this.intervalId = setInterval(() => this.displayWords(), interval);
    },

    updateDisplay() {
      document.getElementById("formAndText").style.display = this.playing ? "none" : "block";
      document.getElementById("rsvp").style.display = this.playing ? "block" : "none";
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
      this.updateDisplay();
    },

    pauseRsvp() {
      clearInterval(this.intervalId);
      this.intervalId = null;
      this.playing = false;
      this.rsvpText = "";
      this.updateDisplay();
      this.setupWordDisplay();
    },

    backToDoc() {
      window.location.href = '/documents/' + this.document_id;
    }
  }
}
