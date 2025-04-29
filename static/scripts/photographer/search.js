var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl, {
    delay: { "show": 500, "hide": 100 }  // Custom delay in milliseconds
  })
})


document.addEventListener("DOMContentLoaded", function () {
  searchFilter();
  const spanElement = document.querySelector(".typing-span");
  const texts = ["Photographer", "Wedding", "Product", "Portrait", "Fashion", "Maternity", "Travel", "Baby", "Birthday"];
  let currentIndex = 0;

  function typeText(text, callback) {
      let i = 0;
      spanElement.textContent = ""; // Clear current text
      const interval = setInterval(() => {
          spanElement.textContent += text[i];
          i++;
          if (i === text.length) {
              clearInterval(interval);
              setTimeout(callback, 2000); // Delay before removing the text
          }
      }, 150); // Typing speed in milliseconds
  }

  function deleteText(callback) {
      const text = spanElement.textContent;
      let i = text.length - 1;
      const interval = setInterval(() => {
          spanElement.textContent = text.slice(0, i);
          i--;
          if (i < 0) {
              clearInterval(interval);
              callback();
          }
      }, 50); // Deletion speed in milliseconds
  }

  function cycleTexts() {
      typeText(texts[currentIndex], () => {
          deleteText(() => {
              currentIndex = (currentIndex + 1) % texts.length; // Loop through the array
              cycleTexts();
          });
      });
  }

  cycleTexts(); // Start the cycle
});

// ////////////////////////////// Search filter select ////////////////////////////////////////
const searchServiceData = {
    'vendor': {
        'photographer': 'Photographer',
    },
    'photographer': {
        'wedding': 'Wedding',
        'portrait': 'Portrait',
        'product': 'Product',
        'baby': 'Baby',
        'birthday': 'Birthday',
        'maternity': 'Maternity',
        'fashion': 'Fashion',
        'food': 'Food',
    }
}

function searchFilter() {
  const searchService = document.getElementById('searchService').value;
  // From searchCategory select field check if any option has class name searchService. If so, create a select option field
  const categories = searchServiceData[searchService];
  if (categories) {
      const searchCategoryBox = document.getElementById('searchCategorybox');
      // Create a select option field element
      const select = document.createElement('select');
      select.name = 'category';
      select.id = 'searchCategory';
      select.className = 'form-select';
      // Add the options to the select option field
      for (const [key, value] of Object.entries(categories)) {
          const option = document.createElement('option');
          option.value = key;
          option.textContent = value;
          select.appendChild(option);
      }
      searchCategoryBox.innerHTML = '';
      searchCategoryBox.appendChild(select);
  } else {
      const searchCategoryBox = document.getElementById('searchCategorybox');
      searchCategoryBox.innerHTML = '';
  }
}
// //////////////////////////////////// Search filter select //////////////////////////////////////