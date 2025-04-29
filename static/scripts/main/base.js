// let lastScrollY = window.scrollY;
window.addEventListener('scroll', function() {
    const element = document.querySelector('#MH01');
    
    if (window.scrollY > 1) {  // If the scroll position is greater than 1px
        element.classList.add('scrolled');
    } else {
        element.classList.remove('scrolled');
    }
    // Hide by transforming element top -100% when scrolling down and Show when scrolling up
    // const currentScrollY = window.scrollY;

    // if (currentScrollY > lastScrollY) {
    //   // Scrolling down: Hide the header
    //   element.style.transform = 'translateY(-100%)';
    // } else {
    //   // Scrolling up: Show the header
    //   element.style.transform = 'translateY(0)';
    // }

    // lastScrollY = currentScrollY;
});

var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl, {
      delay: { show: 500, hide: 100 }, // Custom delay in milliseconds
    });
  });

document.addEventListener('DOMContentLoaded', function () {
    var toastElList = [].slice.call(document.querySelectorAll('.toast'))
    var toastList = toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl)
    })
    toastList.forEach(toast => toast.show())  // Show all the toasts
});


function togglePassword (e) {
    const id = e.getAttribute('data-id');
    const password = document.getElementById(id);
    // toggle the type attribute
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    // toggle the eye slash icon
    this.classList.toggle('bi-eye-slash');
    this.classList.toggle('bi-eye-fill');
}

// Validate username
function validateUsername(elem) {
    var username = elem.value;
    var usernameError = document.getElementById("usernameError");
    if (username.length < 3) {
        usernameError.textContent = "Username must be at least 3 characters long";
    } else {
        usernameError.textContent = "";
    }
    // Username space validation. Remove any leading or trailing spaces
    username = username.trim();
    // Remove space in between characters
    username = username.replace(/\s+/g, '');
    // Remove any special characters found in the username except for hyphens and underscores
    username = username.replace(/[^a-zA-Z0-9-_.]/g, '');
    // Remove any previous error message
    return usernameError.textContent === "";
}