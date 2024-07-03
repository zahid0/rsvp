function rsvpApp(document_id, chapter_id) {
  return {
    document_id: document_id,
    chapter_id: chapter_id,
    wpm: 300,
    numWords: 5,
    fontSize: 64,
    words: [],
    dynIndex: 0,
    intervalId: null,
    playing: false,
    fullTextDisplay: '',
    rsvpText: '',

    init() {
      this.fetchWords();
    },

    async fetchWords() {
      try {
        const response = await fetch('/api/documents/' + this.document_id + '/chapters/' + this.chapter_id);
        const data = await response.json();
        this.words = data.content;
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
      const endIdx = this.dynIndex + this.numWords;
      this.rsvpText = this.words.slice(this.dynIndex, endIdx).join(' ');
      this.dynIndex = endIdx >= this.words.length ? 0 : endIdx;

      if (this.dynIndex === 0) {
        this.pauseRsvp();
      }
    },

    initRsvp() {
      const wordsPerSecond = this.wpm / 60;
      const interval = 1000 / wordsPerSecond * this.numWords;
      document.getElementById('rsvp').style.fontSize = `${this.fontSize}px`;
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
      this.initRsvp();
      this.playing = true;
      this.updateDisplay();
    },

    pauseRsvp() {
      clearInterval(this.intervalId);
      this.intervalId = null;
      this.playing = false;
      this.rsvpText = "";
      this.updateDisplay();
      this.setupWordDisplay();
    }
  }
}
