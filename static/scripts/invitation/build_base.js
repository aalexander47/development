var tooltipTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
);

var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl, {
    delay: { show: 500, hide: 100 }, // Custom delay in milliseconds
  });
});

document.addEventListener("DOMContentLoaded", function () {
  var toastElList = [].slice.call(document.querySelectorAll(".toast"));
  var toastList = toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl);
  });
  toastList.forEach((toast) => toast.show()); // Show all the toasts
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

function convertTo12HourFormat(time24) {
  // Split the input time into hours and minutes
  const [hours, minutes] = time24.split(":").map(Number);

  // Determine AM or PM
  const period = hours >= 12 ? "PM" : "AM";

  // Convert hours to 12-hour format
  let hours12 = hours % 12;
  hours12 = hours12 === 0 ? 12 : hours12; // Handle midnight (0 hours)

  // Format the time as HH:MM AM/PM
  const time12 = `${hours12}:${minutes.toString().padStart(2, "0")} ${period}`;

  return time12;
}

// Get the data from the local storage
const data = JSON.parse(localStorage.getItem("invitation_data"));

// Wait for the page to load
function onPageLoad() {
  // Split the text into words
  let typeSplit = new SplitType("[animate]", {
    types: "lines, words, chars",
    tagName: "span",
  });

  // Register ScrollTrigger
  gsap.registerPlugin(ScrollTrigger);

  // GSAP Animation
  gsap.from("[animate] .word", {
    y: "110%",
    opacity: 0,
    rotationZ: 10,
    duration: 0.4,
    ease: "back.out",
    stagger: 0.1,
    scrollTrigger: {
      trigger: "[animate]",
      start: "top 80%", // Adjust when the animation starts
      toggleActions: "play none none none", // Play animation once
    },
  });
}

// Initialize the progress bar and tab contents
document.addEventListener("DOMContentLoaded", function () {
  const progressBar = document.getElementById("progressBar");
  const tabContents = document.querySelectorAll(".tab-content");
  const totalSteps = tabContents.length;
  let currentStep = 1;

  // Initialize progress
  updateProgress();

  function updateProgress() {
    // Calculate progress percentage
    const progressPercent = ((currentStep - 1) / (totalSteps - 1)) * 100;
    progressBar.style.width = `${progressPercent}%`;

    // Hide all tabs first
    tabContents.forEach((tab) => {
      tab.classList.remove("active");
    });

    // Show current tab
    const currentTab = document.querySelector(
      `.tab-content[data-step="${currentStep}"]`
    );
    if (currentTab) {
      currentTab.classList.add("active");
    }
  }

  // Event delegation for navigation buttons
  document.addEventListener("click", function (e) {
    // Next button click
    if (e.target.classList.contains("next-btn")) {
      if (currentStep < totalSteps) {
        currentStep++;
        updateProgress();
      }
    }

    // Finish button click
    if (e.target.classList.contains("finish-btn")) {
      alert("Process completed successfully!");
      const modal = bootstrap.Modal.getInstance(
        document.getElementById("progressModal")
      );
      if (modal) modal.hide();
    }

    // Back button click
    if (e.target.classList.contains("back-btn")) {
      if (currentStep > 1) {
        currentStep--;
        updateProgress();
      }
    }
  });
});

// Wait for the page to load
window.addEventListener("load", onPageLoad);

document.querySelector("input#start_date").addEventListener("change", () => {
  // Get the min date from the start date input
  const startDateInput = document.querySelector("input#start_date");
  const minDate = startDateInput.value;
  // Add 5 days to the min date
  const maxDate = new Date(
    new Date(minDate).getTime() + 5 * 24 * 60 * 60 * 1000
  )
    .toISOString()
    .split("T")[0];
  // Set the max date for the end date input
  document.querySelector("input#end_date").setAttribute("min", maxDate);
});

// billingForm submit event listener
async function processToPayment() {
  try {
    const invitation_data = localStorage.getItem("invitation_data");
    const template_id = document.getElementById("templateID").value;
    // check if the current url has create or update in it
    const current_url = window.location.href;
    const isCreateUrl = current_url.includes("create");
    const isUpdateUrl = current_url.includes("update");

    let invitation_id = null;
    if (isUpdateUrl) {
      invitation_id = document.getElementById("invitationID").value;
    }

    if (!invitation_data) {
      console.error("No invitation data found in localStorage.");
      return;
    }

    if (template_id != JSON.parse(invitation_data)["template"]["id"]) {
      alert("Please select a valid template.");
      return;
    }

    const response = await fetch("/invitation/generate-payment/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({
        invitation_data: JSON.parse(invitation_data),
        page: isCreateUrl ? "create" : isUpdateUrl ? "update" : "other",
        invitation_id: invitation_id,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    const html = data.html;
    document.getElementById("paymentContainer").innerHTML = html;

    if (data.is_payment_required) {
      const amount = data.amount;
      const order_id = data.order_id;
      const razorpay_key = data.razorpay_key_id;
      const currency = data.currency;
      const description = data.description;

      initializePayment(amount, order_id, razorpay_key, currency, description);
    } else {
      // Add event listener to the proceed button to #publishBtn
      document.getElementById("publishBtn").addEventListener("click", () => {
        const invitation_data = localStorage.getItem("invitation_data");
        const csrftoken = getCookie("csrftoken");
        // Create a form element
        var form = document.createElement("form");
        form.action = "/invitation/payment-success/";
        form.method = "POST";
        form.id = "publishForm";
        form.innerHTML = `
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                    <input type="hidden" name="amount" value="${data.amount}">
                    <input type="hidden" name="publish_data" value='${invitation_data}'>
                `;
        document.body.appendChild(form);
        form.submit();
      });
    }
  } catch (error) {
    console.error("Error processing payment:", error);
  }
}

function initializePayment(
  amount,
  order_id,
  razorpay_key,
  currency,
  description
) {
  var options = {
    key: razorpay_key,
    amount: amount * 100, // Convert to paise
    currency: currency,
    name: "Eventic",
    description: description,
    order_id: order_id,
    handler: function (response) {
      const invitation_data = localStorage.getItem("invitation_data");

      const csrftoken = getCookie("csrftoken");
      var form = document.createElement("form");
      form.action = "/invitation/payment-success/";
      form.method = "POST";
      form.id = "razorpayForm";
      form.innerHTML = `
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                <input type="hidden" name="payment_type" value="razorpay">
                <input type="hidden" name="razorpay_payment_id" value="${response.razorpay_payment_id}">
                <input type="hidden" name="razorpay_order_id" value="${response.razorpay_order_id}">
                <input type="hidden" name="razorpay_signature" value="${response.razorpay_signature}">
                <input type="hidden" name="amount" value="${amount}">
                <input type="hidden" name="data" value='${invitation_data}'>
            `;
      document.body.appendChild(form);
      form.submit();
    },
  };

  var rzp1 = new Razorpay(options);

  document.getElementById("payNowBtn").onclick = function (e) {
    rzp1.open();
    e.preventDefault();
  };
}

// Get references to the radio buttons and body element
const viewRadios = document.querySelectorAll('input[name="view"]');
const container = document.querySelector("main");

// Add event listeners to the radio buttons
viewRadios.forEach((radio) => {
  radio.addEventListener("change", (event) => {
    const selectedView = event.target.value;

    // Update the icons for the selected view. Get all three icons
    const desktopIcon = document.querySelector(".bi-laptop-fill");
    const tabletIcon = document.querySelector(".bi-tablet-fill");
    const mobileIcon = document.querySelector(".bi-phone-fill");

    // Check if the element exists
    if (desktopIcon) {
      // Replace the .bi-laptop-fill with .bi-laptop class from the desktop icon
      desktopIcon.classList.replace("bi-laptop-fill", "bi-laptop");
    }

    if (tabletIcon) {
      // Replace the .bi-tablet-fill with .bi-tablet class from the tablet icon
      tabletIcon.classList.replace("bi-tablet-fill", "bi-tablet");
    }

    if (mobileIcon) {
      // Replace the .bi-phone-fill with .bi-phone class from the mobile icon
      mobileIcon.classList.replace("bi-phone-fill", "bi-phone");
    }

    // Remove all existing view classes
    container.classList.remove("desktop-view", "tablet-view", "mobile-view");

    // Add the selected view class to the body
    switch (selectedView) {
      case "desktop":
        container.classList.add("desktop-view");
        // Replace the .bi-laptop class with .bi-laptop-fill
        document
          .querySelector(".bi-laptop")
          .classList.replace("bi-laptop", "bi-laptop-fill");
        break;
      case "tablet":
        container.classList.add("tablet-view");
        // Replace the .bi-tablet class with .bi-tablet-fill
        document
          .querySelector(".bi-tablet")
          .classList.replace("bi-tablet", "bi-tablet-fill");
        break;
      case "mobile":
        container.classList.add("mobile-view");
        // Replace the .bi-phone class with .bi-phone-fill
        document
          .querySelector(".bi-phone")
          .classList.replace("bi-phone", "bi-phone-fill");
        break;
      default:
        container.classList.add("desktop-view");
        // Replace the .bi-laptop class with .bi-laptop-fill
        document
          .querySelector(".bi-laptop")
          .classList.replace("bi-laptop", "bi-laptop-fill");
        break;
    }
  });
});

// Set the default view to Desktop on page load
window.addEventListener("load", () => {
  container.classList.add("desktop-view");
});

/**
 * Component Options:
 * 'd' - Day with leading zero (01-31)
 * 'j' - Day without leading zero (1-31)
 * 'm' - Month with leading zero (01-12)
 * 'n' - Month without leading zero (1-12)
 * 'Y' - Full year (2025)
 * 'y' - Short year (25)
 * 'A' - Full weekday name (Monday)
 * 'a' - Short weekday name (Mon)
 * 'F' - Full month name (March)
 * 'M' - Short month name (Mar)
 * 'S' - Day with ordinal suffix (24th)
 * 'U' - Unix timestamp
 */
function getDateComponent(dateStr, component) {
  if (!dateStr) return "";

  // Try parsing with Date object first
  let dateObj = new Date(dateStr);

  // If that fails, try manual parsing
  if (isNaN(dateObj.getTime())) {
    // Try common separators (/, -, .) with different formats
    const formats = [
      { regex: /(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})/, order: [1, 0, 2] }, // DD-MM-YYYY
      { regex: /(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})/, order: [2, 1, 0] }, // YYYY-MM-DD
      { regex: /(\d{1,2})[-/.](\d{1,2})[-/.](\d{2})/, order: [1, 0, 2] }, // DD-MM-YY
    ];

    for (const format of formats) {
      const match = dateStr.match(format.regex);
      if (match) {
        const day = parseInt(match[format.order[0] + 1]);
        const month = parseInt(match[format.order[1] + 1]) - 1; // JS months are 0-indexed
        let year = parseInt(match[format.order[2] + 1]);

        // Handle 2-digit years
        if (year < 100) {
          year += year < 50 ? 2000 : 1900;
        }

        dateObj = new Date(year, month, day);
        if (!isNaN(dateObj.getTime())) break;
      }
    }

    if (isNaN(dateObj.getTime())) return "Invalid Date";
  }

  // Component extraction
  const padZero = (num) => num.toString().padStart(2, "0");
  const ordinalSuffix = (num) => {
    const j = num % 10,
      k = num % 100;
    if (j === 1 && k !== 11) return num + "st";
    if (j === 2 && k !== 12) return num + "nd";
    if (j === 3 && k !== 13) return num + "rd";
    return num + "th";
  };

  const components = {
    d: padZero(dateObj.getDate()), // Leading zero (01-31) Date
    j: dateObj.getDate().toString(), // No leading zero (1-31) Date
    m: padZero(dateObj.getMonth() + 1), // Leading zero (01-12) Month
    n: (dateObj.getMonth() + 1).toString(), // No leading zero (1-12) Month
    Y: dateObj.getFullYear().toString(), // Full year (2025)
    y: dateObj.getFullYear().toString().slice(-2), // Short year (25)
    A: [
      "Sunday",
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
    ][dateObj.getDay()], // Full weekday name (Monday)
    a: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][dateObj.getDay()], // Short weekday name (Mon)
    F: [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ][dateObj.getMonth()], // Full month name (March)
    M: [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ][dateObj.getMonth()], // Short month name (Mar)
    S: ordinalSuffix(dateObj.getDate()), // Day with ordinal suffix (24th)
  };

  return components[component] || "Invalid Component";
}
// Usage examples:
// console.log(getDateComponent("2025-03-24", "d"));  // "24"
// console.log(getDateComponent("2025-03-24", "A"));  // "Monday"
// console.log(getDateComponent("24/03/2025", "F"));  // "March"
// console.log(getDateComponent("03-24-2025", "S"));  // "24th"

// Add event listener to all .editor-data elements
const editorData = document.querySelectorAll(".editor-data");
editorData.forEach((element) => {
  element.addEventListener("click", () => {
    let data_type = element.getAttribute("data-type");
    let data_label = element.getAttribute("data-label");
    let data_key = element.getAttribute("data-key");
    const data = JSON.parse(localStorage.getItem("invitation_data"));

    if (data_type === "text") {
      // Show the modal
      let editorModalElement = document.getElementById("textEditorModal");
      let editorModal = new bootstrap.Modal(editorModalElement);
      editorModal.show();

      // Set the modal title
      editorModalElement.querySelector(".modal-title").textContent = data_label;

      // Set the modal text
      let text = data["invitation"][data_key];
      if (text) {
        editorModalElement.querySelector("#textInput").value = text;
      }

      // Set the save button data-id attribute
      editorModalElement
        .querySelector("#saveTextBtn")
        .setAttribute("data-id", element.id);
    }

    if (data_type === "address") {
      // Show the modal
      let editorModalElement = document.getElementById("addressEditorModal");
      let editorModal = new bootstrap.Modal(editorModalElement);
      editorModal.show();

      // Set the modal title
      editorModalElement.querySelector(".modal-title").textContent = data_label;

      // Set the modal address data
      if (data["invitation"]["venueLocation"]) {
        let venue = data["invitation"]["venueLocation"]["venue"];
        let address = data["invitation"]["venueLocation"]["address"];
        let city = data["invitation"]["venueLocation"]["city"];
        let state = data["invitation"]["venueLocation"]["state"];
        let country = data["invitation"]["venueLocation"]["country"];
        let postalCode = data["invitation"]["venueLocation"]["postalCode"];
        let mapUrl = data["invitation"]["venueLocation"]["mapUrl"];

        if (venue) {
          editorModalElement.querySelector("#venueInput").value = venue;
        }
        if (address) {
          editorModalElement.querySelector("#addressInput").value = address;
        }
        if (city) {
          editorModalElement.querySelector("#cityInput").value = city;
        }
        if (state) {
          editorModalElement.querySelector("#stateInput").value = state;
        }
        if (country) {
          editorModalElement.querySelector("#countryInput").value = country;
        }
        if (postalCode) {
          editorModalElement.querySelector("#postalCodeInput").value =
            postalCode;
        }
        if (mapUrl) {
          editorModalElement.querySelector("#mapUrlInput").value = mapUrl;
        }
      }

      // Set the save button data-id attribute
      editorModalElement
        .querySelector("#saveAddressBtn")
        .setAttribute("data-id", element.id);
    }

    if (data_type === "datetime") {
      // Show the modal
      let editorModalElement = document.getElementById("dateTimeEditorModal");
      let editorModal = new bootstrap.Modal(editorModalElement);
      editorModal.show();

      // Set the modal title
      editorModalElement.querySelector(".modal-title").textContent = data_label;

      // Set the modal address data
      let date = data["invitation"]["eventDate"];
      let time = data["invitation"]["eventTime"];
      let timezone = data["invitation"]["timezone"];
      if (date) {
        editorModalElement.querySelector("#dateInput").value = date;
      }
      if (time) {
        editorModalElement.querySelector("#timeInput").value = time;
      }
      if (timezone) {
        editorModalElement.querySelector("#timeZoneInput").value = timezone;
      }

      // Set the save button data-id attribute
      editorModalElement
        .querySelector("#saveDateTimeBtn")
        .setAttribute("data-id", element.id);
    }
  });
});

// Save text button event listener
const saveTextBtn = document.querySelector("#saveTextBtn");
saveTextBtn.addEventListener("click", () => {
  // Get the text input value
  let text = document.querySelector("#textInput").value;

  // Get the element id
  let elementId = saveTextBtn.getAttribute("data-id");

  let element = document.getElementById(elementId);

  // If the element id and animate the split type
  if (element.getAttribute("data-type") === "text") {
    // Create a new element
    let newElement = document.createElement("span");
    newElement.textContent = text;

    // Split the text into words
    let typeSplit = new SplitType(newElement, {
      types: "lines, words, chars",
      tagName: "span",
    });

    // Replace the element with the new element innerHTML
    element.innerHTML = newElement.innerHTML;
  }

  // Save the data to the local storage
  let data = JSON.parse(localStorage.getItem("invitation_data"));
  data["invitation"][element.getAttribute("data-key")] = text;
  localStorage.setItem("invitation_data", JSON.stringify(data));

  text.value = "";

  // Hide the modal
  let editorModal = new bootstrap.Modal(
    document.getElementById("textEditorModal")
  );
  editorModal.hide();
  // Move focus to the body
  document.body.focus();
});

const saveAddressBtn = document.querySelector("#saveAddressBtn");
saveAddressBtn.addEventListener("click", () => {
  // Get the text input value
  let venue = document.querySelector("#venueInput").value;
  let address = document.querySelector("#addressInput").value;
  let city = document.querySelector("#cityInput").value;
  let state = document.querySelector("#stateInput").value;
  let country = document.querySelector("#countryInput").value;
  let countryCode = country.split("-|-")[0];
  let countryName = country.split("-|-")[1];
  let postalCode = document.querySelector("#postalCodeInput").value;
  let mapUrl = document.querySelector("#mapUrlInput").value;

  let element = document.getElementById("address_text");

  // Create a new element
  let newElement = document.createElement("span");
  let address_info = `${venue}`;
  if (address) {
    address_info += `, ${address}`;
  }
  if (city) {
    address_info += `, ${city}`;
  }
  if (state) {
    address_info += `, ${state}`;
  }
  if (country) {
    address_info += `, ${countryName}`;
  }
  if (postalCode) {
    address_info += `, ${postalCode}`;
  }
  newElement.innerHTML = address_info;

  // Split the text into words
  let typeSplit = new SplitType(newElement, {
    types: "lines, words, chars",
    tagName: "span",
  });

  // Replace the element with the new element innerHTML
  element.innerHTML = newElement.innerHTML;

  // Save the data to the local storage
  let address_data = {
    venue: venue,
    address: address,
    city: city,
    state: state,
    country: country,
    countryCode: countryCode,
    countryName: countryName,
    postalCode: postalCode,
    mapUrl: mapUrl,
  };
  let data = JSON.parse(localStorage.getItem("invitation_data"));
  data["invitation"]["venueLocation"] = address_data;
  localStorage.setItem("invitation_data", JSON.stringify(data));

  // Hide the modal
  let editorModal = new bootstrap.Modal(
    document.getElementById("addressEditorModal")
  );
  editorModal.hide();
  // Move focus to the body
  document.body.focus();
});

const saveDateTimeBtn = document.querySelector("#saveDateTimeBtn");
saveDateTimeBtn.addEventListener("click", () => {
  // Get the text input value
  let eventDate = document.querySelector("#dateInput").value;
  let eventTime = document.querySelector("#timeInput").value;
  let timezone = document.querySelector("#timeZoneInput").value;

  // If the element id and animate the split type
  // Create a new element
  const weeding_date = new Date(eventDate);
  const options = { year: "numeric", month: "long", day: "numeric" };
  date = weeding_date.toLocaleDateString("en-US", options);

  let newDateElement = document.createElement("span");
  newDateElement.innerHTML = date;

  // Split the text into words
  let typeDateSplit = new SplitType(newDateElement, {
    types: "lines, words, chars",
    tagName: "span",
  });

  // Replace the element with the new element innerHTML
  document.getElementById("date_text").innerHTML = newDateElement.innerHTML;

  // Create a new element
  let newTimeElement = document.createElement("span");
  newTimeElement.innerHTML = convertTo12HourFormat(eventTime);

  // Split the text into words
  let typeTimeSplit = new SplitType(newTimeElement, {
    types: "lines, words, chars",
    tagName: "span",
  });

  // Replace the element with the new element innerHTML
  document.getElementById("time_text").innerHTML = newTimeElement.innerHTML;

  // Save the data to the local storage
  let data = JSON.parse(localStorage.getItem("invitation_data"));
  data["invitation"]["eventDate"] = eventDate;
  data["invitation"]["eventTime"] = eventTime;
  data["invitation"]["timezone"] = timezone;
  localStorage.setItem("invitation_data", JSON.stringify(data));

  // Hide the modal
  let editorModal = new bootstrap.Modal(
    document.getElementById("dateTimeEditorModal")
  );
  editorModal.hide();
  // Move focus to the body
  document.body.focus();
});
