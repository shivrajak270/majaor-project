document.getElementById('addBtn').addEventListener('click', function() {
    // Get input values
    const sentence = document.getElementById('sentence').value;
    const meaning = document.getElementById('meaning').value;

    // Validate input
    if (sentence.trim() === '' || meaning.trim() === '') {
        alert('Both fields are required!');
        return;
    }

    // Create new list item
    const listItem = document.createElement('li');

    // Create sentence and meaning elements
    const sentenceElement = document.createElement('span');
    sentenceElement.classList.add('sentence');
    sentenceElement.textContent = sentence;

    const meaningElement = document.createElement('span');
    meaningElement.classList.add('meaning');
    meaningElement.textContent = meaning;

    // Append sentence and meaning to list item
    listItem.appendChild(sentenceElement);
    listItem.appendChild(meaningElement);

    // Append the list item to the conversation list
    document.getElementById('conversation-list').appendChild(listItem);

    // Clear input fields
    document.getElementById('sentence').value = '';
    document.getElementById('meaning').value = '';
});
