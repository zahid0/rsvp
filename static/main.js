function setupWordDisplay() {
  let fulltextdisplay = document.getElementById("fulltextdisplay");
  fulltextdisplay.innerHTML = ""; // clear previous content

  for(let i = 0; i < words.length; i++) {
    if (words[i] === "<br>") {
      fulltextdisplay.appendChild(document.createElement('br'));
    }
    else {
      let word = document.createElement('span');
      word.innerHTML = words[i];
      if(i === dynIndex) {
        word.classList.add('highlight'); // initially highlight the word at dynIndex
      }
      word.style.marginRight = "5px";

      word.onclick = function() {
        fulltextdisplay.childNodes[dynIndex].classList.remove('highlight');
        dynIndex = i;
        word.classList.add('highlight');
      };

      fulltextdisplay.appendChild(word);
    }
  }
}

function displayWords() {
  var displayChunk = words.slice(dynIndex, dynIndex + numWords).join(' ');
  rsvpElement.innerHTML = displayChunk;
  dynIndex = (dynIndex + numWords);

  // Check if all words have been displayed
  if (dynIndex >  words.length) {
    dynIndex = 0;
    pauseRsvp();
  }
}

// Init rsvp function
function init_rsvp() {
  var wpm = Number(document.getElementById("wpm").value);
  numWords = Number(document.getElementById("num_words").value);
  var wordsPerSecond = wpm / 60;
  var interval = 1000 / wordsPerSecond * numWords;
  var fontSize = document.getElementById("font_size").value;
  rsvpElement.style.fontSize = fontSize + 'px'; // add input field to provide font size
  // Set the interval for updating the rsvp text
  intervalId = setInterval(displayWords, interval);
}

function updateDisplay() {
  document.getElementById("formAndText").style.display = playing ? "none" : "block";
  document.getElementById("rsvp").style.display = playing ? "block" : "none";
}

// Function to toggle play/pause
function togglePlayPause() {
  if(playing) {
    pauseRsvp();
  } else {
    playRsvp();
  }
}


// Plays the rsvp effect. Init it if not initialized yet
function playRsvp() {
  init_rsvp();
  playing = true;
  playPauseButton.value = "Pause";
  updateDisplay();
}

// Stops the rsvp effect
function pauseRsvp() {
  clearInterval(intervalId);
  intervalId = null;
  playing = false;
  playPauseButton.value = "Play";
  rsvpElement.textContent = "";
  updateDisplay();
  setupWordDisplay();
}

// Plays or pauses the rsvp effect when spacebar is pressed
document.addEventListener("keypress", function(event) {
  if(event.key === " ") {
    event.preventDefault(); // prevent form from being submitted
    togglePlayPause();
  }
});


var rsvpElement = document.getElementById("rsvp");
var playPauseButton = document.getElementById("playPause");
var intervalId = null; // to keep track of the interval
var dynIndex = 0; // to keep track of the current word being displayed
var numWords = 1;
var playing = false; // initially paused
var words;

playPauseButton.addEventListener("click", togglePlayPause);

fetch('/content')
  .then(response => response.json())
  .then(data => {
    words = data.content;
    updateDisplay();
    setupWordDisplay();
  })
  .catch(error => console.error('Error:', error));


