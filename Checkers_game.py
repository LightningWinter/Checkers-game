print('SLAI Game Development research project')

import turtle
import tkinter
import math
import copy
from icecream import ic


class Board:

    def __init__(self):
        self.data = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]

    def __getitem__(self, indicies):
        return (self.data[indicies[0]][indicies[1]])

    def __setitem__(self, indicies, value):
        self.data[indicies[0]][indicies[1]] = value

    def __str__(self):
        return str(self.data)

    def updateBoard(self, row, column, value):
        self.__setitem__(self.data[row][column], value)


class Player:
    def __init__(self,isPlayer1):
        self.isPlayer1 = isPlayer1
        self.pieces = []
        self.won = False
        self.captureMoves = []
        self.piecesWithCaptures = []

class humanPlayer(Player):
    def __init__(self,isPlayer1):
        super().__init__(isPlayer1)
        self.isComputerPlayer = False


class computerPlayer(Player):
    def __init__(self, isPlayer1):
        super().__init__(isPlayer1)
        self.isComputerPlayer = True
    

    def getComputerMove(self, gameApp, position):
        #The move selection process should start with the best eval found being the worst case scenario, depending on if the computer is first or second. For the first player, player 1, worst case scenario is -inf for all moves. For second player, worst case scenario is inf for all moves.
        if self.isPlayer1:
            bestEval = -math.inf
        else:
            bestEval = math.inf
        bestMove = []
        pieceMoving = None
        gameApp.calculatePiecesWithCaptures(self, gameApp.board)
        
        #If there are captures
        if len(self.piecesWithCaptures) > 0:
            for piece in self.piecesWithCaptures:
                moves = gameApp.determinePieceCaptures(piece,gameApp.board)
                piecePosition = [piece.rowIndex,piece.colIndex]
                
                for move in moves:
                    print("\n\nNEW BASE CAPTURE BRANCH\n\n")
                    newPosition = position.createCopyPosition()
                    newPieceMoving = newPosition.board[piecePosition[0],piecePosition[1]]     
                    captureSquare = gameApp.determineCaptureSquare(move,newPieceMoving)
                    newPosition.board = newPieceMoving.movePieceInMinimax(piecePosition,move,newPosition.board)
                    if newPosition.board[captureSquare[0],captureSquare[1]] in newPosition.player1.pieces:
                        newPosition.player1.pieces.remove(newPosition.board[captureSquare[0],captureSquare[1]])
                    elif newPosition.board[captureSquare[0],captureSquare[1]] in newPosition.player2.pieces:
                        newPosition.player2.pieces.remove(newPosition.board[captureSquare[0],captureSquare[1]])
                    newPosition.board[captureSquare[0],captureSquare[1]] = 0
                    newPosition.player1ToMove = not(newPosition.player1ToMove)
                    print("getting Eval")
                    eval = gameApp.minimax(3, newPosition, self, -math.inf, math.inf)
                    if self.isPlayer1:
                        if bestMove == []:
                            bestEval = eval
                            bestMove = move
                            pieceMoving = piece
                        if eval > bestEval:
                            bestEval = eval
                            bestMove = move
                            pieceMoving = piece
                    else:
                        if bestMove == []:
                            bestEval = eval
                            bestMove = move
                            pieceMoving = piece
                        if eval < bestEval:
                            bestEval = eval
                            bestMove = move
                            pieceMoving = piece
        #If there aren't any captures
        else:
            for piece in self.pieces:
                #areCaptures will always be false here
                moves, areCaptures = gameApp.determinePieceMoves(piece, gameApp.board)
                piecePosition = [piece.rowIndex,piece.colIndex]
                for move in moves:
                    print("\n\nNEW BASE NON CAPTURE BRANCH\n\n")
                    #when i programmed determinePieceMoves I for some reason returned the moves in backwards order, the below line is to correct that (im too lazy to fix it properly)
                    move[0],move[1] = move[1],move[0]
                    newPosition = position.createCopyPosition()
                    newPieceMoving = newPosition.board[piecePosition[0],piecePosition[1]]
                    newPosition.board = newPieceMoving.movePieceInMinimax(piecePosition,move,newPosition.board)
                    newPosition.player1ToMove = not(newPosition.player1ToMove)
                    eval = gameApp.minimax(3,newPosition,self, -math.inf, math.inf)
                    if self.isPlayer1:
                        if bestMove == []:
                            bestEval = eval
                            bestMove = move
                            pieceMoving = piece
                        if eval > bestEval:
                            bestEval = eval
                            bestMove = move
                            pieceMoving = piece
                    else:
                        if bestMove == []:
                            bestEval = eval
                            bestMove = move
                            pieceMoving = piece
                        if eval < bestEval:
                            bestEval = eval
                            bestMove = move
                            pieceMoving = piece
        print("Evaluation: ",bestEval)
        gameApp.currentComputerEval.set(str(bestEval))
        return(bestMove, pieceMoving)


    def handleCaptureChainInMinimax(self, gameApp, piece, position, moves):
        #Assumes that a follow up capture has been detected in the position passed to this function
        piecePosition = [piece.rowIndex, piece.colIndex]
        for move in moves:
            newPosition = position.createCopyPosition()
            newBoard = newPosition.board
            newPieceMoving = newBoard[piecePosition[0],piecePosition[1]]
            if newPosition.player1ToMove:
                opposingPlayer = newPosition.player2
            else:
                opposingPlayer = newPosition.player1
            newPieceMoving = newBoard[piecePosition[0],piecePosition[1]]
            captureSquare = gameApp.determineCaptureSquare(move, newPieceMoving)
            try:
                
                opposingPlayer.pieces.remove(newBoard[captureSquare[0],
                                                    captureSquare[1]])
                newBoard[captureSquare[0], captureSquare[1]] = 0
            except:
                print("no")
                pass
            newBoard = newPieceMoving.movePieceInMinimax([newPieceMoving.rowIndex, newPieceMoving.colIndex],[move[0],move[1]], newBoard)
            if position.player1ToMove:
                newPosition = minimaxPosition(newBoard, newPosition.player1, opposingPlayer, newPosition.player1ToMove)
            else:
                newPosition = minimaxPosition(newBoard, opposingPlayer, newPosition.player2, newPosition.player1ToMove)
                
            #check if there is a follow up capture for the piece being examined. If so, recusively call this function again. 
            followUpMoves = gameApp.determinePieceCaptures(newPieceMoving, newPosition.board)
            if len(followUpMoves) > 0:
                branchEndPositions = self.handleCaptureChainInMinimax(gameApp, newPieceMoving, newPosition, followUpMoves)
                for Position in branchEndPositions:
                    yield(Position)
                
            
            else:
                yield(newPosition)
            

        
    def generateChildPositions(self, gameApp, position):
        #Creates a generator object via yeild that returns child boards one by one as it's called. This saves memory, because each board will only be used once in minimax anyway.
        board = position.board
        if position.player1ToMove:
            currentPlayer = position.player1
            opposingPlayer = position.player2
        else:
            currentPlayer = position.player2
            opposingPlayer = position.player1
        piecesWithCaptures = gameApp.calculatePiecesWithCaptures(currentPlayer, board)
        if len(piecesWithCaptures) > 0:
            for piece in piecesWithCaptures:
                moves = gameApp.determinePieceCaptures(piece, board)
                piecePosition = [piece.rowIndex,piece.colIndex]
                for move in moves:
                    newPosition = position.createCopyPosition()
                    newBoard = newPosition.board
                    newPieceMoving = newBoard[piecePosition[0],piecePosition[1]]
                    if newPosition.player1ToMove:
                        newCurrentPlayer = newPosition.player1
                        newOpposingPlayer = newPosition.player2
                    else:
                        newCurrentPlayer = newPosition.player2
                        newOpposingPlayer = newPosition.player1
                    
                    # CRUCIAL: FIGURE OUT HOW TO HANDLE PLAYER PIECE LISTS IN MINIMAX TREE!!!!!
                    #THIS PART OF THE FUNCTION IS NOT DONE!!!
                    captureSquare = gameApp.determineCaptureSquare(
                    move, newPieceMoving)
                    #ic(newBoard[captureSquare[0], captureSquare[1]])
                    if newBoard[captureSquare[0], captureSquare[1]] in newCurrentPlayer.pieces:
                        print("damn")
                        gameApp.showPositionBoard(position.board)
                        ic(captureSquare)
                        ic(newPieceMoving.isPlayer1)
                        ic(newPieceMoving.rowIndex)
                        ic(newPieceMoving.colIndex)
                        ic(newBoard[captureSquare[0],captureSquare[1]].isPlayer1)
                        ic(piece.isPlayer1)
                        ic(position.board[captureSquare[0],captureSquare[1]].isPlayer1)
                        gameApp.showPositionBoard(newBoard)
                        
                    elif newBoard[captureSquare[0], captureSquare[1]] in newOpposingPlayer.pieces:
                        pass
                    else:
                        print("nien")
                    try:
                        newOpposingPlayer.pieces.remove(newBoard[captureSquare[0],
                                                    captureSquare[1]])
                        newBoard[captureSquare[0],captureSquare[1]] = 0
                    except:
                        
                        print(newPosition.player1ToMove)
                        print("try statement failed")
                        
                    newBoard = newPieceMoving.movePieceInMinimax([newPieceMoving.rowIndex, newPieceMoving.colIndex],[move[0],move[1]], newBoard)
                    if not(newBoard == newPosition.board):
                        print("nah")

                    #Check for follow up moves

                    #TEMPORARILY COMMENTED OUT
                    followUpMoves = gameApp.determinePieceCaptures(newPieceMoving, newPosition.board)
                    if len(followUpMoves) > 0:
                        chainEndPositions = self.handleCaptureChainInMinimax(gameApp, newPieceMoving, newPosition, followUpMoves)
                        for pos in chainEndPositions:
                           pos.player1ToMove = not(newPosition.player1ToMove)
                           yield(pos)
                    
                    newPosition.player1ToMove = not(newPosition.player1ToMove)
                    yield(newPosition)
        else:
            for piece in currentPlayer.pieces:
                moves, areCaptures = gameApp.determinePieceMoves(piece, board)
                piecePosition = [piece.rowIndex,piece.colIndex]
                for move in moves:
                    move[0], move[1] = move[1], move[0]
                    newPosition = position.createCopyPosition()
                    newBoard = newPosition.board
                    newPieceMoving = newBoard[piecePosition[0],piecePosition[1]]
                    if position.player1ToMove:
                        newCurrentPlayer = newPosition.player1
                        newOpposingPlayer = newPosition.player2
                    else:
                        newCurrentPlayer = newPosition.player2
                        newOpposingPlayer = newPosition.player1
                    newBoard = newPieceMoving.movePieceInMinimax([newPieceMoving.rowIndex, newPieceMoving.colIndex],[move[0],move[1]], newBoard)
                    newPosition.player1ToMove = not(newPosition.player1ToMove)
                    yield(newPosition)
                    
class minimaxPosition:
    def __init__(self, board, player1, player2, player1ToMove):
        self.board = board
        self.player1 = player1
        self.player2 = player2
        self.player1ToMove = player1ToMove

    def __getitem__(self, indicies):
        return (self.board[indicies[0]][indicies[1]])

    def __setitem__(self, indicies, value):
        self.board[indicies[0]][indicies[1]] = value

    def __str__(self):
        return str(self.board)

    def updateBoard(self, row, column, value):
        self.__setitem__(self.board[row][column], value)

    def createCopyPosition(self):
        newPlayer1 = copy.deepcopy(self.player1)
        newPlayer2 = copy.deepcopy(self.player2)

        newboard = copy.deepcopy(self.board)
        #print("\n\nIN CREATE COPY POSITION\n\n")
        for piece in newPlayer1.pieces:
            newboard[piece.rowIndex, piece.colIndex] = piece
            #print(piece)
        #print("\n")
        for piece in newPlayer2.pieces:
            newboard[piece.rowIndex, piece.colIndex] = piece
            #print(piece)
        return(minimaxPosition(newboard, newPlayer1, newPlayer2, self.player1ToMove))
                        
        
        

class Tile(turtle.RawTurtle):

    def __init__(self, gameApp, rowIndex, colIndex, color):
        # The  super().__init__ call should be the first call we make in the
        # __init__ of a derived class.  Here we call RawTurtle's __init__ so
        # drawing happens on the gameApp's canvas.
        super().__init__(gameApp.canvas)

        # Save the three arguments passed in so we can refer to them later.
        self.gameApp = gameApp
        self.rowIndex = rowIndex
        self.colIndex = colIndex
        self.highlightedColor = '#FFFF65'
        self.regularColor = color
        # Set up the tile.
        self.color(
            color)  # Colour of the tile specified using RGB hexadecimals.
        self.shape('tile')  # We registered this shape so we can use it now.
        self.penup()  # Don't leave trails when moving.
        self.goto(100 * colIndex, 100 * rowIndex)
        self.onclick(self.leftClickHandler)


    def __deepcopy__(self,memo):
        copy.copy(self)
    
    def leftClickHandler(self, x, y):
        self.gameApp.onTileClick(self)


class Piece(Tile):

    def __init__(self, gameApp, color, rowIndex, colIndex, isPlayer1):
        super().__init__(gameApp, rowIndex, colIndex, color)
        self.shape('piece')
        self.color(color)
        self.isKing = False
        self.isPlayer1 = isPlayer1
        if self.isPlayer1:
            self.promotionSquares = [[0,1],[0,3],[0,5],[0,7]]
        else:
            self.promotionSquares = [[7,0],[7,2],[7,4],[7,6]]

    def __deepcopy__(self,memo):
       return(Piece(self.gameApp, self.color, self.rowIndex, self.colIndex, self.isPlayer1))
        
    
    
    def movePieceTo(self, rowIndex, colIndex):
        self.gameApp.board[self.rowIndex, self.colIndex] = 0
        self.gameApp.board[rowIndex, colIndex] = self
        self.goto(100 * colIndex, 100 * rowIndex)
        self.rowIndex, self.colIndex = rowIndex, colIndex

        if [self.rowIndex,self.colIndex] in self.promotionSquares:
            self.isKing = True
            self.shape('kinged_piece')

    def movePieceInMinimax(self, originalPos, newPos, board):
        board[originalPos[0], originalPos[1]] = 0
        board[newPos[0], newPos[1]] = self
        self.rowIndex, self.colIndex = newPos[0], newPos[1]
        if [newPos[0],newPos[1]] in self.promotionSquares:
            self.isKing = True
        return(board)

class MinimaxPiece:
    def __init__(self, rowIndex, colIndex, isPlayer1):
        self.rowIndex = rowIndex
        self.colIndex = colIndex
        self.isPlayer1 = isPlayer1
        self.isKing = False
        if self.isPlayer1:
            self.promotionSquares = [[0,1],[0,3],[0,5],[0,7]]
        else:
            self.promotionSquares = [[7,0],[7,2],[7,4],[7,6]]

    def movePieceInMinimax(self, originalPos, newPos, board):
        board[originalPos[0], originalPos[1]] = 0
        self.rowIndex, self.colIndex = newPos[0], newPos[1]
        if [newPos[0],newPos[1]] in self.promotionSquares:
            self.isKing = True
        board[newPos[0], newPos[1]] = self
        return(board)

    
    
class Game(tkinter.Frame):
    """
    The checkers game controller.

    A Game object *is* a tkinter.Frame object by inheritance.  So it has
    methods such as pack() already defined.
    """

    def __init__(self, root=None):
        super().__init__(root)
        # Save the root window as self.root so I can refer to it later.
        self.root = root
        self.highlightedTiles = []
        self.tileClicked = None
        self.BluePlayer = humanPlayer(True)
        self.GreenPlayer = computerPlayer(False)
        self.inCaptureChain = False
        self.captureChainPiece = None
        self.gameOver = False
        #build the window and initialize a game
        self._buildWindow()
        self.startNewGame()
        self.testingSlotPiece = 0
    
    def startNewGame(self):
        #initialize variables
        self.board = Board()
        self.tiles = []
        self.pieces = []
        inactiveColor = '#1A1A00'
        activeColor = '#FF6666'
        self.playerToMove = self.BluePlayer
        self.playerNotMoving = self.GreenPlayer
        self.inCaptureChain = False
        self.captureChainPiece = None
        self.gameOver = False
        #create empty board
        for i in range(8):
            for j in range(8):
                self.tiles.append(Tile(self, i, j, activeColor))
                activeColor, inactiveColor = inactiveColor, activeColor
            activeColor, inactiveColor = inactiveColor, activeColor

        #place the pieces on their starting spots
        self.setupPlayer1Pieces()
        self.setupPlayer2Pieces()
        #update the display to show the board and pieces
        self.screen.update()
        

    def setupPlayer1Pieces(self):
        for i in range(0, 8, 2):
            newPiece1 = Piece(self, '#00CDFF', 7, i, True)
            newPiece2 = Piece(self, '#00CDFF', 5, i, True)
            self.pieces.append(newPiece1)
            self.pieces.append(newPiece2)
            self.BluePlayer.pieces.append(newPiece1)
            self.BluePlayer.pieces.append(newPiece2)
            self.board[7, i] = newPiece1
            self.board[5, i] = newPiece2
        for i in range(1, 8, 2):
            newPiece = Piece(self, '#00CDFF', 6, i, True)
            self.pieces.append(newPiece)
            self.BluePlayer.pieces.append(newPiece)
            self.board[6, i] = newPiece

    def setupPlayer2Pieces(self):
        for i in range(0, 8, 2):
            newPiece = Piece(self, '#32FF00', 1, i, False)
            self.pieces.append(newPiece)
            self.GreenPlayer.pieces.append(newPiece)
            self.board[1, i] = newPiece
        for i in range(1, 8, 2):
            newPiece1 = Piece(self, '#32FF00', 0, i, False)
            newPiece2 = Piece(self, '#32FF00', 2, i, False)
            self.GreenPlayer.pieces.append(newPiece1)
            self.GreenPlayer.pieces.append(newPiece2)
            self.pieces.append(newPiece1)
            self.pieces.append(newPiece2)
            self.board[0, i] = newPiece1
            self.board[2, i] = newPiece2

    def isGameOver(self, player, board):
        if len(player.pieces) == 0:
            return(True)
        for piece in player.pieces:
            moves = self.determinePieceMoves(piece, board)
            if len(moves) != 0 :
                return(False)
        return(True)
        
    def updateGameStatus(self, player):
        if self.gameOver:
            self.gameOver = True
        if self.isGameOver(player, self.board):
            self.gameOver = True
            if player.isPlayer1:
                message = "Player 2 wins!"
            else:
                message = "Player 1 wins!"
            self.onGameOver(message)
        else:
            self.gameOver = False

    def showPositionBoard(self, board):
        showBoard = copy.deepcopy(board)
        for row in showBoard[:,:]:
            for i in range(len(row)):
                if row[i] != 0:
                    if row[i].isPlayer1:
                        if row[i].isKing:
                            row[i] = 2
                        else:
                            
                            row[i] = 1
                    else:
                        if row[i].isKing:
                            row[i] = -2
                        else:
                            
                            row[i] = -1
            ic(row)
            
    
    def onGameOver(self,text):
        tkinter.messagebox.showinfo(message=text, title="Game over")

    
    def isMoveInbounds(self, targetSquareX, targetSquareY):
        if targetSquareX > 7:
            return (False)
        if targetSquareX < 0:
            return (False)
        if targetSquareY > 7:
            return (False)
        if targetSquareY < 0:
            return (False)
        return (True)

    def isSquareBlocked(self, targetSquareX, targetSquareY, board):
        if board[targetSquareY, targetSquareX] != 0:
            return (True)
        else:
            return (False)

    def isMoveACapture(self, targetSquareX, targetSquareY, piece, board):
        #assumes that isSquareBlocked returned True for the move being considered.
        if board[targetSquareY,
                      targetSquareX].isPlayer1 != piece.isPlayer1:
            captureSquareX = targetSquareX + (targetSquareX - piece.colIndex)
            captureSquareY = targetSquareY + (targetSquareY - piece.rowIndex)
            if captureSquareX < 0 or captureSquareY < 0:
                return(False)
            try:
                if self.board[captureSquareY, captureSquareX] == 0:
                    return True
            except:
                return(False)
        return (False)


    def minimax(self, depth, position, compPlayer, alpha, beta):
        #ic(position.player1ToMove)
        #self.showPositionBoard(position.board)
        # if at bottom of the tree, return the static evaluation of the board
        if depth == 0:
            return(self.posEval(position.board, position))
        if position.player1ToMove:
            currPlayer = position.player1
            oppoPlayer = position.player2
        else:
            currPlayer = position.player2
            oppoPlayer = position.player1
        #if position is terminal (game is over), return either positive or negative infinity, depending on the turn
        if self.isGameOver(currPlayer, position.board):
            if position.player1ToMove:
                return(-math.inf)
            else:
                return(math.inf)

        if position.player1ToMove:
            bestFound = -math.inf
        else:
            bestFound = math.inf
        for pos in compPlayer.generateChildPositions(self, position):
            #print("going down")
            posEval = self.minimax(depth - 1, pos, compPlayer, alpha, beta)
            #print("back up")
            if position.player1ToMove:
                bestFound = max(posEval, bestFound)
                alpha = max(alpha, bestFound)
                if beta <= alpha:
                    break
            else:
                bestFound = min(posEval, bestFound)
                beta = min(beta, bestFound)
                if beta < alpha:
                    break
        return(bestFound)
    
    
    
    def returnLegalMove(self, targetSquareX, targetSquareY, piece, board):
        if not self.isMoveInbounds(targetSquareX, targetSquareY):
            return (None)
        if not self.isSquareBlocked(targetSquareX, targetSquareY, board):
            return ([targetSquareX, targetSquareY])
        if self.isMoveACapture(targetSquareX, targetSquareY, piece, board):
            return ([
                targetSquareX + (targetSquareX - piece.colIndex),
                targetSquareY + (targetSquareY - piece.rowIndex)
            ])
        return (None)

    def determinePieceCaptures(self, piece, board):
        piecePosX = piece.colIndex
        piecePosY = piece.rowIndex
        capturesAvailible = []
        if piece.isPlayer1:
            movesToConsider = [[piecePosY - 1, piecePosX + 1],
                               [piecePosY - 1, piecePosX - 1]]
        elif not (piece.isPlayer1):
            movesToConsider = [[piecePosY + 1, piecePosX + 1],
                               [piecePosY + 1, piecePosX - 1]]
        if piece.isKing:
            movesToConsider = [[piecePosY - 1, piecePosX + 1],
                               [piecePosY - 1, piecePosX - 1], 
                               [piecePosY + 1, piecePosX + 1],
                               [piecePosY + 1, piecePosX - 1]]

        for move in movesToConsider:
            #movementArray represents the direction of the move (something like [1,-1])
            movementArray = [move[0]-piecePosY, move[1]-piecePosX]
            if not self.isMoveInbounds(move[0] + movementArray[0], move[1] + movementArray[1]):
                continue
            if board[move[0],move[1]] == 0:
                continue
            if board[move[0],move[1]].isPlayer1 == piece.isPlayer1:
                continue
            if board[move[0] + movementArray[0], move[1] + movementArray[1]] != 0:
                continue
            else:
                capturesAvailible.append([move[0] + movementArray[0], move[1] + movementArray[1]])
        return(capturesAvailible)

    
    def calculatePiecesWithCaptures(self, player, board):
        player.piecesWithCaptures = []
        piecesWithCaptures = []
        for piece in player.pieces:
            captures = self.determinePieceCaptures(piece, board)
            if len(captures) > 0:
                player.piecesWithCaptures.append(piece)
                piecesWithCaptures.append(piece)

        return(piecesWithCaptures)
                
                


    
    def determinePieceMoves(self, piece, board):
        piecePosX = piece.colIndex
        piecePosY = piece.rowIndex
        #movesToConsider contains every target square that a piece could possibly go to, with the exception of leap moves (captures)
        #capture moves are forced in checkers, so it is best to keep capture and non-capture moves separate, because then I can check at the end if there are any capture moves availible, and if so, I can return only the capture list
        movesToConsider = []
        captureMoves = []
        nonCaptureMoves = []

        if piece.isPlayer1:
            movesToConsider = [[piecePosX + 1, piecePosY - 1],
                               [piecePosX - 1, piecePosY - 1]]
        elif not (piece.isPlayer1):
            movesToConsider = [[piecePosX + 1, piecePosY + 1],
                               [piecePosX - 1, piecePosY + 1]]
        if piece.isKing:
            movesToConsider = [[piecePosX + 1, piecePosY - 1],
                               [piecePosX - 1, piecePosY - 1],
                               [piecePosX + 1, piecePosY + 1],
                               [piecePosX - 1, piecePosY + 1]]

        for move in movesToConsider:
            #returnLegalMove returns None if the input move is illegal AND there isnt a capture in that direction. If the move is legal, the move is returned in the form of [x,y], and if there is a capture in that direction, the capture square is returned in the form of [x,y]
            legalMove = self.returnLegalMove(move[0], move[1], piece, board)
            if legalMove == None:
                continue
            elif legalMove[0] == move[0]:
                nonCaptureMoves.append(legalMove)
            else:
                captureMoves.append(legalMove)

        if len(captureMoves) != 0:
            return (captureMoves,True)
        else:
            return (nonCaptureMoves,False)

    def clearHighlightedTiles(self):
        for tiile in self.highlightedTiles:
            tiile.color(tiile.regularColor)
        self.highlightedTiles = []
        self.screen.update()

    def determineCaptureSquare(self, move, piece):
        if abs(move[1] - piece.colIndex) > 1:
            return ([
                max(move[0],piece.rowIndex) - 1,
                max(move[1],piece.colIndex) - 1
            ])
        return None


    def posEval(self, board, position):
        player1MaterialCount = 0
        player2MaterialCount = 0
        player1Bonuses = 0
        player2Bonuses = 0
        numPlayer1Pieces = len(position.player1.pieces)
        numPlayer2Pieces = len(position.player2.pieces)
        totalPiecesOnBoard = numPlayer1Pieces + numPlayer2Pieces
        #PlayerToMove
        for piece in position.player1.pieces:
            if piece.isKing:
                player1MaterialCount += 2.5
                pieceDistFromWall1 = min(piece.colIndex, 7 - piece.colIndex)
                pieceDistFromWall2 = min(piece.rowIndex, 7 - piece.rowIndex)
                player1Bonuses += (pieceDistFromWall1 + pieceDistFromWall2)
            else:
                player1MaterialCount += 1.4
                if piece.rowIndex == 7:
                    player1Bonuses += .7
                pieceDistFromWall = min(piece.colIndex, 7 - piece.colIndex)
                player1Bonuses += (8 - pieceDistFromWall) / 21
                pieceDistToPromo = piece.rowIndex
                player1Bonuses += ((8-pieceDistToPromo) / (2 * totalPiecesOnBoard))
                unimpededPathwayFound = True
                numNonKingBlockers = 0
                #determine unimpeded pathways to promotion
                for OppoPiece in position.player2.pieces:
                    if OppoPiece.rowIndex < piece.rowIndex and abs(piece.colIndex - OppoPiece.colIndex) <= pieceDistToPromo:
                        if OppoPiece.isKing:
                            unimpededPathwayFound = False
                            break
                        else:
                            numNonKingBlockers += 1
                            if numNonKingBlockers > 1:
                                unimpededPathwayFound = False
                                break
                if unimpededPathwayFound:
                    player1Bonuses += 4
        for piece in position.player2.pieces:
            if piece.isKing:
                player2MaterialCount += 2.5
                pieceDistFromWall1 = min(piece.colIndex, 7 - piece.colIndex)
                pieceDistFromWall2 = min(piece.rowIndex, 7 - piece.rowIndex)
                player2Bonuses += (pieceDistFromWall1 + pieceDistFromWall2) / (4 * totalPiecesOnBoard)
            else:
                player2MaterialCount += 1.4
                if piece.rowIndex == 0:
                    player2Bonuses += .7
                pieceDistFromWall = min(piece.colIndex, 7 - piece.colIndex)
                player2Bonuses += (8 - pieceDistFromWall) / 21
                pieceDistToPromo = 7 - piece.rowIndex
                player2Bonuses += ((8-pieceDistToPromo) / (2 * totalPiecesOnBoard))

                #determine unimpeded pathways
                unimpededPathwayFound = True
                numNonKingBlockers = 0
                for OppoPiece in position.player1.pieces:
                    if OppoPiece.rowIndex > piece.rowIndex and abs(piece.colIndex - OppoPiece.colIndex) <= pieceDistToPromo:
                        if OppoPiece.isKing:
                            unimpededPathwayFound = False
                            break
                        else:
                            numNonKingBlockers += 1
                            if numNonKingBlockers > 1:
                                unimpededPathwayFound = False
                                break
                if unimpededPathwayFound:
                    player2Bonuses += 4
        player1TotalScore = (5 * player1MaterialCount) + player1Bonuses
        player2TotalScore = (5 * player2MaterialCount) + player2Bonuses
        
        overallScore = player1TotalScore - player2TotalScore
        return(overallScore)



    def ConvertGamePosToMinimaxPos(self, board, playerNotMoving, playerMoving, player1ToMove):
        #This function creates a minimax position that uses minimax pieces (that don't have direct access to gameApp) as opposed to current game pieces (the objects with gameApp access that contain graphics data that minimax doesnt need)
        player1 = Player(True)
        player2 = Player(False)
        #first, the board new board is created using minimaxPieces, and the new pieces are appended to the appropriate player piece lists
        minimaxBoard = Board()
        for row in range(8):
            for col in range(8):
                if board[row, col] != 0:
                    boardPiece = board[row, col]
                    newPiece = MinimaxPiece(boardPiece.rowIndex, boardPiece.colIndex, boardPiece.isPlayer1)
                    if boardPiece.isKing:
                        newPiece.isKing = True
                    minimaxBoard[row, col] = newPiece
                    if newPiece.isPlayer1:
                        player1.pieces.append(newPiece)
                    else:
                        player2.pieces.append(newPiece)

        newMinimaxPosition = minimaxPosition(minimaxBoard, player1, player2, player1ToMove)
        return(newMinimaxPosition)
        
        
    def onTileClick(self, tile):
        if self.gameOver:
            return 
        if self.playerToMove.isComputerPlayer:
            return
        if self.board[tile.rowIndex, tile.colIndex] == 0:
            if tile in self.highlightedTiles:
                captureSquare = self.determineCaptureSquare(
                    [tile.rowIndex, tile.colIndex], self.tileClicked)
                if not (captureSquare == None):
                    
                    self.pieces.remove(self.board[captureSquare[0],
                                                  captureSquare[1]])
                    self.playerNotMoving.pieces.remove(self.board[captureSquare[0],
                                                  captureSquare[1]])
                    self.board[captureSquare[0],captureSquare[1]].ht()
                    self.board[captureSquare[0], captureSquare[1]] = 0
                    self.tileClicked.movePieceTo(tile.rowIndex, tile.colIndex)
                    self.screen.update()
                    followUpMoves = self.determinePieceCaptures(self.tileClicked, self.board)
                    # If there are follow up moves, len(followUpMoves) should be greater than 0
                    if len(followUpMoves) != 0:
                        self.inCaptureChain = True
                        self.clearHighlightedTiles()
                        for move in followUpMoves:
                            self.tiles[(move[0] * 8) + move[1]].color(
                            self.tiles[(move[0] * 8) + move[1]].highlightedColor
                            )
                            self.highlightedTiles.append(self.tiles[(move[0] * 8) +
                                                            move[1]])
                            self.screen.update()
                    else:
                        self.inCaptureChain = False
                        followUpMoves = []
                self.tileClicked.movePieceTo(tile.rowIndex, tile.colIndex)
                self.screen.update()
                if not self.inCaptureChain:
                    self.clearHighlightedTiles()
                    self.playerToMove, self.playerNotMoving = self.playerNotMoving, self.playerToMove
                    self.updateGameStatus(self.playerToMove)
                    if self.gameOver:
                        return
                    # The human player has just made a move, and the turn has switched. It's time for the computer to make a move!!!!!
                    print("Computer Turn!")
                    #testing minimax move generation - you can delete this
                    #print("\n\n\n NEW MOVE \n\n\n")
                    #for pos in self.playerToMove.generateChildPositions(self,self.ConvertGamePosToMinimaxPos(self.board, self.playerNotMoving, self.playerToMove, False)):
                        #print("showing board")
                        #self.showPositionBoard(pos.board)
                    #end of testing

                    
                    computerMove, pieceMoving = self.playerToMove.getComputerMove(self,self.ConvertGamePosToMinimaxPos(self.board, self.playerNotMoving, self.playerToMove, False))
                    self.testingSlotPiece = pieceMoving
                    captureSquare = self.determineCaptureSquare(
                    computerMove, pieceMoving)
                    if captureSquare == None:
                        pieceMoving.movePieceTo(computerMove[0],computerMove[1])
                    else:
                        self.pieces.remove(self.board[captureSquare[0],
                                                  captureSquare[1]])
                        self.playerNotMoving.pieces.remove(self.board[captureSquare[0],
                                                    captureSquare[1]])
                        self.board[captureSquare[0],captureSquare[1]].ht()
                        self.board[captureSquare[0], captureSquare[1]] = 0
                        pieceMoving.movePieceTo(computerMove[0],computerMove[1])
                        
                        # check for follow up moves, and have the computer evalutate them if they exist
                        followUpMoves = self.determinePieceCaptures(pieceMoving, self.board)
                        while len(followUpMoves) > 0:
                            computerMove, pieceMoving = self.playerToMove.getComputerMove(self,self.ConvertGamePosToMinimaxPos(self.board, self.playerNotMoving, self.playerToMove, False))
                            
                            captureSquare = self.determineCaptureSquare(
                            computerMove, pieceMoving)
                            self.pieces.remove(self.board[captureSquare[0],
                                                  captureSquare[1]])
                            self.playerNotMoving.pieces.remove(self.board[captureSquare[0],
                                                    captureSquare[1]])
                            self.board[captureSquare[0],captureSquare[1]].ht()
                            self.board[captureSquare[0], captureSquare[1]] = 0
                            pieceMoving.movePieceTo(computerMove[0],computerMove[1])
                            followUpMoves = self.determinePieceCaptures(pieceMoving, self.board)
                            

                            
                    self.playerToMove, self.playerNotMoving = self.playerNotMoving, self.playerToMove
                    self.updateGameStatus(self.playerToMove)

                #computer has now made it's move        
                        
            
            if not self.inCaptureChain:
                self.clearHighlightedTiles()
            return 
        else:
            self.calculatePiecesWithCaptures(self.playerToMove, self.board)
            ic(self.playerToMove.piecesWithCaptures)
            if self.inCaptureChain:
                if self.board[tile.rowIndex,tile.colIndex] == self.captureChainPiece:
                    pass
            
            elif self.board[tile.rowIndex,tile.colIndex] in self.playerToMove.pieces:
                if len(self.playerToMove.piecesWithCaptures) > 0:
                    print("greater than 0")
                    if not self.board[tile.rowIndex,tile.colIndex] in self.playerToMove.piecesWithCaptures:
                        print("returning nothing")
                        return
                    
                self.tileClicked = self.board[tile.rowIndex, tile.colIndex]
                moves, movesAreCaptures = self.determinePieceMoves(self.tileClicked, self.board)
                self.clearHighlightedTiles()
                for move in moves:
                    self.tiles[(move[1] * 8) + move[0]].color(
                        self.tiles[(move[1] * 8) + move[0]].highlightedColor)
                    self.highlightedTiles.append(self.tiles[(move[1] * 8) +
                                                            move[0]])
        self.screen.update()

    def _buildWindow(self):
        """Part of __init__, to build the window."""
        self.root.title('Checkers')
        # Tk things are not displayed until pack() is called.
        self.pack()

        self.canvas = tkinter.Canvas(self, width=800, height=800)
        # Pack the canvas to the left of... something.  (See below.)
        self.canvas.pack(side='left')

        # Create a new Frame that's packed into the current (self) Frame.  The
        # padx and pady keyword arguments are optional, to create a little bit
        # of padding around the buttons.
        sideBar = tkinter.Frame(self, padx=10, pady=10)

        # Pack the sideBar on the right side of the canvas.  The optional
        # 'fill' makes the sideBar grow in the y-direction

        sideBar.pack(side='right', fill='y')

        # Inside the sideBar Frame, we can add "widgets".  A Button is a widget
        # that can be clicked.  When clicked, it'll call the root window
        # created in main() to destroy() itself.
        self.quitButton = tkinter.Button(sideBar,
                                         text='Quit',
                                         command=self.root.destroy)
        self.quitButton.pack(side='bottom')

        self.newGameButton = tkinter.Button(sideBar,
                                            text='New game',
                                            command=self.startNewGame)
        self.newGameButton.pack()  # When omitted, defaults to side='top'.

        EvalDisplayLabel = tkinter.Label(sideBar, text='Computer Evaluation')
        EvalDisplayLabel.pack()

        self.currentComputerEval = tkinter.StringVar()
        self.currentComputerEval.set('0')
        self.currentComputerEvalLabel = tkinter.Label(sideBar, textvariable=self.currentComputerEval)
        self.currentComputerEvalLabel.pack()
        
        # Create a 'dummy' turtle to configure this canvas a bit.
        theTurtle = turtle.RawTurtle(self.canvas)
        theTurtle.ht()
        self.screen = theTurtle.getscreen()
        # Usually (0,0) is in the middle; let's make (0,0) upper-left corner.
        self.screen.setworldcoordinates(0, 800, 800, 0)
        # Turn on buffering; this makes drawing a lot faster.
        self.screen.tracer(0)
        # A turtle can only use a new shape that's registered first.  Here we
        # create a polygonal shape called 'tile' that is a square.
        self.screen.register_shape('tile',
                                   ((0, 0), (0, 100), (100, 100), (100, 0)))

        self.screen.register_shape('piece', ((15, 50), (30, 20), (70, 20),
                                             (85, 50), (70, 80), (30, 80)))

        self.screen.register_shape('kinged_piece',((50,5),(5,50),(50,95),(95,50)))

def main():
    print('Welcome to Checkers!')
    root = tkinter.Tk()
    theGame = Game(root)
    theGame.mainloop()
    print('Farewell.')


if __name__ == '__main__':
    main()