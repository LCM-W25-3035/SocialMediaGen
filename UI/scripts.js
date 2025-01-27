// Function to populate the social media post generator with news content
function generatePost(newsContent) {
    const newsInput = document.getElementById('newsInput');
    newsInput.value = newsContent;
}

// Handle the generation of the social media post when button is clicked
document.getElementById('generatePostBtn').addEventListener('click', function() {
    const newsInput = document.getElementById('newsInput').value;
    const generatedPost = document.getElementById('generatedPost');
    
    if(newsInput.trim() === "") {
        generatedPost.innerHTML = "<p>Please select a news article to generate a post.</p>";
    } else {
        generatedPost.innerHTML = `<h3>Generated Social Media Post:</h3><p>${newsInput}</p>`;
    }
});
