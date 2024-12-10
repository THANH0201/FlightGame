'use strict';

window.onload = function() {
  const playerId = localStorage.getItem('player_id');
  if (playerId) {
    const homeMenu = document.getElementById('home');
    homeMenu.href = 'game.html';
  }
};