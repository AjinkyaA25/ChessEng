'''
Main driver file for Chess. Establishes GameState.
'''

import pygame as p
from Chess import ChessEngine, ChessAI
from multiprocessing import Process, Queue
TOTALWIDTH = 950
WIDTH = 512
HEIGHT = 512
DIMENSION = 8 # 8 x 8 board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animation later
IMAGES = {}

'''
 Will initialize a gload dictionary of images. Will be called once because it is expensive to load
 images. 
'''

def loadImages(screen):
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    font = p.font.SysFont('Arial', 20, True, False)
    textObject = font.render("White", 0, p.Color('White'))
    textLocation = p.Rect(550, 0, 700, 0)
    screen.blit(textObject, textLocation)
    textObject = font.render("Black", 0, p.Color('White'))
    textLocation = p.Rect(650, 0, 700, 0)
    screen.blit(textObject, textLocation)
    textObject = font.render("White", 0, p.Color('White'))
    textLocation = p.Rect(750, 0, 700, 0)
    screen.blit(textObject, textLocation)
    textObject = font.render("Black", 0, p.Color('White'))
    textLocation = p.Rect(850, 0, 700, 0)
    screen.blit(textObject, textLocation)


    # To access the images just use IMAGES['wP'] for example because it is in a dictionary

'''
Main Driver which will handle user input and updating game graphics.
'''

def main():
    p.init()
    screen = p.display.set_mode((TOTALWIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('black'))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    loadImages(screen)
    running = True
    sqSelected = () # no square is initially selected (tuple: (row,col))
    playerClicks = [] # keeps track of player clicks [(tuple: (row,col), tuple: (row,col))]
    gameOver = False
    playerOne = False #If human is playing white, then true. If an AI is playing, then false
    playerTwo = False #True if a human is playing and false otherwise
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    notation = ""
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            # Mouse handler
            elif event.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # location is a list with [x,y] coordinates of the mouse
                    row = location[0] // SQ_SIZE
                    col = location[1] // SQ_SIZE
                    if 0 <= row < 8 and 0 <= col < 8:
                        if sqSelected == (col, row): # user clicked the same square twice
                            sqSelected = () # deselect the square
                            playerClicks = [] # restart the process
                        else:
                            sqSelected = (col, row)
                            playerClicks.append(sqSelected) # append for both 1st and 2nd clicks
                        if len(playerClicks)  == 2 and humanTurn: #2nd click completed
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i]) #makeMove flips the whiteToMove variable and increases turn
                                    writeNotation(screen, move.getChessNotation(), not gs.whiteToMove, gs.turn, gs.inCheck())
                                    #print(gs.castleRightsLog[-1].wks, gs.castleRightsLog[-1].wqs, gs.castleRightsLog[-1].bks, gs.castleRightsLog[-1].bqs)


                                    moveMade = True
                                sqSelected = () #reset the user clicks
                                playerClicks = []
            #key handlers
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:

                    gs.undoMove()

                    gs.turn -= 1 #turn increases after undo so need to reset it back
                    if gs.turn < 1: gs.turn = 1

                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

                    moveMade = True #to create valid moves after the undo
                if event.key == p.K_r:
                    gs = ChessEngine.GameState()
                    loadImages(screen)
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = False

        #AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print('AIThinking...')
                returnQueue = Queue() #used to pass data between threads
                moveFinderProcess = Process(target = ChessAI.findBestMove, args = (gs, validMoves, returnQueue))
                moveFinderProcess.start() #calls findBestMove
                #AIMove = ChessAI.findBestMove(gs, validMoves)
            if not moveFinderProcess.is_alive():
                print('done Thinking')
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = ChessAI.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                writeNotation(screen, AIMove.getChessNotation(), not gs.whiteToMove, gs.turn, gs.inCheck())
                moveMade = True
                AIThinking = False


        if moveMade:
            validMoves = gs.getValidMoves()
            moveUndone = False
            moveMade = True

        drawGameState(screen, gs, validMoves, sqSelected)
        #writeNotation(screen, notation, gs.whiteToMove, gs.turn)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black WINS by checkmate")
            else:
                drawText(screen, "White WINS by checkmate")
        if gs.staleMate:
            gameOver = True
            drawText(screen, "StaleMate")
        if gs.checkRepetition():
            gameOver = True
            drawText(screen, "Draw by repetition")
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Display the move on the screen so that users know the notation.
writeNotation is called after moveMade, which would increase the turn even though the 
notation needs to be done for the turn before so if it is black's turn by the time this function is called,
the turn indicator needs to be decreased. 
'''
def writeNotation(screen, notation, whiteToMove, turn, check):
    if not whiteToMove:
        turn -= 1
    #print(turn)
    INCREMENT = HEIGHT//30
    font = p.font.SysFont('Helvetica', 18)
    textObject = None
    if check is True:
        textObject = font.render(str(turn) + ".  " + notation + "+", 0, p.Color("White"))
    else:
        textObject = font.render(str(turn) + ".  " + notation, 0, p.Color("White"))
    textLocation = None
    if whiteToMove is True: #whites turn
        if turn < 30:
            textLocation = p.Rect(550, turn * INCREMENT, 700, 0)
            p.draw.rect(screen, 'burlywood3', p.Rect(550, turn * INCREMENT + 3, 90, INCREMENT))
        else:
            textLocation = p.Rect(750, (turn - 29) * INCREMENT, 700, 0)
            p.draw.rect(screen, 'burlywood3', p.Rect(750, (turn - 29) * INCREMENT + 3, 90, INCREMENT))
    else: #black turn
        if turn < 30:
            textLocation = p.Rect(650, turn * INCREMENT, 912, 0)
            p.draw.rect(screen, 'burlywood4', p.Rect(650, turn * INCREMENT + 3, 90, INCREMENT))
        else:
            textLocation = p.Rect(850, (turn - 29) * INCREMENT, 912, 0)
            p.draw.rect(screen, 'burlywood4', p.Rect(850, (turn - 29) * INCREMENT + 3, 90, INCREMENT))
    screen.blit(textObject, textLocation)



'''
Draws the text for gameOver
'''
def drawText(screen, text):
    font = p.font.SysFont('Helvetica', 40, True, False)
    textObject = font.render(text, 0, p.Color('Darkslategrey'))
    textLocation = p.Rect(0,0, WIDTH, HEIGHT).move(WIDTH//2 - textObject.get_width()//2, HEIGHT//2 - textObject.get_height()//2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Steelblue'))
    screen.blit(textObject, textLocation.move(3,3))
'''
Highlight the squares selected and the moves for the piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row,col = sqSelected[0], sqSelected[1]
        #if gs.whiteToMove:
            #if gs.board[row][col][0] == "w":
        #else:
            #if gs.board[row][col][0] == "b":
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value --> 0 meaning transparent 255 meaning opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row  and move.startCol == col:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))





'''
Draws the squares on the board and the pieces on the board. 
Adjusts graphics for current game state. 
DrawBoard must come before drawPieces otherwise the pieces wont be visible.
'''
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # will draw the squares on the board

    # useful for adding piece highlighting or move suggestion
    highlightSquares(screen,gs,validMoves, sqSelected)
    drawPieces(screen, gs.board) # will draw the pieces on the gameState

'''
Draws the squares on the board. 
'''
def drawBoard(screen):
    colors = [p.Color('burlywood3'), p.Color('burlywood4')]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            # even is light and odd is dark
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            # col * SQ_SIZE is the x starting point
            # row * SQ_SIZE is the y starting point
            # SQ_SIZE is how far to draw the rectangle


'''
Draws the pieces on the board using the current gameState.
'''
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--": # not empty
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == '__main__':
    main()