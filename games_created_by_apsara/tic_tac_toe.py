import random
board = [[' ' for _ in range(3)] for _ in range(3)]

def print_board():
    for row in board:
        print(" | ".join(row))
        print("-" * 5)

def check_win(player):
    for row in board:
        if row.count(player) == 3:
            return True
    for col in range(3):
        check = []
        for row in range(3):
            check.append(board[row][col])
        if check.count(player) == 3:
            return True
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        return True
    if board[0][2] == player and board[1][1] == player and board[2][0] == player:
        return True
    return False

def human_turn():
    while True:
        row = int(input("Enter row (1-3): ")) - 1
        col = int(input("Enter column (1-3): ")) - 1
        if board[row][col] == ' ':
            board[row][col] = 'X'
            break

def computer_turn():
    # This is a very simple computer AI. In a real game, you'd want something more complex.
    while True:
        row = random.randint(0, 2)
        col = random.randint(0, 2)
        if board[row][col] == ' ':
            board[row][col] = 'O'
            break

def main():
    while True:
        print_board()
        human_turn()
        if check_win('X'):
            print_board()
            print("Human wins!")
            break
        if not any(' ' in row for row in board):
            print_board()
            print("It's a draw!")
            break
        computer_turn()
        if check_win('O'):
            print_board()
            print("Computer wins!")
            break

if __name__ == "__main__":
    main()
