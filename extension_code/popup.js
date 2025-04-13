// popup.js (revised: displays individual rubric entries with regrade buttons)
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

          container.innerHTML = "";
          const responseData = data.rubrics || { message: "No rubric data returned" };

          if (typeof responseData === "string") {
            container.innerText = responseData;
          } else {
            for (const [questionLabel, detail] of Object.entries(responseData)) {
              const questionMatch = questionLabel.match(/(?:Question\s*)(\d+(?:\.\d+)?)/i);
              const questionId = questionMatch ? questionMatch[1] : questionLabel;

              const section = document.createElement("div");
              section.innerHTML = `<strong>${questionLabel}</strong>`;

              // Render main rubrics with individual regrade buttons
              if (detail.main && detail.main.length > 0) {
                section.innerHTML += "<br><em>Main Rubrics:</em>";
                const list = document.createElement("ul");
                detail.main.forEach((r, idx) => {
                  const item = document.createElement("li");
                  const btn = document.createElement("button");
                  btn.textContent = `Request Regrade: ${r.points} pts`;
                  btn.style.marginLeft = "10px";
                  btn.onclick = () => {
                    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                      if (tabs.length > 0) {
                        chrome.tabs.sendMessage(tabs[0].id, {
                          action: "openQuestion",
                          question: questionId,
                          regradeText: r.comment
                        });
                        statusDiv.innerHTML = `<p>📬 Autofilled regrade for ${questionLabel} - rubric ${idx + 1}</p>`;
                      }
                    });
                  };
                  item.innerHTML = `${r.points} — ${r.comment}`;
                  item.appendChild(btn);
                  list.appendChild(item);
                });
                section.appendChild(list);
              }

              // Render sub rubrics with individual regrade buttons
              if (detail.sub && Object.keys(detail.sub).length > 0) {
                for (const [subQ, rubrics] of Object.entries(detail.sub)) {
                  const subLabel = document.createElement("div");
                  subLabel.innerHTML = `<br><em>Sub ${subQ}:</em>`;
                  const subList = document.createElement("ul");
                  rubrics.forEach((r, idx) => {
                    const subItem = document.createElement("li");
                    const btn = document.createElement("button");
                    btn.textContent = `Request Regrade`;
                    btn.style.marginLeft = "10px";
                    btn.onclick = () => {
                      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                        if (tabs.length > 0) {
                          chrome.tabs.sendMessage(tabs[0].id, {
                            action: "openQuestion",
                            question: questionId,
                            regradeText: r.comment
                          });
                          statusDiv.innerHTML = `<p>📬 Autofilled regrade for ${questionLabel} - sub ${subQ}</p>`;
                        }
                      });
                    };
                    subItem.innerHTML = `${r.points} — ${r.comment}`;
                    subItem.appendChild(btn);
                    subList.appendChild(subItem);
                  });
                  section.appendChild(subLabel);
                  section.appendChild(subList);
                }
              }

              container.appendChild(section);
              container.appendChild(document.createElement("hr"));
            }
          }

          statusDiv.innerHTML = "<p style='color: green'>✅ Data loaded! Click a rubric to request a regrade.</p>";
        })
        .catch((err) => {
          console.error("❌ Failed to fetch from server:", err);
          statusDiv.innerHTML = "<p style='color: red'>❌ Failed to connect to backend server.</p>";
        });
    });
  });
});
