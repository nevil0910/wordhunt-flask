document.addEventListener("DOMContentLoaded", function() {
    const modeButtons = document.querySelectorAll(".mode-button");
    
    // Handle mode selection
    modeButtons.forEach(button => {
        button.addEventListener("click", function() {
            const selectedMode = this.dataset.mode;
            localStorage.setItem("gameMode", selectedMode);
            window.location.href = "game.html";
        });
    });

    // Fetch grid data when on game page
    if (window.location.pathname.includes("game.html")) {
        const mode = localStorage.getItem("gameMode");
        fetch(`/get_grid?mode=${mode}`)
            .then(response => response.json())
            .then(data => {
                renderGrid(data.grid);
                renderWords(data.words);
            })
            .catch(error => console.error("Error loading game data:", error));
    }
});

function renderGrid(grid) {
    const gridContainer = document.getElementById("grid");
    gridContainer.innerHTML = "";
    grid.forEach(row => {
        const rowDiv = document.createElement("div");
        rowDiv.classList.add("grid-row");
        row.forEach(letter => {
            const cell = document.createElement("div");
            cell.classList.add("grid-cell");
            cell.textContent = letter;
            rowDiv.appendChild(cell);
        });
        gridContainer.appendChild(rowDiv);
    });
}

function renderWords(words) {
    const wordsContainer = document.getElementById("word-list");
    wordsContainer.innerHTML = "";
    words.forEach(word => {
        const wordItem = document.createElement("div");
        wordItem.classList.add("word-item");
        wordItem.textContent = word;
        wordsContainer.appendChild(wordItem);
    });
}
