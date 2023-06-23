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

function validateProfileForm() {
  var isValid = true;

  // Perform validation checks for each field
  var nameInput = document.getElementById('nameInput');
  var imsiInput = document.getElementById('imsiInput');
  var kiInput = document.getElementById('kiInput');
  var opcInput = document.getElementById('opcInput');

  var submitErrorVisible = (document.getElementById('submitError').textContent.trim() !== '');

  // Validation checks for 'name' field
  var nameErrorElement = document.getElementById('nameError');
  if (nameInput.value.trim() === '' && submitErrorVisible) {
    nameErrorElement.textContent = 'Name cannot be empty';
    isValid = false;
  } else {
    nameErrorElement.textContent = '';
    if(nameInput.value.trim() === '') {
      isValid = false;
    }
  }

  // Validation checks for 'imsi' field
  var imsiErrorElement = document.getElementById('imsiError');
  if (!/^\d{15}$/.test(imsiInput.value) && (imsiInput.value.trim() !== '' || submitErrorVisible)) {
    imsiErrorElement.textContent = 'IMSI must be exactly 15 digits';
    isValid = false;
  } else {
    imsiErrorElement.textContent = '';
    if(imsiInput.value.trim() === '') {
      isValid = false;
    }
  }

  // Validation checks for 'ki' field
  var kiErrorElement = document.getElementById('kiError');
  if (!/^[0-9a-fA-F]{32}$/.test(kiInput.value) && (kiInput.value.trim() !== '' || submitErrorVisible)) {
    kiErrorElement.textContent = 'KI must be 128 bits in hexadecimal format';
    isValid = false;
  } else {
    kiErrorElement.textContent = '';
    if(kiInput.value.trim() === '') {
      isValid = false;
    }
  }

  // Validation checks for 'opc' field
  var opcErrorElement = document.getElementById('opcError');
  if (!/^[0-9a-fA-F]{32}$/.test(opcInput.value) && (opcInput.value.trim() !== '' || submitErrorVisible)) {
    opcErrorElement.textContent = 'OPC must be 128 bits in hexadecimal format';
    isValid = false;
  } else {
    opcErrorElement.textContent = '';
    if(opcInput.value.trim() === '') {
      isValid = false;
    }    
  }

  return isValid;
}

function submitProfileForm() {
  showLoadingOverlay();

  var form = document.getElementById('simProfileForm');
  var isValid = validateProfileForm();
  var submitErrorElement = document.getElementById('submitError');

  if (isValid) {
    var formData = $(form).serialize();
    submitErrorElement.textContent = '';

    $.ajax({
      url: '/create-sim-profile',
      method: 'POST',
      data: formData,
      success: function(response) {
        setTimeout(function() {         
          resetProfileForm();
        }, 1000);
        console.log(response);
      },
      error: function(xhr, status, error) {
        console.error(error);
        submitErrorElement.textContent = 'Please check your input values';
        hideLoadingOverlay();
      }
    });
  } else {
    hideLoadingOverlay();
    // Display an error message
    submitErrorElement.textContent = 'Please check your input values';
    validateProfileForm(); 
    console.log('Profile form contains invalid values');
  }
}

function resetProfileForm() {
  showLoadingOverlay();

  document.getElementById('simProfileForm').reset();
  document.getElementById('nameError').textContent = '';
  document.getElementById('imsiError').textContent = '';
  document.getElementById('kiError').textContent = '';
  document.getElementById('opcError').textContent = '';
  document.getElementById('submitError').textContent = '';

  var myModal = document.getElementById('myModal');
  var modal = bootstrap.Modal.getInstance(myModal);
  modal.hide();

  hideLoadingOverlay();
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
        console.log(xhr.responseJSON.message);
      }
    });
  });
});


// Starte die Aktualisierung alle 3 Sekunden
setInterval(reloadView, 3000);