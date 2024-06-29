document.addEventListener('DOMContentLoaded', function() {

    // This function will be called when the page loads
    function fetchAndUpdateUserCoins() {
        fetch('/get-user-coins') 
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('coin-count').textContent = data.coins;
            })
            .catch(error => {
                console.error('Could not fetch coins:', error);
            });
    }

    fetchAndUpdateUserCoins();
});