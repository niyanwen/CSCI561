import sys
import copy

board_score = [[0 for col in range(5)] for row in range(5)]

final_board_state = [[0 for col in range(5)] for row in range(5)]

PLAYER = ''

outputFile1 = open('next_state.txt', 'w')
outputFile2 = open('traverse_log.txt', 'w')
outputFile3 = open('trace_state.txt', 'w')

"""=====================process Input==================================="""
def processInput():
	
	board_state = [[0 for col in range(5)] for row in range(5)]
	global PLAYER

	with open(sys.argv[-1], 'r') as inputFile:
			inputList = [line.rstrip() for line in inputFile.readlines()]
			TASK = inputList[0]
			''' ===== for part2 ====='''
			if TASK == '4':
				processInput2(inputList)
				return

			''' ===== for part2 ====='''
			PLAYER = inputList[1]
			CUTOFF = int(inputList[2])

			for seq in range(3,8):
				for i in range(5):
					board_score[seq-3][i] = int(inputList[seq].split(' ')[i])

			for seq in range(8,13):
				state = list(inputList[seq])
				for i in range(5):
					board_state[seq-8][i] = state[i]

					
	if PLAYER == 'X':
		OPPONENT = 'O'
	if PLAYER == 'O':
		OPPONENT = 'X'

	print TASK
	print PLAYER 
	print CUTOFF 
	print board_score 
	print board_state

	if TASK == '1':
		Max(board_state, PLAYER, 0, -1, -1, CUTOFF)

	if TASK == '2':
		print 'Node,Depth,Value'
		outputFile2.write('Node,Depth,Value'+'\n')
		Max(board_state, PLAYER, 0, -1, -1, CUTOFF)

	if TASK == '3':
		print 'Node,Depth,Value,Alpha,Beta'
		outputFile2.write('Node,Depth,Value,Alpha,Beta'+'\n')
		Alpha(board_state, PLAYER, 0, -1, -1, CUTOFF, -sys.maxint, sys.maxint)

	

	
	print final_board_state
	printNextState(outputFile1, final_board_state)

'''====================== Deal With Two Players ============================================'''

def processInput2(inputList):
	board_state = [[0 for col in range(5)] for row in range(5)]

	PLAYER1 = inputList[1]
	TASK1 = inputList[2]
	CUTOFF1 = int(inputList[3])
	PLAYER2 = inputList[4]
	TASK2 = inputList[5]
	CUTOFF2 = int(inputList[6])

	global board_score

	for seq in range(7,12):
		for i in range(5):
			board_score[seq-7][i] = int(inputList[seq].split(' ')[i])

	for seq in range(12,17):
		state = list(inputList[seq])
		for i in range(5):
			board_state[seq-12][i] = state[i]

	print TASK1
	print PLAYER1 
	print CUTOFF1
	print TASK2
	print PLAYER2 
	print CUTOFF2  
	print board_score 
	print board_state

	global final_board_state
	global outputFile3
	content = ''

	final_board_state = copy.deepcopy(board_state)

	PLAYER1_TURN = 1
	PLAYER2_TURN = 0

	while(End(final_board_state) == False):

		if TASK1 == '1' and PLAYER1_TURN == 1:
			Max(final_board_state, PLAYER1, 0, -1, -1, 1)	
			content += printTraceState('',final_board_state)
			if(End(final_board_state)):
				break
			PLAYER1_TURN = 0
			PLAYER2_TURN = 1

		if TASK1 == '2' and PLAYER1_TURN == 1:
			Max(final_board_state, PLAYER1, 0, -1, -1, CUTOFF1)	
			content += printTraceState('',final_board_state)
			if(End(final_board_state)):
				break
			PLAYER1_TURN = 0
			PLAYER2_TURN = 1

		if TASK1 == '3' and PLAYER1_TURN == 1:
			Alpha(final_board_state, PLAYER1, 0, -1, -1, CUTOFF1, -sys.maxint, sys.maxint)	
			content += printTraceState('',final_board_state)
			if(End(final_board_state)):
				break
			PLAYER1_TURN = 0
			PLAYER2_TURN = 1

		if TASK2 == '1' and PLAYER2_TURN == 1:
			Max(final_board_state, PLAYER2, 0, -1, -1, 1)
			content += printTraceState('',final_board_state)
			if(End(final_board_state)):
				break
			PLAYER1_TURN = 1
			PLAYER2_TURN = 0

		if TASK2 == '2' and PLAYER2_TURN == 1:
			Max(final_board_state, PLAYER2, 0, -1, -1, CUTOFF2)
			content += printTraceState('',final_board_state)
			if(End(final_board_state)):
				break
			PLAYER1_TURN = 1
			PLAYER2_TURN = 0

		if TASK2 == '3' and PLAYER2_TURN == 1:
			Alpha(final_board_state, PLAYER2, 0, -1, -1, CUTOFF2, -sys.maxint, sys.maxint)
			content += printTraceState('',final_board_state)
			if(End(final_board_state)):
				break
			PLAYER1_TURN = 1
			PLAYER2_TURN = 0

	print final_board_state
	outputFile3.write(content)

'''====================== MiniMax ===================================='''
def Max(board_state, PLAYER, depth, upi, upj, CUTOFF):
	global final_board_state
	newPLAYER = PLAYER
	value = 0
	bestValue = -sys.maxint

	tmp_board_state = copy.deepcopy(board_state)

	# Terminal situation
	if End(board_state):
		value = cal_eval(board_state,PLAYER)
		printMinMax(upi,upj,depth,value)
		return value

	if (depth >= CUTOFF):
		value = cal_eval(board_state,PLAYER)
		printMinMax(upi,upj,depth,value)
		return value

	printMinMax(upi, upj, depth, bestValue)

	for i in range(0,5):
		for j in range(0,5):
			if board_state[i][j] == '*':
				new_board_state = makeMove(tmp_board_state, i, j, PLAYER)
				value = Min(new_board_state, newPLAYER, depth+1, i, j, CUTOFF)
				# newPLAYER = changeMainPlayer(PLAYER)
				tmp_board_state = copy.deepcopy(board_state)
				
				if value > bestValue:
					bestValue = value
					'''new plus'''
					if depth == 0:
						final_board_state = copy.deepcopy(new_board_state)


				printMinMax(upi,upj,depth,bestValue)

	return bestValue

def Min(board_state, PLAYER, depth, upi, upj, CUTOFF):
	global final_board_state
	value = 0
	bestValue = sys.maxint
	newPLAYER = PLAYER

	tmp_board_state = copy.deepcopy(board_state)

	# Terminal situation
	if End(board_state):
		value = cal_eval(board_state,PLAYER)
		printMinMax(upi,upj,depth,value)
		return value

	if (depth >= CUTOFF):
		value = cal_eval(board_state,PLAYER)
		printMinMax(upi,upj,depth,value)
		return value
	
	printMinMax(upi, upj, depth, bestValue)


	for i in range(0,5):
		for j in range(0,5):
			if board_state[i][j] == '*':

				newPLAYER = changeMainPlayer(PLAYER) 
				new_board_state = makeMove(tmp_board_state, i, j, newPLAYER)
				newPLAYER = changeMainPlayer(newPLAYER)
				value = Max(new_board_state, newPLAYER, depth+1, i, j, CUTOFF)
				tmp_board_state = copy.deepcopy(board_state)

				if value < bestValue:
					bestValue = value



				printMinMax(upi,upj,depth,bestValue)	

	return bestValue

'''====================== AlphaBeta ==================================''' 
def Alpha(board_state, PLAYER, depth, upi, upj, CUTOFF, alpha, beta):
	global final_board_state
	newPLAYER = PLAYER
	value = 0
	bestValue = -sys.maxint

	tmp_board_state = copy.deepcopy(board_state)

	# Terminal situation
	if End(board_state):
		value = cal_eval(board_state,PLAYER)
		printAlphaBeta(upi,upj,depth,value,alpha,beta)
		return value

	if (depth >= CUTOFF):
		value = cal_eval(board_state,PLAYER)
		printAlphaBeta(upi,upj,depth,value,alpha,beta)
		return value

	printAlphaBeta(upi, upj, depth, bestValue,alpha,beta)

	for i in range(0,5):
		for j in range(0,5):
			if board_state[i][j] == '*':
				new_board_state = makeMove(tmp_board_state, i, j, PLAYER)
				value = Beta(new_board_state, newPLAYER, depth+1, i, j, CUTOFF, alpha, beta)
				tmp_board_state = copy.deepcopy(board_state)
				
				if value > bestValue:
					bestValue = value
					final_board_state = copy.deepcopy(new_board_state)

				if value > alpha and value < beta:
					alpha = value

				printAlphaBeta(upi,upj,depth,bestValue,alpha,beta)

				if value >= beta:
					return value

	return bestValue

def Beta(board_state, PLAYER, depth, upi, upj, CUTOFF, alpha, beta):
	global final_board_state
	value = 0
	bestValue = sys.maxint
	newPLAYER = PLAYER

	tmp_board_state = copy.deepcopy(board_state)

	# Terminal situation
	if End(board_state):
		value = cal_eval(board_state,PLAYER)
		printAlphaBeta(upi,upj,depth,value,alpha,beta)
		return value

	if (depth >= CUTOFF):
		value = cal_eval(board_state,PLAYER)
		printAlphaBeta(upi,upj,depth,value,alpha,beta)
		return value

	printAlphaBeta(upi, upj, depth, bestValue,alpha,beta)

	for i in range(0,5):
		for j in range(0,5):
			if board_state[i][j] == '*':
				newPLAYER = changeMainPlayer(PLAYER)
				new_board_state = makeMove(tmp_board_state, i, j, newPLAYER)
				newPLAYER = changeMainPlayer(newPLAYER)
				value = Alpha(new_board_state, newPLAYER, depth+1, i, j, CUTOFF, alpha, beta)
				tmp_board_state = copy.deepcopy(board_state)

				if value < bestValue:
					bestValue = value

				if value < beta and value > alpha:
					beta = value;

				printAlphaBeta(upi,upj,depth,bestValue,alpha,beta)

				if value <= alpha:
					return value	

	return bestValue


def makeMove(board_state, i, j, PLAYER):

	board_state[i][j] = PLAYER

	if PLAYER == 'X':
		OPPONENT = 'O'
	else:
		OPPONENT = 'X'

	# left is the same
	if j-1 >= 0 and board_state[i][j-1] == PLAYER:
		if j+1 <= 4 and board_state[i][j+1] == OPPONENT:
			board_state[i][j+1] = PLAYER
		if i+1 <= 4 and board_state[i+1][j] == OPPONENT:
			board_state[i+1][j] = PLAYER
		if i-1 >= 0 and board_state[i-1][j] == OPPONENT:
			board_state[i-1][j] = PLAYER
	# right is the same
	if j+1 <= 4 and board_state[i][j+1] == PLAYER:
		if j-1>=0 and board_state[i][j-1] == OPPONENT:
			board_state[i][j-1] = PLAYER
		if i+1 <= 4 and board_state[i+1][j] == OPPONENT:
			board_state[i+1][j] = PLAYER
		if i-1 >= 0 and board_state[i-1][j] == OPPONENT:
			board_state[i-1][j] = PLAYER
	# up is the same
	if i-1 >= 0 and board_state[i-1][j] == PLAYER:
		if j-1>=0 and board_state[i][j-1] == OPPONENT:
			board_state[i][j-1] = PLAYER
		if i+1 <= 4 and board_state[i+1][j] == OPPONENT:
			board_state[i+1][j] = PLAYER
		if j+1 <= 4 and board_state[i][j+1] == OPPONENT:
			board_state[i][j+1] = PLAYER
	# down is the same
	if i+1 <=4 and board_state[i+1][j] == PLAYER:
		if j-1>=0 and board_state[i][j-1] == OPPONENT:
			board_state[i][j-1] = PLAYER
		if i-1 >= 0 and board_state[i-1][j] == OPPONENT:
			board_state[i-1][j] = PLAYER
		if j+1 <= 4 and board_state[i][j+1] == OPPONENT:
			board_state[i][j+1] = PLAYER

	return board_state

def printAlphaBeta(i, j, depth, value,alpha,beta):

	line = ''

	if i<0 and j<0 :
		line += 'root'+','
		# chr(65) = 'A'
	else:
		line += chr(j+65)
		line += str(i+1)+','

	line += str(depth)+','

	if (value == sys.maxint):
		line += 'Infinity'+','
	elif (value == -sys.maxint):
		line += '-Infinity'+','
	else:
		line += str(value)+','

	if (alpha == sys.maxint):
		line += 'Infinity'+','
	elif (alpha == -sys.maxint):
		line += '-Infinity'+','
	else:
		line += str(alpha)+','

	if (beta == sys.maxint):
		line += 'Infinity'
	elif (beta == -sys.maxint):
		line += '-Infinity'
	else:
		line += str(beta)

	print line
	outputFile2.write(line+'\n')

def printMinMax(i, j, depth, value):

	line = ''

	if i<0 and j<0 :
		line += 'root'+','
		# chr(65) = 'A'
	else:
		line += chr(j+65)
		line += str(i+1)+','

	line += str(depth)+','

	if (value == sys.maxint):
		line += 'Infinity'
	elif (value == -sys.maxint):
		line += '-Infinity'
	else:
		line += str(value)

	# print line
	outputFile2.write(line+'\n')
	
def End(board_state):
	gameIsEnd = True
	for i in range(0,5):
		for j in range(0,5):
			if board_state[i][j] == '*':
				gameIsEnd = False
	return gameIsEnd

def changeMainPlayer(PLAYER):
	if PLAYER == 'X':
		PLAYER = 'O' 
		OPPONENT = 'X'
	else:
		PLAYER = 'X'
		OPPONENT = 'O'

	return PLAYER

def cal_eval(board_state, PLAYER):

	p_score = 0
	o_score = 0

	if PLAYER == 'X':
		OPPONENT = 'O'
	else:
		OPPONENT = 'X'

	for i in range(0,5):
		for j in range(0,5):
			if board_state[i][j] == PLAYER:
				p_score += board_score[i][j] 

	for i in range(0,5):
		for j in range(0,5):
			if board_state[i][j] == OPPONENT:
				o_score += board_score[i][j] 

	return p_score-o_score

def printNextState(outputFile, board_state):
	outputString = ""
	outputString += "".join(board_state[0]) + "\n"
	outputString += "".join(board_state[1]) + "\n"
	outputString += "".join(board_state[2]) + "\n"
	outputString += "".join(board_state[3]) + "\n"
	outputString += "".join(board_state[4]) + "\n"
	outputFile.write(outputString)

def printTraceState(content, board_state):
	content += "".join(board_state[0]) + "\n"
	content += "".join(board_state[1]) + "\n"
	content += "".join(board_state[2]) + "\n"
	content += "".join(board_state[3]) + "\n"
	content += "".join(board_state[4]) + "\n"

	return content


def main():
	processInput()


if __name__ == '__main__':
	main()