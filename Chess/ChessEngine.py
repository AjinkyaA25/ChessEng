import copy
"""
This class will be used to determine the current game state and the possible valid moves.
Will store the move log as well.
"""

class GameState():
    def __init__(self):
        # board is a 8 x 8 in a 2d list
        # first character represents color and 2nd character represents the type of piece
        # R - rook, N - Knight, B - Bishop, Q - Queen, K - King, P - Pawn
        # -- represents a space with no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {'P': self.getPawnMoves,
                              'R': self.getRookMoves,
                              'N': self.getKnightMoves,
                              'B': self.getBishopMoves,
                              'Q': self.getQueenMoves,
                              'K': self.getKingMoves
                              }
        self.whiteToMove = True
        self.moveLog = []
        self.turnValues = {"w": True, "b": False}  # checking for opposite colored piece
        self.whiteKinglocation = (7,4)
        self.blackKinglocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.isEnPassantMove = False
        self.enpassantPossible = () #coordinates for the square where pawnPromotion is possible
        self.currentCastlingRights = CastleRights(True,True,True,True)
        self.castleRightsLog = [copy.deepcopy(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))]
        self.enPassantLog = [copy.deepcopy(self.enpassantPossible)]
        self.whiteCastle = False
        self.blackCastle = False
        self.turn = 1
        self.boardLog = [copy.deepcopy(self.board)]
        self.validMoves = []



    '''
    Takes a move as a parameter and changes the board accordingly.
    Will not work for castling or enpassant.
    '''
    def makeMove(self, move):
        #print("*********boardlog before move")
        #print(self.boardLog)


        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        #print(move.pieceMoved)
        self.moveLog.append(move) #log the move
        self.whiteToMove = not self.whiteToMove #swap players
        #update kings location if moved
        if move.pieceMoved == "wK":
            self.whiteKinglocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKinglocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
            #print("Pawn Promotion")

        #enpassant move
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--" #capturing the pawn

        #update enPassantPossible
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        #castle
        if move.isCastleMove: #the kings position/movement is stored in the move
            if move.endCol - move.startCol == 2: #kingside castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves the rook from its home square to the castled square
                self.board[move.endRow][move.endCol + 1] = "--" #removes the rook from that space

            else: #queenside castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"
            if self.whiteToMove:
                self.whiteCastle = True
            else:
                self.blackCastle = True

        #update castlingRights
        self.updateCastleRights(move)
        self.castleRightsLog.append(copy.deepcopy(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)))
        self.enPassantLog.append(copy.deepcopy(self.enpassantPossible))

        if self.whiteToMove:
            self.turn += 1


        self.boardLog.append(copy.deepcopy(self.board))
        #print("*********boardlog after move")
        #print(self.boardLog)



    '''
    This will undo the last move.
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured

            #update the king if moved
            if move.pieceMoved == "wK":
                self.whiteKinglocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKinglocation = (move.startRow, move.startCol)
            #undo enPassant move
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--" #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                #making sure that the enpassant is possible again

            self.enPassantLog.pop()
            self.enpassantPossible = self.enPassantLog[-1]

            #undo castle Rights
            self.castleRightsLog.pop() #gets rid of the last element
            castleRights = copy.deepcopy(self.castleRightsLog[-1])
            self.currentCastlingRights = castleRights #changes it to the last element in the list
            #print(self.currentCastlingRights.wks,self.currentCastlingRights.wqs,self.currentCastlingRights.bks,self.currentCastlingRights.bqs)

            #undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else: #queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol + 1] = "--"
                if self.whiteToMove:
                    self.whiteCastle = False
                else:
                    self.blackCastle = False

            self.whiteToMove = not self.whiteToMove

            self.boardLog.pop()
            self.checkMate = False
            self.staleMate = False

    '''
    This method checks if a draw has occured. A draw by repetition occurs when 2 players reach the same position 
    3 times in a game. 
    '''
    def checkRepetition(self):

        for i in range(len(self.boardLog)):
            counter = 1
            for j in range(i + 1, len(self.boardLog)):
                if self.isEqualToBoard(self.boardLog[i], self.boardLog[j]):
                    counter += 1
            if counter == 3:
                return True

        return False


    '''
    Checks if the board is the exact same as another time
    '''
    def isEqualToBoard(self, boardOne, boardTwo):
        for row in range(len(boardOne)):
            for col in range(len(boardOne[row])):
                if boardOne[row][col] != boardTwo[row][col]:
                    return False
        return True




    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRights.bks = False

        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False



    '''
    All moves considering the possibility that the opponent may capture the king 
    on their turn.
    '''
    def getValidMoves(self):
        turn = self.turn
        tempEnpassantPossible = self.enpassantPossible

        boardLog = self.boardLog
        #print("*************boardLog before valid MOves")
        #print(self.boardLog)

        #for log in self.castleRightsLog:
           #print(log.wks, log.wqs, log.bks, log.bqs)
        tempCastlingRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                          self.currentCastlingRights.wqs, self.currentCastlingRights.bqs) #copy the current castling rights
        # 1. generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKinglocation[0], self.whiteKinglocation[1], moves)
        else:
            self.getCastleMoves(self.blackKinglocation[0], self.blackKinglocation[1], moves)
        #lets pretend whiteToMove is True, meaning it is white's turn

        # 2. for each move, make the moves
        for i in range(len(moves) - 1, -1 , -1): #going backwards through the list

            self.makeMove(moves[i])
            #whiteToMove will be changed to False because the move is made

            # 3. generate all opponents moves
            # 4. for each opponent move, see if it attacks the king
            self.whiteToMove = not self.whiteToMove
            #to check if White is under attack we need to swap the variable again so whiteToMove is True
            if self.inCheck():
                # 5. if they do attack the kind, remove the move from valid moves
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            #whiteToMove is False now because undoMove will make it True
            self.undoMove() # ends up back with whiteToMove being True




        if len(moves) == 0: #either chekmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            staleCheck = ["wK","bK","--"]
            self.staleMate = True
            #only 2 kings left on the board
            for row in range(len(self.board)):
                for col in range(len(self.board[row])):
                    if self.board[row][col] not in staleCheck: #found a piece that is not a king
                        self.staleMate = False
            self.checkMate = False
        #if self.checkRepetition():
            #self.staleMate = True
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastlingRights
        self.turn = turn
        self.boardLog = boardLog
        #print("*************boardLog after valid MOves")
        #print(self.boardLog)
        self.validMoves = moves
        return moves

    '''
    Will determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKinglocation[0], self.whiteKinglocation[1])
        else:
            return self.squareUnderAttack(self.blackKinglocation[0], self.blackKinglocation[1])
    '''
    Will determine if the enemy can attack the square row,col
    '''
    def squareUnderAttack(self,row,col):
        self.whiteToMove = not self.whiteToMove #switch to opponent moves
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch the turn back
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False


    '''
    All moves without considering the possibility that the opponent may capture the king.
    '''
    def getAllPossibleMoves(self):

        moves = []  # list of move objects Move((6, 4), (4, 4), self.board)
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                color = self.board[row][col][0]
                if (color == "w" and self.whiteToMove) or (color == "b" and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    #if piece == "R":
                        #print("Rook on col " + str(col))
                    self.moveFunctions[piece](row, col, moves)

        return moves


    '''
    Generates all possible pawn moves for the Pawn located at row,col.
    Checks if pawn is capable of moving 2 squares at once. 
    STILL NEED TO IMPLEMENT ENPASSANT AND PROMOTION 
    '''
    def getPawnMoves(self, row, col, moves):

        if self.whiteToMove:
            if self.board[row-1][col] == "--": #the space in front is empty
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row-2][col] == "--": #pawn has not moved
                    moves.append(Move((row, col), (row-2, col), self.board))

            #POSSIBLE CAPTURES
            if col - 1 >= 0: #to the left
                if self.board[row-1][col-1][0] == 'b':
                    moves.append(Move((row, col), (row-1, col-1), self.board))
                elif (row-1,col-1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row-1, col-1), self.board, isEnpassantMove=True))

            if col + 1 <= 7: #to the right
                if self.board[row-1][col+1][0] == 'b':
                    moves.append(Move((row, col), (row-1, col+1), self.board))
                elif (row-1,col+1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row-1, col+1), self.board, isEnpassantMove=True))

        else: #black's turn
            if self.board[row + 1][col] == "--":  # the space in front is empty
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))

            #POSSIBLE CAPTURES
            if col - 1 >= 0: #captures to the left
                if self.board[row + 1][col-1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col-1), self.board))
                elif (row+1,col-1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row+1, col-1), self.board, isEnpassantMove=True))
            if col + 1 <= 7: #captures to the right
                if self.board[row + 1][col+1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col+1), self.board))
                elif (row+1,col+1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row+1, col+1), self.board, isEnpassantMove=True))



    '''
    Generates all possible rook moves for the Rook located at row,col.
    Rooks move up and down and left and right.
    '''
    def getRookMoves(self, row, col, moves):

        startRow = row
        startCol = col

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for direction in directions:
            row = startRow #resets the value back to the start for each iteration
            col = startCol
            row += direction[0] #starts with the first iteration increment
            col += direction[1]

            while 0 <= row < 8 and 0 <= col < 8:
                if self.board[row][col] == "--": #blank space
                    #print("Rook Move: [" +  str(row) +  ", " + str(col) + "]")
                    moves.append(Move((startRow,startCol),(row,col), self.board))
                    row += direction[0]
                    col += direction[1]
                elif self.turnValues[self.board[row][col][0]] != self.whiteToMove:
                    moves.append(Move((startRow, startCol), (row, col), self.board))
                    break
                else: #same piece found
                    break



    '''
    Generates all possible Knight moves for the Knight located at row,col.
    Knight moves in the following directions:
    Up 2 left 1
    Up 2 right 1
    Down 2 left 1
    Down 2 right 1
    Right 2 up 1
    Right 2 down 1
    Left 2 up 1
    Left 2 down 1
    '''
    def getKnightMoves(self, row, col, moves):

        possibleKnightMoves = [(-1, 2), (1, 2), (-1, -2), (1, -2),
                               (2, 1), (2, -1), (-2, 1), (-2, -1)]
        for move in possibleKnightMoves:
            rowCheck = row + move[0]
            colCheck = col + move[1]
            if 0 <= rowCheck < 8 and 0 <= colCheck < 8: #checks the bounds
                if self.board[rowCheck][colCheck] == "--" or self.turnValues[self.board[rowCheck][colCheck][0]] != self.whiteToMove:
                    moves.append(Move((row, col), (rowCheck, colCheck), self.board))


    '''
    Generates all possible Bishop moves for the Bishop located at row,col
    Bishop moves diagonally in increments of:
    [1, 1] , [1, -1], [-1, 1], [-1, -1]
    '''
    def getBishopMoves(self, row, col, moves):

        startRow = row
        startCol = col

        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for direction in directions:
            row = startRow #resetting back to the original position
            col = startCol
            row += direction[0] #adding the values needed
            col += direction[1]
            while 0 <= row < 8 and 0 <= col < 8: #bound checking
                if self.board[row][col] == "--": #blank space found so valid
                    moves.append(Move((startRow, startCol), (row, col), self.board))
                    row += direction[0]
                    col += direction[1]
                elif self.turnValues[self.board[row][col][0]] != self.whiteToMove: #opposing piece found
                    moves.append(Move((startRow, startCol), (row, col), self.board))
                    break #cant look past the opposing piece
                else: #same color piece
                    break



    '''
    Generates all possible Queen moves for the Queen located at row,col
    The queen moves both diagonally like a bishop and horizontally and vertically like a rook
    '''
    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)


    '''
    Generates all possible King moves for the King located at row,col
    '''
    def getKingMoves(self,row, col, moves):

        possibleKingMoves = [(0, 1), (1, 0), (-1, 0), (0, -1),
                             (1, -1), (-1, 1), (1, 1), (-1, -1)]
        for move in possibleKingMoves:
            rowCheck = row + move[0]
            colCheck = col + move[1]
            if 0 <= rowCheck < 8 and 0 <= colCheck < 8: #checks the bounds
                if self.board[rowCheck][colCheck] == "--" or self.turnValues[self.board[rowCheck][colCheck][0]] != self.whiteToMove:
                    moves.append(Move((row, col), (rowCheck, colCheck), self.board))



    '''
    Generates all valid moves for castling if there are any and adds them to the moves. 
    '''

    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row,col):
            return #cant castle
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(row, col, moves)

    def getKingSideCastleMoves(self, row, col, moves):
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--":
            if not self.squareUnderAttack(row,col+1) and not self.squareUnderAttack(row, col+2):
                #print("kingside valid")
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove = True))

    def getQueenSideCastleMoves(self, row, col, moves):
        if self.board[row][col-1] == "--" and self.board[row][col-2] == "--" and self.board[row][col-3] == "--":
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                #print("queenside valid")
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs




'''
This class is responsible for creating moves, mapping them out, and for notation purposes.
'''
class Move():

    # maps keys to values
    # key : value

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        # No piece captured would make piece.captured = "--"
        self.pieceCaptured = board[self.endRow][self.endCol]

        #pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.isPawnPromotion = True

        #enPassant
        self.isEnPassantMove = isEnpassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        self.isCastleMove = isCastleMove

        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #creates a unique move id for each move because no 2 pieces can make the same move


    # @override equals method
    def __eq__(self, other):
        if isinstance(other, Move) :
            return self.moveId == other.moveId


    '''
    Creates the appropriate chess notation for the pieces
    '''
    def getChessNotation(self):
        #return = self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "P":
                if self.isPawnPromotion: #pawn captures and promotes
                    return self.colsToFiles[self.startCol] + "x" + self.getRankFile(self.endRow, self.endCol) + "=Q"
                return self.colsToFiles[self.startCol] + "x" + self.getRankFile(self.endRow, self.endCol) #normal pawn capture
            else:
                return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol) #other pieces capture
        else: #captured square is blank
            if self.pieceMoved[1] == "P":
                if self.isPawnPromotion:#pawn just promotes
                    return self.getRankFile(self.endRow, self.endCol) + "=Q"
                if self.startCol != self.endCol: #enpassant
                    return self.colsToFiles[self.startCol] + "x" + self.getRankFile(self.endRow, self.endCol)
                return self.getRankFile(self.endRow, self.endCol) #pawn just moved forward
            elif self.pieceMoved[1] == "K" and self.endCol - self.startCol == 2: #Kingside Castle
                return "O - O"
            elif self.pieceMoved[1] == "K" and self.startCol - self.endCol == 2: #QueenSide Castle
                return "O - O - O"
            else:
                return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol) #piece moves to another square


    '''
    Helper method for finding the rank and file for chess Notation.
    '''
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]