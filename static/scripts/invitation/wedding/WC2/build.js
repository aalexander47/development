// Check if the data exists
const template_id = document.getElementById("templateID").value;
if (data) {
    if (template_id === data['template']['id']) {
        // Set the data to the form
        try {
            if (data['invitation']['groom']) {
                document.querySelector('#groom').value = data['invitation']['groom'];
                document.querySelector('#groom_text').textContent = data['invitation']['groom'];
            } else {
                document.querySelector('#groom_text').textContent = 'Groom';
            }

            if (data['invitation']['bride']) {
                document.querySelector('#bride').value = data['invitation']['bride'];
                document.querySelector('#bride_text').textContent = data['invitation']['bride'];
            } else {
                document.querySelector('#bride_text').textContent = 'Bride';
            }

            document.querySelector('#wedding_date').value = data['invitation']['eventDate'];

            // Change the date format
            if (data['invitation']['eventDate']) {
                const weeding_date = new Date(data['invitation']['eventDate']);
                const options = { year: 'numeric', month: 'long', day: 'numeric' };
                data.eventDate = weeding_date.toLocaleDateString('en-US', options);
                document.querySelector('#date_text').textContent = data['invitation']['eventDate'];
            } else {
                document.querySelector('#date_text').textContent = '11th April, 2021';
            }

            if (data['invitation']['eventTime']) {
                document.querySelector('#wedding_time').value = data['invitation']['eventTime'];
            } else {
                document.querySelector('#wedding_time').value = '10:00 AM';
            }

            if (data['invitation']['venueLocation']) {
                const venue = data['invitation']['venueLocation']['venue'];
                const address = data['invitation']['venueLocation']['address'];
                const city = data['invitation']['venueLocation']['city'];
                const state = data['invitation']['venueLocation']['state'];
                const country = data['invitation']['venueLocation']['country'];
                const postalCode = data['invitation']['venueLocation']['postalCode'];

                document.querySelector('#address').value = address;
                // Set the address
                let address_info = ``;
                if (venue) {
                    address_info += `${venue}`;
                }
                if (address) {
                    address_info += `${address}`;
                }
                if (city) {
                    address_info += `, ${city}`;
                }
                if (state) {
                    address_info += `, ${state}`;
                }
                if (country) {
                    address_info += `, ${country}`;
                }
                if (postalCode) {
                    address_info += `, ${postalCode}`;
                }
                document.querySelector('#address_text').textContent = address_info;
            } else {
                document.querySelector('#address_text').textContent = 'Vakil Nagar, Erandwane, Pune, Maharashtra 411004';
            }

            document.querySelector('#start_date').value = data.startDate;
            document.querySelector('#end_date').value = data.endDate;
            document.querySelector('#rsvpToggle').checked = data['invitation']['rsvp'];
            document.querySelector('#commentToggle').checked = data['invitation']['comment'];
            document.querySelector('#thankYouToggle').checked = data['invitation']['thankYouPage'];
            document.querySelector('#thankYouPageDays').value = data['invitation']['thankYouPageDays'];
        } catch (error) {
            console.error(error);
        }
    } else {
        const invitation_data = {
            "invitation": {},
            "template": {
                "id": template_id
            }
        }
        localStorage.setItem('invitation_data', JSON.stringify(invitation_data));
    }
} 
else {
    const invitation_data = {
        "invitation": {},
        "template": {
            "id": template_id
        }
    }
    localStorage.setItem('invitation_data', JSON.stringify(invitation_data));
}

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

        if (data['invitation']['venueLocation']['venue']) {
            document.querySelector('#venue').value = data['invitation']['venueLocation']['venue'];
        }

        if (data['invitation']['venueLocation']['address']) {
            document.querySelector('#address').value = data['invitation']['venueLocation']['address'];
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
    const address = document.querySelector('#address').value;
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
            address: address
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