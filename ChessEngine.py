"""
This class is responsible for storing all the information about the current state of a chess game. It will also be
responsible for determining the valid moves at the current state. It will also keep a move log.
"""
class GameState():
    def __init__(self):
        #board is an 8x8 2d list, each element of the list has 2 characters.
        #The first character represents the color of the piece, 'b' or 'w'
        #The second character represents tge type of piece, 'K','Q','R','B','N' or 'P'
        # "--" represents an empty space with no piece
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"], 
            ["--","--","--","--","--","--","--","--"], 
            ["--","--","--","--","--","--","--","--"], 
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        self.moveFunctions = {'p':self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False


    '''
    Takes a Move as a parameter and executes it (this will not work for castling, pawn protection and en-passant )
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players
        #update the king's location if it has moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)


    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns back
            #update the king's move
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.StartRow, move.StartCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.endRow, move.endCol)

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        #1.) Generate all possible moves
        moves = self.getAllPossibleMoves()
        #2.) For each move, make the move
        for i in range(len(moves)-1, -1, -1):    #when removing from a list go backwards through that list
            self.makeMove(moves[i])
            #3.) Generate all oponents moves
            #4.) for each of the opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])#5.) if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  #wither checkmate or stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        return moves
        
    def inCheck(self):
        if self.whiteToMove:
            return self.sqaureUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.sqaureUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def sqaureUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #sqaure is under attack
                return True
        return False



    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):          #number of rows
            for c in range(len(self.board[r])):   #number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls the appropriate move function
        return moves

    ''' 
    Get all the pawn moves for the pawn located at row, col and add these moves to list
    '''
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:   #white pawn moves
            if self.board[r - 1][c] == "--":  #1 sqaure pawn advance
                moves.append(Move((r, c), (r-1, c),self.board))
                if r == 6 and self.board[r-2][c] == "--":  #2 sqaure pawn advance
                    moves.append(Move((r, c), (r-2, c),self.board))
                if c-1 >= 0: #capture to the left
                    if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                if c+1 <= 7: #captures to the right
                    if self.board[r-1][c+1] == 'b' : #enemy piece to capture
                        moves.append(Move((r, c), (r-1, c+1), self.board))
        else: #black pawn moves
            if self.board[r + 1][c] == "--":   # 1 sqaure move
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 sqaure moves
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # captures
            if c - 1 >= 0: #capture to left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c),(r + 1, c - 1), self.board))
            if c + 1 <= 7: # capture to right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c),(r + 1, c + 1), self.board))
        #add pawn promotions later

    ''' 
    Get all the Rook moves for the pawn located at row, col and add these moves to list
    '''
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = r + d[1] * i
                if 0 <= endRow < 8 and 0<= endCol < 8:      #on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":                    #empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:         #enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:                                   # friendly piece invalid
                        break
                else:           #off board
                    break

    ''' 
    Get all the Bishop moves for the pawn located at row, col and add these moves to list
    '''
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))   # 4 diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):                           # bishop can move max of 7 squares
                endRow = r + d[0] * i
                endCol = r + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:     #is it on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":                    # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:         # enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:                                   # friendly piece invalid
                        break
                else:                                       #off board
                    break

    ''' 
    Get all the Knight for the pawn located at row, col and add these moves to list
    '''
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:             #not an ally piece(empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    ''' 
    Get all the Queen moves for the pawn located at row, col and add these moves to list
    '''
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)    


    ''' 
    Get all the king moves for the pawn located at row, col and add these moves to list
    '''
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:             #not an ally piece(empty or enemy
                    moves.append(Move((r, c), (endRow, endCol), self.board))



class Move():
    # Maps ranks (1-8) to rows (7-0) and vice versa
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    # Maps files (a-h) to columns (0-7) and vice versa
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # Generates chess notation for the move
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]








# class Move():
#     #maps keys to values
#     # key : value
#     ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4": 4,
#                    "5" : 3, "6" : 2, "7" : 1, "8": 0}
#     rowsToRanks = {v: k for k, v in filesToCols.items()}
#     filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
#                    "e": 4, "f": 5, "g": 6, "h": 7}
#     colToFiles = {v: k for k, v in filesToCols.items()}

#     def __init__(self, startSq, endSq, board):
#         self.startRow = startSq[0]
#         self.startCol = startSq[1]
#         self.endRow = endSq[0]
#         self.endCol = endSq[1]
#         self.pieceMoved = board[self.startRow][self.startCol]
#         self.pieceCaptured = board[self.endRow][self.endCol]

#     def getChessNotation(self):
#         #you can add to make this like real chess notation
#         return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

#     def getRankFile(self, r, c):
#         return self.colsToFiles[c] + self.rowsToRanks[r]