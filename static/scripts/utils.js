var tooltipTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
);
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl, {
    delay: { show: 500, hide: 100 }, // Custom delay in milliseconds
  });
});

export function getCookieWithFallback(name, fallbackValue) {
  var cookieValue = getCookie(name);
  return cookieValue !== null ? cookieValue : fallbackValue;
}

// Function to set URL parameters
export function setUrlParameter(key, value) {
  // Get the current URL
  let url = new URL(window.location.href);

  // Set the parameter
  url.searchParams.set(key, value);

  // Replace the current URL with the modified one
  history.replaceState(null, null, url.href);
}

// Function to get URL parameters
export function getUrlParameter(key, default_val) {
  // Get the current URL
  let url = new URL(window.location.href);

  // Get the parameter value
  let value = url.searchParams.get(key);

  // Handle errors if the parameter does not exist
  if (value === null) {
    // You can choose to return a default value or handle the error in another way
    return default_val;
  }

  return value;
}

// Function to remove a URL parameter
export function removeUrlParameter(key) {
  // Get the current URL
  let url = new URL(window.location.href);

  // Remove the parameter
  url.searchParams.delete(key);

  // Replace the current URL with the modified one
  history.replaceState(null, null, url.href);
}

// Function to set a cookie
export function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + value + expires + "; path=/";
}

// Function to get a cookie value by name
export function getCookie(name) {
  var nameEQ = name + "=";
  var cookies = document.cookie.split(";");
  for (var i = 0; i < cookies.length; i++) {
    var cookie = cookies[i];
    while (cookie.charAt(0) == " ") cookie = cookie.substring(1, cookie.length);
    if (cookie.indexOf(nameEQ) == 0)
      return cookie.substring(nameEQ.length, cookie.length);
  }
  return null;
}

export function generateRandomId(length) {
  const characters =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let randomId = "";

  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * characters.length);
    randomId += characters.charAt(randomIndex);
  }

  return randomId;
}

// JavaScript function to check file size
function checkFileSize(file) {
  const input = file;
  const maxSize = 2 * 1024 * 1024; // 2MB in bytes

  if (input.files && input.files[0]) {
    const fileSize = input.files[0].size;

    if (fileSize > maxSize) {
      alert(
        "The file size exceeds the 2MB limit. Please upload a smaller file."
      );
      input.value = ""; // Clear the input field
      return false;
    } else {
      return true;
    }
  }
}
