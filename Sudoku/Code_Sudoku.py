import random
import pygame # pip install pygame
import sys
import time 
import cv2 #pip install opencv-python
import mediapipe as mp # pip install opencv-python mediapipe
import threading



class Board:
    #Create a 9x9 board for the sudoku

    #0 is an empty cell, 1-9 is the number of the filled cell

    #size of the board is 9, size of a square is 3 (9 squares in the board)
    #grid is the list who store the cell values 

    def __init__(self):
        self.size_board = 9
        self.size_square = 3
        self.grid = [[0 for i in range(self.size_board)] for j in range (self.size_board)]

    
    def set_a_value(self, row, col, value):
        #Set the value of a specific cell

        if 0 <= row < self.size_board and 0 <= col < self.size_board:
            self.grid[row][col] = value
        else:
            raise IndexError('Row or column out of valid range.')

    def get_a_value(self, row, col):
        #Get the value of a specific cell

        if 0 <= row < self.size_board and 0 <= col < self.size_board:
            return self.grid[row][col]
        else:
            raise IndexError('Row or column out of valid range.')

    def is_cell_empty(self, row, col):
        #Return True is the cell is empty
        return self.grid[row][col] == 0

    def copy_board(self):
        #Create a copy of the Sudoku board
        new_board = Board()
        for i in range(self.size_board):
            for j in range(self.size_board):
                new_board.set_a_value(i, j, self.grid[i][j])
        return new_board

    def print_board(self):
        #print the board to have an easy access
        for i in range(self.size_board):
            if i % self.size_square == 0 and i != 0:
                print('-' * (self.size_board * 2 + 3))

            row_str = ''
            for j in range(self.size_board):
                if j % self.size_square == 0 and j != 0:
                    row_str += '| '
                value = self.grid[i][j]
                row_str += str(value) + ' ' if value != 0 else '. '
            print(row_str.strip())


class Generator:
    #This class generate a sudoku grid, it can also remove some of the numbers to be able to play the game
    def __init__(self):
        self.board = Board()
        self.validator = Validator()

    def no_same_row(self, row, value):
        #check if the value is already in the row
        for i in range(self.board.size_board):
            if self.board.get_a_value(row, i) == value:
                return False
        return True

    def no_same_col(self, col, value):
        #check if the value is already in the col
        for i in range(self.board.size_board):
            if self.board.get_a_value(i, col) == value:
                return False
        return True

    def no_same_square(self, row, col, value):
        #check if the value is already in the square
        r1_square = (row // self.board.size_square) * self.board.size_square
        c1_square = (col // self.board.size_square) * self.board.size_square

        for i in range(r1_square, r1_square + self.board.size_square):
            for j in range(c1_square, c1_square + self.board.size_square):
                if self.board.get_a_value(i, j) == value:
                    return False
        return True

    def is_safe(self, row, col, value):
        #check if we can place the number is the selected cell (return a bool)
        return (self.no_same_row(row, value) and
                self.no_same_col(col, value) and
                self.no_same_square(row, col, value))
   
    def fill_board(self, row, col):
        #Recursion the fill the board from a given cell
        #+1 row when we are in the last col
        if col == self.board.size_board:
            col = 0
            row += 1

        # end if it was tha last row
        if row == self.board.size_board:
            return True

        # Generate numbers in random order 
        num = list(range(1, 10))
        random.shuffle(num)

        for i in num:
            if self.is_safe(row, col, i):
                self.board.set_a_value(row, col, i)
                if self.fill_board(row, col + 1):
                    return True
                # Backtrack
                self.board.set_a_value(row, col, 0)

        return False

    def create_puzzle(self, diff='easy'):
        #remove num to create the puzzle
        if diff == 'easy':
            remove = 20
        elif diff == 'medium':
            remove = 30
        elif diff == 'hard':
            remove = 40

        #list of all the positions
        position_nums = [(i, j) for i in range(self.board.size_board) for j in range(self.board.size_board)]
        random.shuffle(position_nums)

        c_removed = 0

        for (i, j) in position_nums:
            if c_removed >= remove:
                break
            current_num = self.board.get_a_value(i, j)
            if current_num != 0:
                #try to remove and check if there is only 1 sol
                self.board.set_a_value(i, j, 0)
                if self.validator.unique_sol(self.board):
                    #only 1 sol, we can remove it
                    c_removed += 1
                else:
                    #Reset the num because there is more than 1 sol
                    self.board.set_a_value(i, j, current_num)
    
    def generate_sol(self):
        #generate the solution
        return self.fill_board(0, 0)

    def get_board(self):
        return self.board

class Validator:
    #Class to check if there is only one solution to the puzzle we created
    def __init__(self):
        pass

    def safe_to_place(self, board, row, col, num):
        #need to recreate the functions to check if the position is safe because I couldn't use the ones from generator class
        # Check row
        for i in range(board.size_board):
            if board.get_a_value(row, i) == num:
                return False

        # Check column
        for i in range(board.size_board):
            if board.get_a_value(i, col) == num:
                return False

        # Check square
        r1_square = (row // board.size_square) * board.size_square
        c1_square = (col // board.size_square) * board.size_square

        for i in range(r1_square, r1_square + board.size_square):
            for j in range(c1_square, c1_square + board.size_square):
                if board.get_a_value(i, j) == num:
                    return False
        return True

    def count_sol(self, board, row, col):
        #count the solutions
        if col == board.size_board:
            col = 0
            row += 1

        if row == board.size_board:
            self.solutions += 1
            return

        if self.solutions > 1:
            #stop the function if we have more than 1 solution, no need to go further
            return

        if board.is_cell_empty(row, col):
            for i in range(1, 10):
                if self.safe_to_place(board, row, col, i):
                    board.set_a_value(row, col, i)
                    self.count_sol(board, row, col + 1)
                    # Backtrack
                    board.set_a_value(row, col, 0)
                    if self.solutions > 1:
                        #No need to go further if we finid more than one solution
                        return
        else:
            # Next cell if this one is filled with a number
            self.count_sol(board, row, col + 1)        
    
    def unique_sol(self, board):
        #return true if the grid only has 1 solution
        board_copy = board.copy_board()
        self.solutions = 0
        self.count_sol(board_copy, 0, 0)

        return self.solutions == 1



# variables for the sudoku game (size and colors)
width = 450
height = 510
top = 60
wh = (255, 255, 255)
bla = (0, 0, 0)
gr = (200, 200, 200)
blu = (52, 152, 219)
re = (231, 76, 60)


class Sudoku_game:
    def __init__(self, finger_counter, diff='hard'):
        #initialization of the sudoku game with pygame

        pygame.init()
        # create the screen with the given sizes
        self.screen = pygame.display.set_mode((width, height))
        # display the title 
        pygame.display.set_caption('Sudoku')
        #start a clock
        self.clock = pygame.time.Clock()

        #set the size and type of character for the message to confirm the count of fingers
        self.font = pygame.font.SysFont('arial', 40)

        # set the finger counter
        self.finger_counter = finger_counter

        #set the sudoku generator
        generator = Generator()
        #generate the solution
        generator.generate_sol()
        #copy the board to save as the solution board
        self.solution_board = generator.get_board().copy_board()
        #create the puzzle removing cells according to the difficulty
        generator.create_puzzle(diff)
        # get the board
        self.puzzle_board = generator.get_board()

        #set all the parameters to 0
        self.selected_row = 0
        self.selected_col = 0

        self.mistakes = 0
        self.max_mistakes = 5
        self.game_over = False

        #parameters for the count of finger set to 0 
        self.last_count = 0
        self.finger_start_time = None
        self.duration = 3.0

        self.pending_number = None
        self.show_confirm_prompt = False
    
    def run(self):
        running = True

        while running:
            self.clock.tick(30)
            for e in pygame.event.get():
                #stop the game if we quit
                if e.type == pygame.QUIT:
                    running = False
                else:
                    #if the event is not quitting and the game is not over, run the input function
                    if self.game_over == False:
                        self.input(e)

            # run the check input function
            self.check_finput()

            #run the draw function
            self.draw()

            #handle win and loss 
            if self.solved() and running:
                print('You won!')
                running = False
            
            if self.game_over:
                print('Game over!')
                running = False 

        pygame.quit()
        sys.exit()

    def check_finput(self):
        #don't count if you have the confirm prompt
        if self.show_confirm_prompt:
            return

        #read the finger detection function and check if the number is correct
        with self.finger_counter.lock:
            current_count = self.finger_counter.count
        
        # don't do anything if the count is 0
        if current_count == 0:
            return
            
        #reset timer if count changed
        if current_count != self.last_count:
            self.last_count = current_count
            self.finger_start_time = time.time()


        #if same number for more than 3 sec, we consider it as the number to input and we can show the message to confirm
        else :
            if self.finger_start_time:
                elapsed_time = time.time() - self.finger_start_time
                if elapsed_time > self.duration:
                    self.pending_number = self.last_count
                    self.show_confirm_prompt = True

            

    def draw(self):
        #function to draw all the game

        # fill the screen cerated with white
        self.screen.fill(wh)
        #set the size and type of character for the mistakes
        self.font_1 = pygame.font.SysFont('arial', 15)
        #dispay the word 'Mistakes' in the upper left part
        txt_msitakes = self.font_1.render('Mistakes:', True, re)
        self.screen.blit(txt_msitakes, (10, 40))
        # draw a X for each mistakes
        self.draw_mistakes()

        for i in range(self.puzzle_board.size_board + 1):
            # set the thickness of the lines (thickner for the 3x3 squares)
            line_th = 1
            if i % 3 == 0:
                line_th = 4
            
            # draw the vertical lines
            start_x = i * 450//9
            start_y = top
            end_x = i * 450//9
            end_y = 450 + top
            pygame.draw.line(self.screen, bla, 
                             (start_x, start_y), (end_x, end_y), line_th)
        
            # draw the horizontal lines
            start_x = 0
            start_y = i * 450//9 + top
            end_x = 450
            end_y = i * 450//9 + top
            pygame.draw.line(self.screen, bla, 
                             (start_x, start_y), (end_x, end_y), line_th)
            
        # set the blue background when a cell is selected 
        sel_cell = pygame.Rect(self.selected_col * 450//9, 
                                   top + self.selected_row * 450//9, 450//9, 450//9)
        pygame.draw.rect(self.screen, blu, sel_cell, 3)

        # fill the cells with the board number and check if the numbers filled are the good ones 
        for i in range(self.puzzle_board.size_board):
            for j in range(self.puzzle_board.size_board):
                value = self.puzzle_board.get_a_value(i, j)
                if value != 0:
                    correct_val = self.solution_board.get_a_value(i, j)
                    color = bla if value == correct_val else re #black if good, red if false

                    text = self.font.render(str(value), True, color)
                    text_rect = text.get_rect(center=(j * 450//9 + 450//18, top + i * 450//9 + 450//18))

                    self.screen.blit(text, text_rect)

        #display the message to confirm if the show_confirm_prompt variable is true and if we have a number locked
        if self.show_confirm_prompt and self.pending_number:
            txt_surf = self.font.render(f'Confirm {self.pending_number}? press ENTER', True, re)
            self.screen.blit(txt_surf, (10, -6))



        pygame.display.update()

    def draw_mistakes(self):
        # function to draw the number of mistakes
        for i in range(self.mistakes):
            txt_surf = self.font_1.render('X', True, re)
            self.screen.blit(txt_surf, (80 + i * 15, 40))


    def input(self, event):
        #function to handle the user inputs 

        # change cell when a keyboard arrow is pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_row = (self.selected_row - 1) 
            elif event.key == pygame.K_DOWN:
                self.selected_row = (self.selected_row + 1)
            elif event.key == pygame.K_LEFT:
                self.selected_col = (self.selected_col - 1)
            elif event.key == pygame.K_RIGHT:
                self.selected_col = (self.selected_col + 1)
            
            # when pressing enter, fill the number showed in the message in the board 
            # checked here to upper the or not the number of mistakes and checked again in the draw function to light in red or not
            elif event.key == pygame.K_RETURN:
                if self.show_confirm_prompt and self.pending_number:
                    num = self.pending_number
                    correct_num = self.solution_board.get_a_value(self.selected_row, self.selected_col)

                    self.puzzle_board.set_a_value(self.selected_row, self.selected_col, num)
                    if num != correct_num:
                        self.mistakes += 1
                        if self.mistakes >= self.max_mistakes:
                            self.game_over = True
                            #game over if too many mistakes
                    #reset to 0 the variables for next input
                    self.show_confirm_prompt = False
                    self.pending_number = None  

            # cancel the message if you press 'ESC'
            elif event.key == pygame.K_ESCAPE:
                if self.show_confirm_prompt:
                    self.show_confirm_prompt = False
                    self.pending_number = None

            # handle keyboard input if it's a number
            elif event.unicode in '123456789':
                num = int(event.unicode)
                correct_num = self.solution_board.get_a_value(self.selected_row, self.selected_col)

                self.puzzle_board.set_a_value(self.selected_row, self.selected_col, num)

                if num != correct_num:
                    self.mistakes += 1
                    if self.mistakes >= self.max_mistakes:
                        self.game_over = True


        #handle mouse input
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos
                
                if 450+top > y >= top:
                    board_y = y - top
                    row = board_y // (450 // 9)
                    col = x // (450 // 9)

                    if 0 <= row < 9 and 0 <= col < 9:
                        val = self.puzzle_board.get_a_value(row, col)
                        correct_val = self.solution_board.get_a_value(row, col)
                        # if we click in a cell with a wrong number, it'll remove it
                        if val != correct_val and val != 0:
                            self.puzzle_board.set_a_value(row, col, 0)
                        #else, it'll select the cell
                        else : 
                            self.selected_row = row
                            self.selected_col = col
        

            
                

    def solved(self):
        #if all values are correct, return True
        for i in range(self.puzzle_board.size_board):
            for j in range(self.puzzle_board.size_board):
                if self.puzzle_board.get_a_value(i, j) != self.solution_board.get_a_value(i, j):
                    return False
        return True





class Finger_count:
    def __init__(self, max_hands=2, detection_confidence=0.5, tracking_confidence=0.5):
        
        #initialize the hands module 
        self.mp_hands = mp.solutions.hands
        #create a hands object 
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=max_hands, min_detection_confidence=detection_confidence, min_tracking_confidence=tracking_confidence)
        #initialize the draw on the hands for a better visualisation
        self.mp_draw = mp.solutions.drawing_utils

        # Thumb, Index, Middle, Ring, Pinky
        self.finger_tips = [4, 8, 12, 16, 20]

        #initialize the count 
        self.count = 0

        self.running = True

        #initialize a lock to have a safer access to the count variable
        self.lock = threading.Lock()

    def count_fing_one_hand(self, hand_landmarks, handedness_label):

        # Convert landmarks into a list of (x, y) normalized coordinates
        normalized_landmarks = [(i.x, i.y) for i in hand_landmarks.landmark]

        count = 0

        #check the thumb (not same logic for left and right)
        thumb_tip_x = normalized_landmarks[self.finger_tips[0]][0]
        thumb_ip_x = normalized_landmarks[self.finger_tips[0] - 1][0]

        # for right hand the thumb is counted if tip is left of ip
        # to change if we have time, it's not working really well
        if handedness_label == 'Right':
            if thumb_tip_x < thumb_ip_x:
                count += 1
        # for left opposite
        else:
            if thumb_tip_x > thumb_ip_x:
                count += 1

        # for the other fingers, count if tip is higher than pip
        for i in self.finger_tips[1:]:
            tip_y = normalized_landmarks[i][1]
            pip_y = normalized_landmarks[i - 2][1]
            if tip_y < pip_y:
                count += 1
        
        return count
    

    
    def run(self, camera_index=0):
        #access the webcam
        cap = cv2.VideoCapture(camera_index)

        while self.running:
            #read camera frame
            success, img = cap.read()

            if not success:
                break

            #flip for selfie vue
            img = cv2.flip(img, 1)

            #convert the image to RGB for mediapipe 
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            #process image to detect hands 
            results = self.hands.process(img_rgb)

            tot_fingers = 0

            #if hands is detected, count on each hands
            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    hand_label = handedness.classification[0].label #Right or left
                    #count for this hand and add to the total
                    tot_fingers += self.count_fing_one_hand(hand_landmarks, hand_label)

                    #draw the landmarks and connections
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            #ignore 0 and 10
            if 1 <= tot_fingers <= 9:
                count = tot_fingers
            else:
                count = 0
            
            #update the count variable with the lock
            with self.lock:
                self.count = count
                

            #display the count at top left corner
            cv2.putText(img, f'Fingers: {count}', (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            cv2.imshow('Finger Counter', img)

            #esc to exit
            if cv2.waitKey(1) == 27:
                break
        
        cap.release()
        cv2.destroyAllWindows()


def main():
    # create the finger counter
    fc = Finger_count()

    # start its thread
    t_fc = threading.Thread(target=fc.run, daemon=True)
    t_fc.start()

    # run de sudoku game
    sudoku = Sudoku_game(fc)
    sudoku.run()

    # stop the counter when the game is finished
    fc.stop()
    t_fc.join()

if __name__ == '__main__':
    main()
