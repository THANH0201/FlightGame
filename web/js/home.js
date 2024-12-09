'use strict';

const backendUrl = 'http://127.0.0.1:5000/';

// Loading page ****************************************************************
window.onload = () => {
  const textElement = document.querySelector('.intro-text p');
  const textContent = 'Get ready for an exciting flight adventure! Explore world-famous airports, learn about global weather patterns, and complete thrilling missions. Embark on your journey, build your team, and conquer the skies!';
  let charIndex = 0;

  function typeText() {
    if (charIndex < textContent.length) {
      textElement.textContent += textContent.charAt(charIndex);
      charIndex++;
      setTimeout(typeText, 100);  // Typing Speed
    }
  }

  // Clear Text and Start Animation
  textElement.textContent = '';
  typeText();
};

// Modal Management ************************************************************
const registerModal = document.getElementById('registerModal');
const loginModal = document.getElementById('loginModal');

const openRegisterBtn = document.getElementById('openRegister');
const openLoginBtn = document.getElementById('openLogin');

const closeRegisterBtn = document.getElementById('closeRegister');
const closeLoginBtn = document.getElementById('closeLogin');

openRegisterBtn.addEventListener('click', () => {
  registerModal.style.display = 'flex';
});

openLoginBtn.addEventListener('click', () => {
  loginModal.style.display = 'flex';
});

closeRegisterBtn.addEventListener('click', () => {
  registerModal.style.display = 'none';
});

closeLoginBtn.addEventListener('click', () => {
  loginModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
  if (e.target === registerModal) registerModal.style.display = 'none';
  if (e.target === loginModal) loginModal.style.display = 'none';
});

// REGISTRATION INITIAL ********************************************************
const continentList = document.querySelector('#reg-continent');
const countryList = document.querySelector('#reg-country');
const airportList = document.querySelector('#reg-airport');

// Start with adding continents
async function showContinents() {
  const response = await fetch(`${backendUrl}continents`);
  const continents = await response.json();
  for (const cont of continents) {
    const option = document.createElement('option');
    option.value = cont.continent;
    option.innerText = cont.continent;
    continentList.appendChild(option);
  }
}

showContinents(); // this starts the loading of continents

// when continent is selected get countries and add to second list...
continentList.addEventListener('change', async function() {
  countryList.innerHTML = '<option disabled selected value="">Select your country</option>'; // empty the country and airport lists because the user might change continent
  airportList.innerHTML = '<option disabled selected value="">Select your airport</option>';
  const response = await fetch(
      `${backendUrl}countries/` + continentList.value);
  const countries = await response.json();
  for (const country of countries) {
    const option = document.createElement('option');
    option.value = country.iso_country;
    option.innerText = country.name;
    countryList.appendChild(option);
  }
});

// when country is selected get airports and add to third list...
countryList.addEventListener('change', async function() {
  airportList.innerHTML = '<option disabled selected value="">Select your airport</option>'; // empty the airport list because the user might change country
  const response = await fetch(
      `${backendUrl}airports/` + countryList.value);
  const airports = await response.json();
  for (const airport of airports) {
    const option = document.createElement('option');
    option.value = airport.ident;
    option.innerText = airport.name;
    airportList.appendChild(option);
  }
});

// REGISTER ********************************************************************
const registerForm = document.querySelector('.register-form');
registerForm.addEventListener('submit', async function(e) {
  e.preventDefault();

  // Clear existing error messages
  const errorMessage = document.querySelectorAll('.error-message');
  errorMessage.forEach((msg) => msg.remove());

  let isValid = isValidPlane() && await isUserExist();

  // If all validations pass, submit the form
  if (isValid) {
    // Collect form data
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    try {
      // Send data to the API
      const response = await fetch(`${backendUrl}register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (response.ok) {
        // alert('Registration successful! Player ID: ' + result.player_id);
        localStorage.setItem('player_id', result.player_id);
        window.location.href = 'game.html';
      } else {
        displayErrorMessage(null,
            result.error || 'Registration failed. Please try again.');
      }
    } catch (error) {
      displayErrorMessage(null, 'An error occurred. Please try again.');
    }
  }
});

function isValidPlane() {
  // Check if a plane is selected
  const selectedPlane = document.querySelector('input[name="plane"]:checked');
  if (!selectedPlane) {
    displayErrorMessage(document.querySelector('#reg-plane'),
        'Please select a plane.');
    return false;
  }

  return true;
}

async function isUserExist() {
  const username = document.querySelector('#reg-username').value;
  const response = await fetch(`${backendUrl}player/${username}`);
  const data = await response.json();
  console.log(`isUserExist: ${data?.id}`);
  if (data) {
    displayErrorMessage(document.querySelector('#reg-username'),
        'Username is already taken.<br/>Please choose another.');
    return false;
  }

  return true;
}

/**
 * Function to display an error message below a form field
 * @param {HTMLElement} field - The form field element
 * @param {string} message - The error message to display
 */
function displayErrorMessage(field, message) {
  const error = document.createElement('div');
  error.className = 'error-message';
  error.innerHTML = message;
  const container = field ?
      field.parentElement :
      document.querySelector('.register-form');
  container.appendChild(error);
}

// LOGIN ***********************************************************************
const loginForm = document.querySelector('.login-form');
loginForm.addEventListener('submit', async function(e) {
  e.preventDefault();

  // Clear previous error messages
  const errorMessage = document.getElementById('login-error-message');
  errorMessage.style.display = 'none';

  // Collect form data
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value.trim();

  // Validate form inputs
  if (!username || !password) {
    showError('Username and password are required.');
    return;
  }

  try {
    // Send data to the API
    const response = await fetch(`${backendUrl}login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({username, password}),
    });

    const result = await response.json();

    if (response.ok) {
      // Handle successful login
      // alert(`Welcome back, ${result.username}! Your score: ${result.total_score}`);
      localStorage.setItem('player_id', result.player_id);
      window.location.href = 'game.html';
    } else {
      showError(result.error || 'Login failed. Please try again.');
    }
  } catch (error) {
    showError('An error occurred. Please try again.');
  }
});

// Function to display an error message
function showError(message) {
  const errorMessage = document.getElementById('login-error-message');
  errorMessage.textContent = message;
  errorMessage.style.display = 'block';
}