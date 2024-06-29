document.addEventListener('DOMContentLoaded', function() {
    // Function to update the table with the quizzes
    function updateQuizzesTable(quizzes) {
        const tableBody = document.querySelector('.leaderboard tbody');
        tableBody.innerHTML = ''; // Clear the current table contents

        quizzes.forEach(quiz => {
            const editUrl = `/create_quiz/${quiz.unique_id}`;
            console.log(editUrl)
            const row = `<tr>
                <td class="table-qtitle">${quiz.title}</td>
                <td class="table-qdesc">${quiz.description}</td>
                <td>${quiz.num_questions}</td>
                <td><a href="${editUrl}" class="edit-question-button">Edit</a></td>
            </tr>`;
            tableBody.innerHTML += row;
        });
    }

    // Function to fetch quizzes from the server
    function fetchQuizzes() {
        fetch('/get-my-quizzes') 
            .then(response => response.json())
            .then(data => {
                updateQuizzesTable(data.quizzes);
            })
            .catch(error => console.error('Error fetching quizzes:', error));
    }

    fetchQuizzes();
});
