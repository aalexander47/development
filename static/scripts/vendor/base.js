document.addEventListener('DOMContentLoaded', function () {
    var toastElList = [].slice.call(document.querySelectorAll('.toast'))
    var toastList = toastElList.map(function (toastEl) {
      return new bootstrap.Toast(toastEl)
    })
    toastList.forEach(toast => toast.show())  // Show all the toasts
});

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl, {
    delay: { "show": 500, "hide": 100 }  // Custom delay in milliseconds
  })
})

let lastScrollY = window.scrollY;
window.addEventListener('scroll', function() {
    const element = document.querySelector('#MH01');
    
    if (window.scrollY > 1) {  // If the scroll position is greater than 1px
        element.classList.add('scrolled');
    } else {
        element.classList.remove('scrolled');
    }
    // Hide by transforming element top -100% when scrolling down and Show when scrolling up
    const currentScrollY = window.scrollY;

    if (currentScrollY > lastScrollY) {
      // Scrolling down: Hide the header
      element.style.transform = 'translateY(-100%)';
    } else {
      // Scrolling up: Show the header
      element.style.transform = 'translateY(0)';
    }

    lastScrollY = currentScrollY;
});