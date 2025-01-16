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
        self.whiteToMove = True
        self.moveLog = []


    '''
    Takes a Move as a parameter and executes it (this will not work for castling, pawn protection and en-passant )
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players


    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns back


    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        return self.getAllPossibleMoves() #for now we will not worry about checks
        
    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = [Move((6,4),(4,4), self.board)]
        for r in range(len(self.board)):          #number of rows
            for c in range(len(self.board[r])):   #number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
        return moves

    ''' 
    Get all the pawn moves for the pawn located at row, col and add these moves to list
    '''
    def getPawnMoves(self, r, c, moves):
        pass


    ''' 
    Get all the Rook moves for the pawn located at row, col and add these moves to list
    '''
    def getRookMoves(self, r, c, moves):
        pass

    

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