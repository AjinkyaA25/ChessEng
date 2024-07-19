import random
import copy

pieceScores = {"K": 1.5, "Q": 9, "N": 3, "B": 3, "P": 1, "R": 5}
KnightScore = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]

BishopScore = [[2, 1, 1, 1, 1, 1, 1, 2],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [2, 1, 1, 1, 1, 1, 1, 2]]

RookScore =   [[1, 1, 3, 4, 4, 3, 1, 1],
               [3, 4, 4, 4, 4, 4, 4, 3],
               [1, 2, 2, 3, 3, 2, 2, 1],
               [2, 2, 2, 3, 3, 2, 2, 2],
               [2, 2, 2, 3, 3, 2, 2, 2],
               [1, 2, 2, 3, 3, 2, 2, 1],
               [3, 4, 4, 4, 4, 4, 4, 3],
               [1, 1, 3, 4, 4, 3, 1, 1]]

QueenScore =  [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 3, 3, 2, 2, 1],
               [1, 1, 3, 3, 3, 3, 1, 1],
               [1, 1, 3, 4, 4, 3, 1, 1],
               [1, 1, 3, 4, 4, 3, 1, 1],
               [1, 1, 3, 3, 3, 3, 1, 1],
               [1, 2, 2, 3, 3, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]

KingScore =   [[2, 2, 3, 1, 1, 1, 3, 2],
               [2, 2, 2, 1, 1, 1, 2, 2],
               [1, 1, 1, 1, 1, 1, 1, 1],
               [1, 1, 1, 1, 1, 1, 1, 1],
               [1, 1, 1, 1, 1, 1, 1, 1],
               [1, 1, 1, 1, 1, 1, 1, 1],
               [2, 2, 2, 1, 1, 1, 2, 2],
               [2, 2, 3, 1, 1, 1, 3, 2]]

WhitePawnScore = [[1, 1, 1, 1, 1, 1, 1, 1],
                  [4, 4, 4, 4, 4, 4, 4, 4],
                  [2, 2, 2, 2, 2, 2, 2, 2],
                  [2, 2, 2, 3, 3, 2, 2, 2],
                  [1, 1, 4, 4, 4, 2, 1, 1],
                  [2, 1, 2, 4, 4, 1, 1, 2],
                  [1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1]]

BlackPawnScore = [[1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1],
                  [2, 1, 2, 4, 4, 1, 1, 2],
                  [1, 1, 4, 4, 4, 2, 1, 1],
                  [2, 2, 2, 3, 3, 2, 2, 2],
                  [2, 2, 2, 2, 2, 2, 2, 2],
                  [4, 4, 4, 4, 4, 4, 4, 4],
                  [1, 1, 1, 1, 1, 1, 1, 1]]


piecePositionScores = {"N" : KnightScore, "B" : BishopScore, "R" : RookScore,
                       "Q" : QueenScore, "K" : KingScore, "bP": BlackPawnScore, "wP": WhitePawnScore}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4
gsList = []
nextMoveList = []
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

'''
Finds the best move ONLY on depth 2 because there are only 2 for loops, one for your moves and one for the response to those moves
Implements the algorithm without recursion
'''
def findBestMoveMinMaxWithoutRecursion(gs, validMoves):
    turn = gs.turn
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves: #if it was white's turn
        gs.makeMove(playerMove) #make the move for white

        opponentsMoves = gs.getValidMoves()
        oppMaxScore = -CHECKMATE
        for oppMove in opponentsMoves:
            #finds the best possible move that black can make
            gs.makeMove(oppMove) #make the move for black
            if gs.checkMate:
                score = - turnMultiplier * CHECKMATE #meaning that black can checkmate white in 2 moves. Bad for white
            elif gs.staleMate:
                score = STALEMATE
            else: #if better move for black found
                score = -turnMultiplier * scoreBoard(gs)
            if score > oppMaxScore:
                oppMaxScore = score


            gs.undoMove()

        if oppMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = oppMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
        gs.turn = turn #resets turn from any modifications
    return bestPlayerMove


'''
Helper method to make the first recursive call
start alpha at the lowest maximum score to get better 
start beta at the highest maximum score to get better
'''
def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    turn = gs.turn
    nextMove = None
    nextMovelist = []
    gs.validMoves = validMoves
    gsList.append(copy.deepcopy(gs))
    #findMoveMinMax(gs, validMoves,DEPTH, gs.whiteToMove)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    gs.turn = turn #turn changes because of the makeMove function
    returnQueue.put(nextMove)

'''
MinMax algorithm with recursion
'''
def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)
    random.shuffle(validMoves)

    if whiteToMove:
        maxScore = -CHECKMATE #worst score possible
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH: #only sets a move if you are at the first call of the stack otherwise it may return a move that is not available
                    nextMove = move
                    print(maxScore)
            gs.undoMove()
            return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
                    print(minScore)
            gs.undoMove()
            return minScore


'''
Finds the best move in a smaller algorithm compared to findMoveMinMax because the negative sign will 
end up returning the highest value regardless of the player color. 
'''
def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    random.shuffle(validMoves)
    if depth == 0: #base case
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        #negative sign makes it so that black's best move is white's worst move
        #should always return a positive value regardless of whose turn because of -turn multiplier
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)

        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


'''
If a move is found that makes the opponents position very good, then do not look any further for that variation.
@:param alpha is the upper bound while @:param beta is the lower bound
if maxScore is greater than alpha, then maxScore becomes the new alpha value
if alpha becomes greater than beta, then break out of that branch
-beta becomes the new alpha
-alpha become the new beta because it will be the opposite players turn
'''
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    random.shuffle(validMoves)
    if depth == 0: #base case
        return turnMultiplier * scoreBoard(gs)
    
    #move ordering - implement later for better pruning

    maxScore = -CHECKMATE
    for move in validMoves:

        gs.makeMove(move)
        nextMoves = validMovesFinder(gs, gsList)
        #negative sign makes it so that black's best move is white's worst move
        #should always return a positive value regardless of whose turn because of -turn multiplier
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)

        if score > maxScore:
            if depth == DEPTH:
                nextMoveList.append(move)
                if gs.staleMate or gs.checkRepetition(): #after the move is made is it a draw
                    if score >= 4: #winning by more than 4
                        nextMoveList.pop()
                        if len(nextMoveList) != 0:
                            nextMove = nextMoveList[-1]
                            print("Stalemate avoided")
                        else:
                            nextMove = move


                else:
                    maxScore = score
                    nextMove = nextMoveList[-1]
                if len(nextMoveList) != 0 and nextMove != None:
                    print(nextMove.getChessNotation(), score)
            else:
                maxScore = score

        gs.undoMove()
        #pruning
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


'''
Score the board on a more complex level.
Positive score is good for white.
Negative score is good for black.
If gs.whiteToMove is True, that means black has just played the last move and vice versa
'''
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:  # white got checkmated. Very good for black
            return -CHECKMATE
        else:
            return CHECKMATE  # black got mated

    score = 0
    piecePositionScore = 0
    totalPieceScore = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                # score positionally
                if square[1] == "P":  # pawns
                    piecePositionScore = piecePositionScores[square][row][col] * 0.1
                else:  # other pieces
                    piecePositionScore = piecePositionScores[square[1]][row][col] * 0.1
                # score by material
                if square[0] == "w":
                    totalPieceScore += pieceScores[square[1]]
                    score += pieceScores[square[1]] + piecePositionScore
                elif square[0] == "b":
                    totalPieceScore -= pieceScores[square[1]]
                    score -= pieceScores[square[1]] + piecePositionScore

    return score


'''
Will return the valid moves of a prior game state if the same position has been reached before.
If that position is different from all the gamestates, then it will generate new moves.
The goal of this method is to decrease the amount of times generating valid moves.
'''
def validMovesFinder(gs, gsList):
    for gameState in gsList:
        if gameState.whiteToMove == gs.whiteToMove: #if it is the same persons turn
            for row in range(len(gs.board)):
                for col in range(len(gs.board[row])):
                    if gs.board[row][col] != gameState.board[row][col]: #break if not the same board
                        gs.validMoves = gs.getValidMoves()
                        gsList.append(copy.deepcopy(gs))
                        #print(str(row) + "," +  str(col) + gs.board[row][col] + "###########" + gameState.board[row][col])
                        #print("different boards at " + str(row) + "," + str(col) + "......... PIECE IS" + gs.board[row][col])
                        return gs.validMoves
            #found the same board state prior
            #does not check for castling/enpassant changes
            print("same board state found")
            return gameState.validMoves
        else:
            #print("opposing turn")
            gs.validMoves = gs.getValidMoves()
            gsList.append(copy.deepcopy(gs))
            return gs.validMoves