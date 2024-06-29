document.getElementById('searchButton').addEventListener('click', function() {
    let quizId = document.getElementById('quiz-id').value;
    quizId = quizId.toLowerCase();
  
    if (quizId) {
        fetch('/leaderboards', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quizId: quizId })
        })
        .then(response => response.json())
        .then(data => {
            // console.log(response);
            // Clear existing rows in the leaderboard table
            const tableBody = document.querySelector(".leaderboard tbody");
            tableBody.innerHTML = '';
    
            // Populate table with new rows based on data
            data.forEach((entry, index) => {
                const row = tableBody.insertRow();
                const rankCell = row.insertCell(0);
                const countryCell = row.insertCell(1);
                const userCell = row.insertCell(2);
                const scoreCell = row.insertCell(3);
        
                rankCell.textContent = index + 1;
                userCell.textContent = entry.username;
                scoreCell.textContent = entry.score;
        
                // If there is a reward image URL, create an image element and append it to the userCell
                if (entry.rewardImageUrl) {
                    const image = document.createElement('img');
                    image.src = '/static/' + entry.rewardImageUrl;
                    image.alt = 'Reward';
                    image.className = 'reward-icon'; 
                    userCell.appendChild(image);
                }
                if (entry.country_code) { 
                    const flagImage = document.createElement('img');
                    flagImage.src = `/static/images/flags/${entry.country_code}.png`; 
                    flagImage.alt = `${entry.country} Flag`; 
                    flagImage.className = 'flag-icon'; 
                    countryCell.appendChild(flagImage);
                } else {
                    countryCell.textContent = ""; // Fallback to text if no countryCode
                }
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else {
        alert('Please enter a Quiz ID.');
    }
});
  


