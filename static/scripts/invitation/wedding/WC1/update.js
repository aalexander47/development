// Check if the data exists
const template_id = document.getElementById("templateID").value;

const invitation_data_local_storage = {
    "invitation": JSON.parse(invitation_data),
    "template": {
        "id": template_id
    }
}
localStorage.setItem('invitation_data', JSON.stringify(invitation_data_local_storage));