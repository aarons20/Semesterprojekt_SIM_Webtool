function copyToClipboard(value, button) {
    const textarea = document.createElement('textarea');
    textarea.value = value;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);

    // Add 'copied' class to button
    button.classList.add('copied');
    button.classList.add('share-animation');

    // Remove 'copied' class after a delay
    setTimeout(function() {
        button.classList.remove('copied');
        button.classList.remove('share-animation');
    }, 1000); // Adjust the duration as needed
  }
  
  function reloadView() {
    var accordionItems = document.querySelectorAll("#myAccordion .accordion-item");
    // Create an array to store the state of each accordion item
    var accordionState = [];

    // Iterate over each accordion item
    accordionItems.forEach(function(item) {
      var isOpen = item.querySelector(".accordion-collapse").classList.contains("show");
      accordionState.push(isOpen);
    });
    console.log(accordionState)

    // Convert the accordion state to a JSON string to send in the AJAX request
    var accordionStateJson = JSON.stringify(accordionState);

    // AJAX request to retrieve updated profiles from the server
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/get-updated-profiles", true);   
    xhr.onreadystatechange = function() {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          var parser = new DOMParser();
          // Parse the response HTML
          var parsedHTML = parser.parseFromString(xhr.responseText, "text/html");

          // Update the content of the accordion with the new profile data
          var accordionContainer = document.getElementById("myAccordion");
          accordionContainer.innerHTML = parsedHTML.getElementById("myAccordion").innerHTML;
          var status_indicator = document.getElementById("statusIndicator");
          status_indicator.innerHTML = parsedHTML.getElementById("statusIndicator").innerHTML;
            
          // Restore the accordion state based on the response
          var updatedAccordionItems = document.querySelectorAll("#myAccordion .accordion-item");
          updatedAccordionItems.forEach(function(updatedItem, index) {
            var isOpen = accordionState[index];
            if (isOpen) {
              updatedItem.querySelector(".accordion-collapse").classList.add("show");
              updatedItem.querySelector(".accordion-button").classList.remove("collapsed");
            } else {
              updatedItem.querySelector(".accordion-collapse").classList.remove("show");
              updatedItem.querySelector(".accordion-button").classList.add("collapsed");
            }
          });
        } else {
          console.error("Error retrieving profile data");
        }
      }
    };
    xhr.send();
  }

  // Starte die Aktualisierung alle 3 Sekunden
  setInterval(reloadView, 3000);