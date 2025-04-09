let startCell = null;
let isDragging = false;
let svgLine = null;
let selectedCells = [];
let foundWords = new Set();
let foundLines = []; 
let currentSelectionWord = '';
let gameMode = document.querySelector("h1.title")?.textContent.toLowerCase().includes("easy") ? "easy" : 
               document.querySelector("h1.title")?.textContent.toLowerCase().includes("normal") ? "normal" : "hard";
let score = 0;
console.log(`Initial score set to: ${score}`);

let timeLeft;

// Set initial time based on game difficulty
function setInitialTime() {
    if (gameMode === "easy") {
        timeLeft = 30;
    } else if (gameMode === "normal") {
        timeLeft = 120;
    } else if (gameMode === "hard") {
        timeLeft = 240;
    } else {
        timeLeft = 60;
    }
    const timerElement = document.getElementById("timer");
    if (timerElement) {
        timerElement.textContent = timeLeft;
    } 
}

let timerInterval;

const allowedDirections = [
    {dx: 1, dy: 0},   
    {dx: -1, dy: 0},  
    {dx: 0, dy: 1},   
    {dx: 0, dy: -1},  
    {dx: 1, dy: 1},   
    {dx: -1, dy: -1}, 
    {dx: -1, dy: 1},  
    {dx: 1, dy: -1}   
];

// Check if selection is valid
function isValidSelection(start, end) {
    let startX = parseInt(start.dataset.x);
    let startY = parseInt(start.dataset.y);
    let endX = parseInt(end.dataset.x);
    let endY = parseInt(end.dataset.y);
   
    if (startX === endX && startY === endY) return false;
   
    let dx = Math.sign(endX - startX);
    let dy = Math.sign(endY - startY);
   
    return allowedDirections.some(dir => dir.dx === dx && dir.dy === dy);
}

// Get selected word from cells
function getSelectedWordFromCells(cells) {
    return cells.map(cell => cell.dataset.letter).join('');
}

// Calculate cells between start and end (inclusive)
function getCellsBetween(start, end) {
    const cells = [];
    const startX = parseInt(start.dataset.x);
    const startY = parseInt(start.dataset.y);
    const endX = parseInt(end.dataset.x);
    const endY = parseInt(end.dataset.y);

    const dx = Math.sign(endX - startX);
    const dy = Math.sign(endY - startY);
    const steps = Math.max(Math.abs(endX - startX), Math.abs(endY - startY));

    let currentX = startX;
    let currentY = startY;

    for (let i = 0; i <= steps; i++) {
        const cell = document.querySelector(`td[data-x="${currentX}"][data-y="${currentY}"]`);
        if (cell) {
            cells.push(cell);
        }
        currentX += dx;
        currentY += dy;
    }
    return cells;
}

// Create a permanent line for found words
function createPermanentLine(startCell, endCell) {
    let svgRect = document.getElementById("svgContainer").getBoundingClientRect();
    let startRect = startCell.getBoundingClientRect();
    let endRect = endCell.getBoundingClientRect();
    
    let permanentLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
    permanentLine.setAttribute("stroke", "green");
    permanentLine.setAttribute("stroke-width", "4");
    permanentLine.setAttribute("stroke-linecap", "round");
    permanentLine.setAttribute("x1", startRect.left + startRect.width/2 - svgRect.left);
    permanentLine.setAttribute("y1", startRect.top + startRect.height/2 - svgRect.top);
    permanentLine.setAttribute("x2", endRect.left + endRect.width/2 - svgRect.left);
    permanentLine.setAttribute("y2", endRect.top + endRect.height/2 - svgRect.top);
    permanentLine.setAttribute("class", "word-line permanent");
    
    document.getElementById("svgContainer").appendChild(permanentLine);
    foundLines.push(permanentLine);
}

// Handle Mouse Down on the grid container
function handleGridMouseDown(event) {
    const targetCell = event.target.closest('td');
    if (!targetCell || (typeof window.validWords !== 'undefined' && foundWords.size === window.validWords.size)) return;

    event.preventDefault();
    startCell = targetCell;
    isDragging = true;
    selectedCells = [startCell];
    currentSelectionWord = startCell.dataset.letter;

    if (svgLine) svgLine.remove();
    svgLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
    svgLine.setAttribute("stroke", "blue");
    svgLine.setAttribute("stroke-width", "4");
    svgLine.setAttribute("stroke-linecap", "round");
    svgLine.setAttribute("class", "word-line temporary");
    document.getElementById("svgContainer").appendChild(svgLine);

    let rect = startCell.getBoundingClientRect();
    let svgRect = document.getElementById("svgContainer").getBoundingClientRect();
    svgLine.setAttribute("x1", rect.left + rect.width / 2 - svgRect.left);
    svgLine.setAttribute("y1", rect.top + rect.height / 2 - svgRect.top);
    svgLine.setAttribute("x2", rect.left + rect.width / 2 - svgRect.left);
    svgLine.setAttribute("y2", rect.top + rect.height / 2 - svgRect.top);
}

// Handle Mouse Move globally
function handleDocumentMouseMove(event) {
    if (!isDragging || !startCell) return;

    const svgRect = document.getElementById("svgContainer").getBoundingClientRect();
    
    svgLine.setAttribute("x2", event.clientX - svgRect.left);
    svgLine.setAttribute("y2", event.clientY - svgRect.top);

    const currentCell = document.elementFromPoint(event.clientX, event.clientY)?.closest('td');
    
    if (currentCell && currentCell !== selectedCells[selectedCells.length - 1]) {
        if (isValidSelection(startCell, currentCell)) {
             const cellsBetween = getCellsBetween(startCell, currentCell);
             selectedCells = cellsBetween;
        } else {
             selectedCells = [startCell];
        }
    }
}

// Handle Mouse Up globally
function handleDocumentMouseUp(event) {
    if (!isDragging || !startCell) return;
    isDragging = false;

    const endCell = document.elementFromPoint(event.clientX, event.clientY)?.closest('td');

    if (!endCell || !isValidSelection(startCell, endCell)) {
        if (svgLine) svgLine.remove();
        resetSelectionState();
        return;
    }

    selectedCells = getCellsBetween(startCell, endCell);
    const selectedWord = getSelectedWordFromCells(selectedCells);

    if (window.validWords.has(selectedWord) && !foundWords.has(selectedWord)) {
        if (svgLine) svgLine.remove();
        createPermanentLine(startCell, endCell);

        selectedCells.forEach(cell => cell.classList.add("found-word"));
        foundWords.add(selectedWord);

        document.querySelectorAll(".word-list li").forEach(li => {
            if (li.textContent === selectedWord) {
                li.style.textDecoration = "line-through";
            }
        });

        updateScore(gameMode);

        if (foundWords.size === window.validWords.size) {
            console.log("All words found! Refreshing grid...");
            setTimeout(() => {
                refreshGame(false);
            }, 500);
        }
    } else {
        if (svgLine) {
             svgLine.setAttribute("stroke", "red");
             setTimeout(() => {
                 if (svgLine) svgLine.remove();
             }, 300);
        }
    }

    resetSelectionState();
}

// Function to reset selection state variables
function resetSelectionState() {
    startCell = null;
    isDragging = false;
    selectedCells = [];
}

// Clean up on mouse leave window (if drag is active)
function handleDocumentMouseLeave(event) {
    if (isDragging && !event.relatedTarget && !event.toElement) {
        if (svgLine) svgLine.remove();
        resetSelectionState();
    }
}


const scoreElement = document.getElementById("current-score");
if (scoreElement) {
    scoreElement.textContent = score;
} else {
    console.error("#current-score element not found!");
}

const timerElement = document.getElementById("timer");
if (timerElement) {
    timerElement.textContent = timeLeft;
} else {
    console.error("#timer element not found!");
}

// Function to update score
function updateScore(mode) {
    let currentMode = window.gameMode || 'easy';
    let pointsPerWord = currentMode === "easy" ? 50 : currentMode === "normal" ? 100 : 150;
    
    console.log(`Updating score. Mode: ${currentMode}, Points per word: ${pointsPerWord}`); 
    
    if (isNaN(score)) { 
        console.error("Score is NaN before update! Resetting to 0.");
        score = 0; 
    }
    console.log(`Before addition - Score: ${score} (Type: ${typeof score}), Points: ${pointsPerWord} (Type: ${typeof pointsPerWord})`);

    score += pointsPerWord;
    document.getElementById("current-score").textContent = score;
    
    localStorage.setItem('persistentWordSearchScore', score.toString());
    console.log(`Score updated to: ${score}`); 
}

// Save current mode to localStorage
localStorage.setItem('wordSearchGameMode', gameMode);

// Start the timer
function startTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    
    const timerElement = document.getElementById("timer");
    if (!timerElement) return;

    timerElement.textContent = timeLeft; 

    timerInterval = setInterval(() => {
        timeLeft--;
        timerElement.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            handleGameOver(); 
        }
    }, 1000);
}

// Function to handle game over when timer expires
function handleGameOver() {
    console.log("Game Over! Timer expired.");
    if (timerInterval) {
        clearInterval(timerInterval);
    }

    fetch('/end-game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ score: score }) 
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { 
                throw new Error(err.error || 'Network response was not ok');
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Score submitted:', data.message);
        window.location.href = '/score'; 
    })
    .catch(error => {
        console.error('Error submitting score:', error);
        alert('Could not save your score. Proceeding anyway.');
        window.location.href = '/score';
    });
}

// Function to refresh the game board and state
function refreshGame(resetScore = false) {
    console.log("refreshGame called, resetScore:", resetScore);
    if (timerInterval) {
        clearInterval(timerInterval);
    }

    if (resetScore) {
        console.log("Resetting score to 0");
        score = 0;
        const scoreElement = document.getElementById("current-score");
        if (scoreElement) {
            scoreElement.textContent = score;
        }
        localStorage.setItem('persistentWordSearchScore', '0');
    }

    foundWords.clear();
    document.querySelectorAll(".word-list li").forEach(li => {
        li.style.textDecoration = "none";
    });
    document.querySelectorAll(".found-word").forEach(cell => {
        cell.classList.remove("found-word");
    });
    
    foundLines.forEach(line => line.remove());
    foundLines = [];
    document.querySelectorAll('#svgContainer line.permanent').forEach(line => line.remove());

    setInitialTime();
    startTimer();

    fetch(`/new-grid`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok fetching grid');
            }
            return response.json();
        })
        .then(data => {
            const gridTableBody = document.querySelector('.word-grid tbody');
            if (!gridTableBody) {
                 console.error("Could not find .word-grid tbody");
                 return;
            }
            gridTableBody.innerHTML = '';
            
            data.grid.forEach((row, rowIndex) => {
                const tr = gridTableBody.insertRow();
                row.forEach((letter, colIndex) => {
                    const td = tr.insertCell();
                    td.dataset.x = colIndex;
                    td.dataset.y = rowIndex;
                    td.dataset.letter = letter;
                    td.textContent = letter;
                });
            });

            const wordListUl = document.querySelector('.word-list ul');
            if (!wordListUl) {
                console.error("Could not find .word-list ul");
                return;
            }
            wordListUl.innerHTML = '';
            
            data.words.forEach(word => {
                const li = document.createElement('li');
                li.textContent = word;
                wordListUl.appendChild(li);
            });

            window.validWords = new Set(data.words);
            console.log("New grid loaded successfully.");
        })
        .catch(error => {
            console.error('Error fetching or processing new grid:', error);
            alert("Failed to load a new game grid. Please try again.");
        });
}

// Initial setup on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log(`DOMContentLoaded start - score: ${score} (Type: ${typeof score})`);
    
    const scoreElement = document.getElementById("current-score");
    if (scoreElement) {
        scoreElement.textContent = score;
    } else {
        console.error("#current-score element not found!");
    }

    // Prevent text selection in the grid
    const wordGrid = document.querySelector('.word-grid');
    if (wordGrid) {
        wordGrid.addEventListener('selectstart', (e) => e.preventDefault());
        wordGrid.addEventListener('mousedown', (e) => e.preventDefault());
    }

    setInitialTime();
    startTimer();

    const gridContainer = document.querySelector('.grid-container');
    if (gridContainer) {
        gridContainer.addEventListener('mousedown', handleGridMouseDown);
    } else {
        console.error("Grid container not found for mousedown listener.");
    }
    
    document.addEventListener('mousemove', handleDocumentMouseMove);
    document.addEventListener('mouseup', handleDocumentMouseUp);
    document.addEventListener('mouseleave', handleDocumentMouseLeave);

    const newGameButton = document.getElementById('new-game-button'); 
    const controlsContainer = document.getElementById('controls-container');

    if (!newGameButton && controlsContainer) {
        console.warn("New Game button not found in HTML, creating dynamically.");
        const btn = document.createElement('button');
        btn.id = 'new-game-button'; 
        btn.textContent = 'New Game';
        btn.classList.add('btn');
        btn.addEventListener('click', () => refreshGame(true));
        controlsContainer.appendChild(btn); 
    } else if (newGameButton) {
        newGameButton.addEventListener('click', () => refreshGame(true));
    } else {
        console.error("Could not find or create New Game button or its container.");
    }

    if (typeof validWords === 'undefined') {
        console.error("Initial validWords is not defined. Word checking might fail until refresh.");
        window.validWords = new Set(); 
    } else {
        window.validWords = validWords;
    }

    const gridTable = document.querySelector('.word-grid');
    if (gridTable && !gridTable.querySelector('tbody')) {
        const tbody = document.createElement('tbody');
        while (gridTable.firstChild) {
            tbody.appendChild(gridTable.firstChild);
        }
        gridTable.appendChild(tbody);
    }
});


