function openQuestion(questionId) {
  chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
    if (tabs.length === 0) {
      console.error("No active tab found");
      return;
    }
    
    // Check if we're on a Gradescope page
    const url = tabs[0].url;
    if (!url.includes("gradescope.com")) {
      document.getElementById("status").innerHTML = 
        "<p style='color: red'>Please navigate to a Gradescope assignment page first!</p>";
      return;
    }
    
    // Update status
    document.getElementById("status").innerHTML = 
      `<p>Attempting to open Question ${questionId}...</p>`;
    
    // Send message to content script
    chrome.tabs.sendMessage(tabs[0].id, {
      action: "openQuestion",
      question: questionId,
    }, response => {
      if (chrome.runtime.lastError) {
        console.error("Error sending message:", chrome.runtime.lastError);
        document.getElementById("status").innerHTML = 
          `<p style='color: red'>Error: Could not communicate with page. Make sure you're on a Gradescope assignment page.</p>`;
      } else if (response && response.success) {
        document.getElementById("status").innerHTML = 
          `<p style='color: green'>${response.message}</p>`;
      } else {
        document.getElementById("status").innerHTML = 
          `<p style='color: orange'>${response.message || "Unknown error occurred"}</p>`;
      }
    });
  });
}

// Load and parse the regrade suggestions file
document.addEventListener('DOMContentLoaded', function() {
  // Add a status div for feedback
  const container = document.getElementById("suggestionsBox");
  const statusDiv = document.createElement("div");
  statusDiv.id = "status";
  container.parentNode.insertBefore(statusDiv, container.nextSibling);
  
  // Add direct question opener form
  const form = document.createElement("div");
  form.innerHTML = `
    <p>Quick open question number:</p>
    <input type="number" id="questionInput" min="1" style="width: 60px">
    <button id="openButton">Open</button>
  `;
  container.parentNode.insertBefore(form, container);
  
  // Add event listener for the button
  document.getElementById("openButton").addEventListener("click", function() {
    const questionNum = document.getElementById("questionInput").value;
    if (questionNum) {
      openQuestion(questionNum);
    }
  });
  
  // Load suggestions if regrade.txt exists
  fetch(chrome.runtime.getURL("regrade.txt"))
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to load regrade.txt");
      }
      return response.text();
    })
    .then(text => {
      // Look for both Q1: and Question 1: formats
      const regex = /(?:Q|Question\s*)(\d+):/g;
      let match;
      let lastIndex = 0;
      
      while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
          container.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
        }
        
        const questionNum = match[1]; // Extract number
        const link = document.createElement("a");
        link.textContent = match[0]; // Keep the original format (Q1: or Question 1:)
        link.href = "#";
        link.style.color = "blue";
        link.style.fontWeight = "bold";
        link.onclick = function() {
          openQuestion(questionNum);
          return false;  // Prevent default action
        };
        
        container.appendChild(link);
        lastIndex = regex.lastIndex;
      }
      
      if (lastIndex < text.length) {
        container.appendChild(document.createTextNode(text.slice(lastIndex)));
      }
    })
    .catch(error => {
      console.error("Error loading suggestions:", error);
      container.innerHTML = 
        `<p>No regrade.txt file found or error loading suggestions.</p>
         <p>You can still use the quick open feature above.</p>`;
    });
});