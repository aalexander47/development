// Add custom toasts
document.addEventListener("DOMContentLoaded", function () {
  var toastElList = [].slice.call(document.querySelectorAll(".toast"));
  var toastList = toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl);
  });
  toastList.forEach((toast) => toast.show()); // Show all the toasts
});

// Add custom tooltips
var tooltipTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
);
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl, {
    delay: { show: 500, hide: 100 }, // Custom delay in milliseconds
  });
});

// Select the scrollable element
const scrollableComponent = document.querySelector("#cmsContent");

// Add scroll event listener to the scrollable element
scrollableComponent.addEventListener("scroll", function () {
  const element = document.querySelector("#MH01");

  // Check the scrollTop position of the scrollable component
  if (scrollableComponent.scrollTop > 1) {
    // If the scroll position is greater than 1px
    element.classList.add("scrolled");
  } else {
    element.classList.remove("scrolled");
  }
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

let intervalId;
let previousCount = 0; // Initialize a variable to track the previous count
const fetchNotificationCount = async () => {
  // Continue only if the path has "/dashboard/" or "/vendor/" at the beginning
  if (
    !window.location.pathname.startsWith("/dashboard/") &&
    !window.location.pathname.startsWith("/vendor/")
  ) {
    return;
  }
  
  // URL of your Django REST API endpoint
  const apiUrl = "/api/notifications/count/";

  try {
    const response = await fetch(apiUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "same-origin", // Include credentials for same-origin requests
    });

    if (!response.ok) {
      // Handle unauthorized access (e.g., refresh token)
      throw new Error("Unauthorized access");
    }

    const data = await response.json();

    // Update your notification count UI element
    let unreadCountElem = document.getElementById(
      "sidebarUnreadNotificationCount"
    );
    let unreadNotificationBadge = document.getElementById("notificationBadge");

    if (data.notification_count > 0) {
      let title_text = document.querySelector("title").innerText;
      if (title_text.includes(") ")) {
        title_text = title_text.split(") ")[1];
      }
      let notification_count;
      if (data.notification_count > 9) {
        notification_count = "9+";
      } else {
        notification_count = data.notification_count;
      }
      // Update the title only if the count has changed
      if (data.notification_count !== previousCount) {
        document.querySelector(
          "title"
        ).innerText = `(${notification_count}) ${title_text}`;
        unreadCountElem.innerText = notification_count;
        unreadCountElem.classList.remove("d-none");
        previousCount = notification_count; // Update previous count
      }
      if (unreadNotificationBadge) {
        unreadNotificationBadge.classList.remove("d-none");
      }
    } else {
      unreadCountElem.classList.add("d-none");
      if (unreadNotificationBadge) {
        unreadNotificationBadge.classList.add("d-none");
      }
      // Reset the title if count is zero and previousCount is not zero
      if (previousCount !== 0) {
        document.querySelector("title").innerText = document
          .querySelector("title")
          .innerText.split(") ")[1]; // Reset title
        previousCount = 0; // Reset previous count
      }
    }

    // Check if element with ID 'sidebarUnreadBugCount' exists in the DOM
    if (data.bug_count != 0) {
      let unreadBugCountElem = document.getElementById("sidebarUnreadBugCount");
      // Update the bug count UI element
      if (data.bug_count > 0) {
        unreadBugCountElem.innerText = data.bug_count;
        unreadBugCountElem.classList.remove("d-none");
      } else {
        unreadBugCountElem.classList.add("d-none");
      }
    }
  } catch (error) {
    console.error("Error fetching notification count:", error);
  }
};

// Function to start polling for notifications
// const startPolling = () => {
//   intervalId = setInterval(() => {
//     if (document.visibilityState === "visible") {
//       fetchNotificationCount();
//     }
//   }, 300000); // 300000 milliseconds = 5 minutes
// };

// Function to stop polling
// const stopPolling = () => {
//   clearInterval(intervalId);
// };

// // Event listeners to start/stop polling based on window focus
// window.addEventListener("focus", startPolling);
// window.addEventListener("blur", stopPolling);

// // Start polling when the page loads
// startPolling();
fetchNotificationCount();

// Content Area Modal
// Open contentAreaModal
$(document).ready(function () {
  $("#contentAreaModal").on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget);
    var _id = button.data("id");
    var modal = $(this);
    var contentBox = document.getElementById(_id);
    modal.find("#saveContentArea").attr("data-id", _id);
    modal
      .find("h5.modal-title")
      .html(contentBox.querySelector(".content-area-label-text").innerHTML);
    modal
      .find("#contentArea")
      .html(contentBox.querySelector("div.content-area").innerHTML);
    // Make a cursor at the end of the contenteditable div
    modal.find("#contentArea").focus();
  });
});

// Onclick saveContentArea button
document
  .getElementById("saveContentArea")
  .addEventListener("click", function () {
    const contentArea = document.querySelector(
      "#contentAreaModal #contentArea"
    );
    let id = this.getAttribute("data-id");
    const contentBox = document.getElementById(id);
    contentBox.querySelector("div.content-area").innerHTML =
      contentArea.innerHTML;
    contentBox.querySelector("textarea").innerHTML = contentArea.innerHTML;
    $("#contentAreaModal").modal("hide");
    // clear contentArea
    document.querySelector("#contentAreaModal h5.modal-title").innerHTML =
      "Content Area";
    contentArea.innerHTML = "";
    id = "";
  });


// Onclick clearFormatting button
document
  .getElementById("clearFormatting")
  .addEventListener("click", function () {
    const editableDiv = document.querySelector(
      "#contentAreaModal #contentArea"
    );

    // Get all child elements inside the contenteditable div
    const elements = editableDiv.querySelectorAll("*");

    elements.forEach((element) => {
      // Remove all attributes
      for (let i = element.attributes.length - 1; i >= 0; i--) {
        element.removeAttribute(element.attributes[i].name);
      }
    });

    // Optionally clean up classes or unnecessary spans
    const spans = editableDiv.querySelectorAll("span");
    spans.forEach((span) => {
      if (span.getAttribute("style") === null) {
        span.replaceWith(...span.childNodes);
      }
    });
  });

// Onclick insertVideo button
// Check if id "insertVideoBtn" exists
if (document.getElementById("insertVideoBtn")) {
  document
    .getElementById("insertVideoBtn")
    .addEventListener("click", function () {
      const videoUrl = prompt("Enter the YouTube video URL:");
  
      if (videoUrl) {
        // Extract the video ID from the URL using regex
        const videoIdMatch = videoUrl.match(
          /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/
        );
  
        if (videoIdMatch && videoIdMatch[1]) {
          const videoId = videoIdMatch[1];
          const iframeHtml = `<div style="display: grid; width: 100%; height: auto; place-items: center;">
                                      <iframe 
                                          style="display: block; margin: 0 auto !important; width: auto; max-width: 900px; height: 100%; aspact-ratio: 16/9; object-fit: cover;"
                                          src="https://www.youtube.com/embed/${videoId}" 
                                          frameborder="0" 
                                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                                          allowfullscreen>
                                      </iframe>
                                  </div>`;
  
          // Insert the iframe HTML at the cursor position
          document.execCommand("insertHTML", false, iframeHtml);
        } else {
          alert("Invalid YouTube URL. Please try again.");
        }
      }
    });
}


// Get references to the editor and buttons
const editor = document.getElementById("contentArea");
const buttons = document.querySelectorAll("button.content-area-editor-btn");

// Add click listeners to buttons for formatting
buttons.forEach(button => {
    button.addEventListener("click", () => {
        const command = button.getAttribute("data-command");
        const value = button.getAttribute("data-value");

        // Execute the command
        document.execCommand(command, false, value);

        // Update button states
        updateButtonStates();
    });
});

// Function to update button states based on selection
function updateButtonStates() {
    buttons.forEach(button => {
        const command = button.getAttribute("data-command");
        const value = button.getAttribute("data-value");

        // Check if the selected text matches the formatting
        if (command === "formatBlock" && document.queryCommandValue(command) === value) {
            button.classList.add("active");
        } else {
            button.classList.remove("active");
        }
    });
}

// Listen for selection changes in the editor
document.addEventListener("selectionchange", () => {
    if (document.activeElement === editor) {
        updateButtonStates();
    }
});
