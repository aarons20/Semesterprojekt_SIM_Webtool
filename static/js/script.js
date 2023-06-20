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

  // AJAX request to retrieve updated profiles from the server
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/get-updated-profiles", true);   
  xhr.onreadystatechange = function() {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        // Create an array to store the state of each accordion item
        var accordionState = [];
        // Iterate over each accordion item
        accordionItems.forEach(function(item) {
          var isOpen = item.querySelector(".accordion-collapse").classList.contains("show");
          accordionState.push(isOpen);
        });
        
        // Parse the response HTML
        var parser = new DOMParser();        
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

        // disable buttons if no SIM detected
        var isSIMConnected = document.getElementById("statusIndicator")
                  .querySelector(".circle").classList.contains("green") ? true : false;
        if (isSIMConnected) {
          enableUI()
        } else {
          disableUI()
        }
      } else {
        console.error("Error retrieving profile data");
      }
    }
  };
  xhr.send();
}

// Disable UI elements
function disableUI() {
  $(".update-profile-button").prop("disabled", true);
  // Add additional code to disable other UI elements if needed
}

// Enable UI elements
function enableUI() {
  $(".update-profile-button").prop("disabled", false);
  // Add additional code to enable other UI elements if needed
}

// Function to show the loading overlay
function showLoadingOverlay() {
  document.getElementById("loading-overlay").style.display = "flex";
}

// Function to hide the loading overlay
function hideLoadingOverlay() {
  document.getElementById("loading-overlay").style.display = "none";
}

// Function to show the loading overlay
function showErrorOverlay() {
  document.getElementById("error-overlay").style.display = "flex";
}

// Function to hide the loading overlay
function hideErrorOverlay() {
  document.getElementById("error-overlay").style.display = "none";
}

function submitForm() {
  showLoadingOverlay();
  // Get the form data
  var formData = $('#simProfileForm').serialize();  
  // Send an AJAX request to the backend
  $.ajax({
    url: '/create-sim-profile',
    method: 'POST',
    data: formData,
    success: function(response) {  
      document.getElementById('simProfileForm').reset() 
      console.log(response)
      hideLoadingOverlay()
    },
    error: function(xhr, status, error) {        
      console.error(error);
      hideLoadingOverlay()     
    }
  });
}


$(document).ready(function() {
  hideLoadingOverlay();
  // Add click event listener to a parent element containing profile buttons
  $("main").on("click", "button.update-profile-button", function() {
    disableUI();
    showLoadingOverlay();

    // Get the imsi data attribute of the clicked button
    var imsi = $(this).data("imsi");
    
    // Send the imsi to the backend using AJAX
    $.ajax({
      type: "POST",
      url: "/write-sim-profile",
      data: { 
        imsi: imsi 
      },
      success: function(response) {
        // Handle the response from the backend
        reloadView();

        enableUI();
        setTimeout(function() {         
          hideLoadingOverlay();
        }, 2000);
        console.log(response);
      },
      error: function(xhr, status, error) {
        // Handle any errors that occur during the AJAX request
        enableUI();
        hideLoadingOverlay();
        console.log("Error: " + xhr.responseJSON.message);
      }
    });
  });
});

// Prevent browser error logging
window.onerror = function(message, source, lineno, colno, error) {
  return true;
};

// Starte die Aktualisierung alle 3 Sekunden
setInterval(reloadView, 3000);