// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "openQuestion") {
    const questionNumber = request.question;
    console.log(`Attempting to expand Q${questionNumber}`);
    
    // First approach: Try to find question headers by the heading text
    const headings = document.querySelectorAll('h2, h3, h4');
    let foundQuestion = false;
    
    for (const heading of headings) {
      // Match both "Question X" and "Question XX" formats
      if (heading.textContent.trim().match(new RegExp(`Question\\s*${questionNumber}\\b`))) {
        console.log(`Found heading for Question ${questionNumber}`);
        
        // Try to find the expandable element nearby
        // Look for the parent question container which often has a click handler
        let container = heading.closest('.question-container') || heading.parentElement;
        if (container) {
          console.log('Found container, attempting to expand');
          // Try clicking the container itself (some Gradescope layouts use this)
          container.click();
          
          // Also try to find any links or buttons nearby
          const expandElements = container.querySelectorAll('a, button, .expander, .question-header');
          if (expandElements.length > 0) {
            console.log(`Found ${expandElements.length} potential expand elements`);
            expandElements.forEach(el => el.click());
          }
          
          // Scroll to the question
          heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
          foundQuestion = true;
        }
        
        // Some Gradescope pages use a different structure with a specific rubric toggle
        const rubricToggles = document.querySelectorAll('.rubric-toggle, .toggle-rubric, [data-qa="toggle-rubric"]');
        rubricToggles.forEach(toggle => {
          const toggleQuestion = toggle.closest('.question');
          if (toggleQuestion && toggleQuestion.textContent.includes(`Question ${questionNumber}`)) {
            console.log('Found rubric toggle, clicking');
            toggle.click();
            foundQuestion = true;
          }
        });
      }
    }
    
    // Second approach: Try by matching question number in various formats
    if (!foundQuestion) {
      console.log('Trying alternative approach');
      // Look for question elements by class or data attributes
      const questionElements = document.querySelectorAll('.question, [data-question-id], .question-container');
      
      questionElements.forEach(el => {
        // Check if this element contains the question number anywhere in its text
        if (el.textContent.match(new RegExp(`Question\\s*${questionNumber}\\b`))) {
          console.log('Found question element via text content');
          // Try to click any headers, links, or buttons
          const clickables = el.querySelectorAll('h2, h3, h4, a, button, .expander, .question-header');
          if (clickables.length > 0) {
            clickables.forEach(c => c.click());
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            foundQuestion = true;
          } else {
            // As a last resort, try clicking the element itself
            el.click();
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            foundQuestion = true;
          }
        }
      });
    }
    
    // Send response back with success status
    sendResponse({
      success: foundQuestion, 
      message: foundQuestion ? 
        `Found and attempted to expand Question ${questionNumber}` : 
        `Could not find Question ${questionNumber} on the page`
    });
    return true; // Keep the message channel open for async response
  }
});

// Log that content script has loaded properly
console.log('Gradescope Regrade Helper content script loaded');

// Additional debugging - log DOM structure to console for inspection
setTimeout(() => {
  console.log('Gradescope page structure:');
  const questions = document.querySelectorAll('h2, h3, h4, .question, .question-container');
  console.log(`Found ${questions.length} potential question elements`);
  questions.forEach((q, i) => {
    console.log(`Element ${i+1}:`, q.tagName, q.className, q.textContent.substring(0, 50) + '...');
  });
}, 2000);