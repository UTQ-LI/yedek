const navLinks = document.querySelectorAll('.nav-item');
const pages = document.querySelectorAll('.page');

navLinks.forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const currentPage = document.querySelector(`[data-page="${link.dataset.page}"]`);
    const nextPage = document.querySelector(`[data-page="${link.getAttribute('href').replace('#', '')}"]`);

    if (nextPage) {
      currentPage.classList.add('animate-out');
      nextPage.classList.add('animate-in');

      setTimeout(() => {
        currentPage.classList.remove('animate-out');
        nextPage.classList.remove('animate-in');
      }, 500);
    }
  });
});

// IP address display
const ipElement = document.getElementById('ip-address');

fetch('https://jsonip.com')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok ' + response.statusText);
    }
    return response.json();
  })
  .then(data => {
    ipElement.textContent = data.ip;
  })
  .catch(error => {
    ipElement.textContent = 'Could not fetch IP address.';
    console.error('Error fetching IP address:', error);
  });