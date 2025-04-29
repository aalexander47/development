
document.addEventListener('DOMContentLoaded', function () {
    const portfolioImagesContainer = document.getElementById('portfolioImages');
    const portfolioImagesElems = portfolioImagesContainer.getElementsByClassName('portfolio-img');
    const prevButton = document.querySelector('.prev-btn');
    const nextButton = document.querySelector('.next-btn');
    const spaceBoxStart = document.querySelector('.space-box-start');
    const spaceBoxEnd = document.querySelector('.space-box-end');
    const containerRect = portfolioImagesContainer.getBoundingClientRect();

    // Set the widths of the space boxes
    if (portfolioImagesElems.length > 0) {
        const firstImageWidth = portfolioImagesElems[0].offsetWidth;
        const lastImageWidth = portfolioImagesElems[portfolioImagesElems.length - 1].offsetWidth;
        
        spaceBoxStart.style.width = `${(containerRect.width / 2) - (firstImageWidth / 2)}px`;
        spaceBoxEnd.style.width = `${(containerRect.width / 2) - (lastImageWidth / 2)}px`;
    }

    function updateActiveImage() {
        const containerCenterX = containerRect.left + containerRect.width / 2;

        let closestImage = null;
        let closestDistance = Infinity;

        Array.from(portfolioImagesElems).forEach(image => {
            const imageRect = image.getBoundingClientRect();
            const imageCenterX = imageRect.left + imageRect.width / 2;

            const distance = Math.abs(containerCenterX - imageCenterX);
            if (distance < closestDistance) {
                closestDistance = distance;
                closestImage = image;
            }
        });

        // Remove 'active' class from all images
        Array.from(portfolioImagesElems).forEach(image => image.classList.remove('active'));

        // Add 'active' class to the closest image
        if (closestImage) {
            closestImage.classList.add('active');
            if (closestImage.classList.contains('next')) {
              closestImage.classList.remove('next');
            };
            if (closestImage.classList.contains('prev')) {
              closestImage.classList.remove('prev');
            };
        }
        const target = document.querySelector('#portfolioImages .active'); // Select the target element

        if (target) {
            // Function to get all previous siblings
            const getPreviousSiblings = (elem) => {
                let siblings = [];
                while (elem = elem.previousElementSibling) {
                    if (elem.classList.contains('next')) {
                      elem.classList.remove('next');
                    };
                    siblings.push(elem);
                }
                return siblings;
            };

            // Function to get all next siblings
            const getNextSiblings = (elem) => {
                let siblings = [];
                while (elem = elem.nextElementSibling) {
                    siblings.push(elem);
                    if (elem.classList.contains('prev')) {
                      elem.classList.remove('prev');
                    };
                }
                return siblings;
            };

            const previousSiblings = getPreviousSiblings(target);
            const nextSiblings = getNextSiblings(target);

            // You can now add classes to the siblings or manipulate them as needed
            previousSiblings.forEach(sibling => sibling.classList.add('prev'));
            nextSiblings.forEach(sibling => sibling.classList.add('next'));
        }
    }

    function scrollToImage(direction) {
        const containerCenterX = containerRect.left + containerRect.width / 2;

        let closestImage = null;
        let closestDistance = Infinity;

        Array.from(portfolioImagesElems).forEach(image => {
            const imageRect = image.getBoundingClientRect();
            const imageCenterX = imageRect.left + imageRect.width / 2;

            const distance = Math.abs(containerCenterX - imageCenterX);
            if (distance < closestDistance) {
                closestDistance = distance;
                closestImage = image;
            }
        });

        if (closestImage) {
            let targetImage;
            if (direction === 'next') {
                targetImage = closestImage.nextElementSibling;
            } else {
                targetImage = closestImage.previousElementSibling;
            }

            if (targetImage && targetImage.classList.contains('portfolio-img')) {
                portfolioImagesContainer.scroll({
                    left: targetImage.offsetLeft - (portfolioImagesContainer.offsetWidth / 2 - targetImage.offsetWidth / 2),
                    behavior: 'smooth'
                });
            }
        }
    }

    // Update active image on scroll
    portfolioImagesContainer.addEventListener('scroll', updateActiveImage);

    // Button event listeners
    prevButton.addEventListener('click', () => scrollToImage('prev'));
    nextButton.addEventListener('click', () => scrollToImage('next'));

    // Initial call to set the active image on page load
    updateActiveImage();
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
  
  async function trackLead(elem) {
    const lead_type = elem.getAttribute("data-lead-type");
    elem.disabled = true;
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