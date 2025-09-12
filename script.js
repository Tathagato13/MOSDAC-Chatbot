// let sessionId = null;

// function sendMessage() {
//   const inputField = document.getElementById("input");
//   let input = inputField.value.trim();
//   if (!input) return;

//   const mainDiv = document.getElementById("message-section");

//   const welcome = document.querySelector(".welcome-message");
//   if (welcome) welcome.remove();

//   const userDiv = document.createElement("div");
//   userDiv.classList.add("message", "user-message");
//   userDiv.innerHTML = `
//     <div class="message-header"><i class="fas fa-user"></i> You</div>
//     <div class="message-content">${input}</div>`;
//   mainDiv.appendChild(userDiv);

//   showTypingIndicator();
//   inputField.value = "";

//   const formData = new URLSearchParams();
//   formData.append("message", input);
//   if (sessionId) {
//     formData.append("session_id", sessionId);
//   }

//   fetch("/chat", {
//     method: "POST",
//     headers: { "Content-Type": "application/x-www-form-urlencoded" },
//     body: formData
//   })
//     .then(res => res.json())
//     .then(data => {
//       sessionId = data.session_id || sessionId;
//       removeTypingIndicator();
//       const botDiv = document.createElement("div");
//       botDiv.classList.add("message", "bot-message");
//       botDiv.innerHTML = `
//         <div class="message-header"><i class="fas fa-robot"></i> AI ChatBot</div>
//         <div class="message-content">${data.response}</div>`;
//       mainDiv.appendChild(botDiv);
//       mainDiv.scrollTop = mainDiv.scrollHeight;
//     });
// }



// function showTypingIndicator() {
//   const mainDiv = document.getElementById("message-section");
//   const typingDiv = document.createElement("div");
//   typingDiv.classList.add("typing-indicator");
//   typingDiv.id = "typing-indicator";
//   typingDiv.innerHTML = `<span></span><span></span><span></span>`;
//   mainDiv.appendChild(typingDiv);
//   mainDiv.scrollTop = mainDiv.scrollHeight;
// }

// function removeTypingIndicator() {
//   const typingDiv = document.getElementById("typing-indicator");
//   if (typingDiv) typingDiv.remove();
// }

// document.addEventListener("DOMContentLoaded", () => {
//   document.getElementById("input").addEventListener("keydown", function (e) {
//     if (e.key === "Enter") {
//       sendMessage();
//     }
//   });
// });


// let sessionId = null;
// let preferBulletPoints = false;

// function formatResponse(response) {
//   // Remove asterisks from the response
//   let formattedResponse = response.replace(/\*/g, '');
  
//   // Check if user prefers bullet points
//   if (preferBulletPoints) {
//     // Convert lines that look like list items to bullet points
//     formattedResponse = formattedResponse.replace(/^\s*™/gm, '•');
//     // Add line breaks between bullet points
//     formattedResponse = formattedResponse.replace(/\n/g, '<br>');
//   } else {
//     // Default to paragraph format
//     // Replace line breaks with spaces for paragraph flow
//     formattedResponse = formattedResponse.replace(/\n/g, ' ');
//     // Trim multiple spaces
//     formattedResponse = formattedResponse.replace(/\s+/g, ' ');
//   }
  
//   return formattedResponse;
// }

// function sendMessage() {
//   const inputField = document.getElementById("input");
//   let input = inputField.value.trim();
//   if (!input) return;

//   const mainDiv = document.getElementById("message-section");

//   const welcome = document.querySelector(".welcome-message");
//   if (welcome) welcome.remove();

//   const userDiv = document.createElement("div");
//   userDiv.classList.add("message", "user-message");
//   userDiv.innerHTML = `
//     <div class="message-header"><i class="fas fa-user"></i> You</div>
//     <div class="message-content">${input}</div>`;
//   mainDiv.appendChild(userDiv);

//   // Check if user is asking for bullet points
//   preferBulletPoints = input.toLowerCase().includes("bullet") || 
//                       input.toLowerCase().includes("point") || 
//                       input.toLowerCase().includes("list");

//   showTypingIndicator();
//   inputField.value = "";

//   const formData = new URLSearchParams();
//   formData.append("message", input);
//   if (sessionId) {
//     formData.append("session_id", sessionId);
//   }

//   fetch("/chat", {
//     method: "POST",
//     headers: { "Content-Type": "application/x-www-form-urlencoded" },
//     body: formData
//   })
//     .then(res => res.json())
//     .then(data => {
//       sessionId = data.session_id || sessionId;
//       removeTypingIndicator();
//       const botDiv = document.createElement("div");
//       botDiv.classList.add("message", "bot-message");
//       botDiv.innerHTML = `
//         <div class="message-header"><i class="fas fa-robot"></i> AI ChatBot</div>
//         <div class="message-content">${formatResponse(data.response)}</div>`;
//       mainDiv.appendChild(botDiv);
//       mainDiv.scrollTop = mainDiv.scrollHeight;
//     });
// }

// function showTypingIndicator() {
//   const mainDiv = document.getElementById("message-section");
//   const typingDiv = document.createElement("div");
//   typingDiv.classList.add("typing-indicator");
//   typingDiv.id = "typing-indicator";
//   typingDiv.innerHTML = `<span></span><span></span><span></span>`;
//   mainDiv.appendChild(typingDiv);
//   mainDiv.scrollTop = mainDiv.scrollHeight;
// }

// function removeTypingIndicator() {
//   const typingDiv = document.getElementById("typing-indicator");
//   if (typingDiv) typingDiv.remove();
// }

// document.addEventListener("DOMContentLoaded", () => {
//   document.getElementById("input").addEventListener("keydown", function (e) {
//     if (e.key === "Enter") {
//       sendMessage();
//     }
//   });
// });


let sessionId = null;
let preferBulletPoints = false;
let isTyping = false;
let messageCounter = 0; // To generate unique IDs for each message

function formatResponse(response) {
  // Remove asterisks from the response
  let formattedResponse = response.replace(/\*/g, '');
  
  // Check if user prefers bullet points
  if (preferBulletPoints) {
    // Convert lines that look like list items to bullet points
    formattedResponse = formattedResponse.replace(/^\s*™/gm, '•');
    // Add line breaks between bullet points
    formattedResponse = formattedResponse.replace(/\n/g, '<br>');
  } else {
    // Default to paragraph format
    // Replace line breaks with spaces for paragraph flow
    formattedResponse = formattedResponse.replace(/\n/g, ' ');
    // Trim multiple spaces
    formattedResponse = formattedResponse.replace(/\s+/g, ' ');
  }
  
  return formattedResponse;
}

function typeWriter(element, text, speed = 30) {
  let i = 0;
  isTyping = true;
  
  function typing() {
    if (i < text.length) {
      element.innerHTML = text.substring(0, i + 1);
      i++;
      setTimeout(typing, speed);
    } else {
      isTyping = false;
    }
  }
  
  typing();
}

function sendMessage() {
  if (isTyping) return; // Prevent new messages while typing
  
  const inputField = document.getElementById("input");
  let input = inputField.value.trim();
  if (!input) return;

  const mainDiv = document.getElementById("message-section");

  const welcome = document.querySelector(".welcome-message");
  if (welcome) welcome.remove();

  // Create user message
  const userDiv = document.createElement("div");
  userDiv.classList.add("message", "user-message");
  userDiv.innerHTML = `
    <div class="message-header"><i class="fas fa-user"></i> You</div>
    <div class="message-content">${input}</div>`;
  mainDiv.appendChild(userDiv);

  // Check if user is asking for bullet points
  preferBulletPoints = input.toLowerCase().includes("bullet") || 
                      input.toLowerCase().includes("point") || 
                      input.toLowerCase().includes("list");

  showTypingIndicator();
  inputField.value = "";
  mainDiv.scrollTop = mainDiv.scrollHeight;

  const formData = new URLSearchParams();
  formData.append("message", input);
  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      sessionId = data.session_id || sessionId;
      removeTypingIndicator();
      
      // Create bot message container with unique ID
      const botDiv = document.createElement("div");
      botDiv.classList.add("message", "bot-message");
      const responseId = `bot-response-${messageCounter++}`;
      botDiv.innerHTML = `
        <div class="message-header"><i class="fas fa-robot"></i> AI ChatBot</div>
        <div class="message-content" id="${responseId}"></div>`;
      mainDiv.appendChild(botDiv);
      
      const responseElement = document.getElementById(responseId);
      const formattedResponse = formatResponse(data.response);
      typeWriter(responseElement, formattedResponse);
      
      // Scroll as the message is being typed
      const scrollInterval = setInterval(() => {
        mainDiv.scrollTop = mainDiv.scrollHeight;
        if (!isTyping) clearInterval(scrollInterval);
      }, 100);
    });
}

function showTypingIndicator() {
  const mainDiv = document.getElementById("message-section");
  const typingDiv = document.createElement("div");
  typingDiv.classList.add("typing-indicator");
  typingDiv.id = "typing-indicator";
  typingDiv.innerHTML = `<span></span><span></span><span></span>`;
  mainDiv.appendChild(typingDiv);
  mainDiv.scrollTop = mainDiv.scrollHeight;
}

function removeTypingIndicator() {
  const typingDiv = document.getElementById("typing-indicator");
  if (typingDiv) typingDiv.remove();
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("input").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });
});