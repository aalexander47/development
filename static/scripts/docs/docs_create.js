function execCmd(command, value = null) {
  document.execCommand(command, false, value);
}

function debounce(func, delay) {
  let timerId;

  return function (...args) {
    if (timerId) {
      clearTimeout(timerId);
    }

    timerId = setTimeout(() => {
      func.apply(this, args);
      timerId = null;
    }, delay);
  };
}

function createLink(target) {
  const url = prompt("Enter the URL:");
  if (url) {
    const aTag = `<a href="${url}" target="${target}" role="button">${window
      .getSelection()
      .toString()}</a>`;
    execCmd("insertHTML", aTag);
  }
}

function addImage() {
  const imageUrl = prompt("Enter the image URL:");
  const altText = prompt("Enter the alt text (optional):");
  const className = prompt("Enter the class name (optional):");
  if (imageUrl) {
    let imgTag = `<img src="${imageUrl}"`;
    if (altText) {
      imgTag += ` alt="${altText}"`;
    }
    if (className) {
      imgTag += ` class="${className}"`;
    }
    imgTag += ">";
    execCmd("insertHTML", imgTag);
  }
}

function updateCodeOutput() {
  const allBoxes = document.querySelectorAll(".content-box");
  let boxID = "";
  allBoxes.forEach((elem) => {
    const inputCheck = elem.querySelector("input[name='edit_box']").checked;
    if (inputCheck) {
      boxID = elem.getAttribute("data-box-id");
    }
  })
  if (boxID) {
    const outputDiv = document.querySelector(`#box-${boxID} #output-${boxID}`);
    const heading = document.querySelector(`#box-${boxID} #linkingText-${boxID}`).value;
    const codeEditor = document.querySelector(`#box-${boxID} #code-editor-${boxID}`);
    const innerCode = document.querySelector(`#editor-${boxID}`).innerHTML;
    if (heading.length > 0) {
      outputDiv.innerHTML = `<h2 class="h5 sub-title">${heading}</h2>` + innerCode;
    } else {
      outputDiv.innerHTML = innerCode;
    }
    codeEditor.value = innerCode;
  } else {
    alert("Please select the box first which you want to edit");
  }
}
const debouncedUpdateCodeOutput = debounce(() => {updateCodeOutput();}, 300);

function  setTabParam(elem) {
  const urlParams = new URLSearchParams(window.location.search);
  const tab = urlParams.get("tab");
  if (tab) {
    urlParams.set("tab", elem.getAttribute("aria-controls"));
  } else {
    urlParams.append("tab", elem.getAttribute("aria-controls"));
  }
  const newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname + "?" + urlParams.toString();
  window.history.pushState(null, null, newUrl);
}

function checkActiveTab() {
  // Get tab parameter from URL
  const urlParams = new URLSearchParams(window.location.search);
  const tab = urlParams.get("tab");
  if (tab) {
    document.getElementById(`pills-${tab}-tab`).click();
  }
}
checkActiveTab();

function updateEditorOutput() {
  const allBoxes = document.querySelectorAll(".content-box");
  const editableDiv = document.querySelector(
    "#contentContainer .edit-box input[name='edit_box']:checked"
  );
  let boxID = editableDiv.getAttribute("data-id");
  if(boxID) {
    const outputDiv = document.querySelector(`#box-${boxID} #output-${boxID}`);
    const heading = document.querySelector(`#box-${boxID} #linkingText-${boxID}`).value;
    const editorDiv = document.querySelector(`#editor-${boxID}`);
    const textCode = document.querySelector(`#code-editor-${boxID}`).value;
    if (heading.length > 0) {
      outputDiv.innerHTML = `<h5 class="h5 sub-title">${heading}</h5>` + textCode;
    } else {
      outputDiv.innerHTML = textCode;
    }
    editorDiv.innerHTML = textCode;
  } else {
    alert("Please select the box first which you want to edit");
  }
}
const debouncedUpdateEditorOutput = debounce(() => {updateEditorOutput();}, 300);

function setTitleName() {
  const title = document.getElementById('docsTitleInput').value;
  if (title.length > 0) {
    document.getElementById('docsTitle').innerHTML = title;
  } else {
    document.getElementById('docsTitle').innerHTML = '--';
  }
}

const debouncedUpdateTitle = debounce(() => {setTitleName();}, 300);

function wrapSelected() {
  const selection = window.getSelection();
  const selectedText = selection.toString();
  const tag = prompt("Enter the tag:");
  const className = prompt("Enter the class name (optional):");
  const id = prompt("Enter the ID (optional):");
  if (selectedText && tag) {
    let wrappedText = `<${tag}`;
    if (className) {
      wrappedText += ` class="${className}"`;
    }
    if (id) {
      wrappedText += ` id="${id}"`;
    }
    wrappedText += `>${selectedText}</${tag}>`;
    const range = selection.getRangeAt(0);
    range.deleteContents();
    const fragment = range.createContextualFragment(wrappedText);
    range.insertNode(fragment);
  }
}

function wrapCustomTag() {
  const selection = window.getSelection();
  if (selection.rangeCount > 0) {
    const range = selection.getRangeAt(0);
    const wrapperTag = prompt("Enter the wrapper tag:");
    const wrapperAttributes = prompt(
      "Enter the wrapper attributes (optional):"
    );
    if (wrapperTag) {
      const wrapperElement = document.createElement(wrapperTag);
      if (wrapperAttributes) {
        const attributesArr = wrapperAttributes.split(",");
        attributesArr.forEach((attribute) => {
          const [attrName, attrValue] = attribute.split("=");
          if (attrName && attrValue) {
            wrapperElement.setAttribute(attrName.trim(), attrValue.trim());
          }
        });
      }
      range.surroundContents(wrapperElement);
    }
  }
}

let dragCard = null;
function dragDownStart() {
  const cards = document.querySelectorAll("#contentContainer .edit-box");

  // Add event listeners for drag events on each card
  cards.forEach((card) => {
    card.addEventListener("dragstart", dragStart);
    card.addEventListener("dragover", dragOver);
    card.addEventListener("dragend", dragEnd);
  });
}
dragDownStart();

function dragStart(e) {
  dragCard = this;
  setTimeout(() => {
    this.style.opacity = "0.5";
  }, 0);
}

function dragOver(e) {
  e.preventDefault();
  const afterElement = getDragAfterElement(this, e.clientY);
  const container = this.parentNode;

  if (afterElement == null) {
    container.appendChild(dragCard);
  } else {
    container.insertBefore(dragCard, afterElement);
  }
}

function dragEnd(e) {
  this.style.opacity = "1";
  dragCard = null;
}

function getDragAfterElement(card, y) {
  const draggableElements = [
    ...document.querySelectorAll(".edit-box:not(.dragging)"),
  ];

  return draggableElements.reduce(
    (closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;

      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      } else {
        return closest;
      }
    },
    { offset: Number.NEGATIVE_INFINITY }
  ).element;
}

function previewArticle() {
  // Remove all the checked from the radio inputs
  const radioInputs = document.querySelectorAll(
    "#contentContainer .edit-box input[name='edit_box']"
  );
  radioInputs.forEach((radioInput) => {
    radioInput.checked = false;
  });
}

function generateRandomId(length) {
  const characters =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let id = "";

  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * characters.length);
    id += characters.charAt(randomIndex);
  }
  return id;
}

function checkActiveRadio() { 
  const radioInputs = document.querySelectorAll(
    "#contentContainer .edit-box input[name='edit_box']"
  );
  document.getElementById("contentBox").disabled = false;
  let isActive = false;
  for (let i = 0; i < radioInputs.length; i++) {
    if (radioInputs[i].checked) {
      isActive = true;
      break;
    }
  }
  if (isActive) {
    document.getElementById("deleteBoxBtn").disabled = false;
  } else {
    document.getElementById("deleteBoxBtn").disabled = true;
  }
  showHideBox();
}

function showHideBox() {
  const allBoxes = document.querySelectorAll(".content-box");
  allBoxes.forEach((elem) => {
    const inputCheck = elem.querySelector("input[name='edit_box']").checked;
    if (inputCheck) {
      elem.querySelector(".card-main-container").style.setProperty("display", "block");
    } else {
      elem.querySelector(".card-main-container").style.setProperty("display", "none");
    }
  })
}
showHideBox();

function deleteElement(elem) {
  const remove_elem_id = elem.getAttribute("data-remove-id");
  document.querySelector("#deleteBoxModal #deleteBoxID").innerHTML = remove_elem_id;
  document.querySelector("#deleteBoxModal #deleteBoxBtn").dataset.id = remove_elem_id;
}

document.getElementById("deleteBoxBtn").addEventListener("click", function () {
  const remove_elem_id = this.dataset.id;
  document.getElementById(`${remove_elem_id}ContentArea`).remove();
  $("#deleteBoxModal").modal("hide");
});

// Add Content Box
document.getElementById("addContentBox").addEventListener("click", function () {
  setElementValues();
  const container = document.getElementById("contentContainer");
  const boxID = generateRandomId(10);

  const newElement = document.createElement("div");
  newElement.classList.add("content-area-container");
  newElement.setAttribute("id", `${boxID}ContentArea`);
  newElement.setAttribute("draggable", "true"); // Make the element draggable

  newElement.innerHTML = `
      <input type="hidden" name="content_area_id" value="${boxID}">
      <div class="content-area-label">
        <span class="content-area-label-text">${boxID}</span>
        <button type="button" class="delete-box-btn" data-remove-id="${boxID}" data-bs-toggle="modal" data-bs-target="#deleteBoxModal" onclick="deleteElement(this)"><i class="bi bi-trash"></i></button>
      </div>
      <div class="content-area-box">
          <div class="content-area custom-scrollbar" data-bs-target="#contentAreaModal" data-bs-toggle="modal" data-id="${boxID}ContentArea"></div>
          <textarea name="content" class="d-none"></textarea>
      </div>`;

  container.appendChild(newElement);
  addDragAndDropListeners(); // Add drag-and-drop event listeners to new elements
});

// Drag-and-Drop Functionality
function addDragAndDropListeners() {
  const containers = document.querySelectorAll("#contentContainer");
  const draggableItems = document.querySelectorAll(".content-area-container");

  draggableItems.forEach((item) => {
      item.addEventListener("dragstart", () => {
          item.classList.add("dragging");
      });

      item.addEventListener("dragend", () => {
          item.classList.remove("dragging");
      });
  });

  containers.forEach((container) => {
      container.addEventListener("dragover", (e) => {
          e.preventDefault();
          const afterElement = getDragAfterElement(container, e.clientY);
          const draggingElement = document.querySelector(".dragging");
          if (afterElement == null) {
              container.appendChild(draggingElement);
          } else {
              container.insertBefore(draggingElement, afterElement);
          }
      });
  });
}

// Button .nav-link if  aria-controls="content" aria-selected="true" then Button#addContentBox show else hide
const navLinks = document.querySelectorAll(".nav-link");

// Loop through each .nav-link element
navLinks.forEach((link) => {
  // Add a click event listener to each .nav-link element
  link.addEventListener("click", () => {
    // Check if the clicked .nav-link has aria-controls="content" and aria-selected="true"
    if (link.getAttribute("aria-controls") === "content" && link.getAttribute("aria-selected") === "true") {
      // Show the #addContentBox button
      document.getElementById("addContentBox").style.display = "block";
    } else {
      // Hide the #addContentBox button
      document.getElementById("addContentBox").style.display = "none";
    }
  });
})

document.getElementById("tabType").addEventListener("change", function () {
  const selectedTab = this.value;
  const contentArea = document.querySelector(".modal-content-area-container");
  const codeArea = document.querySelector(".modal-code-area-container");

  if (selectedTab === "content") {
      codeArea.classList.add("d-none");
      contentArea.classList.remove("d-none");
  } else {
      codeArea.classList.remove("d-none");
      contentArea.classList.add("d-none");
  }
});

const contentArea = document.getElementById("contentArea");
const codeArea = document.getElementById("codeArea");

// Sync contenteditable with the code area
contentArea.addEventListener("input", () => {
    // Update code area with content from contenteditable
    codeArea.textContent = contentArea.innerHTML.trim();
    // Prism.highlightElement(codeArea); // Reapply syntax highlighting
});

// Sync code area with the contenteditable
codeArea.addEventListener("change", () => {
    // Update contenteditable with code area's content
    contentArea.innerHTML = codeArea.textContent.trim();
});

// Helper Function: Find the Element to Place After
function getDragAfterElement(container, y) {
  const draggableElements = [
      ...container.querySelectorAll(".content-area-container:not(.dragging)"),
  ];

  return draggableElements.reduce(
      (closest, child) => {
          const box = child.getBoundingClientRect();
          const offset = y - box.top - box.height / 2;
          if (offset < 0 && offset > closest.offset) {
              return { offset: offset, element: child };
          } else {
              return closest;
          }
      },
      { offset: Number.NEGATIVE_INFINITY }
  ).element;
}

// Dummy Functions: Replace with your implementations
function generateRandomId(length) {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

function setElementValues() {
  const inputs = document.getElementsByTagName('input');
  const textareas = document.getElementsByTagName('textarea');

  // Set values for input fields
  for (let i = 0; i < inputs.length; i++) {
    const input = inputs[i];
    input.setAttribute('value', input.value);
  }

  // Set values for textareas
  for (let i = 0; i < textareas.length; i++) {
    const textarea = textareas[i];
    textarea.setAttribute('value', textarea.value);
    textarea.innerText = textarea.value;
  }
}

function createSeoFriendlyUrlKey(inputString) {
  const replaceMap = {
    ' ': '-',
    '?': '',
    "'": '',
  };
  // Replace symbols with their corresponding URL-friendly keys
  let result = inputString.replace(/[ ?']/g, (match) => replaceMap[match]);
  // Remove consecutive dashes
  result = result.replace(/-+/g, '-');
  // Remove consecutive colon
  result = result.replace(/:+/g, '');
  // Remove consecutive "
  result = result.replace(/"+/g, '');
  // Remove leading and trailing dashes
  result = result.replace(/^-+|-+$/g, '');

  return result.toLowerCase(); // Convert to lowercase for consistency
}

const debouncedCreateUrl = debounce((elem) => {
  const inputValue = elem.value;
  const boxId = elem.getAttribute("data-id");
  const seoFriendlyKey = createSeoFriendlyUrlKey(inputValue);
  document.getElementById(`linkedID-${boxId}`).value = seoFriendlyKey;
  updateEditorOutput();
}, 1000); // 300 milliseconds delay before executing the function

function saveContentData() {
  // Get all edit-box elements
  const editBoxes = document.querySelectorAll(".edit-box");

  // Create an array to store the card data
  const cardData = [];

  // Iterate over each edit-box
  editBoxes.forEach((editBox) => {
    // Create an object to hold the card's data
    const card = {};

    card.id = editBox.getAttribute("data-box-id");  

    const card_type = editBox.getAttribute("data-box-type");
    card.cardType = card_type;

    if (card_type === "content") {
      // Get the linking text value
      const linkingText = editBox.querySelector(
        'input[id^="linkingText-"]'
      ).value;
      card.linkingText = linkingText;

      // Get the linking ID value
      const linkedID = editBox.querySelector('input[id^="linkedID-"]').value;
      card.linkedID = linkedID;

      // Get the code editor content
      const codeEditorContent = editBox.querySelector(
        'textarea[id^="code-editor-"]'
      ).value;
      card.codeEditorContent = codeEditorContent;
    }

    // Add the card object to the cardData array
    cardData.push(card);
  });

  const content_keywords = document.getElementById("content_keywords").value.trim().split(', ');
  const sidebar_keywords = document.getElementById("sidebar_keywords").value.trim().split(', ');

  // Create a new Set from the combined array (removes duplicates)
  const uniqueKeywords = new Set([...content_keywords, ...sidebar_keywords]);

  // Convert the Set back to an array if needed
  const search_keywords = Array.from(uniqueKeywords);
  const data = {
    'name': document.getElementById("article_name").value,
    'url': document.getElementById("article_url").value,
    'thumbnail': document.getElementById("thumbnail").value,
    'search_keywords': search_keywords,
    "basic": {
      'recommendation_title': document.getElementById("recommendation_title").value,
      'short_description': document.getElementById("short_description").value.trim(),
      'sub_article_title': document.getElementById("sub_article_title").value,
      'thumbnail': document.getElementById("recommendation_thumbnail").value,
      'content_keywords': document.getElementById("content_keywords").value.trim(),
      'sidebar_keywords': document.getElementById("sidebar_keywords").value.trim(),
    },
      "seo": {
        "title": document.getElementById("head_title").value,
        "image_url": document.getElementById("head_image_url").value,
        "description": document.getElementById("head_description").value.trim(),
        "keywords": document.getElementById("head_keywords").value.trim(),
        "canonical_url": document.getElementById("canonical_url").value,
        "og_title": document.getElementById("og_title").value,
        "og_description": document.getElementById("og_description").value.trim(),
        "og_image": document.getElementById("og_image").value,
        "twitter_title": document.getElementById("twitter_title").value,
        "twitter_description": document.getElementById("twitter_description").value.trim(),
        "twitter_image": document.getElementById("twitter_image").value
    },
    "content": {
      "heading": document.getElementById("contentHeading").value,
      "content": cardData
    },
    'recommendation': {
      'previous_article_id': document.getElementById("previous_article_id").value,
      'next_article_id': document.getElementById("next_article_id").value,
      'recommendation_article_id': document.getElementById("recommendation_article_id").value,
    },
  }
  sendDataToDB(data, "update")
}

function getIdFromUrl(url) {
  const parts = url.split('/');
  return parts.at(-1);
}

function sendDataToDB(dataToSave, requestForData) {
  // Get the current URL
  const currentURL = window.location.pathname;
    
    // Defining async function
    async function saveArticleData() {
      await $.ajax({
          type: "POST",
          async: false,
          url: currentURL,
          data: {
              csrfmiddlewaretoken: getCookie("csrftoken"),
              data: JSON.stringify(dataToSave),
              [requestForData]: true,
          },
          success: function (response) {
              if (response.ok) {
                alert(response.msg);
              } else {
                alert(response.msg)
              }
          }
      })
      .catch((error) => {
        alert("Error: ",error)
      });
  }
  saveArticleData();
}