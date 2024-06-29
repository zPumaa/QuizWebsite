let currentQuestionIndex = 0;
let timebarInterval;
let startTime;
let score = 0;
let answerClicked = false
let questionHistory = [];
let isAnswerBeingProcessed = false;
let coins = 5
const timeLimit = 20; // 20 seconds for each question
const timebar = document.querySelector(".timebar");

function resetTileStyles() {
    document.querySelectorAll(".corner-tile").forEach(tile => {
        tile.classList.remove("flash-green", "flash-red");
        tile.classList.remove("correct", "incorrect");
        tile.disabled = false; 
        tile.style.opacity = '1';
    });
}

function startTimer() {
    let timeLeft = timeLimit + 1;
    startTime = Date.now();

    // Reset the timebar instantly without transition
    timebar.style.transition = 'none'; 
    timebar.style.width = '100%';
    timebar.style.backgroundColor = "green";

    // Allow a short break for the style changes to take effect
    setTimeout(() => {
        // Re-enable the transitions for countdown
        timebar.style.transition = 'width 950ms linear, background-color 1s linear';
    }, 50); // Small timeout to ensure the width reset happens without transition

    if (timebarInterval) clearInterval(timebarInterval);

    timebarInterval = setInterval(function () {

        if (timeLeft <= 0) {
            console.log("Time has finished.")
            clearInterval(timebarInterval);
            setTimeout(tryGoToNextQuestion, 50);
        }

        timeLeft -= 1;
        let widthPercentage = (timeLeft / timeLimit) * 100;
        timebar.style.width = widthPercentage + '%';
        timebar.style.backgroundColor = `hsl(${120 * (widthPercentage / 100)}, 100%, 50%)`;

    }, 950);
}



function showQuestion(question, answers) {
    resetTileStyles();
    answerClicked = false;
    // console.log(window.quizData[currentQuestionIndex]);
    
    
    let correctIndex = window.quizData[currentQuestionIndex].correct_index;
    // console.log("correct index", correctIndex);
    if (correctIndex === 0, 1, 2, 3) {
        correct_answer = window.quizData[currentQuestionIndex].answers[correctIndex];
        // console.log("there is a correct index.", correct_answer);
    } else {
        correct_answer = window.quizData[currentQuestionIndex].correct_answer;
        // console.log("no index.", correct_answer);
    }
    

    correct_answer = String(correct_answer).trim();

    questionHistory[currentQuestionIndex] = {
        question: question,
        selectedAnswer: "Unanswered",
        correctAnswer: correct_answer,
        points: 0
    };

    const questionElement = document.querySelector(".quiz-question label");
    const answerElements = document.querySelectorAll(".corner-tile");

    // Display the question number and the question
    questionElement.innerHTML = "Question " + (currentQuestionIndex + 1) + ": " + question;

    for (let i = 0; i < answerElements.length; i++) {
        answers[i] = answers[i].trim()
        answerElements[i].innerHTML = answers[i]
        answerElements[i].onclick = () => {
            handleAnswerClick(answerElements[i]);
        };
    }
    adjustFontSizeForAnswerTiles();
    setTimeout(startTimer, 500); // Correctly set the timer to start
}

function tryGoToNextQuestion() {
    console.log("Trying to go to next question");
    if (answerClicked) {
        console.log("Answer already clicked, returning early");
        setTimeout(goToNextQuestion, 800);
        return;
    }

    console.log("Time has finished, going to next question.")
    answerClicked = true;
    clearInterval(timebarInterval);

    setTimeout(goToNextQuestion, 100);
}

function goToNextQuestion() {
    currentQuestionIndex++;

    if (currentQuestionIndex < window.quizData.length) {
        const nextQuestion = window.quizData[currentQuestionIndex];
        showQuestion(nextQuestion.question, nextQuestion.answers);
    } else {
        alert("Quiz finished!");
    }

    if (currentQuestionIndex >= window.quizData.length) {
        showResults(); // Show results at the end of the quiz
    }
}


function handleAnswerClick(clickedAnswer) {
    if (isAnswerBeingProcessed) {
        // Ignore additional clicks if an answer is already being processed
        return;
    }
    isAnswerBeingProcessed = true;

    console.log("Answer clicked");
    answerClicked = true;
    clearInterval(timebarInterval);

    const elapsedTime = (Date.now() - startTime) / 1000; // Corrected time calculation
    const timeScore = Math.max(1000 - Math.floor(elapsedTime / timeLimit * 1000), 300);
    let points = clickedAnswer.innerText === window.quizData[currentQuestionIndex].answers[window.quizData[currentQuestionIndex].correct_index] ? Math.round(timeScore) : 0;

    
    let correctIndex = window.quizData[currentQuestionIndex].correct_index;
    if (correctIndex === 0, 1, 2, 3) {
        correct_answer = window.quizData[currentQuestionIndex].answers[correctIndex];
    } else {
        correct_answer = window.quizData[currentQuestionIndex].correct_answer;
    }

    // console.log(correct_answer);

    correct_answer = String(correct_answer).trim();



    questionHistory[currentQuestionIndex].selectedAnswer = clickedAnswer.innerText;
    questionHistory[currentQuestionIndex].points = points;

    if (clickedAnswer.innerText.toLowerCase() === correct_answer.toLowerCase()) {
        clickedAnswer.classList.add("flash-green", "correct");
        clickedAnswer.innerText = ''; // Clear text to show only the tick
        score += points;
        coins += 10;
    } else {
        clickedAnswer.classList.add("flash-red", "incorrect");
        clickedAnswer.innerText = ''; 
        coins += 1;
    }
      
    updateScoreDisplay();
    tryGoToNextQuestion();

    setTimeout(() => {
        isAnswerBeingProcessed = false;
    }, 1200);
}


function showResults() {
    const modal = document.getElementById("quizResultModal");
    const finalScoreElement = document.getElementById("finalScore");
    const questionCirclesElement = document.getElementById("questionCircles");
    const questionDetailsElement = document.getElementById("questionDetails");

    finalScoreElement.innerText = `Final Score: ${score}`;
    questionCirclesElement.innerHTML = ""; // Clear previous circles

    questionHistory.forEach((item, index) => {
        const circle = document.createElement("span");
        circle.innerText = index + 1;
        circle.classList.add("question-circle");

        // Determine if the answer was correct and add appropriate class
        if (item.selectedAnswer === item.correctAnswer) {
            circle.classList.add("correct"); // Add 'correct' class for right answers
        } else {
            circle.classList.add("incorrect"); // Add 'incorrect' class for wrong answers
        }

        circle.onclick = () => showQuestionDetails(index);
        questionCirclesElement.appendChild(circle);
    });

    sendQuizResults();
    sendCoins();

    modal.style.display = "block";
}

function sendQuizResults() {
    quiz_id = document.getElementById("quiz-id-label").textContent;
    console.log(quiz_id)

    const data = {
        score: score,
        quiz_id: quiz_id 
    };

    fetch('/submit_quiz', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(response => {
        if (response.ok) {
            console.log("Score submitted successfully.");
        } else {
            console.error("Failed to submit score.");
        }
    }).catch(error => console.error('Error:', error));
}

function sendCoins() {
    const data = {
        coins: coins
    }

    fetch('/add_coins', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(response => {
        if (response.ok) {
            console.log("Coins added successfully.");
        } else {
            console.error("Failed to add coins.");
        }
    }).catch(error => console.error('Error:', error));
}

function showQuestionDetails(questionIndex) {
    const questionDetails = questionHistory[questionIndex];
    const questionDetailsElement = document.getElementById("questionDetails");

    // Populate and show details of the selected question
    questionDetailsElement.innerHTML = `
        <p class="details-question">Question ${questionIndex + 1}: ${questionDetails.question}</p>
        <p class="details-answer">Your Answer: <span class="highlight">${questionDetails.selectedAnswer}</span></p>
        <p class="details-correct">Correct Answer: <span class="highlight-answer">${questionDetails.correctAnswer}</span></p>
        <p class="details-score">Points Scored: <span class="highlight-score">${questionDetails.points}</span></p>`;
}


function updateScoreDisplay() {
    const scoreElement = document.getElementById("score"); 
    scoreElement.innerText = `Score: ${score}`;
}

document.querySelector(".close-button").onclick = function () {
    document.getElementById("quizResultModal").style.display = "none";
};

document.getElementById('fifty-fifty-btn').addEventListener('click', useFiftyFifty);

function useFiftyFifty() {
    // Check if the 50/50 option was already used for this quiz session
    if (window.usedFiftyFifty) {
        alert("You've already used the 50/50 option for this quiz.");
        return;
    }

    fetch('/use_fifty_fifty', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // User had a 50/50 and used it successfully
            document.getElementById('fifty-fifty-btn').disabled = true;
            window.usedFiftyFifty = true; // Ensure it can't be used again in this quiz
            disableTwoIncorrectAnswers(); 
            console.log(data.message); 
        } else {
            // User did not have any 50/50 rewards left
            alert(data.message); // Alert the user
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function disableTwoIncorrectAnswers() {
    let incorrectIndexes = [];
    const answers = window.quizData[currentQuestionIndex].answers;
    const correctIndex = window.quizData[currentQuestionIndex].correct_index;

    // Find two random incorrect answers
    while (incorrectIndexes.length < 2) {
        let randomIndex = Math.floor(Math.random() * answers.length);
        if (randomIndex !== correctIndex && !incorrectIndexes.includes(randomIndex)) {
            incorrectIndexes.push(randomIndex);
        }
    }

    // Disable the buttons for the two incorrect answers
    document.querySelectorAll('.corner-tile').forEach((tile, index) => {
        if (incorrectIndexes.includes(index)) {
            tile.disabled = true; 
            tile.style.opacity = '0.5';
        }
    });
}

document.addEventListener('DOMContentLoaded', (event) => {
    const stars = document.querySelectorAll('.star');

    function updateStars(ratingValue) {
        stars.forEach((star) => {
            const starValue = parseInt(star.getAttribute('data-value'), 10);
            if (starValue <= ratingValue) {
                star.classList.add('selected');
            } else {
                star.classList.remove('selected');
            }
        });
    }

    stars.forEach((star) => {
        star.addEventListener('click', () => {
            const ratingValue = parseInt(star.getAttribute('data-value'), 10);
            updateStars(ratingValue);
        });
    });
});

document.getElementById('submitRating').addEventListener('click', () => {
    const selectedRating = document.querySelectorAll('.star.selected').length;
    const quiz_id = document.getElementById("quiz-id-label").textContent;

    const data = {
        rating: selectedRating,
        quiz_id: quiz_id // This will be either 1 for random or the unique quiz ID
    };

    console.log(selectedRating, quiz_id)
    if (selectedRating > 0) {
        fetch('/submit_rating', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            // Handle any follow-up after receiving a response from the server
            console.log('Rating submitted successfully:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    } else {
        alert('Please select a rating before submitting.');
    }
});

// This function adjusts the font size of the answer text based on its length
function adjustFontSizeForAnswerTiles() {
    const tiles = document.querySelectorAll('.corner-tile');
    
    tiles.forEach(tile => {
        let fontSize = 32; 
        const maxCharLength = 20; // Define the max number of characters for the base font size
    
        if (tile.textContent.length > maxCharLength) {
            fontSize -= (tile.textContent.length - maxCharLength) / 10; // Reduce font size based on character count
            fontSize = Math.max(fontSize, 10); // Set a minimum font size
        }
    
        tile.style.fontSize = `${fontSize}px`; // Apply the new font size
    });
}

function useReplacement() {

    if (window.usedReplacement) {
        alert("You've already used the Replacement option for this quiz.");
        return;
    }
    // console.log(window.replacement);

    fetch('/use_replacement', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.success) {
            // User had a Replacement and used it successfully
            document.getElementById('replace-question-btn').disabled = true;
            window.usedReplacement = true; // Ensure it can't be used again in this quiz
            replaceCurrentQuestion();
            console.log(data.message); 
        } else {
            alert(data.message); // Alert the user
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
  
function replaceCurrentQuestion() {
    // Check if a replacement question exists
    if (!window.replacement) {
        console.error("No replacement question available or index mismatch");
        return;
    }

    // Replace the content of the current question with the replacement question
    const replacementQuestion = window.replacement;
    window.quizData[currentQuestionIndex] = replacementQuestion;

    // Re-show the question without incrementing the question index
    showQuestion(replacementQuestion.question, replacementQuestion.answers);
}

document.addEventListener('DOMContentLoaded', function() {
    if (window.replacement && Object.keys(window.replacement).length > 0) {
        // If replacement is not empty, add the click event listener to the button
        document.getElementById('replace-question-btn').addEventListener('click', useReplacement);
    } else {
        // If replacement is empty, disable the button
        const replaceBtn = document.getElementById('replace-question-btn');
        replaceBtn.disabled = true;
        replaceBtn.style.opacity = '0.5';
        replaceBtn.style.cursor = 'not-allowed';
    }
});

// Start the quiz when the page loads
updateScoreDisplay();
window.onload = () => {
    window.usedFiftyFifty = false;
    window.usedReplacement = false;
    console.log(Object.keys(window.replacement).length);
    if (window.quizData && window.quizData.length > 0) {
        const firstQuestion = window.quizData[currentQuestionIndex];
        showQuestion(firstQuestion.question, firstQuestion.answers);
    } else {
        console.error("No quiz data available");
    }
};


