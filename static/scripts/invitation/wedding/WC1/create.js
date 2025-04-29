// Check if the data exists
const template_id = document.getElementById("templateID").value;
if (data) {
    if (template_id === data['template']['id']) {
        // Set the data to the form
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

        // Change the date format
        if (data['invitation']['eventDate']) {
            let date = data['invitation']['eventDate'];
            document.querySelector('#wedding_date').value = date;
            const weeding_date = new Date(date);
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            data.eventDate = weeding_date.toLocaleDateString('en-US', options);
            document.querySelector('#date_text').textContent = data.eventDate;
        } else {
            document.querySelector('#date_text').textContent = '11th April, 2021';
        }

        if (data['invitation']['eventTime']) {
            document.querySelector('#wedding_time').value = data['invitation']['eventTime'];
            // Change the time format from 24 hours to 12 hours AM/PM
            let time = data['invitation']['eventTime'];
            document.querySelector('#time_text').textContent = convertTo12HourFormat(time);
        } else {
            document.querySelector('#time_text').textContent = '10:00 AM';
        }

        if (data['invitation']['venueLocation']) {
            const venue = data['invitation']['venueLocation']['venue'];
            const address = data['invitation']['venueLocation']['address'];
            const city = data['invitation']['venueLocation']['city'];
            const state = data['invitation']['venueLocation']['state'];
            const country = data['invitation']['venueLocation']['country'];
            const countryName = data['invitation']['venueLocation']['countryName'];
            const countryCode = data['invitation']['venueLocation']['countryCode'];
            const postalCode = data['invitation']['venueLocation']['postalCode'];
            const mapUrl = data['invitation']['venueLocation']['mapUrl'];

            // Set the address
            let address_info = ``;
            if (venue) {
                document.querySelector('#venue').value = venue;
                address_info += `${venue}`;
            }
            if (address) {
                document.querySelector('#address').value = address;
                address_info += `${address}`;
            }
            if (city) {
                document.querySelector('#city').value = city;
                address_info += `, ${city}`;
            }
            if (state) {
                document.querySelector('#state').value = state;
                address_info += `, ${state}`;
            }
            if (country) {
                document.querySelector('#country').value = country;
                // Split country text wherever there is a -|- and choose the second part
                address_info += `, ${countryName}`;
            }
            if (postalCode) {
                document.querySelector('#postalCode').value = postalCode;
                address_info += `, ${postalCode}`;
            }
            if (mapUrl) {
                document.querySelector('#mapUrl').value = mapUrl;
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
    } else {
        const invitation_data_local_storage = {
            "invitation": {},
            "template": {
                "id": template_id
            }
        }
        localStorage.setItem('invitation_data', JSON.stringify(invitation_data_local_storage));
    }
} 
else {
    const invitation_data_local_storage = {
        "invitation": {},
        "template": {
            "id": template_id
        }
    }
    localStorage.setItem('invitation_data', JSON.stringify(invitation_data_local_storage));
}