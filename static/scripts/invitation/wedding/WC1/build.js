// Next button event listener
const nextBtn = document.querySelector('.nextBtn');
nextBtn.addEventListener('click', () => {
    // Get the data from the local storage
    const data = JSON.parse(localStorage.getItem('invitation_data'));

    // Set the data to the form
    if (data) {
        if (data['invitation']['groom']) {
            document.querySelector('#groom').value = data['invitation']['groom'];
        }

        if (data['invitation']['bride']) {
            document.querySelector('#bride').value = data['invitation']['bride'];
        }

        if (data['invitation']['eventDate']) {
            document.querySelector('#wedding_date').value = data['invitation']['eventDate'];
        }

        if (data['invitation']['eventTime']) {
            document.querySelector('#wedding_time').value = data['invitation']['eventTime'];
        }

        if (data['invitation']['timezone']) {
            document.querySelector('#timezone').value = data['invitation']['timezone'];
        }

        if (data['invitation']['venueLocation']) {
            const venue = data['invitation']['venueLocation']['venue'];
            const address = data['invitation']['venueLocation']['address'];
            const city = data['invitation']['venueLocation']['city'];
            const state = data['invitation']['venueLocation']['state'];
            const country = data['invitation']['venueLocation']['country'];
            const postalCode = data['invitation']['venueLocation']['postalCode'];
            const mapUrl = data['invitation']['venueLocation']['mapUrl'];

            document.querySelector('#venue').value = venue;
            document.querySelector('#address').value = address;
            document.querySelector('#city').value = city;
            document.querySelector('#state').value = state;
            document.querySelector('#country').value = country;
            document.querySelector('#postalCode').value = postalCode;
            document.querySelector('#mapUrl').value = mapUrl;
        }
    }
});

// Onclick event listener for the backToOtherBtn
const backToOtherBtn = document.querySelector('#backToOtherBtn');
backToOtherBtn.addEventListener('click', () => {
    // Clear the paymentContainer
    document.querySelector('#paymentContainer').innerHTML = `
                    <div class="loader-container d-flex justify-content-center align-items-center py-5">
                        <div class="box-circle-loader"></div>
                    </div>`;

    // Check if any for element exists with the id razorpayForm or publishForm
    if (document.getElementById('razorpayForm')) {
        document.getElementById('razorpayForm').remove();
    }
    if (document.getElementById('publishForm')) {
        document.getElementById('publishForm').remove();
    }
});

// proceedBtn button event listener
const invitationDetailsForm = document.querySelector('#invitationDetailsForm');
invitationDetailsForm.addEventListener('submit', (e) => {
    e.preventDefault();
    // Get the data from the form
    const groom = document.querySelector('#groom').value;
    const bride = document.querySelector('#bride').value;
    const eventDate = document.querySelector('#wedding_date').value;
    const eventTime = document.querySelector('#wedding_time').value;
    const timezone = document.querySelector('#timezone').value;
    let country = document.querySelector('#country').value;
    let countryCode = country.split('-|-')[0];
    let countryName = country.split('-|-')[1];
    const address = {
        "venue": document.querySelector('#venue').value,
        "address": document.querySelector('#address').value,
        "city": document.querySelector('#city').value,
        "state": document.querySelector('#state').value,
        "country": country,
        "countryName": countryName,
        "countryCode": countryCode,
        "postalCode": document.querySelector('#postalCode').value,
        "mapUrl": document.querySelector('#mapUrl').value,
    }
    const templateId = document.querySelector('#templateID').value;

    // Add the data to the local storage
    let data = {
        template: {
            id: templateId
        },
        invitation: {
            groom: groom,
            bride: bride,
            eventDate: eventDate,
            eventTime: eventTime,
            timezone: timezone,
            venueLocation: address
        }
    };
    localStorage.setItem('invitation_data', JSON.stringify(data));
    document.getElementById("proceedToOtherBtn").click();
});

// Proceed to payment button event listener
const otherInfoForm = document.querySelector('#otherInfoForm');
otherInfoForm.addEventListener('submit', (e) => {
    e.preventDefault();
    // Save the RSVP and Comment toggle values to the local storage
    let data = JSON.parse(localStorage.getItem('invitation_data'));
    data.startDate = document.querySelector('#start_date').value;
    data.endDate = document.querySelector('#end_date').value;
    data['invitation']['rsvp'] = document.querySelector('#rsvpToggle').checked;
    data['invitation']['comment'] = document.querySelector('#commentToggle').checked;
    data['invitation']['thankYouPage'] = document.querySelector('#thankYouToggle').checked;
    data['invitation']['thankYouPageDays'] = document.querySelector('#thankYouPageDays').value;
    localStorage.setItem('invitation_data', JSON.stringify(data));
    
    if (!document.getElementById("signupModal")) {
        processToPayment();
    }
    document.getElementById("proceedToPaymentBtn").click();
});
