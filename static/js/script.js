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
  