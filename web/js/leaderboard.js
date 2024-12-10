'use strict';

const backendUrl = 'http://127.0.0.1:5000/';

window.onload = async () => {
  const playerId = localStorage.getItem('player_id');
  if (playerId) {
    const homeMenu = document.getElementById('home');
    homeMenu.href = 'game.html';
  }

  try {
    const response = await fetch(`${backendUrl}leaderboard`);

    if (!response.ok) {
      throw new Error('Failed to fetch leaderboard.');
    }

    const players = await response.json();
    populateLeaderboard(players);

  } catch (error) {
    console.error('Error:', error);
    alert('Failed to load leaderboard. Please try again.');
  }
};

// Populate Leaderboard Table
function populateLeaderboard(players) {
  const leaderboardBody = document.getElementById('leaderboard-body');
  leaderboardBody.innerHTML = '';  // Clear previous content

  players.forEach((player, index) => {
    const row = document.createElement('tr');

    row.innerHTML = `
            <td>
                <span class="rank-badge">${index + 1}</span>
            </td>
            <td class="username">
                <i class="material-icons profile-icon">account_circle</i> ${player.username}
            </td>
            <td class="score">
                <i class="material-icons">star</i> ${player.total_score}
            </td>
            <td class="adventures">
                <i class="material-icons">flight_takeoff</i> ${player.total_adventure}
            </td>
        `;
    leaderboardBody.appendChild(row);
  });
}
