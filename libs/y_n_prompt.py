def yn():
	reply = str(input()).lower().strip()
	if reply[0] == 'y':
		return True
	if reply[0] == 'n':
		return False
	else :
		print("invalid input [y/n] ?", end=" ")
		return yn()