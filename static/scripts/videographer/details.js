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
  const callButton = document.querySelector(".slide-container");
  if (callButton) {
    const firstBox = document.querySelector("#serviceDetails");
    const lastBox = document.querySelector("#mainContainer");
    const firstBoxRect = firstBox.getBoundingClientRect();
    const lastBoxRect = lastBox.getBoundingClientRect();
    if (
      firstBoxRect.bottom < 120 &&
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

const slideButton = document.getElementById("slide-button");
const slideContainer = document.querySelector(".slide-container");
const slideText = document.querySelector(".slide-text");
if (slideButton && slideContainer && slideText) {
  let isDragging = false;
  let startX = 0;
  let currentX = 0;
  let buttonWidth = slideButton.offsetWidth;
  let containerWidth = slideContainer.offsetWidth;
  let textWidth = slideText.offsetWidth - 8;
  
  slideButton.addEventListener("mousedown", function (e) {
    isDragging = true;
    startX = e.clientX;
  });
  
  document.addEventListener("mousemove", function (e) {
    if (isDragging) {
      currentX = e.clientX;
      let offset = currentX - startX;
  
      // Make sure button doesn't move out of bounds
      if (offset < 0) offset = 0;
      if (offset > textWidth - buttonWidth) offset = textWidth - buttonWidth;
  
      slideButton.style.transform = `translateX(${offset}px)`;
    }
  });
  
  document.addEventListener("mouseup", async function (e) {
    if (isDragging) {
      isDragging = false;
      if (currentX - startX >= textWidth - buttonWidth) {
        // Action for the "Call"
        slideContainer.classList.add("active");
        const is_inactive = callButton.classList.contains("inactive");
        if (is_inactive) {
          // Show requestCallbackModal if the button is not active
          document.getElementById("requestCallback").click();
        } else {
          await trackLead("call_slider");
        }
        slideButton.style.transform = "translateX(0)";
      } else {
        // Reset button position
        slideButton.style.transform = "translateX(0)";
        slideContainer.classList.remove("active");
      }
    }
  });
  
  slideButton.addEventListener("touchstart", function (e) {
    isDragging = true;
    startX = e.touches[0].clientX;
  });
  
  document.addEventListener("touchmove", function (e) {
    if (isDragging) {
      currentX = e.touches[0].clientX;
      let offset = currentX - startX;
  
      // Make sure button doesn't move out of bounds
      if (offset < 0) offset = 0;
      if (offset > textWidth - buttonWidth) offset = textWidth - buttonWidth;
  
      slideButton.style.transform = `translateX(${offset}px)`;
    }
  });
  
  document.addEventListener("touchend", async function (e) {
    if (isDragging) {
      isDragging = false;
      if (currentX - startX >= textWidth - buttonWidth) {
        // Action for the "Call"
        slideContainer.classList.add("active");
        const is_inactive = document
          .querySelector("#slideContainer")
          .classList.contains("inactive");
        if (is_inactive) {
          // Show requestCallbackModal if the button is not active
          document.getElementById("requestCallback").click();
        } else {
          // Send lead tracking it's a asynchronous call
          await trackLead("call_slider");
        }
        slideButton.style.transform = "translateX(0)";
      } else {
        // Reset button position
        slideButton.style.transform = "translateX(0)";
        slideContainer.classList.remove("active");
      }
    }
  });
}

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

async function trackLead(lead_type) {
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

    // Handle the success action once data is received
    if (
      result.action &&
      (lead_type === "phone" || lead_type === "call_slider")
    ) {
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
  let like_count = document.getElementById('likeCount');

  if (is_liked === 'false') {
    likeButton.classList.add("liked");
    likeButton.classList.replace("bi-heart", "bi-heart-fill");
    likeButton.setAttribute("title", "Unlike");
    if (like_count.innerHTML === "") {
      like_count.innerHTML = 1;
    } else {
      like_count.innerHTML = parseInt(like_count.innerHTML) + 1;
    }
    likeButton.setAttribute('data-liked', 'true');
  } else {
    likeButton.classList.remove("liked");
    likeButton.classList.replace("bi-heart-fill", "bi-heart");
    likeButton.setAttribute("title", "Like");
    if (parseInt(like_count.innerHTML) === 1) {
      like_count.innerHTML = "";
    } else {
      like_count.innerHTML = parseInt(like_count.innerHTML) - 1;
    }
    likeButton.setAttribute('data-liked', 'false');
  }
  
  try {
    // Prepare data to send (similar to the original AJAX request)
    const post_data = new URLSearchParams();
    post_data.append("service_id", service_id);
    post_data.append("vendor_id", vendor_id);

    const response = await fetch(`/videographer/like/`, {
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
      if (parseInt(like_count.innerHTML) === 1) {
        like_count.innerHTML = "";
      } else {
        like_count.innerHTML = parseInt(like_count.innerHTML) - 1;
      }
      likeButton.setAttribute('data-liked', 'false');
    } else {
      likeButton.classList.remove("liked");
      likeButton.classList.replace("bi-heart-fill", "bi-heart");
      likeButton.setAttribute("title", "Like");
      if (like_count.innerHTML === "") {
        like_count.innerHTML = 1;
      } else {
        like_count.innerHTML = parseInt(like_count.innerHTML) + 1;
      }
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

    const response = await fetch(`/videographer/save/`, {
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