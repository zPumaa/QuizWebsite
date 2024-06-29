function adjustFontSize() {
    var div = document.querySelector('.price-tag');
    var divs = document.querySelectorAll('.price-tag'); 
    var height = div.offsetHeight; 
    var fontSize = height * 0.6; 
    divs.forEach(function(div) {
        div.style.fontSize = fontSize + 'px'; // Set the font size 
    });
}
  
function adjustCoinSize() {
    var div = document.querySelector('.price-tag'); 
    var height = div.offsetHeight;
    var coinSize = height * 0.7;
    var coins = document.querySelectorAll('.price-coin');

    coins.forEach(function(coin) {
      coin.style.height = coinSize + 'px';
      coin.style.width = coinSize + 'px';
    });
}

// Run the function when the window resizes and on page load
window.addEventListener('resize', adjustFontSize);
window.addEventListener('resize', adjustCoinSize);
window.addEventListener('load', adjustFontSize);
window.addEventListener('load', adjustCoinSize);

document.addEventListener('DOMContentLoaded', function() {
    // Find all buy-reward buttons and attach the buyReward function with the correct ID
    var buyButtons = document.querySelectorAll('.buy-reward-btn');
    buyButtons.forEach(function(button, index) {
        button.addEventListener('click', function() {
            buyReward(index + 1);
        });
    });
});
  
function buyReward(rewardId) {
    fetch('/buy_reward', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rewardId: rewardId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('coin-count').textContent = data.newCoinBalance;
            showMessage('Reward successfully purchased!');
        } else {
            showMessage('Could not complete purchase: ' + data.message, true);
        }
    })
    .catch(error => {
        console.error('Error purchasing reward:', error);
        showMessage('An error occurred during the purchase.', true);
    });
}

function showMessage(message, isError) {
    var messageBox = document.getElementById('message-box');
    messageBox.textContent = message;
    messageBox.style.display = 'block';
    messageBox.style.color = isError ? 'red' : 'green';
    // Hide the message box after 5 seconds
    setTimeout(function() {
        messageBox.style.display = 'none';
    }, 5000);
}
  



