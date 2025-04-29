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
    if (!checkFileSize(input)) {
        remove_btn.setAttribute("data-file-exists", "false");
        remove_btn.classList.remove("d-block");
        remove_btn.classList.add("d-none");
        document.getElementById("file_exists").value = "removed";
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
        document.getElementById("file_exists").value = "changed";
    };

    reader.readAsDataURL(file);
}

function checkFileSize(input_file) {
    const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB in bytes

    const files = input_file.files;
    const id = input_file.id;

    if (files && files[0]) {
        const file = files[0];
        const fileSize = file.size;

        if (fileSize > MAX_FILE_SIZE) {
            // Clear the selected file
            input_file.value = "";
            
            // Display warning message
            alert(
                "Error: File size exceeds the maximum limit of 500KB. Please choose a smaller image."
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
    document.getElementById("file_exists").value = "removed";
}

function createPackage() {
    let packageContainer = document.getElementById("packageContainer");
    let packages = packageContainer.querySelectorAll(".package").length;

    if (packages >= 5) {
        alert("You can add only 5 packages.");
        return;
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
                            <input type="text" name="packagePricePer" class="q-control form-control" id="packagePricePer_${uid}" placeholder="Day, Hour..." value="">
                        </div>
                    </div>
                </div>
                <div class="row align-items-center mb-1 pe-2">
                    <div class="col">
                        <label for="packageDetails_${uid}" class="text-secondary">Package Details</label>
                    </div>
                    <div class="col-auto"><label id="packageDetails_${uid}__charCount">0/500</label></div>
                </div>
                <textarea name="packageDetails" id="packageDetails_${uid}" class="q-control h-md" placeholder="--" rows="5" maxlength="500" onkeyup="countChars(this)"></textarea>
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
                            <input type="text" name="addOnPricePer" class="q-control form-control" id="addOnPricePer_${uid}" placeholder="Day, Hour..." value="">
                        </div>
                    </div>
                </div>
                <div class="row align-items-center mb-1 pe-2">
                    <div class="col">
                        <label for="addOnDetails_${uid}" class="text-secondary">Add On Details</label>
                    </div>
                    <div class="col-auto"><label id="addOnDetails_${uid}__charCount">0/500</label></div>
                </div>
                <textarea name="addOnDetails" id="addOnDetails_${uid}" class="q-control h-md" placeholder="--" rows="5" maxlength="500" onkeyup="countChars(this)"></textarea>
            </div>
        </div>
    </div>`;
    packageContainer.insertAdjacentHTML("beforeend", block);
}