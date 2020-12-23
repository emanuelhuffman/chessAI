#This file contains the logic to the chess ai
from copy import copy, deepcopy

#Logic for ID-DLMM*********************************

#return an integer value of the board state for player color
def getBoardVal(board, color):
  totalValue = 0
  piecesOfValue = "PRNBQ" #the pieces that we're scoring the board off of
  pointValue = "15339"
  if color == "black":
    piecesOfValue = "prnbq" #change color to black
  for i in range(8):
    for j in range(8): #loop through entire board
      if board[i][j] in piecesOfValue: #if piece matches our pieces of value
        piece = board[i][j] #grab the piece and set to a variable
        index = piecesOfValue.find(piece) #grab the index of that piece in pieesOfValue
        value = pointValue[index] #set the value based off that index using pointValue variable
        totalValue += int(value) #increment the total value according to that piece
  return totalValue
        
#generate moves for all pieces for player color
def generateMoves(board, fen, color):
  #promotion zone for pawns, doesn't matter the color because it's impossible for a white pawn to be on the a1 square or for a black pawn to be on the a8 square
  promotionZone = ["a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"]
  
  #pieces to promote to
  promotionPieces = ["R", "N", "B", "Q"]
  
  validMoves = [] #all valid moves of all pieces stored here
  validMovesPlus = [] #all valid moves that keep/move player out of check
  
  splitFen = fen.split()
  numberMoves = splitFen[5]
  
  pawnMoves = []
  pawnMoves += validPawnMoveGen(fen, color)
  for i in pawnMoves:
    if i[2:5] in promotionZone: #if pawn moves into promotion zone
      for j in promotionPieces: #add all valid moves to promote to Q, B, R, N
        if color == 'white':
          pawnMoves.append(i + j) #append Q, B, R, or N onto moves
        else: #piece is black
          pawnMoves.append(i + j.lower()) #change piece to black pawn
      pawnMoves.remove(i) #remove original promtion move (i.e. a7a8 removed since
                          #we already have a7a8Q, a7a8R, a7a8B, a7a8N) a7a8 useless now

  validMoves += pawnMoves #add all the valid moves together
  validMoves += validRookMoveGen(fen, color, 'R')
  validMoves += validBishopMoveGen(fen, color, 'B')
  validMoves += validQueenMoveGen(fen, color)
  validMoves += validKingMoveGen(fen, color)
  validMoves += validKnightMoveGen(fen, color)
  
    
  for i in validMoves: #go through all moves in validMoves
    #if the move does not put player in check, then add to validMovesPlus
    if not isInCheck(makeMove(deepcopy(board), i), color):
      validMovesPlus.append(i)
    
  return validMovesPlus

#returns the opposite color given to it
def oppositeColor(color):
  return "black" if color == "white" else "white"

#------------------------------------------------------------------------------------
#general game logic********************************

#takes a fen string and turns it into a 2d array representation.
#pre: game state's fen must be passed in.
#post: return value of 2d array matrix
def fenToGrid(fen):
  '''
  My grid representation

  0  r|n|b|q|k|b|n|r
  1  p|p|p|p|p|p|p|p
  2  o|o|o|o|o|o|o|o
  3  o|o|o|o|o|o|o|o
  4  o|o|o|o|o|o|o|o
  5  o|o|o|o|o|o|o|o
  6  P|P|P|P|P|P|P|P
  7  R|N|B|Q|K|B|N|R
  
     a b c d e f g h
     0 1 2 3 4 5 6 7
  
  example fen: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
  lowercase = black, uppercase = white
  where 'o's are blank squares
  '''
  
  #all pieces in chess
  PIECES = "rnbqkpRNBQKP"
  
  #initalize 2d array
  board = []
  for i in range(0,8):
    row = []
    for j in range(0,8):
      row.append('o')
    board.append(row)
    
  #cut up fen, only want first part (i.e. rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR)
  cutFen = "" #newly cut fen variable
  i = 0 #index
  while fen[i] != " ": #continue concatenating to string until we reach a space
    cutFen += fen[i]
    i += 1 #inc index
  fen = cutFen #set fen equal to newly cut fen
  
  #import fen to board
  i = 0 #row
  j = 0 #column
  for q in fen: #parse through each char in fen
    if q in PIECES: #if the char is a chess piece, then put it on the board
      board[i][j] = q
    elif q == '/': #if it is a '/', then increment row
      i += 1
      j = 0
      continue #skips incrementation of j, moves to next iteration
    else: #otherwise, it's a number, add x amount of empty spaces to board
      intq = int(q)
      for r in range(intq): #keep putting in o's until number of spaces is reached
        board[i][j] = 'o'
        j += 1
      continue #skips the additional incrementation of j, moves to next iteration

    j += 1 #increment column
    if j >= 8: #handle wrap around.
      j = 0
      
  return board

#Makes given move on given board and returns the board back
#pre: A 2d grid representation of the board and a move (i.e. "a2a3") that must be a string
#post: returns a 2d grid represenation of the board after given move has been made
def makeMove(board, move):
  #board = fenToGrid(fen)
  #make it easier to manipulate (i.e. a2a3 --> 0203)
  note = noteToNum(move) + noteToNum(move[2] + move[3])
  pieceToMove = board[8 - int(note[1])][int(note[0])] #grab piece being moved
  board[8 - int(note[1])][int(note[0])] = 'o' #set that square to empty
  board[8 - int(note[3])][int(note[2])] = pieceToMove #set piece to new square
  
  return deepcopy(board)

#Returns a list of pieces on the board for the player color
#pre: must have the list of moves as 2 character string
#post: returns a list of 2 charecter long strings
def findPieces(moveList):
  pieceList = []
  for i in range(len(moveList)):
    if moveList[i][:2] not in pieceList:
      pieceList.append(moveList[i][:2])
  
  return pieceList


#returns a list of valid moves for a specific piece
def findMovesForPiece(moveList, piece):
  validMoves = []
  for i in range(len(moveList)):
    if moveList[i][:2] == piece:
      validMoves.append(moveList[i])
  
  return validMoves


#finds all instances of a piece and returns a list with their coordinates
#pre: must pass in board and piece, (2d string array, single char)
#post: returns a list containing the coordinates for each piece
def findAllInstancesOfPiece(board, piece):
  boardRow = "01234567" #chess board coordinate scheme (row)
  boardColumn = "abcdefgh" #chess board coordinate scheme (column)
  pawnList = []
  for i in range(8): #parse through grid for white pawns (P's)
    for j in range(8):
      if board[i][j] == piece:
        coordinate = boardColumn[j] + boardRow[i] #grab coordinate of pawn piece
        pawnList.append(coordinate) #store them in list
  return pawnList


#My move generator creates a move based on an inverted board
#so this function inverts it so it can properly be read
#also, my board reads a grid from 0 to 7 wherease it should be read
#as 1 to 8. This function fixes that.
#pre: a string that contains the move to be inverted
#post: returns a string with the inverted move
def invertMove(move):
  invertedMove = ""
  invertedMove += move[0]
  invertedMove += str(8 - int(move[1]))
  invertedMove += move[2]
  invertedMove += str(8 - int(move[3]))
  return invertedMove

#takes a single coordinate (piece) and inverts it to bused on board
def invertCoordinate(coord):
  invertedCoord = ""
  invertedCoord += coord[0]
  invertedCoord += str(8 - int(coord[1]))
  return invertedCoord

#this function just converts the notation to something easier to
#manipulate (i.e. a2b3 --> 0213)
def noteToNum(note):
  boardColumn = "abcdefgh" #chess board coordinate scheme (column)
  newNote = ""
  newNote += str(boardColumn.find(note[0]))
  newNote += note[1]
  return newNote

#pawn move generator
#pre: game state's fen must be passed in.
#post: returns a list of valid moves that each pawn on the board can make.
def validPawnMoveGen(fen, color):
  boardRow = "01234567" #chess board coordinate scheme (row)
  boardColumn = "abcdefgh" #chess board coordinate scheme (column)
  
  whiteInvalidCapture = "RNBQKPok" #string of invalid objects to try to capture for white
  blackInvalidCapture = "rnbqkpoK" #string of invalid objects to try to capture for black
  
  #list of coordinates where white pawn can move double
  doubleMoveW = ["a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6"]
  
  #list of coordinates where black pawn can move double
  doubleMoveB = ["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"]
  
  pawnListW = [] #stores coordinates of white pawns on board
  
  pawnListB = [] #stores coordinates of black pawns on board
  
  validMoveW = [] #list of valid moves for white pawns
  
  validMoveB = [] #list of valid moves for black pawns
  
  fenSplit = fen.split() #split fen
  enPassant = fenSplit[3] #grab the en pasant checker
  
  board = fenToGrid(fen) #convert fen to a chess board represenation
  if color == 'white': #we are playing as white
    if len(enPassant) == 2:
      invertedMove = invertCoordinate(enPassant)
      note = noteToNum(invertedMove)
      if (int(note[0]) + 1) <= 7:
        if board[int(note[1]) + 1][int(note[0]) + 1] == 'P':
          validMove = boardColumn[int(note[0]) + 1] + str(int(note[1]) + 1) + invertedMove
          validMoveW.append(invertMove(validMove))
      if (int(note[0]) - 1) >= 0:
        if board[int(note[1]) + 1][int(note[0]) - 1] == 'P':
          validMove = boardColumn[int(note[0]) - 1] + str(int(note[1]) + 1) + invertedMove
          validMoveW.append(invertMove(validMove))
    
    #find all white pawns on the board and set equal to pawnListW
    pawnListW = findAllInstancesOfPiece(board, 'P')
    
    #Now that we have our list of pawns and their coordinates
    #we can now generate valid moves for each piece
    for i in pawnListW:
      #below is the capture to the right logic for pawns
      note = noteToNum(i) #turn notation into easier to manipulate format a2 --> 02
      if int(note[0]) + 1 <= 7 and int(note[1]) - 1 >= 0:
        if board[int(note[1]) - 1][int(note[0]) + 1] not in whiteInvalidCapture:
          validMove = i + boardColumn[int(note[0]) + 1] + str(int(note[1]) - 1)
          validMoveW.append(invertMove(validMove)) #need to invert since my board is inverted
      #below is the capture to the left logic for pawns
      if int(note[0]) - 1 >= 0 and int(note[1]) - 1 >= 0:
        if board[int(note[1]) - 1][int(note[0]) - 1] not in whiteInvalidCapture:
          validMove = i + boardColumn[int(note[0]) - 1] + str(int(note[1]) - 1)
          validMoveW.append(invertMove(validMove)) #need to invert since my board is inverted
      
      #if it is at initial square and no piece is blocking it, then it is valid (double move validity)
      if (i in doubleMoveW) and (board[int(i[1]) - 2][boardColumn.find(i[0])] == 'o') and (board[int(i[1]) - 1][boardColumn.find(i[0])] == 'o'):
        validMove = i + i[0] + str(int(i[1]) - 2)
        validMoveW.append(invertMove(validMove))
        
      #if space infront of pawn is empty, then it is valid to move forward (single move validity)
      if board[int(i[1]) - 1][boardColumn.find(i[0])] == 'o':
        #current coordinate + same column + next row
        validMove = i + i[0] + str(int(i[1]) - 1)
        validMoveW.append(invertMove(validMove)) #add the valid move to the list of valid moves for white
    return validMoveW #return list of valid moves for white
  #--------------------------------------------------------------------------
  else: #else we are playing as black
    if len(enPassant) == 2:
      invertedMove = invertCoordinate(enPassant)
      note = noteToNum(invertedMove)
      if (int(note[0]) + 1) <= 7:
        if board[int(note[1]) - 1][int(note[0]) + 1] == 'p':
          validMove = boardColumn[int(note[0]) + 1] + str(int(note[1]) - 1) + invertedMove
          validMoveB.append(invertMove(validMove))
      if (int(note[0]) - 1) >= 0:
        if board[int(note[1]) - 1][int(note[0]) - 1] == 'p':
          validMove = boardColumn[int(note[0]) - 1] + str(int(note[1]) - 1) + invertedMove
          validMoveB.append(invertMove(validMove))
    
    #find all black pawns on the board and set equal to pawnListB
    pawnListB = findAllInstancesOfPiece(board, 'p')
    
    #Now that we have our list of pawns and their coordinates
    #we can now generate valid moves for each piece
    for i in pawnListB:
      #below is the capture to the right logic for pawns
      note = noteToNum(i) #turn notation into easier to manipulate format a2 --> 02
      if int(note[0]) + 1 <= 7 and int(note[1]) + 1 <= 7:
        if board[int(note[1]) + 1][int(note[0]) + 1] not in blackInvalidCapture:
          validMove = i + boardColumn[int(note[0]) + 1] + str(int(note[1]) + 1)
          validMoveB.append(invertMove(validMove)) #need to invert since my board is inverted
      #below is the capture to the left logicf or pawns
      if int(note[0]) - 1 >= 0 and int(note[1]) + 1 <= 7:
        if board[int(note[1]) + 1][int(note[0]) - 1] not in blackInvalidCapture:
          validMove = i + boardColumn[int(note[0]) - 1] + str(int(note[1]) + 1)
          validMoveB.append(invertMove(validMove)) #need to invert since my board is inverted
  
      #if it is at initial square and no piece is blocking it, then it is valid (double move validity)
      if (i in doubleMoveB) and (board[int(i[1]) + 2][boardColumn.find(i[0])] == 'o') and (board[int(i[1]) + 1][boardColumn.find(i[0])] == 'o'):
        validMove = i + i[0] + str(int(i[1]) + 2)
        validMoveB.append(invertMove(validMove))
        
      #if space infront of pawn is empty, then it is valid to move forward
      if board[int(i[1]) + 1][boardColumn.find(i[0])] == 'o':
        #current coordinate + same column + next row
        validMove = i + i[0] + str(int(i[1]) + 1)
        validMoveB.append(invertMove(validMove)) #add the valid move to the list of valid moves for white
    return validMoveB #return list of valid moves for black

#generatores a list of valid moves for rook. (note: piece was passed in to also generate moves for queen)
def validRookMoveGen(fen, color, piece):
  boardRow = "01234567" #chess board coordinate scheme (row)
  boardColumn = "abcdefgh" #chess board coordinate scheme (column)
  
  whiteInvalidCapture = "RNBQKPk" #string of invalid objects to try to capture for white
  blackInvalidCapture = "rnbqkpK" #string of invalid objects to try to capture for black
  whiteValidCapture = "rnbqp"
  blackValidCapture = "RNBQP"
  
  rookListW = [] #stores coordinates of white rooks on board
  
  rookListB = [] #stores coordinates of black rooks on board
  
  validMoveW = [] #list of valid moves for white rooks
  
  validMoveB = [] #list of valid moves for black rooks
  
  board = fenToGrid(fen)
  if color == "white":
    rookListW = findAllInstancesOfPiece(board, piece.upper())
    for i in rookListW: #find all instances of rook on the board
      note = noteToNum(i) #translate to easier to manipulate string
      distance = 1 #this gets incremented as we check how far the rook can move
      #ADD ALL VALID MOVES THAT GO IN THE NORTH DIRECTION
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) - distance >=0) and (board[int(note[1]) - distance][int(note[0])] not in whiteInvalidCapture):
        validMove = i + i[0] + str(int(note[1]) - distance)
        validMoveW.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) - distance][int(note[0])] in whiteValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the rook can move further now
      
      #NOW ADD VALID MOVES THAT GO IN THE SOUTH DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) + distance <= 7) and (board[int(note[1]) + distance][int(note[0])] not in whiteInvalidCapture):
        validMove = i + i[0] + str(int(note[1]) + distance)
        validMoveW.append(invertMove(validMove)) #adds a south moving valid move to list
        if board[int(note[1]) + distance][int(note[0])] in whiteValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the rook can move further now
      
      #NOW ADD VALID MOVES THAT GO IN THE EAST DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[0]) + distance <= 7) and (board[int(note[1])][int(note[0]) + distance]) not in whiteInvalidCapture:
        validMove = i + boardColumn[(int(note[0]) + distance)] + i[1]
        validMoveW.append(invertMove(validMove)) #adds a south moving valid move to list
        if board[int(note[1])][int(note[0]) + distance] in whiteValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the rook can move further now
        
      #NOW ADD VALID MOVES THAT GO IN THE WEST DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[0]) - distance >= 0) and (board[int(note[1])][int(note[0]) - distance]) not in whiteInvalidCapture:
        validMove = i + boardColumn[(int(note[0]) - distance)] + i[1]
        validMoveW.append(invertMove(validMove)) #adds a south moving valid move to list
        if board[int(note[1])][int(note[0]) - distance] in whiteValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the rook can move further now
    return validMoveW
  #------------------------------------------------
  else: #we are playing as black
    rookListB = findAllInstancesOfPiece(board, piece.lower())
    for i in rookListB: #find all instances of rook on the board
      note = noteToNum(i) #translate to easier to manipulate string
      distance = 1 #this gets incremented as we check how far the rook can move
      #ADD ALL MOVES THAT GO IN THE NORTH DIRECTION
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) - distance >=0) and (board[int(note[1]) - distance][int(note[0])] not in blackInvalidCapture):
        validMove = i + i[0] + str(int(note[1]) - distance)
        validMoveB.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) - distance][int(note[0])] in blackValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the rook can move further now
      
      #NOW ADD VALID MOVES THAT GO IN THE SOUTH DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) + distance <= 7) and (board[int(note[1]) + distance][int(note[0])] not in blackInvalidCapture):
        validMove = i + i[0] + str(int(note[1]) + distance)
        validMoveB.append(invertMove(validMove)) #adds a south moving valid move to list
        if board[int(note[1]) + distance][int(note[0])] in blackValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the rook can move further now
      
      #NOW ADD VALID MOVES THAT GO IN THE EAST DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[0]) + distance <= 7) and (board[int(note[1])][int(note[0]) + distance]) not in blackInvalidCapture:
        validMove = i + boardColumn[(int(note[0]) + distance)] + i[1]
        validMoveB.append(invertMove(validMove)) #adds a south moving valid move to list
        if board[int(note[1])][int(note[0]) + distance] in blackValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the rook can move further now
        
      #NOW ADD VALID MOVES THAT GO IN THE WEST DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[0]) - distance >= 0) and (board[int(note[1])][int(note[0]) - distance]) not in blackInvalidCapture:
        validMove = i + boardColumn[(int(note[0]) - distance)] + i[1]
        validMoveB.append(invertMove(validMove)) #adds a south moving valid move to list
        if board[int(note[1])][int(note[0]) - distance] in blackValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the rook can move further now
    return validMoveB

#generates valid moves for the bishop (note: piece was passed in to also make valid moves for queen)
def validBishopMoveGen(fen, color, piece):
  boardRow = "01234567" #chess board coordinate scheme (row)
  boardColumn = "abcdefgh" #chess board coordinate scheme (column)
  
  whiteInvalidCapture = "RNBQKPk" #string of invalid objects to try to capture for white
  blackInvalidCapture = "rnbqkpK" #string of invalid objects to try to capture for black
  whiteValidCapture = "rnbqp"
  blackValidCapture = "RNBQP"
  
  rookListW = [] #stores coordinates of white bishops on board
  
  rookListB = [] #stores coordinates of black bishops on board
  
  validMoveW = [] #list of valid moves for white bishops
  
  validMoveB = [] #list of valid moves for black bishops
  
  board = fenToGrid(fen)
  if color == "white":
    rookListW = findAllInstancesOfPiece(board, piece.upper())
    for i in rookListW: #find all instances of bishop on the board
      note = noteToNum(i) #translate to easier to manipulate string
      distance = 1 #this gets incremented as we check how far the bishop can move
      #ADD ALL VALID MOVES THAT GO IN THE TOP-RIGHT DIRECTION
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) - distance >= 0) and (int(note[0]) + distance <= 7) and \
            (board[int(note[1]) - distance][int(note[0]) + distance] not in whiteInvalidCapture):
        validMove = i + boardColumn[int(note[0]) + distance] + str(int(note[1]) - distance)
        validMoveW.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) - distance][int(note[0]) + distance] in whiteValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the bishop can move further now
      
      #NOW ADD ALL VALID MOVES THAT GO IN THE BOTTOM-RIGHT DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the bishop can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) + distance <= 7) and (int(note[0]) + distance <= 7) and \
            (board[int(note[1]) + distance][int(note[0]) + distance] not in whiteInvalidCapture):
        validMove = i + boardColumn[int(note[0]) + distance] + str(int(note[1]) + distance)
        validMoveW.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) + distance][int(note[0]) + distance] in whiteValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the bishop can move further now 
        
      #NOW ADD ALL VALID MOVES THAT GO IN THE BOTTOM-LEFT DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the bishop can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) + distance <= 7) and (int(note[0]) - distance >= 0) and \
            (board[int(note[1]) + distance][int(note[0]) - distance] not in whiteInvalidCapture):
        validMove = i + boardColumn[int(note[0]) - distance] + str(int(note[1]) + distance)
        validMoveW.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) + distance][int(note[0]) - distance] in whiteValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the bishop can move further now 
        
      #NOW ADD ALL VALID MOVES THAT GO IN THE TOP-LEFT DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the bishop can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) - distance >= 0) and (int(note[0]) - distance >= 0) and \
            (board[int(note[1]) - distance][int(note[0]) - distance] not in whiteInvalidCapture):
        validMove = i + boardColumn[int(note[0]) - distance] + str(int(note[1]) - distance)
        validMoveW.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) - distance][int(note[0]) - distance] in whiteValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the bishop can move further now 
    return validMoveW
  #------------------------------------------------
  else: #we are playing as black
    rookListB = findAllInstancesOfPiece(board, piece.lower())
    for i in rookListB: #find all instances of bishop on the board
      note = noteToNum(i) #translate to easier to manipulate string
      distance = 1 #this gets incremented as we check how far the bishop can move
      #ADD ALL VALID MOVES THAT GO IN THE TOP-RIGHT DIRECTION
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) - distance >= 0) and (int(note[0]) + distance <= 7) and \
            (board[int(note[1]) - distance][int(note[0]) + distance] not in blackInvalidCapture):
        validMove = i + boardColumn[int(note[0]) + distance] + str(int(note[1]) - distance)
        validMoveB.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) - distance][int(note[0]) + distance] in blackValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the bishop can move further now
      
      #NOW ADD ALL VALID MOVES THAT GO IN THE BOTTOM-RIGHT DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the bishop can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) + distance <= 7) and (int(note[0]) + distance <= 7) and \
            (board[int(note[1]) + distance][int(note[0]) + distance] not in blackInvalidCapture):
        validMove = i + boardColumn[int(note[0]) + distance] + str(int(note[1]) + distance)
        validMoveB.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) + distance][int(note[0]) + distance] in blackValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the bishop can move further now 
        
      #NOW ADD ALL VALID MOVES THAT GO IN THE BOTTOM-LEFT DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the bishop can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) + distance <= 7) and (int(note[0]) - distance >= 0) and \
            (board[int(note[1]) + distance][int(note[0]) - distance] not in blackInvalidCapture):
        validMove = i + boardColumn[int(note[0]) - distance] + str(int(note[1]) + distance)
        validMoveB.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) + distance][int(note[0]) - distance] in blackValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the bishop can move further now 
        
      #NOW ADD ALL VALID MOVES THAT GO IN THE TOP-LEFT DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the bishop can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) - distance >= 0) and (int(note[0]) - distance >= 0) and \
            (board[int(note[1]) - distance][int(note[0]) - distance] not in blackInvalidCapture):
        validMove = i + boardColumn[int(note[0]) - distance] + str(int(note[1]) - distance)
        validMoveB.append(invertMove(validMove)) #adds a north moving valid move to list
        if board[int(note[1]) - distance][int(note[0]) - distance] in blackValidCapture: #if captured piece, stop exploring
          break
        #if the valid move is for the king, stop exploring (king only moves a distance of 1)
        if piece.upper() == 'K':
          break;
        distance += 1 #check if the bishop can move further now 
    return validMoveB

#generate valid moves for queen
def validQueenMoveGen(fen, color):
  boardRow = "01234567" #chess board coordinate scheme (row)
  boardColumn = "abcdefgh" #chess board coordinate scheme (column)
  
  whiteInvalidCapture = "RNBQKPk" #string of invalid objects to try to capture for white
  blackInvalidCapture = "rnbqkpK" #string of invalid objects to try to capture for black
  whiteValidCapture = "rnbqp"
  blackValidCapture = "RNBQP"
  
  queenListW = [] #stores coordinates of white queens on board
  
  queenListB = [] #stores coordinates of black queens on board
  
  validMoveW = [] #list of valid moves for white queens
  
  validMoveB = [] #list of valid moves for black queens
  
  board = fenToGrid(fen)
  
  if color == 'white':
    queenListW = findAllInstancesOfPiece(board, 'Q') #grab coordinates of all white queens on board
    for i in queenListW:
      validMoveW += validRookMoveGen(fen, color, 'Q')
      validMoveB += validBishopMoveGen(fen, color, 'Q')
    return validMoveW
  else: #we're playing as black
    queenListB = findAllInstancesOfPiece(board, 'q') #grab coordinates of all black queens on board
    for i in queenListB:
      validMoveB += validRookMoveGen(fen, color, 'q')
      validMoveB += validBishopMoveGen(fen, color, 'q')
    return validMoveB
  
#generate valid moves for king
def validKingMoveGen(fen, color):
  kingListW = [] #stores instance of white king on board
  
  kingListB = [] #stores instances of black king on board
  
  validMoveW = [] #list of valid moves for white king
  
  validMoveB = [] #list of valid moves for black king
  
  board = fenToGrid(fen) #turn fen into 2d grid
  
  fenSplit = fen.split() #split fen
  canCastle = fenSplit[2] #grab the castle checker from fen

  if color == 'white':
    kingListW = findAllInstancesOfPiece(board, 'K') #grab coordinates of all white kings on board
    for i in kingListW:
      validMoveW += validRookMoveGen(fen, color, 'K') #give king the direction of the rook (set distance of 1)
      validMoveW += validBishopMoveGen(fen, color, 'K') #give king the direction of the bishop(set distance of 1)
    return validMoveW
  else: #we're playing as black
    kingListB = findAllInstancesOfPiece(board, 'k') #grab coordinates of all black kings on board
    for i in kingListB:
      validMoveB += validRookMoveGen(fen, color, 'k')
      validMoveB += validBishopMoveGen(fen, color, 'k')
    return validMoveB

    
#checks all 8 options the knight can move and returns a list of moves
#pre: must have fen string and the bo
#post: returns a list of board coordinates that the knight can move to
def validKnightMoveGen(fen, color):
  boardRow = "01234567" #chess board coordinate scheme (row)
  boardColumn = "abcdefgh" #chess board coordinate scheme (column)
  
  whiteInvalidCapture = "RNBQKPk" #string of invalid objects to try to capture for white
  blackInvalidCapture = "rnbqkpK" #string of invalid objects to try to capture for black
  
  knightListW = [] #stores instance of white knight on board
  
  knightListB = [] #stores instances of black knight on board
  
  validMoveW = [] #list of valid moves for white knight
  
  validMoveB = [] #list of valid moves for black knight
  
  board = fenToGrid(fen)
  
  if color == 'white':
    knightListW = findAllInstancesOfPiece(board, 'N')
    for i in knightListW:
      note = noteToNum(i)
      #CHECK IF (2 NORTH 1 WEST) IS A VALID MOVE
      if (int(note[0]) - 1 >= 0) and (int(note[1]) - 2 >= 0) and \
         (board[int(note[1]) - 2][int(note[0]) - 1]) not in whiteInvalidCapture:
           validMove = i + boardColumn[int(note[0]) - 1] + str(int(note[1]) - 2)
           validMoveW.append(invertMove(validMove))
      #CHECK IF (2 NORTH 1 EAST) IS A VALID MOVE
      if (int(note[0]) + 1 <= 7) and (int(note[1]) - 2 >= 0) and \
         (board[int(note[1]) - 2][int(note[0]) + 1]) not in whiteInvalidCapture:
           validMove = i + boardColumn[int(note[0]) + 1] + str(int(note[1]) - 2)
           validMoveW.append(invertMove(validMove))
      #CHECK IF (2 SOUTH 1 EAST) IS A VALID MOVE
      if (int(note[0]) + 1 <= 7) and (int(note[1]) + 2 <= 7) and \
         (board[int(note[1]) + 2][int(note[0]) + 1]) not in whiteInvalidCapture:
           validMove = i + boardColumn[int(note[0]) + 1] + str(int(note[1]) + 2)
           validMoveW.append(invertMove(validMove))
      #CHECK IF (2 SOUTH 1 WEST) IS A VALID MOVE
      if (int(note[0]) - 1 >= 0) and (int(note[1]) + 2 <= 7) and \
         (board[int(note[1]) + 2][int(note[0]) - 1]) not in whiteInvalidCapture:
           validMove = i + boardColumn[int(note[0]) - 1] + str(int(note[1]) + 2)
           validMoveW.append(invertMove(validMove))
      #CHECK IF (1 SOUTH 2 WEST) IS A VALID MOVE
      if (int(note[0]) - 2 >= 0) and (int(note[1]) + 1 <= 7) and \
         (board[int(note[1]) + 1][int(note[0]) - 2]) not in whiteInvalidCapture:
           validMove = i + boardColumn[int(note[0]) - 2] + str(int(note[1]) + 1)
           validMoveW.append(invertMove(validMove))
      #CHECK IF (1 NORTH 2 WEST) IS A VALID MOVE
      if (int(note[0]) - 2 >= 0) and (int(note[1]) - 1 >= 0) and \
         (board[int(note[1]) - 1][int(note[0]) - 2]) not in whiteInvalidCapture:
           validMove = i + boardColumn[int(note[0]) - 2] + str(int(note[1]) - 1)
           validMoveW.append(invertMove(validMove))
      #CHECK IF (1 NORTH 2 EAST) IS A VALID MOVE
      if (int(note[0]) + 2 <= 7) and (int(note[1]) - 1 >= 0) and \
         (board[int(note[1]) - 1][int(note[0]) + 2]) not in whiteInvalidCapture:
           validMove = i + boardColumn[int(note[0]) + 2] + str(int(note[1]) - 1)
           validMoveW.append(invertMove(validMove))
      #CHECK IF (1 SOUTH 2 EAST) IS A VALID MOVE
      if (int(note[0]) + 2 <= 7) and (int(note[1]) + 1 <= 7) and \
         (board[int(note[1]) + 1][int(note[0]) + 2]) not in whiteInvalidCapture:
           validMove = i + boardColumn[int(note[0]) + 2] + str(int(note[1]) + 1)
           validMoveW.append(invertMove(validMove))
    return validMoveW
                                     
  else: #playing as black
    knightListB = findAllInstancesOfPiece(board, 'n')
    for i in knightListB:
      note = noteToNum(i)
      #CHECK IF (2 NORTH 1 WEST) IS A VALID MOVE
      if (int(note[0]) - 1 >= 0) and (int(note[1]) - 2 >= 0) and \
         (board[int(note[1]) - 2][int(note[0]) - 1]) not in blackInvalidCapture:
           validMove = i + boardColumn[int(note[0]) - 1] + str(int(note[1]) - 2)
           validMoveB.append(invertMove(validMove))
      #CHECK IF (2 NORTH 1 EAST) IS A VALID MOVE
      if (int(note[0]) + 1 <= 7) and (int(note[1]) - 2 >= 0) and \
         (board[int(note[1]) - 2][int(note[0]) + 1]) not in blackInvalidCapture:
           validMove = i + boardColumn[int(note[0]) + 1] + str(int(note[1]) - 2)
           validMoveB.append(invertMove(validMove))
      #CHECK IF (2 SOUTH 1 EAST) IS A VALID MOVE
      if (int(note[0]) + 1 <= 7) and (int(note[1]) + 2 <= 7) and \
         (board[int(note[1]) + 2][int(note[0]) + 1]) not in blackInvalidCapture:
           validMove = i + boardColumn[int(note[0]) + 1] + str(int(note[1]) + 2)
           validMoveB.append(invertMove(validMove))
      #CHECK IF (2 SOUTH 1 WEST) IS A VALID MOVE
      if (int(note[0]) - 1 >= 0) and (int(note[1]) + 2 <= 7) and \
         (board[int(note[1]) + 2][int(note[0]) - 1]) not in blackInvalidCapture:
           validMove = i + boardColumn[int(note[0]) - 1] + str(int(note[1]) + 2)
           validMoveB.append(invertMove(validMove))
      #CHECK IF (1 SOUTH 2 WEST) IS A VALID MOVE
      if (int(note[0]) - 2 >= 0) and (int(note[1]) + 1 <= 7) and \
         (board[int(note[1]) + 1][int(note[0]) - 2]) not in blackInvalidCapture:
           validMove = i + boardColumn[int(note[0]) - 2] + str(int(note[1]) + 1)
           validMoveB.append(invertMove(validMove))
      #CHECK IF (1 NORTH 2 WEST) IS A VALID MOVE
      if (int(note[0]) - 2 >= 0) and (int(note[1]) - 1 >= 0) and \
         (board[int(note[1]) - 1][int(note[0]) - 2]) not in blackInvalidCapture:
           validMove = i + boardColumn[int(note[0]) - 2] + str(int(note[1]) - 1)
           validMoveB.append(invertMove(validMove))
      #CHECK IF (1 NORTH 2 EAST) IS A VALID MOVE
      if (int(note[0]) + 2 <= 7) and (int(note[1]) - 1 >= 0) and \
         (board[int(note[1]) - 1][int(note[0]) + 2]) not in blackInvalidCapture:
           validMove = i + boardColumn[int(note[0]) + 2] + str(int(note[1]) - 1)
           validMoveB.append(invertMove(validMove))
      #CHECK IF (1 SOUTH 2 EAST) IS A VALID MOVE
      if (int(note[0]) + 2 <= 7) and (int(note[1]) + 1 <= 7) and \
         (board[int(note[1]) + 1][int(note[0]) + 2]) not in blackInvalidCapture:
           validMove = i + boardColumn[int(note[0]) + 2] + str(int(note[1]) + 1)
           validMoveB.append(invertMove(validMove))
    return validMoveB
  
#checks if king is in check
#pre: the fen string and the color.
#post: returns a bool: true if king is in check, otherwise false
def isInCheck(board, color):
  isChecked = False
  if color == 'white':
    soloKingList = findAllInstancesOfPiece(board, 'K')
    #printBoard(board)
    for q in soloKingList:
      note = noteToNum(q)
      
      #FIRST CHECK IF IN CHECK FROM A KNIGHT*****************************************
      #CHECK IF (2 NORTH 1 WEST)
      if (int(note[0]) - 1 >= 0) and (int(note[1]) - 2 >= 0) and \
          (board[int(note[1]) - 2][int(note[0]) - 1]) == 'n': #if L-shape reaches enemy knight, then is in check
            isChecked = True
      #CHECK IF (2 NORTH 1 EAST)
      if (int(note[0]) + 1 <= 7) and (int(note[1]) - 2 >= 0) and \
          (board[int(note[1]) - 2][int(note[0]) + 1]) == 'n': #check L-shape for all directions
            isChecked = True
      #CHECK IF (2 SOUTH 1 EAST)
      if (int(note[0]) + 1 <= 7) and (int(note[1]) + 2 <= 7) and \
          (board[int(note[1]) + 2][int(note[0]) + 1]) == 'n':
            isChecked = True
      #CHECK IF (2 SOUTH 1 WEST)
      if (int(note[0]) - 1 >= 0) and (int(note[1]) + 2 <= 7) and \
          (board[int(note[1]) + 2][int(note[0]) - 1]) == 'n':
            isChecked = True
      #CHECK IF (1 SOUTH 2 WEST)
      if (int(note[0]) - 2 >= 0) and (int(note[1]) + 1 <= 7) and \
          (board[int(note[1]) + 1][int(note[0]) - 2]) == 'n':
            isChecked = True
      #CHECK IF (1 NORTH 2 WEST)
      if (int(note[0]) - 2 >= 0) and (int(note[1]) - 1 >= 0) and \
          (board[int(note[1]) - 1][int(note[0]) - 2]) == 'n':
            isChecked = True
      #CHECK IF (1 NORTH 2 EAST)
      if (int(note[0]) + 2 <= 7) and (int(note[1]) - 1 >= 0) and \
          (board[int(note[1]) - 1][int(note[0]) + 2]) == 'n':
            isChecked = True
      #CHECK IF (1 SOUTH 2 EAST)
      if (int(note[0]) + 2 <= 7) and (int(note[1]) + 1 <= 7) and \
          (board[int(note[1]) + 1][int(note[0]) + 2]) == 'n':
            isChecked = True
            
      #NOW CHECK IF IN CHECK FROM ROOK OR QUEEN****************************************
      distance = 1 #this gets incremented as we check how far a rook or queen is from the king
      #CHECK ALL VALID MOVES THAT GO IN THE NORTH DIRECTION
      #loops while it does not go off the board and move is either in empty square, rook, or queen
      while (int(note[1]) - distance >=0) and (board[int(note[1]) - distance][int(note[0])] in "orqk"):
        if board[int(note[1]) - distance][int(note[0])] in "rq":
          isChecked = True
          break #in check, so stop searching
        #need to check if king is putting other king in check
        if board[int(note[1]) - distance][int(note[0])] == 'k' and distance == 1:
          isChecked = True
          break #in check, so stop searching
        distance += 1 #check if there are further out queens or rooks
      
      #NOW CHECK VALID MOVES THAT GO IN THE SOUTH DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) + distance <= 7) and (board[int(note[1]) + distance][int(note[0])] in "orqk"):
        if board[int(note[1]) + distance][int(note[0])] in "rq":
          isChecked = True
          break
        if board[int(note[1]) + distance][int(note[0])] == 'k' and distance == 1:
          isChecked = True
          break
        distance += 1
      
      #NOW CHECK VALID MOVES THAT GO IN THE EAST DIRECTION
      #reset distance
      distance = 1
      while (int(note[0]) + distance <= 7) and (board[int(note[1])][int(note[0]) + distance] in "orqk"):
        if board[int(note[1])][int(note[0]) + distance] in "rq":
          isChecked = True
          break
        if board[int(note[1])][int(note[0]) + distance] == "k" and distance == 1:
          isChecked = True
          break
        distance += 1
        
      #NOW CHECK VALID MOVES THAT GO IN THE WEST DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[0]) - distance >= 0) and (board[int(note[1])][int(note[0]) - distance] in "orqk"):
        if board[int(note[1])][int(note[0]) - distance] in "rq":
          isChecked = True
          break
        if board[int(note[1])][int(note[0]) - distance] == "k" and distance == 1:
          isChecked = True
          break
        distance += 1
      
      #NOW CHECK IF IN CHECK FROM BISHOP OR QUEEN********************************************
      distance = 1 #this gets incremented as we check how far the bishop can move
      #CHECK ALL VALID MOVES THAT GO IN THE TOP-RIGHT DIRECTION
      #loops while it does not go off the board and checks for queen or bishop
      while (int(note[1]) - distance >= 0) and (int(note[0]) + distance <= 7) and \
            (board[int(note[1]) - distance][int(note[0]) + distance] in "obqk"):
              #if we find bishop or queen on diagonal, then checked is true, stop searching
              if board[int(note[1]) - distance][int(note[0]) + distance] in "bq":
                isChecked = True
                break
              #if we find a king on diagonal within distance of 1, then checked is true, stop searching
              if board[int(note[1]) - distance][int(note[0]) + distance] == "k" and distance == 1:
                isChecked = True
                break
              distance += 1 #check if there are further out bishop or queen that will put king in check
      
      #NOW CHECK ALL VALID MOVES THAT GO IN THE BOTTOM-RIGHT DIRECTION
      #reset distance
      distance = 1
      while (int(note[1]) + distance <= 7) and (int(note[0]) + distance <= 7) and \
            (board[int(note[1]) + distance][int(note[0]) + distance] in "obqk"):
              if board[int(note[1]) + distance][int(note[0]) + distance] in "bq":
                isChecked = True
                break
              if board[int(note[1]) + distance][int(note[0]) + distance] in "k" and distance == 1:
                isChecked = True
                break
              distance += 1 #check if the bishop can move further now 
        
      #NOW CHECK ALL VALID MOVES THAT GO IN THE BOTTOM-LEFT DIRECTION
      #reset distance
      distance = 1
      while (int(note[1]) + distance <= 7) and (int(note[0]) - distance >= 0) and \
            (board[int(note[1]) + distance][int(note[0]) - distance] in "obqk"):
              if board[int(note[1]) + distance][int(note[0]) - distance] in "bq":
                isChecked = True
                break
              if board[int(note[1]) + distance][int(note[0]) - distance] == "k" and distance == 1:
                isChecked = True
                break
              distance += 1 #check if the bishop can move further now 
        
      #NOW CHECK ALL VALID MOVES THAT GO IN THE TOP-LEFT DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the bishop can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) - distance >= 0) and (int(note[0]) - distance >= 0) and \
            (board[int(note[1]) - distance][int(note[0]) - distance] in "obqk"):
              if board[int(note[1]) - distance][int(note[0]) - distance] in "bq":
                isChecked = True
                break
              if board[int(note[1]) - distance][int(note[0]) - distance] == "k" and distance == 1:
                isChecked = True
                break
              distance += 1 #check if the bishop can move further now 
              
      #NOW CHECK IF IN CHECK BY A PAWN
      #below is pawn move right logic
      if int(note[0]) + 1 <= 7 and int(note[1]) - 1 >= 0:
        if board[int(note[1]) - 1][int(note[0]) + 1] == 'p':
          isChecked = True
      #below is the pawn move left logic
      if int(note[0]) - 1 >= 0 and int(note[1]) - 1 >= 0:
        if board[int(note[1]) - 1][int(note[0]) - 1] == 'p':
          isChecked = True
            
    return isChecked
  #---------------------------------------------------
  else: #playing as black
    soloKingList = findAllInstancesOfPiece(board, 'k')
    for q in soloKingList:
      note = noteToNum(q)
      
      #FIRST CHECK IF IN CHECK FROM A KNIGHT
      #CHECK IF (2 NORTH 1 WEST)
      if (int(note[0]) - 1 >= 0) and (int(note[1]) - 2 >= 0) and \
          (board[int(note[1]) - 2][int(note[0]) - 1]) == 'N': #if L-shape reaches enemy knight, then is in check
            isChecked = True
      #CHECK IF (2 NORTH 1 EAST)
      if (int(note[0]) + 1 <= 7) and (int(note[1]) - 2 >= 0) and \
          (board[int(note[1]) - 2][int(note[0]) + 1]) == 'N': #check L-shape for all directions
            isChecked = True
      #CHECK IF (2 SOUTH 1 EAST)
      if (int(note[0]) + 1 <= 7) and (int(note[1]) + 2 <= 7) and \
          (board[int(note[1]) + 2][int(note[0]) + 1]) == 'N':
            isChecked = True
      #CHECK IF (2 SOUTH 1 WEST)
      if (int(note[0]) - 1 >= 0) and (int(note[1]) + 2 <= 7) and \
          (board[int(note[1]) + 2][int(note[0]) - 1]) == 'N':
            isChecked = True
      #CHECK IF (1 SOUTH 2 WEST)
      if (int(note[0]) - 2 >= 0) and (int(note[1]) + 1 <= 7) and \
          (board[int(note[1]) + 1][int(note[0]) - 2]) == 'N':
            isChecked = True
      #CHECK IF (1 NORTH 2 WEST)
      if (int(note[0]) - 2 >= 0) and (int(note[1]) - 1 >= 0) and \
          (board[int(note[1]) - 1][int(note[0]) - 2]) == 'N':
            isChecked = True
      #CHECK IF (1 NORTH 2 EAST)
      if (int(note[0]) + 2 <= 7) and (int(note[1]) - 1 >= 0) and \
          (board[int(note[1]) - 1][int(note[0]) + 2]) == 'N':
            isChecked = True
      #CHECK IF (1 SOUTH 2 EAST)
      if (int(note[0]) + 2 <= 7) and (int(note[1]) + 1 <= 7) and \
          (board[int(note[1]) + 1][int(note[0]) + 2]) == 'N':
            isChecked = True
            
      #NOW CHECK IF IN CHECK FROM ROOK OR QUEEN****************************************
      distance = 1 #this gets incremented as we check how far a rook or queen is from the king
      #CHECK ALL VALID MOVES THAT GO IN THE NORTH DIRECTION
      #loops while it does not go off the board and move is either in empty square, rook, or queen
      while (int(note[1]) - distance >=0) and (board[int(note[1]) - distance][int(note[0])] in "oRQK"):
        if board[int(note[1]) - distance][int(note[0])] in "RQ":
          isChecked = True
          break #in check, so stop searching
        #have to check if king is checking other king
        if board[int(note[1]) - distance][int(note[0])] == "K" and distance == 1:
          isChecked = True
          break #in check, so stop searching
        distance += 1 #check if there are further out queens or rooks
      
      #NOW CHECK VALID MOVES THAT GO IN THE SOUTH DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) + distance <= 7) and (board[int(note[1]) + distance][int(note[0])] in "oRQK"):
        if board[int(note[1]) + distance][int(note[0])] in "RQ":
          isChecked = True
          break
        if board[int(note[1]) + distance][int(note[0])] == "K" and distance == 1:
          isChecked = True
          break
        distance += 1
      
      #NOW CHECK VALID MOVES THAT GO IN THE EAST DIRECTION
      #reset distance
      distance = 1
      while (int(note[0]) + distance <= 7) and (board[int(note[1])][int(note[0]) + distance] in "oRQK"):
        if board[int(note[1])][int(note[0]) + distance] in "RQ":
          isChecked = True
          break
        if board[int(note[1])][int(note[0]) + distance] == "K" and distance == 1:
          isChecked = True
          break
        distance += 1
        
      #NOW CHECK VALID MOVES THAT GO IN THE WEST DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the rook can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[0]) - distance >= 0) and (board[int(note[1])][int(note[0]) - distance] in "oRQK"):
        if board[int(note[1])][int(note[0]) - distance] in "RQ":
          isChecked = True
          break
        if board[int(note[1])][int(note[0]) - distance] in "K" and distance == 1:
          isChecked = True
          break
        distance += 1
      
      #NOW CHECK IF IN CHECK FROM BISHOP OR QUEEN********************************************
      distance = 1 #this gets incremented as we check how far the bishop can move
      #CHECK ALL VALID MOVES THAT GO IN THE TOP-RIGHT DIRECTION
      #loops while it does not go off the board and checks for queen or bishop
      while (int(note[1]) - distance >= 0) and (int(note[0]) + distance <= 7) and \
            (board[int(note[1]) - distance][int(note[0]) + distance] in "oBQK"):
              #if we find bishop or queen on diagonal, then checked is true, stop searching
              if board[int(note[1]) - distance][int(note[0]) + distance] in "BQ":
                isChecked = True
                break
              #if we find a king on diagonal within distance of 1, then checked is true, stop searching
              if board[int(note[1]) - distance][int(note[0]) + distance] == "K" and distance == 1:
                isChecked = True
                break
              distance += 1 #check if there are further out bishop or queen that will put king in check
      
      #NOW CHECK ALL VALID MOVES THAT GO IN THE BOTTOM-RIGHT DIRECTION
      #reset distance
      distance = 1
      while (int(note[1]) + distance <= 7) and (int(note[0]) + distance <= 7) and \
            (board[int(note[1]) + distance][int(note[0]) + distance] in "oBQK"):
              if board[int(note[1]) + distance][int(note[0]) + distance] in "BQ":
                isChecked = True
                break
              if board[int(note[1]) + distance][int(note[0]) + distance] in "K" and distance == 1:
                isChecked = True
                break
              distance += 1 #check if the bishop can move further now 
        
      #NOW CHECK ALL VALID MOVES THAT GO IN THE BOTTOM-LEFT DIRECTION
      #reset distance
      distance = 1
      while (int(note[1]) + distance <= 7) and (int(note[0]) - distance >= 0) and \
            (board[int(note[1]) + distance][int(note[0]) - distance] in "oBQK"):
              if board[int(note[1]) + distance][int(note[0]) - distance] in "BQ":
                isChecked = True
                break
              if board[int(note[1]) + distance][int(note[0]) - distance] == "K" and distance == 1:
                isChecked = True
                break
              distance += 1 #check if the bishop can move further now 
        
      #NOW CHECK ALL VALID MOVES THAT GO IN THE TOP-LEFT DIRECTION
      #reset distance
      distance = 1 #this gets incremented as we check how far the bishop can move
      #loops while it does not go off the board and does not make an invalid capture
      while (int(note[1]) - distance >= 0) and (int(note[0]) - distance >= 0) and \
            (board[int(note[1]) - distance][int(note[0]) - distance] in "oBQK"):
              if board[int(note[1]) - distance][int(note[0]) - distance] in "BQ":
                isChecked = True
                break
              if board[int(note[1]) - distance][int(note[0]) - distance] == "K" and distance == 1:
                isChecked = True
                break
              distance += 1 #check if the bishop can move further now 
      
      #NOW CHECK IF IN CHECK BY PAWN
      if int(note[0]) + 1 <= 7 and int(note[1]) + 1 <= 7:
        if board[int(note[1]) + 1][int(note[0]) + 1] == 'P':
          isChecked = True
      #below is the move right logic for pawn
      if int(note[0]) - 1 >= 0 and int(note[1]) + 1 <= 7:
        if board[int(note[1]) + 1][int(note[0]) - 1] == 'P':
          isChecked = True
      
    return isChecked
  
#makes the game think faster about its moves
def thinkSpeed(speed):
  if speed == 1:
    return "You are doing fine on time, think at normal speed"
  elif speed == 2:
    return "Hey hurry it up a little bit, make moves a little bit faster"
  elif speed == 3:
    return "Okay you're running pretty low on time, make quick moves"
  elif speed == 4:
    return "You're runnin very low on time, don't think, just make moves"
  else:
    return "sorry :("

#print board
def printBoard(board):
  for i in range(0,8):
    print()
    for j in range(0,8):
      print(board[i][j] + "|", end="")
  print()
