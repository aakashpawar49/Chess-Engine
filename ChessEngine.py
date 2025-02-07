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
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, 
                                            self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]



    '''
    Takes a Move as a parameter and executes it (this will not work for castling, pawn protection and en-passant )
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players
        #update the king's location if moved
        if move.pieceMoved == 'bK':
            self.kingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.kingLocation = (move.endRow, move.endCol)

            #pawn promotion
            if move.isPawnPromotion:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

            #enpassant move 
            if move.isEnpassantMove:
                self.board[move.startRow][move.endCol] = '--' #capturing the pawn


            #update enpassantPossible variables
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
                self.enpassantPossible = ((move.startRow + move.endCol)//2, move.startCol)
            else:
                self.enpassantPossible = ()

            #castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside castle move
                    self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol+1] #moves the rook
                    self.board[move.endRow][move.endCol + 1] = '--' #erase old rook
                else: #queenside castle move
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol-2] #moves the rook
                    self.board[move.endRow][move.endCol - 2] = '--' #erase
            #update castling rights - whenever it is a rook or a king move
            self.updateCastleRights(move)
            self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, 
                                                self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
            
            

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns back
            #update the king's position if needed
            if move.pieceMoved == 'wK':
                self.kingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'wK':
                self.kingLocation = (move.startRow, move.startCol)
            #undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][moe.endCol] = '--' #leave landing sqaure blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            #undo castling rights
            if self.castleRightsLog:
                self.castleRightsLog.pop() #only pop if there are elements 
            #get rid of the new castle rights from the move we are moving
            if self.castleRightsLog:
                self.currentCastlingRights = self.castleRightsLog[-1] #get the last castle
            else:
                self.currentCastlingRights = None # or set to default castling rights
            # self.currentCastlingRight = self.castleRightsLog[-1]   #set the current castle rights to the last one in the list
            #undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #king side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            #ADD THESE
            self.checkmate = False
            self.stalemate = False

    '''
    Update the castle rights given the move
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.wks = False  # Fixed typo here
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.bks = False  # Fixed typo here
          
    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs) #copt current castling rights
        #1.) Generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        #2.) for each move, make the move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            #3.) Generate all opponent's moves
            #4.) for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) #5.) if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: #either checkmate or stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves
    '''
    Determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.sqaureUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.sqaureUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
            
    '''
    Determine if the enemy can attack the sqaure r, c
    '''
    def sqaureUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square is under attack
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
                    elif (r-1, c-1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))                      
                if c+1 <= 7: #captures to the right
                    if self.board[r-1][c+1] == 'b' : #enemy piece to capture
                        moves.append(Move((r, c), (r-1, c+1), self.board))
                    elif (r-1, c+1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))                      


        else: #black pawn moves
            if self.board[r + 1][c] == "--":   # 1 sqaure move
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 sqaure moves
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # captures
            if c - 1 >= 0: #capture to left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c),(r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))                      
            if c + 1 <= 7: # capture to right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c),(r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))                      
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
        # self.getCastleMoves(r, c, moves, allyColor)

    '''
    Generate all valid castle moves for the king at (r, c) and add these to the list of moves
    '''
    def getCastleMoves(self, r, c, moves):
        if self.sqaureUnderAttack(r, c):
            return  # can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.sqaureUnderAttack(r, c+1) and not self.sqaureUnderAttack(r, c+2):
                moves.append(CastleMove((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':  # Check for 3 empty spaces
            if not self.sqaureUnderAttack(r, c-1) and not self.sqaureUnderAttack(r, c-2):
                moves.append(CastleMove((r, c), (r, c-2), self.board, isCastleMove=True))  # Fixed castling logic for queenside


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    # Maps ranks (1-8) to rows (7-0) and vice versa
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    # Maps files (a-h) to columns (0-7) and vice versa
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion 
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # en passant 
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        #castle move
        self.isCastleMove = isCastleMove

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