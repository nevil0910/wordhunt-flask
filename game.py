import random
import string
from words import easy_words, normal_words, hard_words  # Import word lists

def create_grid(size):
    return [["_" for _ in range(size)] for _ in range(size)]

def is_valid_placement(grid, word, row, col, direction):
    size = len(grid)
    word_length = len(word)
    
    # Check boundaries first
    if direction == "H" and col + word_length > size:
        return False
    if direction == "V" and row + word_length > size:
        return False 
    if direction == "D" and (row + word_length > size or col + word_length > size):
        return False
    if direction == "HR" and col - word_length + 1 < 0:
        return False
    if direction == "VR" and row - word_length + 1 < 0:
        return False
    if direction == "DR" and (row - word_length + 1 < 0 or col - word_length + 1 < 0):
        return False
    
    # Check each cell for validity - allow if cell is empty or contains the same letter
    for i in range(word_length):
        curr_row, curr_col = row, col
        
        if direction == "H":
            curr_col += i
        elif direction == "V":
            curr_row += i
        elif direction == "D":
            curr_row += i
            curr_col += i
        elif direction == "HR":
            curr_col -= i
        elif direction == "VR":
            curr_row -= i
        elif direction == "DR":
            curr_row -= i
            curr_col -= i
            
        # Make sure we're still within grid boundaries
        if curr_row < 0 or curr_row >= size or curr_col < 0 or curr_col >= size:
            return False
            
        # If the cell is not empty, it must match the letter we want to place
        if grid[curr_row][curr_col] != "_" and grid[curr_row][curr_col] != word[i]:
            return False
            
    return True

def place_word(grid, grid_filled, word, mode):
    size = len(grid)
    word_length = len(word)
    
    if word_length > size:
        print(f"Word '{word}' is too long ({word_length}) for grid size {size}")
        return False
        
    directions = ["H", "V"] if mode == "easy" else ["H", "V", "D"] if mode == "normal" else ["H", "V", "D", "HR", "VR", "DR"]
    
    if any(True for row in grid_filled for cell in row if cell == True):
        possible_placements = []
        
        for row in range(size):
            for col in range(size):
                if grid[row][col] != "_" and grid[row][col] in word:
                    for direction in directions:
                        for pos in range(len(word)):
                            if word[pos] == grid[row][col]:
                                start_row, start_col = row, col
                                
                                if direction == "H":
                                    start_col = col - pos
                                elif direction == "V":
                                    start_row = row - pos
                                elif direction == "D":
                                    start_col = col - pos
                                    start_row = row - pos
                                elif direction == "HR":
                                    start_col = col + pos
                                elif direction == "VR":
                                    start_row = row + pos
                                elif direction == "DR":
                                    start_col = col + pos
                                    start_row = row + pos
                                
                                # Ensure the starting position is within grid bounds
                                if start_row < 0 or start_row >= size or start_col < 0 or start_col >= size:
                                    continue
                                    
                                # Check if placement at this position is valid
                                if is_valid_placement(grid, word, start_row, start_col, direction):
                                    crossover_score = 0
                                    for i in range(len(word)):
                                        r, c = start_row, start_col
                                        if direction == "H":
                                            c += i
                                        elif direction == "V":
                                            r += i
                                        elif direction == "D":
                                            r += i
                                            c += i
                                        elif direction == "HR":
                                            c -= i
                                        elif direction == "VR":
                                            r -= i
                                        elif direction == "DR":
                                            r -= i
                                            c -= i
                                        
                                        # Extra safety check for bounds    
                                        if 0 <= r < size and 0 <= c < size and grid[r][c] != "_":
                                            crossover_score += 1
                                    
                                    # Higher score for crossovers that create multiple intersections
                                    if crossover_score > 1:
                                        crossover_score *= 2
                                    
                                    possible_placements.append((start_row, start_col, direction, crossover_score))
        
        # If we found valid crossover placements, choose the one with highest score
        if possible_placements:
            possible_placements.sort(key=lambda x: x[3], reverse=True)
            
            # Increase probability of choosing crossovers as more words are added
            # Count how many cells are filled
            filled_count = sum(1 for row in grid_filled for cell in row if cell)
            total_cells = size * size
            filled_percentage = filled_count / total_cells
            
            # Higher crossover probability as the grid fills up
            crossover_probability = max(0.7, min(0.95, 0.7 + filled_percentage))
            
            if random.random() < crossover_probability:  # Higher chance to choose best crossover
                row, col, direction, _ = possible_placements[0]
            else:
                row, col, direction, _ = random.choice(possible_placements)
                
            # Place the word
            for i in range(len(word)):
                if direction == "H":
                    grid[row][col + i] = word[i]
                    grid_filled[row][col + i] = True
                elif direction == "V":
                    grid[row + i][col] = word[i]
                    grid_filled[row + i][col] = True
                elif direction == "D":
                    grid[row + i][col + i] = word[i]
                    grid_filled[row + i][col + i] = True
                elif direction == "HR":
                    grid[row][col - i] = word[i]
                    grid_filled[row][col - i] = True
                elif direction == "VR":
                    grid[row - i][col] = word[i]
                    grid_filled[row - i][col] = True
                elif direction == "DR":
                    grid[row - i][col - i] = word[i]
                    grid_filled[row - i][col - i] = True
            return True
    
    # If no crossovers found or this is the first word, use the original random placement
    random.shuffle(directions)
    
    placement_attempts = 0
    max_attempts = 200  # Increase attempts for harder modes
    
    while placement_attempts < max_attempts:
        placement_attempts += 1
        
        # Calculate valid starting positions based on direction and word length
        direction = random.choice(directions)
        
        # Determine the valid range for row and column based on direction and word length
        if direction == "H":
            max_col = size - word_length
            row = random.randint(0, size - 1)
            col = random.randint(0, max_col)
        elif direction == "V":
            max_row = size - word_length
            row = random.randint(0, max_row)
            col = random.randint(0, size - 1)
        elif direction == "D":
            max_row = size - word_length
            max_col = size - word_length
            row = random.randint(0, max_row)
            col = random.randint(0, max_col)
        elif direction == "HR":
            min_col = word_length - 1
            row = random.randint(0, size - 1)
            col = random.randint(min_col, size - 1)
        elif direction == "VR":
            min_row = word_length - 1
            row = random.randint(min_row, size - 1)
            col = random.randint(0, size - 1)
        elif direction == "DR":
            min_row = word_length - 1
            min_col = word_length - 1
            row = random.randint(min_row, size - 1)
            col = random.randint(min_col, size - 1)
        
        # Double-check that placement is valid
        if is_valid_placement(grid, word, row, col, direction):
            for i in range(len(word)):
                r, c = row, col
                if direction == "H":
                    c += i
                elif direction == "V":
                    r += i
                elif direction == "D":
                    r += i
                    c += i
                elif direction == "HR":
                    c -= i
                elif direction == "VR":
                    r -= i
                elif direction == "DR":
                    r -= i
                    c -= i
                
                # Final safety check
                if 0 <= r < size and 0 <= c < size:
                    grid[r][c] = word[i]
                    grid_filled[r][c] = True
                else:
                    print(f"ERROR: Index out of range for word {word} at ({r},{c})")
                    # Undo placement
                    for j in range(i):
                        if direction == "H":
                            grid[row][col + j] = "_"
                            grid_filled[row][col + j] = False
                        elif direction == "V":
                            grid[row + j][col] = "_"
                            grid_filled[row + j][col] = False
                        elif direction == "D":
                            grid[row + j][col + j] = "_"
                            grid_filled[row + j][col + j] = False
                        elif direction == "HR":
                            grid[row][col - j] = "_"
                            grid_filled[row][col - j] = False
                        elif direction == "VR":
                            grid[row - j][col] = "_"
                            grid_filled[row - j][col] = False
                        elif direction == "DR":
                            grid[row - j][col - j] = "_"
                            grid_filled[row - j][col - j] = False
                    break
            else:  # This executes if the for loop completes normally (no break)
                return True
            
    print(f"Could not place word: {word} after {max_attempts} attempts")
    return False

def fill_empty_spaces(grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == "_":
                grid[i][j] = random.choice(string.ascii_uppercase)

def create_word_grid(mode):
    size = {"easy": 5, "normal": 10, "hard": 15}[mode]
    words_list = easy_words if mode == "easy" else normal_words if mode == "normal" else hard_words
    
    # Convert words to uppercase and remove duplicates
    words_list = list(set([word.upper() for word in words_list]))
    
    # Filter out words that are longer than the grid size
    words_list = [word for word in words_list if len(word) <= size]
    
    if not words_list:
        print(f"No words available for {mode} mode with grid size {size}")
        # Fallback to easier words if needed
        if mode == "hard":
            print("Falling back to normal words")
            words_list = [word.upper() for word in normal_words if len(word) <= size]
        elif mode == "normal":
            print("Falling back to easy words")
            words_list = [word.upper() for word in easy_words if len(word) <= size]
    
    # Shuffle the words list to ensure randomness each time
    random.shuffle(words_list)
    
    # Select more words for each difficulty level
    num_words = 5 if mode == "easy" else 8 if mode == "normal" else 12
    selected_words = random.sample(words_list, min(num_words, len(words_list)))
    
    # Sort words by length (longest first) to prioritize placing longer words
    # which have more potential crossover points
    words = sorted(selected_words, key=len, reverse=True)
    
    grid = create_grid(size)
    
    # Create a grid to track which cells are filled with words
    grid_filled = [[False for _ in range(size)] for _ in range(size)]
    
    placed_words = []
    for word in words:
        success = place_word(grid, grid_filled, word, mode)
        if success:
            placed_words.append(word)
        else:
            print(f"Could not place word: {word}")
    
    fill_empty_spaces(grid)
    
    return grid, placed_words