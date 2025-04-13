# Grade Saver

Grade Saver is a Google Chrome extension for Gradescope that automates regrade requests by extracting rubric details and using AI to generate context-aware requests. This tool streamlines the process of submitting regrade requests, helping you quickly address potential grading errors.

---

## Features

- **Automated Data Extraction:**  
  Utilizes Playwright and Beautiful Soup to scrape Gradescope for incorrect answers and rubric data.

- **Image Pre-Processing:**  
  Uses OpenCV to denoise and enhance scanned images, improving text extraction accuracy.

- **AI-Generated Regrade Requests:**  
  Integrates an AI model to analyze extracted rubric information and generate smart regrade prompts.

- **Seamless Chrome Integration:**  
  A Chrome extension built with Manifest V3 that auto-fills regrade requests directly into Gradescope.

- **Backend Support:**  
  A Flask-based server handles web scraping, image processing, and AI prompting to manage data flow.

---

## Installation

### Prerequisites

- **Google Chrome:** For running the extension.
- **Python 3.7+:** To run the Flask server and required scripts.
- **Node.js (optional):** For managing web scraping tooling if needed.

### Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/gradesaver.git
   cd gradesaver
