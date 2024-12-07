const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const preview = document.getElementById('preview');
const previewImage = document.getElementById('previewImage');
const processBtn = document.getElementById('processBtn');
const resultText = document.getElementById('resultText');

// Prevent default drag/drop behavior
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Add drag styles
['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => {
        dropzone.classList.add('border-indigo-400');
    });
});

['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => {
        dropzone.classList.remove('border-indigo-400');
    });
});

// Handle file drop or click to select a file
dropzone.addEventListener('drop', (e) => {
    const file = e.dataTransfer.files[0];
    handleFile(file);
});

dropzone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    handleFile(file);
});

// Function to handle the selected file
function handleFile(file) {
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.classList.remove('hidden');
            previewImage.src = e.target.result;
            dropzone.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }
}

// Process the image and predict the Kannada letter
processBtn.addEventListener('click', async () => {
    resultText.innerHTML = `
        <div class="animate-spin">
            <i class="bi bi-arrow-repeat text-4xl text-indigo-400"></i>
        </div>
    `;

    // Send the image for prediction after a short delay
    await predictLetter();
});

// Function to predict the letter dynamically
async function predictLetter() {
    const formData = new FormData();
    const fileInput = document.getElementById('fileInput');
    formData.append('image', fileInput.files[0]);

    // Sending image to Flask backend
    const response = await fetch('/predict', {
        method: 'POST',
        body: formData,
    });

    const data = await response.json();
    const predictedLetter = data.predicted_letter;  // Use the predicted letter from the backend

    // Set a timeout to display the predicted letter after 2 seconds
    setTimeout(() => {
        resultText.innerHTML = `
            <div class="text-white-400 text-[250px] font-bold">${predictedLetter}</div>
        `;
    }, 2000);  // Delay for 2 seconds
}
