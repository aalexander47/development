document.getElementById("createOrUpdateForm").addEventListener("submit", function (event) {
    // Prevent form submission
    event.preventDefault();
    // document.getElementById("createOrUpdateBtn").disabled = true;
    let action = this.getAttribute("data-action");
    // if (action === "create") {
    //     document.querySelector("button[name='create_service']").disabled = true;
    // }

    let hasErrors = false;
    // Check for thumbnail
    let file_exists = document.getElementById("file_exists").value;
    if (file_exists === "nofile") {
        document.querySelector("#thumbnailFormBox .invalid-feedback").style.display = "block";
        // Scroll to the thumbnail form box
        document.querySelector("#thumbnailFormBox").scrollIntoView({ behavior: "smooth", block: "center" });
        alert("Please upload a thumbnail");
        hasErrors = true;
        return;
    }

    // If form data-action is create, check for name
    if (action === "create") {
        let image_cards = document.getElementsByClassName("image-card");
        if (image_cards.length < 5) {
            // Scroll to the images form box
            document.querySelector("#dropZone").scrollIntoView({ behavior: "smooth", block: "center" });
            alert("Please upload at least 5 images");
            hasErrors = true;
            return;
        }
    }

    // If no errors, you can submit the form
    if (!hasErrors) {
        document.querySelector("#overlayLoader").style.setProperty("display", "block", "important");
        // Optionally submit the form programmatically
        document.getElementById("createOrUpdateForm").submit();
    }
    document.getElementById("createOrUpdateBtn").disabled = false;
    if (action === "create") {
        document.querySelector("button[name='create_service']").disabled = false;
    }
});

// Get the current date
// const today = new Date();
// // Format the date as YYYY-MM
// const currentMonth = today.toISOString().slice(0, 7);
// // Set the max attribute for the input
// document.getElementById('startedIn').setAttribute('max', currentMonth);

function generateRandomId(length) {
    const characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    let randomId = "";

    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        randomId += characters.charAt(randomIndex);
    }
    return randomId;
}

function removeBlock(elem) {
    const remove_elem_id = elem.getAttribute("data-remove-id");
    const elementToRemove = document.getElementById(remove_elem_id);
    if (elementToRemove) {
        if (confirm("Are you sure you want to remove this block?")) {
            elementToRemove.remove();
        }
    }
    return;
}

function countChars(obj) {
    var maxLength = parseInt(obj.getAttribute('maxlength'));
    var currentLength = obj.value.length;
    var id = obj.id + '__charCount'
    var charCountElement = document.getElementById(id);

    charCountElement.textContent = currentLength + '/' + maxLength;
}

function previewImage(input) {
    let remove_btn = document.getElementById("remove_file");
    let file_exists = document.getElementById("file_exists");

    // Check file exists
    if (!checkFileSize(input)) {
        remove_btn.setAttribute("data-file-exists", "false");
        remove_btn.classList.remove("d-block");
        remove_btn.classList.add("d-none");
        if (file_exists.value != "nofile") {
            file_exists.value = "nofile";
        }
        input.value = "";
        return;
    } 

    var file = input.files[0];
    const id = input.id;
    var reader = new FileReader();

    reader.onload = function (e) {
        document.getElementById("label_" + id).src = e.target.result;
        remove_btn.setAttribute("data-file-exists", "true");
        remove_btn.classList.remove("d-none");
        remove_btn.classList.add("d-block");
        file_exists.value = "changed";
        document.querySelector("#thumbnailFormBox .invalid-feedback").style.display = "none";
    };
    reader.readAsDataURL(file);
    return;
}

function checkFileSize(input_file) {
    const image_for = input_file.getAttribute("data-image-for");
    let file_size = 5;
    const MAX_FILE_SIZE = file_size * 1024 * 1024; // 5MB in bytes

    const files = input_file.files;

    if (files && files[0]) {
        const file = files[0];
        const fileSize = file.size;

        if (fileSize > MAX_FILE_SIZE) {
            // Display warning message
            alert(
                `Error: File size exceeds the maximum limit of ${file_size}MB. Please choose a smaller image.`
            );
            return false;
        }
        return true;
    }
}

function removeFile(e) {
    const id = e.getAttribute("data-id");
    let input_file = document.getElementById(id)
    input_file.value = "";
    document.getElementById("label_" + id).src = e.getAttribute("data-image-src");
    e.setAttribute("data-file-exists", "false");
    e.classList.remove("d-block");
    e.classList.add("d-none");
    document.getElementById("file_exists").value = "nofile";
}

function createPackage() {
    let packageContainer = document.getElementById("packageContainer");
    let packages = packageContainer.querySelectorAll(".package").length;

    if (packages >= 5) {
        alert("You can add only 5 packages.");
        return;
    }
    // Check if the last package is empty
    if (packages > 0 ) {
        let lastPackage = packageContainer.lastElementChild;
        if (lastPackage.querySelector("input[name='packageName']").value === "") {
            // Scroll to the last package
            lastPackage.scrollIntoView({
                behavior: "smooth",
                block: "center",
            })
            alert("Please fill in the package before adding a new one.");
            return;
        }
    }
    const uid = generateRandomId(4);
    const block = `<div class="col-md-6 mt-4 package" id="package_${uid}">
        <div class="form-box mb-0">
            <label for="packageName_${uid}">
                <div class="row align-items-center">
                    <div class="col">Package Name</div>
                    <div class="col-auto">
                        <button type="button" class="btn btn-outline-danger border-0 btn-sm" id="packageRemoveBtn_${uid}" data-remove-id="package_${uid}" onclick="removeBlock(this);"><i class="bi bi-trash3"></i></button>
                    </div>
                </div>
            </label> 
            <div class="input-box mb-2">
                <div class="icon-box"><i class="bi bi-camera"></i></div>
                <input type="text" name="packageName" id="packageName_${uid}" class="q-control form-control" placeholder="--" required>
            </div>
            <div class="text-box">
                <div class="row align-items-center mb-1">
                    <div class="col-md-7 col-6 pe-1">
                        <div class="input-box mb-2">
                            <div class="icon-box"><i class="bi bi-currency-rupee"></i></div>
                            <input type="number" name="packagePrice" id="packagePrice_${uid}" class="q-control form-control" min="0" placeholder="--" required>
                        </div>
                    </div>
                    <div class="col-md-5 col-6 ps-0">
                        <div class="input-box mb-2">
                            <div class="icon-box"><i class="bi bi-slash-lg"></i></div>
                            <input type="text" name="packagePriceUnit" class="q-control form-control" id="packagePriceUnit_${uid}" placeholder="Day, Hour..." value="">
                        </div>
                    </div>
                </div>
                <div class="content-area-container form-box mb-0" id="packageDetails_${uid}ContentArea">
                    <label for="content" class="ph-q-label"><span class="content-area-label-text">Package Details</span></label>
                    <div class="content-area-box bg-white border">
                        <div class="content-area content-area-sm custom-scrollbar" data-bs-target="#contentAreaModal" data-bs-toggle="modal" data-id="packageDetails_${uid}ContentArea"></div>
                        <textarea name="packageDetails" class="d-none"></textarea>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    packageContainer.insertAdjacentHTML("beforeend", block);
}

function createAddOn() {
    let packageContainer = document.getElementById("addOnContainer");
    let addOns = packageContainer.querySelectorAll(".addOn").length;

    if (addOns >= 5) {
        alert("You can add only 5 add-ons");
        return;
    }

    // Check if the last add-on is empty
    if (addOns > 0 ) {
        let lastAddOn = packageContainer.lastElementChild;
        if (lastAddOn.querySelector("input[name='addOnName']").value === "") {
            // Scroll to the last add-on
            lastAddOn.scrollIntoView({
                behavior: "smooth",
                block: "center",
            })
            alert("Please fill in the add-on before adding a new one.");
            return;
        }
    }

    const uid = generateRandomId(4);
    const block = `<div class="col-md-6 mt-4 addOn" id="addOn_${uid}">
        <div class="form-box mb-0">
            <label for="addOnName_${uid}">
                <div class="row align-items-center">
                    <div class="col">Add On Name</div>
                    <div class="col-auto">
                        <button type="button" class="btn btn-outline-danger border-0 btn-sm" id="addOnRemoveBtn_${uid}" data-remove-id="addOn_${uid}" onclick="removeBlock(this);"><i class="bi bi-trash3"></i></button>
                    </div>
                </div>
            </label>
            <div class="input-box mb-2">
                <div class="icon-box"><i class="bi bi-postcard-heart"></i></div>
                <input type="text" name="addOnName" id="addOnName_${uid}" class="q-control form-control" placeholder="--" required>
            </div>
            <div class="text-box">
                <div class="row align-items-center mb-1">
                    <div class="col-md-7 col-6 pe-1">
                        <div class="input-box mb-2">
                            <div class="icon-box"><i class="bi bi-currency-rupee"></i></div>
                            <input type="number" name="addOnPrice" id="addOnPrice_${uid}" class="q-control form-control" min="0" placeholder="--" required>
                        </div>
                    </div>
                    <div class="col-md-5 col-6 ps-0">
                        <div class="input-box mb-2">
                            <div class="icon-box"><i class="bi bi-slash-lg"></i></div>
                            <input type="text" name="addOnPriceUnit" class="q-control form-control" id="addOnPriceUnit_${uid}" placeholder="Day, Hour..." value="">
                        </div>
                    </div>
                </div>
                <div class="content-area-container form-box mb-0" id="addOnDetails_${uid}ContentArea">
                    <label for="content" class="ph-q-label"><span class="content-area-label-text">Add-on Details</span></label>
                    <div class="content-area-box bg-white border">
                        <div class="content-area content-area-sm custom-scrollbar" data-bs-target="#contentAreaModal" data-bs-toggle="modal" data-id="addOnDetails_${uid}ContentArea"></div>
                        <textarea name="addOnDetails" class="d-none"></textarea>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    packageContainer.insertAdjacentHTML("beforeend", block);
}


    
document.addEventListener('DOMContentLoaded', function () {
    dragAndDrop();
});

function dragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const imageCardsContainer = document.getElementById('imageCards');
    let cardId = 0;  // To uniquely identify each card
    
    // When user clicks on drop zone, trigger file input
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Handle file input change
    fileInput.addEventListener('change', handleFiles);
    
    // Handle drag-and-drop functionality
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        handleFiles({ target: { files } });
    });
    
    // Function to handle files
    function handleFiles(e) {
        let files = Array.from(e.target.files); // Convert FileList to an array
        let file_size_error = false;
    
        // Check image cards length
        if (files.length > 10) {
            // Get only 10 images
            files = files.slice(0, 10);
        }
        const current_cards = imageCardsContainer.children.length;
        if (current_cards >= 10) {
            alert('You can upload up to 10 images.');
            fileInput.value = '';
            return;
        }
    
        if ((current_cards + files.length) >= 10) {
            alert('You can upload up to 10 images.');
        }
    
        if (files.length > 10) {
            alert('You can upload up to 10 images.');
        }
    
        var remaining = 10 - current_cards;
        files = files.slice(0, remaining);
    
        for (const file of files) {
            if (file.type.startsWith('image/')) {
                // Check file size
                if (file.size > 5 * 1024 * 1024) {
                    file_size_error = true;
                    continue;
                } else {
                    // Create image card
                    createImageCard(file, cardId++);
                }
            }
        }
    
        if (file_size_error) {
            alert('Some of your images are too large. File size should be less than 5MB.');
        }
    }
    
    // Function to create image card with provided structure
    function createImageCard(file, id) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function (e) {
            const imageUrl = e.target.result;
    
            // Create the card structure
            const card = document.createElement('div');
            card.classList.add('image-card');
    
            card.innerHTML += `
                <div class='image-preview-box'>
                    <label for="image${id}">
                        <img src="${imageUrl}" onerror='this.src="https://eventic-webapp.s3.ap-south-1.amazonaws.com/static/assets/defaults/1x1.png";' id="label_image${id}">
                    </label>
                    <div class='image-content-box'>
                        <div class='text-group'>
                            <div for="describe${id}" class='form-describe'>
                                <div class="textbox-title">Describe</div>
                                <button type='button' class='remove-btn'><i class='bi bi-trash3'></i></button>
                            </div>
                            <div class='text-box-input'>
                                <textarea class='autoResizeTextarea img-description' maxlength='150' name="imageDescription" id="describe${id}" placeholder='--'></textarea>
                            </div>
                            <input type='file' name="imageFile" data-image-for="portfolio" accept="image/*" id="image${id}" onchange="previewImage(this)" data-index="${id}" required>
                        </div>
                    </div>
                </div>
            `;
    
            // Add the remove button functionality
            const removeBtn = card.querySelector('.remove-btn');
            removeBtn.addEventListener('click', () => {
                card.remove();  // Remove the card when clicked
            });
    
            // Add the file to the input element's `files` property
            const inputFile = card.querySelector(`#image${id}`);
            const dt = new DataTransfer();  // Create a DataTransfer object to manipulate files
            dt.items.add(file);  // Add the file
            inputFile.files = dt.files;  // Assign the file to the input
    
            // Append the card to the image cards container
            imageCardsContainer.appendChild(card);
        };
    }
}

// JavaScript function to check file size
function checkFileSize(file) {
    const input = file;
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes

    if (input.files && input.files[0]) {
        const fileSize = input.files[0].size;

        if (fileSize > maxSize) {
            alert(
                "The file size exceeds the 5MB limit. Please upload a smaller file."
            );
            input.value = ""; // Clear the input field
            return false;
        } else {
            return true;
        }
    }
}