const template_id = document.getElementById("templateID").value;
// Get the data from the local storage
const data = JSON.parse(localStorage.getItem('invitation_data'));
if (data) {
    if (template_id === data['template']['id']) {
        // Set the data to the form
        if (data['invitation']['groom']) {
            document.querySelector('#groom_text').textContent = data['invitation']['groom'];
        } else {
            document.querySelector('#groom_text').textContent = 'Groom';
        }

        if (data['invitation']['bride']) {
            document.querySelector('#bride_text').textContent = data['invitation']['bride'];
        } else {
            document.querySelector('#bride_text').textContent = 'Bride';
        }

        // Change the date format
        if (data['invitation']['eventDate']) {
            let date = data['invitation']['eventDate'];
            const weeding_date = new Date(date);
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            data.eventDate = weeding_date.toLocaleDateString('en-US', options);
            document.querySelector('#date_text').textContent = data.eventDate;
        } else {
            document.querySelector('#date_text').textContent = '11th April, 2021';
        }

        if (data['invitation']['eventTime']) {
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
            const postalCode = data['invitation']['venueLocation']['postalCode'];
            const mapUrl = data['invitation']['venueLocation']['mapUrl'];

            // Set the address
            let address_info = ``;
            if (venue) {
                document.querySelector('#venue_text').textContent = venue;
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
    }
} 


function convertTo12HourFormat(time24) {
    // Split the input time into hours and minutes
    const [hours, minutes] = time24.split(':').map(Number);

    // Determine AM or PM
    const period = hours >= 12 ? 'PM' : 'AM';

    // Convert hours to 12-hour format
    let hours12 = hours % 12;
    hours12 = hours12 === 0 ? 12 : hours12; // Handle midnight (0 hours)

    // Format the time as HH:MM AM/PM
    const time12 = `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;

    return time12;
}