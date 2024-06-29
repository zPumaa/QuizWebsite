let chart;

function fetchLastThreeScores(userId, quizId) {
    const url = `/get-last-three-scores?user_id=${userId}&quiz_id=${quizId}`;

    fetch(url)
        .then(response => response.json())
        .then(scores => {
            if(scores.length) {
                createScoreChart(scores);
            } else {
                // Handle case where no scores exist
                console.error('No scores found');
            }
        })
        .catch(error => {
            console.error('Error fetching scores:', error);
        });
}



function createScoreChart(scores) {
    if (chart) {
        chart.destroy();
    }

    const ctx = document.getElementById('scoreChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Attempt 1', 'Attempt 2', 'Attempt 3'],
            datasets: [{
                label: 'Scores',
                data: scores,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(75, 192, 192, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: false,
            // maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

const searchButton = document.getElementById('searchBtn');
searchButton.addEventListener('click', () => {
    const userId = document.getElementById('username').textContent; 
    const quizId = document.getElementById('gamePin').value.toLowerCase();

    console.log(userId, quizId);

    fetchLastThreeScores(userId, quizId);
});

// When the user clicks on the button, toggle between hiding and showing the dropdown content
document.querySelector('.dropbtn').addEventListener('click', function(event) {
    document.querySelector('.dropdown-content').classList.toggle('show');
    event.stopPropagation(); // This stops the click from propagating to the document
});

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.dropdown-content a').forEach(function(item) {
        item.addEventListener('click', function() {
            var selectedRewardId = this.getAttribute('data-reward-id'); 
            var selectedRewardTitle = this.textContent;
            
            document.getElementById("selected-reward-label").textContent = selectedRewardTitle; // Update button text
            
            // Send the selected reward ID to the server
            fetch('/select_reward', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ rewardId: selectedRewardId })
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    console.log('Reward selected successfully');

                    if(data.rewardUrl !== null) {
                        const img = document.querySelector('.centered-image');
                        img.style.display = "block"
                        document.querySelector('.centered-image').src = data.rewardUrl;
                    } else {
                        // const img = document.querySelector('.centered-image');
                        // if (img) img.remove();

                        const img = document.querySelector('.centered-image');
                        if (img) img.style.display = 'none';
                    }
                } else {
                    console.log('Reward selection failed');
                }
            })
            .catch(error => {
                console.error('Error selecting reward:', error);
            });
        });
    });
});

function updateCountry() {
    var country_code = document.getElementById('country').value;
    var flagImage = document.getElementById('country-flag');

    fetch('/update-country', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ country_code: country_code }),
    })
    .then(response => response.json())
    .then(data => {
        console.log(country_code)
        if (country_code.length != 2) {
            flagImage.style.display = 'none';
        } else {
            flagImage.src = '/static/images/flags/' + country_code + '.png';
            flagImage.style = 'block';
        }
    })
    .catch(error => console.error('Error:', error));
}



// Event listener to close the dropdown if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName('dropdown-content');
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
};