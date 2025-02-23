let filePath = '';

const totalMedicines = 5;

function markMedicineTaken() {
    if (medicinesTaken < totalMedicines) {
        medicinesTaken++;
        updateProgressBar();
    }
}

function updateProgressBar() {
    const progress = (medicinesTaken / totalMedicines) * 100;
    document.getElementById('progress').style.width = `${progress}%`;
    document.getElementById('progress-text').innerText = `${medicinesTaken}/${totalMedicines} Medicines Taken`;
}

function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (!file) {
        alert('No file selected');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch(`/upload/${uid}`, { // Use the uid in the URL
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert('File is now loaded');
            filePath = data.file_path;
            sendMessage("Explain my disease like I am five");
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function sendMessage(message) {
    const messageInput = document.getElementById('message-input');
    if (!message) {
        message = messageInput.value.trim();
    }
    if (!message) {
        return;
    }

    const messageElement = document.createElement('div');
    messageElement.className = 'my-2 text-right';
    messageElement.innerHTML = `<span class="inline-block p-2 rounded bg-blue-500 text-white">${message}</span>`;
    document.getElementById('messages').appendChild(messageElement);

    fetch(`/chat/${uid}`, { // Include the uid in the URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, file_path: filePath }),
    })
    .then(response => response.json())
    .then(data => {
        const responseElement = document.createElement('div');
        responseElement.className = 'my-2 text-left';
        responseElement.innerHTML = `<span class="inline-block p-2 rounded bg-gray-300">${data.response}</span>`;
        document.getElementById('messages').appendChild(responseElement);
    })
    .catch(error => {
        console.error('Error:', error);
    });

    if (!messageInput.value) {
        messageInput.value = '';
    }
}