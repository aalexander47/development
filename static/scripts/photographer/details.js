var tooltipTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
);
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl, {
    delay: { show: 500, hide: 100 }, // Custom delay in milliseconds
  });
});

function recommendationCheckboxLimit() {
  var checkboxes = document.getElementsByName("recommend_for");
  var checked_checkboxes = document.querySelectorAll(
    'input[name="recommend_for"]:checked'
  );
  // if the limit crossed disable the inchecked checkboxes
  if (checked_checkboxes.length >= 3) {
    for (var i = 0; i < checkboxes.length; i++) {
      if (!checkboxes[i].checked) {
        checkboxes[i].disabled = true;
      }
    }
  } else {
    for (var i = 0; i < checkboxes.length; i++) {
      checkboxes[i].disabled = false;
    }
  }
}
// add event listener on change on each checkbox
var checkboxes = document.getElementsByName("recommend_for");
for (var i = 0; i < checkboxes.length; i++) {
  checkboxes[i].addEventListener("change", recommendationCheckboxLimit);
}

document.addEventListener("scroll", function () {
  const callButton = document.querySelector("#contactContainer");
  if (callButton) {
    const firstBox = document.querySelector("#serviceDetails");
    const lastBox = document.querySelector("#mainContainer");
    const firstBoxRect = firstBox.getBoundingClientRect();
    const lastBoxRect = lastBox.getBoundingClientRect();
    if (
      firstBoxRect.top < 0 &&
      lastBoxRect.bottom > window.innerHeight - 100
    ) {
      // First box is completely out of view (scrolled up)
      callButton.classList.add("visible");
    } else {
      // First box is in view
      callButton.classList.remove("visible");
    }
  }
});


document.getElementById("share-button").addEventListener("click", function () {
  if (navigator.share) {
      navigator.share({
          title: document.title, // Title of the current page
          text: "Check out this page!", // Message text
          url: window.location.href // Current page URL
      })
      .then(() => console.log("Content shared successfully!"))
      .catch((error) => console.error("Error sharing:", error));
  } else {
      alert("Sharing is not supported on this browser. Please use a modern browser or mobile device.");
  }
});


document.getElementById("copy-link-button").addEventListener("click", function () {
  // Get the current page URL
  const pageUrl = window.location.href;

  // Use the Clipboard API to copy the link
  navigator.clipboard.writeText(pageUrl).then(() => {
      // Show feedback message
      const feedback = document.getElementById("copy-link-button");
      feedback.innerHTML = "<i class='bi bi-check2-circle'></i><span id='copy-feedback'>Copied!</span>";
      setTimeout(() => {
          feedback.innerHTML = "<i class='bi bi-link-45deg'></i><span id='copy-feedback'>Copy Link</span>";
      }, 3000); // Hide after 2 seconds
  }).catch((error) => {
      console.error("Failed to copy link: ", error);
      alert("Unable to copy the link. Please try again.");
  });
});

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Function to trigger lead tracking. Disables the button to prevent multiple clicks. Uses async/await
async function triggerLead(elem) {
  const lead_type = elem.getAttribute("data-lead-type");
  elem.disabled = true;
  if (lead_type == 'phone') {
    elem.querySelector('span.btn-text').innerHTML = "Calling...";
  }
  await trackLead(elem);
  elem.disabled = false;
  if (lead_type == 'phone') {
    elem.querySelector('span.btn-text').innerHTML = "Call Now";
  }
}

async function trackLead(elem) {
  const lead_type = elem.getAttribute("data-lead-type");
  try {
    // Get current domain name
    const url = window.location.href;
    const csrftoken = getCookie("csrftoken");

    // Prepare data to send (similar to the original AJAX request)
    const data = new URLSearchParams();
    data.append("lead", "true");
    data.append("lead_type", lead_type);

    // Perform the async fetch call
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "Content-Type": "application/x-www-form-urlencoded", // ensure the format is correct for form data
      },
      body: data,
    });

    // Check if the response is okay
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    // Parse the response as JSON
    const result = await response.json();

    if (result.error) {
      alert(result.message);
      // Reload the page to get the updated lead count
      window.location.reload();
      return; 
    }

    // Handle the success action once data is received
    if (result.action && lead_type === "phone") {
      // Initiate the phone call
      window.location.href = result.action;
    } else if (result.action) {
      // Open other links (WhatsApp, email, etc.) in a new tab
      window.open(result.action, "_blank");
    } else {
      alert("Something went wrong. Please try again later.");
    }
  } catch (error) {
    // Handle errors
    console.error(error);
    alert("Something went wrong. Please try again later.");
  }
  elem.disabled = false;
}

// Model Report Bootstrap
try {
  var reportReviewModal = document.getElementById("reportReviewModal");
  if (reportReviewModal) {
    reportReviewModal.addEventListener("show.bs.modal", function (event) {
      let is_authenticated = reportReviewModal.getAttribute('data-is-auth');
  
      if (is_authenticated === 'true') {
        // Button that triggered the modal
        var button = event.relatedTarget;
        // Extract info from data-bs-* attributes
        var review_id = button.getAttribute("data-bs-review-id");
        var username = button.getAttribute("data-bs-username");
        // If necessary, you could initiate an AJAX request here
        // Update the modal's content.
        var modalTitle = reportReviewModal.querySelector(".modal-title");
        var modalBodyInput = reportReviewModal.querySelector(
          ".modal-body #reviewID"
        );
    
        modalTitle.textContent = "Report review of " + username;
        modalBodyInput.value = review_id;
      }
    });
  }
} catch (error) {
  console.error("Error:", error);
}

async function likeTrigger(likeButton) {
  const vendor_id = likeButton.getAttribute("data-vendor-id");
  const service_id = likeButton.getAttribute("data-id");
  const is_liked = likeButton.getAttribute('data-liked');
  let like_count = document.getElementById('likeCount').innerHTML;

  if (is_liked === 'false') {
    likeButton.classList.add("liked");
    likeButton.classList.replace("bi-heart", "bi-heart-fill");
    likeButton.setAttribute("title", "Unlike");
    if (like_count === "") {
      like_count = 1;
    } else {
      like_count = parseInt(like_count) + 1;
    }
  } else {
    likeButton.classList.remove("liked");
    likeButton.classList.replace("bi-heart-fill", "bi-heart");
    likeButton.setAttribute("title", "Like");
    like_count.innerHTML = parseInt(like_count.innerHTML) - 1;
    likeButton.setAttribute('data-liked', 'false');
  }
  
  try {
    // Prepare data to send (similar to the original AJAX request)
    const post_data = new URLSearchParams();
    post_data.append("service_id", service_id);
    post_data.append("vendor_id", vendor_id);

    const response = await fetch(`/photographer/like/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: post_data,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
      return
    }
  } catch (error) {
    // Toggle like/unlike state
    if (is_liked === 'true') {
      likeButton.classList.add("liked");
      likeButton.classList.replace("bi-heart", "bi-heart-fill");
      likeButton.setAttribute("title", "Unlike");
      like_count.innerHTML = parseInt(like_count.innerHTML) - 1;
      likeButton.setAttribute('data-liked', 'false');
    } else {
      likeButton.classList.remove("liked");
      likeButton.classList.replace("bi-heart-fill", "bi-heart");
      likeButton.setAttribute("title", "Like");
      let like_count = 
      like_count.innerHTML = parseInt(like_count.innerHTML) + 1;
      likeButton.setAttribute('data-liked', 'true');
    }
    console.error(error);
  }
}

async function saveTrigger(saveButton) {
  const vendor_id = saveButton.getAttribute("data-vendor-id");
  const service_id = saveButton.getAttribute("data-id");
  const is_saved = saveButton.getAttribute('data-saved');

  if (is_saved === 'false') {
    saveButton.classList.add("saved");
    saveButton.classList.replace("bi-bookmark", "bi-bookmark-check-fill");
    saveButton.setAttribute("title", "Unsave");
    saveButton.setAttribute('data-saved', 'true');
  } else {
    saveButton.classList.remove("saved");
    saveButton.classList.replace("bi-bookmark-check-fill", "bi-bookmark");
    saveButton.setAttribute("title", "Like");
    saveButton.setAttribute('data-saved', 'false');
  }
  
  try {
    // Prepare data to send (similar to the original AJAX request)
    const post_data = new URLSearchParams();
    post_data.append("service_id", service_id);
    post_data.append("vendor_id", vendor_id);

    const response = await fetch(`/photographer/save/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: post_data,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    if (data.success) {
      return
    }

  } catch (error) {
    // Toggle save/unsave state
    if (is_saved === 'true') {
      saveButton.classList.remove("saved");
      saveButton.classList.replace("bi-bookmark-check-fill", "bi-bookmark");
      saveButton.setAttribute("title", "Save");
      saveButton.setAttribute('data-saved', 'false');
    } else {
      saveButton.classList.add("saved");
      saveButton.classList.replace("bi-bookmark", "bi-bookmark-check-fill");
      saveButton.setAttribute("title", "Unsave");
      saveButton.setAttribute('data-saved', 'true');
    }
    console.error(error);
  }
}

////////////////////////////////// Accordion /////////////////////////////////
const items = document.querySelectorAll(".accordion button");

function toggleAccordion() {
  const itemToggle = this.getAttribute('aria-expanded');
  
  for (i = 0; i < items.length; i++) {
    items[i].setAttribute('aria-expanded', 'false');
  }
  
  if (itemToggle == 'false') {
    this.setAttribute('aria-expanded', 'true');
  }
}

items.forEach(item => item.addEventListener('click', toggleAccordion));

///////////////////////////////// Accordion /////////////////////////////////