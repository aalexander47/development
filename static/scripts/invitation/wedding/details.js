document.addEventListener('DOMContentLoaded', function() {
  // Set up all download buttons
  document.querySelectorAll('.download-btn').forEach(btn => {
      btn.addEventListener('click', async function() {
          const cardId = this.dataset.target;
          const cardElement = document.getElementById(cardId);
          const originalBtnText = this.textContent;
          
          this.disabled = true;
          this.textContent = 'Generating...';
          
          try {
              // 1. Load all S3 images in this card
              await loadCardImages(cardElement);
              
              // 2. Convert to image
              const canvas = await html2canvas(cardElement, {
                  useCORS: true,
                  scale: 2,
                  logging: true,
                  allowTaint: false,
                  backgroundColor: null,
                  onclone: (doc, element) => {
                      // Handle any images that failed to load
                      element.querySelectorAll('img').forEach(img => {
                          if (!img.complete || img.naturalHeight === 0) {
                              const fallback = doc.createElement('div');
                              fallback.className = 'image-fallback';
                              fallback.textContent = img.dataset.fallback || 'Image not available';
                              img.parentNode.replaceChild(fallback, img);
                          }
                      });
                  }
              });
              
              // 3. Trigger download
              const link = document.createElement('a');
              link.download = `${cardId}-invitation.png`;
              link.href = canvas.toDataURL('image/png');
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              
          } catch (error) {
              console.error(`Error generating ${cardId}:`, error);
              alert('Failed to generate image. Please try again.');
          } finally {
              this.disabled = false;
              this.textContent = originalBtnText;
          }
      });
  });
  
  // Function to load all S3 images in a specific card
  async function loadCardImages(cardElement) {
      const images = cardElement.querySelectorAll('.s3-image');
      const promises = [];
      
      images.forEach(img => {
          img.classList.add('image-loading');
          
          promises.push(new Promise((resolve) => {
              // Ensure CORS is set
              if (!img.crossOrigin) img.crossOrigin = 'anonymous';
              
              // Cache busting
              const originalSrc = img.src.split('?')[0];
              img.src = originalSrc + '?t=' + Date.now();
              
              let loaded = false;
              const timer = setTimeout(() => {
                  if (!loaded) handleImageError(img);
                  resolve();
              }, 5000);
              
              img.onload = () => {
                  loaded = true;
                  clearTimeout(timer);
                  img.classList.remove('image-loading');
                  resolve();
              };
              
              img.onerror = () => {
                  loaded = true;
                  clearTimeout(timer);
                  handleImageError(img);
                  resolve();
              };
          }));
      });
      
      await Promise.all(promises);
  }
  
  function handleImageError(img) {
      img.classList.remove('image-loading');
      const fallback = document.createElement('div');
      fallback.className = 'image-fallback';
      fallback.textContent = img.dataset.fallback || 'Image not available';
      img.parentNode.replaceChild(fallback, img);
  }
});

function shareDivAsImage(share_id) {
  const id = `download_${share_id}`;
  const div = document.getElementById(id);

  if (!div) {
    console.error(`Element with ID "${id}" not found.`);
    return;
  }

  // Ensure images inside the div are fully loaded
  const images = div.getElementsByTagName('img');
  let imagesToLoad = images.length;

  if (imagesToLoad > 0) {
    Array.from(images).forEach((img) => {
      if (!img.complete) {
        img.onload = () => {
          imagesToLoad--;
          if (imagesToLoad === 0) {
            captureAndShare(div);
          }
        };
      } else {
        imagesToLoad--;
        if (imagesToLoad === 0) {
          captureAndShare(div);
        }
      }
    });
  } else {
    captureAndShare(div);
  }
}

function captureAndShare(div) {
  // Add a small delay to ensure the DOM is fully rendered
  setTimeout(() => {
    html2canvas(div, {
      useCORS: true, // Allow cross-origin images
      allowTaint: false, // Prevent tainting issues
      scale: 2, // Higher resolution for better quality
      logging: true, // Enable logging for debugging
    })
      .then((canvas) => {
        canvas.toBlob((blob) => {
          const file = new File([blob], 'wedding-invitation-from-eventic.png', { type: 'image/png' });

          // Check if Web Share API is supported
          if (navigator.share) {
            navigator.share({
              title: 'Check out this image!',
              files: [file],
            })
              .then(() => console.log('Image shared successfully'))
              .catch((error) => console.error('Error sharing image:', error));
          } else {
            // Fallback for desktop browsers
            const image = canvas.toDataURL('image/png');
            copyImageToClipboard(image)
              .then(() => alert('Image copied to clipboard. Paste it to share.'))
              .catch(() => {
                // If copying fails, open the image in a new tab for manual sharing
                const newWindow = window.open();
                newWindow.document.write(`<img src="${image}" alt="Shared Image" />`);
              });
          }
        }, 'image/png');
      })
      .catch((err) => {
        console.error('Error capturing image:', err);
      });
  }, 500); // Adjust the delay as needed
}

function copyImageToClipboard(image) {
  return fetch(image)
    .then((response) => response.blob())
    .then((blob) => navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]));
}

function generateGradientQRCode(elem) {
  let qrContainer = elem.querySelector(".qrcode-box");

  qrContainer.innerHTML = ""; // Clear previous QR codes

  let qrCode = new QRCode(qrContainer, {
    text: window.location.href,
    correctLevel: QRCode.CorrectLevel.H,
  });
}

// Run the QR code generation after DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  generateGradientQRCode(document.getElementById("invitationCard"));
  generateGradientQRCode(document.getElementById("cardQrCode"));
  generateGradientQRCode(document.getElementById("download_invitationCard"));
  generateGradientQRCode(document.getElementById("download_cardQrCode"));
});

// JavaScript to handle the button clicks and show/hide modal and offcanvas
document.getElementById('teamGroomRSVPbtn').addEventListener('click', function () {
  var modal = bootstrap.Modal.getInstance(document.getElementById('rsvpModal'));
  modal.hide();
  var offcanvasLeft = new bootstrap.Offcanvas(document.getElementById('teamGroomModal'));
  offcanvasLeft.show();
});

document.getElementById('teamBrideRSVPbtn').addEventListener('click', function () {
  var modal = bootstrap.Modal.getInstance(document.getElementById('rsvpModal'));
  modal.hide();
  var offcanvasRight = new bootstrap.Offcanvas(document.getElementById('teamBrideModal'));
  offcanvasRight.show();
});


function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


function submitRSVPForm(data, form_elem) {
  // Check if the current url contains 'preview' in it. If it does, do not send the form data to the server
  if (window.location.href.includes('preview')) {
    alert('Preview mode is enabled. RSVP form data will not be sent to the server.');
    // Remove the spinner and enable the button
    var btn = form_elem.querySelector('button[type="submit"]');
    btn.innerHTML = '<i class="bi bi-send-fill me-2"></i>RSVP';
    btn.disabled = false;
    return;
  }
  // Send the RSVP form data to the server
  fetch('/invitation/wedding/rsvp/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(data => {
    // Handle the response from the server
    if (data.success) {
      // Remove the form and show a success message
      alert(data.message);
      console.log(data.message);
      form_elem.remove();
    } else {
      console.log("Error: ",data.message);
      // Remove the spinner and enable the button
      var btn = form_elem.querySelector('button[type="submit"]');
      btn.innerHTML = '<i class="bi bi-send-fill me-2"></i>RSVP';
      btn.disabled = false;
    }
  })
}

document.getElementById('groomRSVPForm').addEventListener('submit', function(e) {
  e.preventDefault();
  // Add spinner to the button
  var btn = document.getElementById('groomRSVPBtn');
  btn.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>&nbsp; Submitting...';
  btn.disabled = true;

  var formData = new FormData(this);
  var data = {};
  formData.forEach(function(value, key) {
    data[key] = value;
  });
  submitRSVPForm(data, this);
});

document.getElementById('brideRSVPForm').addEventListener('submit', function(e) {
  e.preventDefault();
  // Add spinner to the button
  var btn = document.getElementById('brideRSVPBtn');
  btn.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>&nbsp; Submitting...';
  btn.disabled = true;

  var formData = new FormData(this);
  var data = {};
  formData.forEach(function(value, key) {
    data[key] = value;
  });
  submitRSVPForm(data, this);
});


// Get references to the radio buttons and body element
const viewRadios = document.querySelectorAll('input[name="view"]');
const container = document.querySelector('main');

// Add event listeners to the radio buttons
viewRadios.forEach(radio => {
    radio.addEventListener('change', (event) => {
        const selectedView = event.target.value;

        // Update the icons for the selected view. Get all three icons
        const desktopIcon = document.querySelector('.bi-laptop-fill');
        const tabletIcon = document.querySelector('.bi-tablet-fill');
        const mobileIcon = document.querySelector('.bi-phone-fill');


        // Check if the element exists
        if (desktopIcon) {
            // Replace the .bi-laptop-fill with .bi-laptop class from the desktop icon
            desktopIcon.classList.replace('bi-laptop-fill', 'bi-laptop');
        }

        if (tabletIcon) {
            // Replace the .bi-tablet-fill with .bi-tablet class from the tablet icon
            tabletIcon.classList.replace('bi-tablet-fill', 'bi-tablet');
        }

        if (mobileIcon) {
            // Replace the .bi-phone-fill with .bi-phone class from the mobile icon
            mobileIcon.classList.replace('bi-phone-fill', 'bi-phone');
        }

        // Remove all existing view classes
        container.classList.remove('desktop-view', 'tablet-view', 'mobile-view');

        // Add the selected view class to the body
        switch (selectedView) {
            case 'desktop':
                container.classList.add('desktop-view');
                // Replace the .bi-laptop class with .bi-laptop-fill
                document.querySelector('.bi-laptop').classList.replace('bi-laptop', 'bi-laptop-fill');
                break;
            case 'tablet':
                container.classList.add('tablet-view');
                // Replace the .bi-tablet class with .bi-tablet-fill
                document.querySelector('.bi-tablet').classList.replace('bi-tablet', 'bi-tablet-fill');
                break;
            case 'mobile':
                container.classList.add('mobile-view');
                // Replace the .bi-phone class with .bi-phone-fill
                document.querySelector('.bi-phone').classList.replace('bi-phone', 'bi-phone-fill');
                break;
            default:
                container.classList.add('desktop-view');
                // Replace the .bi-laptop class with .bi-laptop-fill
                document.querySelector('.bi-laptop').classList.replace('bi-laptop', 'bi-laptop-fill');
                break;
        }
    });
});

// Set the default view to Desktop on page load
window.addEventListener('load', () => {
    container.classList.add('desktop-view');
});