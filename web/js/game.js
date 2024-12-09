'use strict';

const backendUrl = 'http://127.0.0.1:5000/';
const maxScore = 50;
const minScore = 30;
let map;

// Initialize Game on Load
window.onload = async () => {
  const playerId = localStorage.getItem('player_id');
  if (!playerId) {
    alert('Please log in first!');
    window.location.href = 'index.html';
    return;
  }

  // Load Player Data and Missions
  const gameData = await getGameData();
  loadPlayerData(gameData.player);

  // Initialize Map with Current Mission
  const currentMission = await getCurrentMission();
  initMap(currentMission, gameData.missions);
};

function initMap(currentMission, missions) {
  // Reset Map Container
  leftBox.innerHTML = '<div id="map" class="map-container"></div>';

  // Create or Reset Map
  if (map) {
    map.remove();  // Remove old map if it exists
  }
  map = L.map('left-box').
      setView([currentMission.latitude_deg, currentMission.longitude_deg], 10);  // Center map

  // Add Tile Layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(map);

  // Add Markers for Completed Missions
  missions.map((mission) =>
      L.marker([mission.latitude_deg, mission.longitude_deg]).
          addTo(map).
          bindPopup(
              `${mission.name} (Mission: ${
                  mission.status === 1
                      ? 'Completed'
                      : mission.status === 0
                          ? 'Not Started'
                          : 'Failed'
              })`,
          ),
  );
}

// Load Player Data
function loadPlayerData(player) {
  localStorage.setItem('current_location', player.current_location);
  document.querySelector('#game-status-details').innerHTML = `
        <li><strong>Total Adventures:</strong> ${player.total_adventure}</li>
        <li><strong>Total Score:</strong> ${player.total_score}</li>
        <li><strong>Current Mission:</strong> Visit ${player.current_airport}</li>
    `;
}

// Tab Switching Logic
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    // Remove active class from all buttons and contents
    tabButtons.forEach((b) => b.classList.remove('active'));
    tabContents.forEach((c) => c.classList.remove('active'));

    // Add active class to the clicked button and corresponding content
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  });
});

// Button Elements
const continueBtn = document.getElementById('continue-journey');
const backToMapBtn = document.getElementById('back-to-map');
const leftBox = document.getElementById('left-box');

continueBtn.addEventListener('click', handleContinueJourney);
backToMapBtn.addEventListener('click', handleBackToMap);

async function handleContinueJourney() {
  // Fetch next mission from the server
  const mission = await getCurrentMission();

  // Update Left Box with Mission Info
  leftBox.innerHTML = `
        <div class="mission-box">
            <h2>You Are Now at ${mission.name}!</h2>
            <p>Location: ${mission.latitude_deg}, ${mission.longitude_deg}</p>
            <p id="weather-info">Fetching Weather...</p>
            <p>You must complete this mission to continue your adventure.</p>
            <button class="btn" id="start-mission">Start Mission</button>
        </div>
    `;

  // Fetch Weather Data
  await getWeatherData(mission.latitude_deg, mission.longitude_deg);

  // Update Right Box UI
  continueBtn.classList.add('hidden');
  backToMapBtn.classList.remove('hidden');

  // Start Mission on Button Click
  document.getElementById('start-mission').addEventListener('click', () => {
    fetchQuestionsBasedOnWeather();  // Fetch questions based on weather condition
  });
}

async function getCurrentMission() {
  const playerId = localStorage.getItem('player_id');

  // Fetch next mission from the server
  const response = await fetch(`${backendUrl}mission/${playerId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) throw new Error(
      `Failed to fetch next mission: ${response.statusText}`);

  return await response.json();
}

async function handleBackToMap() {
  // Restore the map view in the left box
  const gameData = await getGameData();
  const currentMission = await getCurrentMission();
  initMap(currentMission, gameData.missions);

  // Update Right Box UI
  backToMapBtn.classList.add('hidden');
  continueBtn.classList.remove('hidden');
}

async function getGameData() {
  const playerId = localStorage.getItem('player_id');
  // Fetch game data
  const response = await fetch(`${backendUrl}game/${playerId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return await response.json();
}

// Set up questions array for the mission
let totalScore = 0;
let currentQuestionIndex = 0;
let weatherCondition = 'clear';  // Default, will change based on the weather
let questions = [];

// const questions = [
//   {
//     question: 'What is the capital of Finland?',
//     options: ['Helsinki', 'Oslo', 'Stockholm', 'Copenhagen'],
//     correct: 0, // The correct option is the first one (Helsinki)
//   },
//   {
//     question: 'What is the color of the sky?',
//     options: ['Blue', 'Red', 'Green', 'Yellow'],
//     correct: 0, // The correct option is the first one (Blue)
//   },
//   // Add more questions as needed
// ];

// OpenWeather API Key and OpenTrivia API URL
const weatherApiKey = '232134e42842e573a3e575478beb3d1e';
const triviaApiUrl = 'https://opentdb.com/api.php?amount=5&type=multiple';

// Get Weather Data
async function getWeatherData(lat, lon) {
  const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${weatherApiKey}&units=metric`;

  try {
    const response = await fetch(weatherUrl);
    const weatherData = await response.json();

    // Extract weather info
    const weatherDescription = weatherData.weather[0].description;
    const temperature = weatherData.main.temp;
    const weatherIcon = weatherData.weather[0].icon;

    // Update Weather Info in the Mission Box
    document.getElementById('weather-info').innerHTML = `
            <img src="http://openweathermap.org/img/wn/${weatherIcon}@2x.png" alt="Weather Icon">
            <strong>${weatherDescription.toUpperCase()}</strong> | Temperature: ${temperature}&deg;C
        `;

    weatherCondition = weatherData.weather[0].main.toLowerCase(); // e.g., clear, clouds, rain
    console.log(`Weather condition: ${weatherCondition}`);
  } catch (error) {
    console.error('Error fetching weather data:', error);
  }
}

// Fetch Questions Based on Weather Condition
async function fetchQuestionsBasedOnWeather() {
  let difficulty = 'easy';

  if (weatherCondition === 'clear') {
    difficulty = 'easy';
  } else if (weatherCondition === 'clouds' || weatherCondition === 'mist') {
    difficulty = 'medium';
  } else if (weatherCondition === 'rain' || weatherCondition === 'snow') {
    difficulty = 'hard';
  }

  try {
    const response = await fetch(
        `${triviaApiUrl}&difficulty=${difficulty}&category=22`);  // Category 22 for general knowledge
    const data = await response.json();
    questions = data.results;
    initMissionStatus(); // Initialize mission status bar
    loadQuestion();      // Load first question
  } catch (error) {
    console.error('Error fetching trivia questions:', error);
  }
}

// Initialize Mission Status Bar
function initMissionStatus() {
  document.getElementById('left-box').innerHTML = `
        <div class="mission-status">
            <div class="question-indicators" id="question-indicators">
                ${questions.map((_, index) => `
                    <span class="indicator" data-index="${index}">${index + 1}</span>
                `).join('')}
            </div>
            <div class="score-display">
                Total Score: <span id="total-score">0</span>
            </div>
        </div>
        <div id="question-content"></div> <!-- Content updated later -->
    `;
}

// Function to load a new question
function loadQuestion() {
  const question = questions[currentQuestionIndex];

  // Update the question text and options
  document.getElementById('question-content').innerHTML = `
        <div class="mission-box" id="mission-question-section">
        <h2 id="mission-question" class="question">${question.question}</h2>
        <div class="options">
            ${question.incorrect_answers.concat(question.correct_answer).
      sort().
      map((option, idx) => `
                <button class="option-btn" data-index="${idx}">${option}</button>
            `).
      join('')}

            <button class="next-btn hidden" id="next-btn">
                <span class="material-icons">arrow_forward</span>
            </button>
        </div>
        </div>
    `;

  setupAnswerSelection();
}

// Handle Option Selection
function setupAnswerSelection() {
  const optionButtons = document.querySelectorAll('.option-btn');
  const nextBtn = document.getElementById('next-btn');
  const indicators = document.querySelectorAll('.indicator');

  optionButtons.forEach((button, idx) => {
    button.addEventListener('click', function() {
      const correctAnswer = questions[currentQuestionIndex].correct_answer;
      const selectedAnswer = button.innerText;

      // Update score and indicators
      if (selectedAnswer === correctAnswer) {
        button.classList.add('correct');
        indicators[currentQuestionIndex]?.classList.add('correct');  // Ensure safe access
        totalScore += 10; // Add 10 points for each correct answer
        document.getElementById('total-score').textContent = totalScore;
      } else {
        button.classList.add('incorrect');
        indicators[currentQuestionIndex].classList.add('incorrect');
        optionButtons.forEach(btn => {
          if (btn.innerText === correctAnswer) {
            btn.classList.add('correct');
          }
        });
      }

      // Disable all buttons after selection
      optionButtons.forEach(btn => btn.disabled = true);

      nextBtn.classList.remove('hidden');
    });
  });

  // Handle Next Button Click
  nextBtn.addEventListener('click', function() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
      loadQuestion(); // Load next question
    } else {
      showResult(); // Show results if all questions are answered
    }
  });
}

// Function to show the result after all questions are answered
async function showResult() {
  const isPass = totalScore >= minScore; // Check if the score is enough to pass

  let result = await updateProgress(isPass);
  if (isPass) {
    // Load Player Data and Missions
    const gameData = await getGameData();
    loadPlayerData(gameData.player);
  }

  const resultMessage = isPass ?
      `Congratulation, mission completed! Your next mission is at ${result.next_airport.name}` :
      'Mission Failed, try again!';
  document.getElementById('left-box').innerHTML = `
        <div class="mission-result">
            <h2>${resultMessage}</h2>
            <p>Your Total Score: <span id="total-score">${totalScore}/${maxScore}</span></p>
            <button class="btn" id="${isPass ?
      'next-adventure' :
      'restart-mission'}">
                ${isPass ? 'Next Adventure' : 'Restart Mission'}
            </button>
        </div>
    `;

  currentQuestionIndex = 0;
  totalScore = 0;

  if (isPass) {
    document.getElementById('next-adventure').
        addEventListener('click', handleContinueJourney);
  } else {
    document.getElementById('restart-mission').
        addEventListener('click', function() {
          fetchQuestionsBasedOnWeather(); // Fetch new weather and questions
        });
  }
}

async function updateProgress(isPass) {
  const playerId = localStorage.getItem('player_id');
  const currentLocation = localStorage.getItem('current_location');

  // Fetch next mission from the server
  const response = await fetch(`${backendUrl}complete-mission`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      player_id: playerId,
      score: totalScore,
      location: currentLocation,
      isPass: isPass,
    }),
  });

  const result = await response.json();
  if (!response.ok) throw new Error(result.error);

  return result;
}

//******************************************************************************
const viewTeamBtn = document.getElementById('view-team-btn');
viewTeamBtn.addEventListener('click', loadMyTeam);

async function loadMyTeam() {
  const playerId = localStorage.getItem('player_id');
  const teamContent = document.getElementById('team-info');
  const noTeamContent = document.getElementById('no-team');

  const response = await fetch(`${backendUrl}my-team/${playerId}`);
  const result = await response.json();

  if (!response.ok) throw new Error(result.message || 'Failed to load team.');

  if (result.message === 'No team found') {
    teamContent.innerHTML = '';
    noTeamContent.classList.remove('hidden');
  } else {
    teamContent.innerHTML = `
            <h3>${result.team.team_name}</h3>
            <ul id="team-members">
                ${result.members.map(
        (member) => `<li><strong>${member.username}</strong> ${member.total_score}</li>`,
    ).join('')}
            </ul>
        `;
    noTeamContent.classList.add('hidden');
  }
}

// Get Modal Elements
const joinModal = document.getElementById('join-team-modal');
const createModal = document.getElementById('create-team-modal');

// Get Close Buttons
const closeJoinModal = document.getElementById('close-join-modal');
const closeCreateModal = document.getElementById('close-create-modal');

// Add Click Event Listeners
document.getElementById('join-team-btn').addEventListener('click', () => {
  joinModal.style.display = 'flex';
  joinModal.classList.remove('hidden');
});

document.getElementById('create-team-btn').addEventListener('click', () => {
  createModal.style.display = 'flex';
  createModal.classList.remove('hidden');
});

// Close Modals on Click
closeJoinModal.addEventListener('click', () => {
  joinModal.classList.add('hidden');
});

closeCreateModal.addEventListener('click', () => {
  createModal.classList.add('hidden');
});

// Join Team
document.getElementById('join-team-btn').
    addEventListener('click', loadAvailableTeams);

async function loadAvailableTeams() {
  const teamList = document.getElementById('team-list');
  const joinModal = document.getElementById('join-team-modal');

  try {
    // Fetch available teams
    const response = await fetch(`${backendUrl}teams`);
    const result = await response.json();

    if (!response.ok) throw new Error('Failed to fetch teams.');

    // Clear Previous Teams and Populate
    teamList.innerHTML = '';
    result.teams.forEach((team) => {
      const teamCard = document.createElement('div');
      teamCard.className = 'team-card';
      teamCard.dataset.teamId = team.id;
      teamCard.innerHTML = `
                <i class="material-icons">groups</i>
                <h3>${team.name}</h3>
            `;

      // Attach Click Event Directly to the Card
      teamCard.addEventListener("click", async function(event) {
          await joinTeam(team.id);
          document.getElementById('join-team-modal').classList.add('hidden');
          await loadMyTeam();  // Refresh the team list
        });
      teamList.appendChild(teamCard);
    });

    // Show Modal
    joinModal.classList.remove('hidden');
  } catch (error) {
    console.error(error);
    alert('Failed to load teams.');
  }
}

// Create Team Form Submission
document.getElementById('create-team-form').
    addEventListener('submit', async (e) => {
      e.preventDefault();

      const teamName = document.getElementById('team-name').value.trim();
      await createTeam(teamName);

      createModal.classList.add('hidden');
      await loadMyTeam();
    });

async function joinTeam(teamId) {
  const playerId = localStorage.getItem('player_id');

  try {
    const response = await fetch(`${backendUrl}join-team`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({team_id: teamId, player_id: playerId}),
    });

    if (!response.ok) throw new Error('Failed to join team.');
    return response.json();
  } catch (error) {
    console.error(error);
    alert('Error joining team.');
  }
}

async function createTeam(teamName) {
  const playerId = localStorage.getItem('player_id');

  try {
    const response = await fetch(`${backendUrl}create-team`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({team_name: teamName, player_id: playerId}),
    });

    if (!response.ok) throw new Error('Failed to create team.');
    return response.json();
  } catch (error) {
    console.error(error);
    alert('Error creating team.');
  }
}