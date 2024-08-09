import tkinter as tk
from tkinter import messagebox

# Create the main window
window = tk.Tk()
window.title("Tic-Tac-Toe")

# Create the game board
board = [['' for _ in range(3)] for _ in range(3)]

# Create the buttons
buttons = []
for i in range(3):
    for j in range(3):
        button = tk.Button(window, text='', width=10, height=5, command=lambda row=i, col=j: click_button(row, col))
        button.grid(row=i, column=j)
        buttons.append(button)

# Player turn
current_player = 'X'

# Function to handle button clicks
def click_button(row, col):
    global current_player
    
    # Check if the button is already clicked
    if board[row][col] != '':
        return
    
    # Update the board and button
    board[row][col] = current_player
    buttons[row * 3 + col].config(text=current_player)
    
    # Check for a winner
    if check_winner():
        messagebox.showinfo("Tic-Tac-Toe", f"Player {current_player} wins!")
        reset_game()
        return
    
    # Check for a draw
    if check_draw():
        messagebox.showinfo("Tic-Tac-Toe", "It's a draw!")
        reset_game()
        return
    
    # Switch players
    current_player = 'O' if current_player == 'X' else 'X'

# Function to check for a winner
def check_winner():
    # Check rows
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != '':
            return True
    
    # Check columns
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] != '':
            return True
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != '':
        return True
    if board[0][2] == board[1][1] == board[2][0] != '':
        return True
    
    return False

# Function to check for a draw
def check_draw():
    for i in range(3):
        for j in range(3):
            if board[i][j] == '':
                return False
    return True

# Function to reset the game
def reset_game():
    global current_player
    current_player = 'X'
    for i in range(3):
        for j in range(3):
            board[i][j] = ''
            buttons[i * 3 + j].config(text='')

# Create the reset button
reset_button = tk.Button(window, text="Reset", command=reset_game)
reset_button.grid(row=3, column=0, columnspan=3)

# Start the main loop
window.mainloop()