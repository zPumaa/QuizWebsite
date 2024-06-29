var modal = document.getElementById('quizModal');
var btn = document.getElementById('playButton');
var span = document.getElementsByClassName('start-modal-close')[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
    modal.style.display = 'block';
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = 'none';
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

document.getElementById('leaderboardButton').addEventListener('click', function() {
    window.location.href = '/leaderboards';
});

document.getElementById('createQuizButton').addEventListener('click', function() {
    window.location.href = '/create_quiz';
});

document.getElementById('playRandomButton').addEventListener('click', function() {
    window.location.href = '/quiz';
});

document.getElementById('playQuizButton').addEventListener('click', function() {
    const uniqueID = document.getElementById('uniqueID').value;
    
    fetch(`/quiz/${uniqueID}`, {
        method: 'POST',
        body: new URLSearchParams({
            'unique_id': uniqueID
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Quiz not found');
        }
        return response.text();
    })
    .then(html => {
        document.open();
        document.write(html);
        document.close();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Quiz not found');
    });
});

document.addEventListener('DOMContentLoaded', function() {

    // Function to update the modal with the quizzes
    function updateQuizzesModal(quizzes) {
        const quizListBody = document.querySelector('.quiz-list-body');
        quizListBody.innerHTML = ''; // Clear existing rows
    
        quizzes.forEach(quiz => {
            const quizRow = document.createElement('div');
            quizRow.classList.add('quiz-list-row');
    
            quizRow.innerHTML = `
                <div class="row-item">${quiz.unique_id}</div>
                <div class="row-item">${quiz.title}</div>
                <div class="row-item">${Number(quiz.average_rating).toFixed(2)} <span class="star">&#9733;</span></div>
            `;
            quizListBody.appendChild(quizRow);
        });
    }
    

    // Function to fetch quizzes from the server
    function fetchQuizzes() {
        fetch('/get-quizzes') // Replace with the actual endpoint
            .then(response => response.json())
            .then(data => {
                updateQuizzesModal(data.quizzes);
            })
            .catch(error => console.error('Error fetching quizzes:', error));
    }

    // Call the function to fetch quizzes when the page loads
    fetchQuizzes();
});
