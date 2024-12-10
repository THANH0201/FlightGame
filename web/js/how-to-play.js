const steps = [
  {
    icon: 'account_circle',
    title: 'Step 1: Create an Account',
    description: 'Register with a unique username, choose a plane, and set your starting location to begin your adventure.',
    img: 'images/register.png',
  },
  {
    icon: 'flight_takeoff',
    title: 'Step 2: Start Your Journey',
    description: 'Click \'Start New Journey\' or \'Continue My Journey\' to begin your adventure across airports worldwide.',
    img: 'images/continue-journey.png',
  },
  {
    icon: 'map',
    title: 'Step 3: Explore the Map',
    description: 'View your current location, completed missions, and upcoming destinations on the interactive map.',
    img: 'images/map.png',
  },
  {
    icon: 'quiz',
    title: 'Step 4: Complete Missions',
    description: 'Answer questions related to your current location’s culture, geography, and weather to progress!',
    img: 'images/mission.png',
  },
  {
    icon: 'groups',
    title: 'Step 5: Join or Create a Team',
    description: 'Collaborate by joining an existing team or creating your own to compete with friends and other players.',
    img: 'images/team.png',
  },
  {
    icon: 'emoji_events',
    title: 'Step 6: Check the Leaderboard',
    description: 'Track your scores and see where you rank among top players and teams worldwide!',
    img: 'images/leaderboard.png',
  },
];

let currentStep = 0;

window.onload = () => {
  const playerId = localStorage.getItem('player_id');
  if (playerId) {
    const homeMenu = document.getElementById('home');
    homeMenu.href = 'game.html';
  }
  
  loadStep(currentStep);
};

function loadStep(stepIndex) {
  const container = document.getElementById('step-container');
  const step = steps[stepIndex];

  container.innerHTML = `
        <div class="step">
            <div class="icon-container">
                <i class="material-icons">${step.icon}</i>
            </div>
            <div class="content">
                <h3>${step.title}</h3>
                <p>${step.description}</p>
                <img src="${step.img}" alt="${step.title}">
            </div>
        </div>
    `;

  // Update Navigation Button States
  document.getElementById('prev-btn').disabled = stepIndex === 0;
  document.getElementById('next-btn').disabled = stepIndex === steps.length - 1;
}

// Navigation Button Events
document.getElementById('prev-btn').addEventListener('click', () => {
  if (currentStep > 0) {
    currentStep--;
    loadStep(currentStep);
  }
});

document.getElementById('next-btn').addEventListener('click', () => {
  if (currentStep < steps.length - 1) {
    currentStep++;
    loadStep(currentStep);
  }
});
