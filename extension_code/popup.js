// popup.js (updated version)
document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById("suggestionsBox");
  const statusDiv = document.getElementById("status");

  const runButton = document.createElement("button");
  runButton.textContent = "Run Gradescope Helper";
  runButton.style.padding = "10px";
  runButton.style.marginBottom = "10px";
  runButton.style.background = "#3366cc";
  runButton.style.color = "white";
  runButton.style.border = "none";
  runButton.style.borderRadius = "6px";
  runButton.style.cursor = "pointer";

  container.insertBefore(runButton, container.firstChild);

  runButton.addEventListener("click", function () {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length === 0) {
        statusDiv.innerHTML = "<p style='color: red'>No active tab found.</p>";
        return;
      }

      const url = tabs[0].url;
      if (!url.includes("gradescope.com")) {
        statusDiv.innerHTML =
          "<p style='color: red'>Please navigate to a Gradescope assignment page first!</p>";
        return;
      }

      statusDiv.innerHTML = "<p>⏳ Running background Python script...</p>";

      fetch("http://localhost:5001/run-scraper", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: url }),
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("✅ Python response:", data);

          // Clear previous content
          container.innerHTML = "";

          const responseData = data.rubrics || { message: "No rubric data returned" };

          if (typeof responseData === "string") {
            container.innerText = responseData;
          } else {
            for (const [question, detail] of Object.entries(responseData)) {
              const section = document.createElement("div");
              section.innerHTML = `<strong>${question}</strong>`;

              if (detail.main && detail.main.length > 0) {
                section.innerHTML += "<br><em>Main:</em><ul>";
                detail.main.forEach((r) => {
                  section.innerHTML += `<li>${r.points} — ${r.comment}</li>`;
                });
                section.innerHTML += "</ul>";
              }

              if (detail.sub && Object.keys(detail.sub).length > 0) {
                for (const [subQ, rubrics] of Object.entries(detail.sub)) {
                  section.innerHTML += `<br><em>Sub ${subQ}:</em><ul>`;
                  rubrics.forEach((r) => {
                    section.innerHTML += `<li>${r.points} — ${r.comment}</li>`;
                  });
                  section.innerHTML += "</ul>";
                }
              }

              container.appendChild(section);
              container.appendChild(document.createElement("hr"));
            }
          }

          statusDiv.innerHTML = "<p style='color: green'> Data loaded!</p>";
        })
        .catch((err) => {
          console.error("❌ Failed to fetch from server:", err);
          statusDiv.innerHTML = "<p style='color: red'> Failed to connect to backend server.</p>";
        });
    });
  });
});
