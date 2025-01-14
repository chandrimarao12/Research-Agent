
document.getElementById('inputField').addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && this.value.trim() !== '') {
        addMessage(this.value, 'user');
        sendMessageToBackend(this.value);
        this.value = '';  // Clear the input field
    }
});

document.getElementById('sendBtn').addEventListener('click', function() {
    const message = document.getElementById('inputField').value;
    if (message.trim() !== '') {
        addMessage(message, 'user');
        sendMessageToBackend(message);
        document.getElementById('inputField').value = '';  // Clear the input field
    }
});

document.getElementById('clearBtn').addEventListener('click', function() {
    document.getElementById('messages').innerHTML = '';
});

document.getElementById('micBtn').addEventListener('click', function() {
    startSpeechRecognition();
});

document.getElementById('imageInput').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const imageUrl = e.target.result;
            addMessage(`<img src="${imageUrl}" alt="Image" class="image-message">`, 'user');
        };
        reader.readAsDataURL(file);
    }
});

function addMessage(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.innerHTML = message;
    document.getElementById('messages').appendChild(messageElement);
    scrollToBottom();
}

// function sendMessageToBackend(message) {
//     fetch('http://127.0.0.1:8000/summarize', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ query: message }),
//     })
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }
//             return response.json();
//         })
//         .then(data => {
//             console.log('Response from backend:', data);
//             addMessage(data.summary, 'bot'); // Ensure this calls the function to add the bot's response to the chat
//         })
//         .catch(error => {
//             console.error('Error in sending request to backend:', error);
//         });
// }

async function sendMessageToBackend(query) {
    const response = await fetch('http://127.0.0.1:8000/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
    });

    if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
    }
    return response.json();
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function startSpeechRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('inputField').value = transcript;
        addMessage(transcript, 'user');
        sendMessageToBackend(transcript);
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error', event);
    };
}