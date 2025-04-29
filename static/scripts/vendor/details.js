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

function previewImage(input) {
  if (!checkFileSize(input)) {
    return;
  }
  var file = input.files[0];
  const id = input.id;
  var reader = new FileReader();

  reader.onload = function (e) {
    document.getElementById("label_" + id).src = e.target.result;
    document.getElementById('remove_'+ id).checked = false;
  };

  reader.readAsDataURL(file);
}

// Function to set URL parameters
function setUrlParameter(key, value) {
  // Get the current URL
  let url = new URL(window.location.href);

  // Set the parameter
  url.searchParams.set(key, value);

  // Replace the current URL with the modified one
  history.replaceState(null, null, url.href);
}

// Function to get URL parameters
function getUrlParameter(key, default_val) {
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
function removeUrlParameter(key) {
  // Get the current URL
  let url = new URL(window.location.href);

  // Remove the parameter
  url.searchParams.delete(key);

  // Replace the current URL with the modified one
  history.replaceState(null, null, url.href);
}

// Function to get a cookie value by name
function getCookie(name) {
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

function getCookieWithFallback(name, fallbackValue) {
  var cookieValue = getCookie(name);
  return cookieValue !== null ? cookieValue : fallbackValue;
}

function generateRandomId(length) {
  const characters =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let randomId = "";

  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * characters.length);
    randomId += characters.charAt(randomIndex);
  }

  return randomId;
}

function removeBlock(elem) {
  const remove_elem_id = elem.getAttribute("data-remove-id");
  const elementToRemove = document.getElementById(remove_elem_id);
  if (elementToRemove) {
    if (confirm("Are you sure you want to remove this block?")) {
      elementToRemove.remove();
    }
  }
  return;
}

function countChars(obj) {
  var maxLength = parseInt(obj.getAttribute("maxlength"));
  var currentLength = obj.value.length;
  var id = obj.id + "__charCount";
  var charCountElement = document.getElementById(id);

  charCountElement.textContent = currentLength + "/" + maxLength;
}

function convertToTitleCase(str) {
  if (!str) {
    return "";
  }
  return str.replace(/\w\S*/g, function (txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
}

function fetchPincodeData() {
  const pincode = document.getElementById("pincode");
  const url = `https://api.postalpincode.in/pincode/${pincode.value}`; // Example API endpoint

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      data = data[0];
      if (data.Status === "Success") {
        document.getElementById("state").value = data.PostOffice[0].State;
        document.getElementById("city").value = data.PostOffice[0].Name;
        document.getElementById("country").value = data.PostOffice[0].Country;
      } else {
        alert("Pincode not found or API error!");
        pincode.value = "";
      }
    })
    .catch((error) => console.error(error));
}

function switchTab(currentTab) {
  const tab_id = currentTab.getAttribute("data-tab");
  const tabs_class = currentTab.getAttribute("data-tab-container");
  const is_set_parameter = currentTab.getAttribute("data-set-parameter");
  const tabContainers = document.querySelectorAll(`.${tabs_class}`);
  tabContainers.forEach((tab) => {
    if (!tab.classList.contains("d-none")) {
      tab.classList.add("d-none");
    }
    if (tab.id === `${tab_id}Container`) {
      tab.classList.remove("d-none");
    }
  });
  if (is_set_parameter === "false") {
    return;
  }

  if (tab_id !== "default") {
    setUrlParameter("tab", tab_id);
  } else {
    removeUrlParameter("tab");
  }
}

$(document).ready(() => {
  const currentTab = getUrlParameter("tab", "default");
  let tab = document.getElementById(`${currentTab}Tab`);
  tab.checked = true;
  switchTab(tab);
});

// function to get the component to insert in a div from an external file:
function getComponentFromUrl(url, targetDivId) {
  const targetDiv = document.getElementById(targetDivId);

  if (!targetDiv) {
    console.error(`Div with id "${targetDivId}" not found.`);
    return;
  }

  fetch(url)
    .then((response) => response.text())
    .then((data) => {
      targetDiv.innerHTML = data;
    })
    .catch((error) =>
      console.error(`Error fetching component from URL: ${error}`)
    );
}

function selectServiceType(service_type) {
  getComponentFromUrl(
    `/vendor/component/${service_type}/`,
    "selectServicesContainer"
  );
}

function showHideElems(show) {
  const services = {
    photographer: "ptgr",
    videographer: "vdgr",
    make_up_artist: "mkup",
  };
  const selected_service = document.getElementById("serviceType").value;
  const elems_to_show = document.querySelectorAll(`.ctgry-${show}`);
  const elems_to_hide = document.querySelectorAll(
    `.ctgry-${services[selected_service]}`
  );

  elems_to_hide.forEach((elem) => {
    elem.style.setProperty("display", "none", "important");
  });
  elems_to_show.forEach((elem) => {
    elem.style.setProperty("display", "block", "important");
  });
  document.getElementById("ctgry_photography").classList.remove("d-none");
}

function photographyShowHide() {
  const category = document.getElementById("photographyCategory").value;
  const categories = {
    wedding: "web",
    product: "pdt",
    portrait: "prt",
    concert: "cct",
    event: "evt",
    fashion: "fsn",
    sports: "spt",
  };
  const show = categories[category];
  showHideElems(show);
}

function addPlanBlock() {
  const uid = generateRandomId(4);
  let block = `
        <div class="col-6 mb-3 plan-card" id="planCard_${uid}">
            <div class="card p-3 rounded-3">
                <div class="row align-items-center">
                    <div class="col-7 pe-1">
                        <div class="form-group">
                            <input type="text" class="form-control shadow-none fs-4" placeholder="Plan name" id="plan_name" name="plan_name" required>
                        </div>
                    </div>
                    <div class="col-5 ps-1">
                        <div class="input-group">
                            <span for="plan_price_${uid}" class="input-group-text"><i class="bi bi-currency-rupee"></i></span>
                            <input type="text" class="form-control shadow-none" placeholder="00" name="plan_price" aria-label="plan_price_${uid}" aria-describedby="plan_price_${uid}">
                            <button class="btn btn-outline-secondary" type="button" id="plan_price_${uid}" data-bs-toggle="collapse" data-bs-target="#planCollapse_${uid}" aria-expanded="false" aria-controls="planCollapse_${uid}"><i class="bi bi-arrow-down"></i></button>
                            <button class="btn btn-outline-danger" type="button" id="plan_remove_btn_${uid}" data-remove-id="planCard_${uid}" onclick="removeBlock(this);"><i class="bi bi-trash3"></i></button>
                        </div>
                    </div>
                </div>
                <div class="collapse" id="planCollapse_${uid}">
                    <div class="mt-2">
                        <div class="form-group">
                            <div class="row align-items-center">
                                <div class="col">
                                    <label for="plan_details_${uid}" class="form-label mb-0">Plan Details</label>
                                </div>
                                <div class="col-auto"><label id="plan_details_${uid}__charCount">0/1000</label></div>
                            </div>
                            <textarea class="custom-scrollbar shadow-none form-control" name="plan_details" id="plan_details_${uid}" rows="8" maxlength="1000" onkeyup="countChars(this)"></textarea>
                        </div>
                    </div>
                </div>                  
            </div>
        </div>`;
  document
    .getElementById("plansContainerBlock")
    .insertAdjacentHTML("beforeend", block);
}

function addFAQBlock() {
  const uid = generateRandomId(4);
  let block = `
        <div class="mb-3 faq-card" id="faqCard_${uid}">
            <div class="card p-3 rounded-3">
                <div class="row align-items-center">
                    <div class="col pe-1">
                        <div class="form-group">
                            <input type="text" class="form-control shadow-none fs-4" placeholder="FAQ Question" id="faq_question" name="faq_question" required>
                        </div>
                    </div>
                    <div class="col-auto ps-1">
                        <div class="input-group">
                            <button class="btn btn-outline-secondary" type="button" id="faq_dropdown_${uid}" data-bs-toggle="collapse" data-bs-target="#faqCollapse_${uid}" aria-expanded="false" aria-controls="faqCollapse_${uid}"><i class="bi bi-arrow-down"></i></button>
                            <button class="btn btn-outline-danger" type="button" id="faq_remove_btn_${uid}" data-remove-id="faqCard_${uid}" onclick="removeBlock(this);"><i class="bi bi-trash3"></i></button>
                        </div>
                    </div>
                </div>
                <div class="collapse" id="faqCollapse_${uid}">
                    <div class="mt-2">
                        <div class="form-group">
                            <div class="row align-items-center">
                                <div class="col">
                                    <label for="faq_answer_${uid}" class="form-label mb-0">Answer</label>
                                </div>
                                <div class="col-auto"><label id="faq_answer_${uid}__charCount">0/500</label></div>
                            </div>
                            <textarea class="custom-scrollbar shadow-none form-control" name="faq_answer" id="faq_answer_${uid}" rows="8" maxlength="500" onkeyup="countChars(this)"></textarea>
                        </div>
                    </div>
                </div>                  
            </div>
        </div>`;
  document
    .getElementById("faqsContainerBlock")
    .insertAdjacentHTML("beforeend", block);
}

function updateEmbedMap(e) {
  const embedMap = e.value;
  const regex = /src="([^"]+)"/;
  const match = embedMap.match(regex);
  if (match) {
    document.getElementById("map_iframe").setAttribute("src", match[1]);
    e.setAttribute("value", match[1]);
    e.value = match[1];
  }
}
