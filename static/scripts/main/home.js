var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl, {
    delay: { "show": 500, "hide": 100 }  // Custom delay in milliseconds
  })
})


document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('portfolioImages');
  const images = container.getElementsByClassName('portfolio-img');
  const prevButton = document.querySelector('.prev-btn');
  const nextButton = document.querySelector('.next-btn');
  const spaceBoxStart = document.querySelector('.space-box-start');
  const spaceBoxEnd = document.querySelector('.space-box-end');
  const containerRect = container.getBoundingClientRect();

  // Set the widths of the space boxes
  if (images.length > 0) {
      const firstImageWidth = images[0].offsetWidth;
      const lastImageWidth = images[images.length - 1].offsetWidth;
      spaceBoxStart.style.width = `${containerRect.width / 2 - (firstImageWidth / 2)}px`;
      spaceBoxEnd.style.width = `${containerRect.width / 2 - (lastImageWidth / 2)}px`;
  }

  function updateActiveImage() {
      const containerCenterX = containerRect.left + containerRect.width / 2;

      let closestImage = null;
      let closestDistance = Infinity;

      Array.from(images).forEach(image => {
          const imageRect = image.getBoundingClientRect();
          const imageCenterX = imageRect.left + imageRect.width / 2;

          const distance = Math.abs(containerCenterX - imageCenterX);
          if (distance < closestDistance) {
              closestDistance = distance;
              closestImage = image;
          }
      });

      // Remove 'active' class from all images
      Array.from(images).forEach(image => image.classList.remove('active'));

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

      Array.from(images).forEach(image => {
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
              container.scroll({
                  left: targetImage.offsetLeft - (container.offsetWidth / 2 - targetImage.offsetWidth / 2),
                  behavior: 'smooth'
              });
          }
      }
  }

  // Update active image on scroll
  container.addEventListener('scroll', updateActiveImage);

  // Button event listeners
  prevButton.addEventListener('click', () => scrollToImage('prev'));
  nextButton.addEventListener('click', () => scrollToImage('next'));

  // Initial call to set the active image on page load
  updateActiveImage();
});

document.addEventListener("DOMContentLoaded", function () {
    const spanElement = document.querySelector(".typing-span");
    const texts = ["Photographer", "Videographer", "MakeUp Artist", "DJ", "Caterer", "Decorator"];
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

// ///////////////////////////// Card Carousel //////////////////////////////////////////////////
window.addEventListener( 'load', () => {
	const COMPONENT_SELECTOR = '.carousel__wrapper';
	const CONTROLS_SELECTOR = '.carousel__controls';
  const CONTENT_SELECTOR = '.carousel__content';

	const components = document.querySelectorAll( COMPONENT_SELECTOR );

	for ( let i = 0; i < components.length; i++ ) {
		const component = components[ i ];
		const content = component.querySelector( CONTENT_SELECTOR );
		let x = 0;
		let mx = 0;
		const maxScrollWidth = content.scrollWidth - content.clientWidth / 2 - content.clientWidth / 2;
		const nextButton = component.querySelector( '.arrow-next' );
		const prevButton = component.querySelector( '.arrow-prev' );

		if ( maxScrollWidth !== 0 ) {
			component.classList.add( 'has-arrows' );
		}

		if ( nextButton ) {
			nextButton.addEventListener( 'click', function ( event ) {
				event.preventDefault();
				x = content.clientWidth / 2 + content.scrollLeft + 0;
				content.scroll( {
					left: x,
					behavior: 'smooth',
				} );
			} );
		}

		if ( prevButton ) {
			prevButton.addEventListener( 'click', function ( event ) {
				event.preventDefault();
				x = content.clientWidth / 2 - content.scrollLeft + 0;
				content.scroll( {
					left: -x,
					behavior: 'smooth',
				} );
			} );
		}

		/**
		 * Mouse move handler.
		 *
		 * @param {object} e event object.
		 */
		const mousemoveHandler = ( e ) => {
			const mx2 = e.pageX - content.offsetLeft;
			if ( mx ) {
				content.scrollLeft = content.sx + mx - mx2;
			}
		};

		/**
		 * Mouse down handler.
		 *
		 * @param {object} e event object.
		 */
		const mousedownHandler = ( e ) => {
			content.sx = content.scrollLeft;
			mx = e.pageX - content.offsetLeft;
			content.classList.add( 'dragging' );
		};

		/**
		 * Scroll handler.
		 */
		const scrollHandler = () => {
			toggleArrows();
		};

		/**
		 * Toggle arrow handler.
		 */
		const toggleArrows = () => {
			if ( content.scrollLeft > maxScrollWidth - 10 ) {
				nextButton.classList.add( 'disabled' );
			} else if ( content.scrollLeft < 10 ) {
				prevButton.classList.add( 'disabled' );
			} else {
				nextButton.classList.remove( 'disabled' );
				prevButton.classList.remove( 'disabled' );
			}
		};

		/**
		 * Mouse up handler.
		 */
		const mouseupHandler = () => {
			mx = 0;
			content.classList.remove( 'dragging' );
		};

		content.addEventListener( 'mousemove', mousemoveHandler );
		content.addEventListener( 'mousedown', mousedownHandler );
		if ( component.querySelector( CONTROLS_SELECTOR ) !== undefined ) {
			content.addEventListener( 'scroll', scrollHandler );
		}
		content.addEventListener( 'mouseup', mouseupHandler );
		content.addEventListener( 'mouseleave', mouseupHandler );
	}
} );

// /////////////////////////// Card Carousel //////////////////////////////////////////////////


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