import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0


'''
Picks and returns a random move.
'''
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

'''
Find the best move based on material alone.
'''
def findBestMoves():
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.validMoves()
        opponentMaxScore = -CHECKMATE
        for opponentsMoves in opponentsMoves:
            gs.makeMove(opponentsMoves)
            if gs.checkmate:
                score = -turnMultiplier * CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove 
        gs.undoMove()
    return bestPlayerMove

'''
Find the best move based on material alone.
'''
def scoreMaterial(board):
    score = 0
    for row in board:
        for sqaure in row:
            if sqaure[0] == 'w':
                score += pieceScore[square[1]]
            elif sqaure[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score            


