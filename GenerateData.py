from CreateMap import create_map,writemap
import  random

move = [[-1, 1, 0, 0], [0, 0, -1, 1]]

def transfromMap(maze_grid):
    max_row=len(maze_grid)
    max_col=len(maze_grid[0])
    for r in range(max_row):
        for c in range(max_col):
            # if blocked
            if maze_grid[r][c] == 0:
                maze_grid[r][c] = "B"
            # if unblocked
            if maze_grid[r][c] == 1:
                maze_grid[r][c] = "N"
            # if hard unblock
            if maze_grid[r][c] == 2:
                maze_grid[r][c] = "T"
            # if unblock highway
            if maze_grid[r][c] == 'a1' or maze_grid[r][c] == 'a2' or maze_grid[r][c] == 'a3' or maze_grid[r][c] == 'a4':
                maze_grid[r][c] = "H"
            # if hard unblock highway
            if maze_grid[r][c] == 'b1' or maze_grid[r][c] == 'b2' or maze_grid[r][c] == 'b3' or maze_grid[r][c] == 'b4':
               maze_grid[r][c] = "H"
    return maze_grid

#select the possible start and goal point
def select_start(maze_grid):
    row = len(maze_grid)
    col = len(maze_grid[0])
    r = random.randint(0, row-1)
    c = random.randint(0, col-1)
    while maze_grid[r][c] == "B":
        r = random.randint(0, row-1)
        c = random.randint(0, col-1)
    cell = (r, c)
    return cell

def randomAction():
    direction = random.randint(0, 3)
    if direction == 0:
        action = [-1,0]
        return action
    elif direction == 1:
        action = [1,0]
        return action
    elif direction == 2:
        action = [0,-1]
        return action
    elif direction == 3:
        action = [0,1]
        return action

def generateGroundTruth(maze_grid):
    max_row=len(maze_grid)
    max_col=len(maze_grid[0])
    number = 100
    actions = []
    evidences = []
    positions = []
    success = False
    while success == False:
        start = select_start(maze_grid)
        r = start[0]
        c = start[1]
        for i in range(number):
            action = randomAction()
            new_r = r+action[0]
            new_c = c+action[1]
            #out of boundry 100% is old position
            if new_r >= max_row or new_r < 0 or new_c >= max_col or new_c < 0 or maze_grid[new_r][new_c] == "B":
                r = r
                c = c
            else:
                #in boundry 90% in new position
                if random.randint(1,100) <= 90:
                    r = new_r
                    c = new_c
            position = (r,c)
            positions.append(position)
            actions.append(action)
            if random.randint(1,100) <= 90:
                evidence = maze_grid[r][c]
            else:
                if  maze_grid[r][c] == "N":
                    if random.randint(1,100) <= 50:
                        evidence = "H"
                    else:
                        evidence = "T"
                elif  maze_grid[r][c] == "H":
                    if random.randint(1,100) <= 50:
                        evidence = "N"
                    else:
                        evidence = "T"
                else:
                    if random.randint(1,100) <= 50:
                        evidence = "N"
                    else:
                        evidence = "H"
            evidences.append(evidence)
        success = True
    return start, positions, actions, evidences

def writeGroundTruthData(filename, maze_grid, start, positions, actions, evidences):
    file = open(filename,'w')
    file.write(str(start[0])+ ',' + str(start[1]) + '\n')
    for i in positions:
        k = ','.join([str(j) for j in i])
        file.write(k+"\n")
    for i in actions:
        k = ','.join([str(j) for j in i])
        file.write(k+" ")
    file.write("\n")

    k = ','.join([str(evidence) for evidence in evidences])
    file.write(k+"\n")

    row=len(maze_grid)
    col=len(maze_grid[0])
    file.write(str(row) + ',' + str(col) + '\n')
    for i in maze_grid:
        k = ' '.join([str(j) for j in i])
        file.write(k+"\n")
    file.close()

def readGroundTruthData(filename):
    file = open(filename,'r')

    line = file.readline()
    start = line

    positions = []
    for i in range(100):
        line = file.readline()
        line = line.strip('\n')
        positions.append(line)

    line = file.readline()
    line = line.strip('\n')
    actions = line

    line = file.readline()
    line = line.strip('\n')
    evidences = line

    line = file.readline()
    maze_grid = []
    while line:
        line = file.readline()
        line = line.strip('\n')
        maze_grid.append(line)
    maze_grid.pop()

    start = list(map(eval,start.split(',')))

    actions = actions.split(' ')
    actions.pop()
    for i in range(len(actions)):
        actions[i] = actions[i].split(',')
        actions[i] = list(map(eval,actions[i]))

    evidences = evidences.split(',')

    for i in range(len(positions)):
        positions[i] = positions[i].split(',')
        positions[i] = list(map(eval,positions[i]))
    for i in range(len(maze_grid)):
        maze_grid[i] = maze_grid[i].split(' ')
        for index,item in enumerate(maze_grid[i]):
            if item == 'N':
                maze_grid[i][index] = "N"
            elif item == 'H':
                maze_grid[i][index] = "H"
            elif item == 'T':
                maze_grid[i][index] = "T"
            elif item == 'B':
                maze_grid[i][index] = "B"
    return maze_grid, start, positions, actions, evidences

#test

# (mymap,hard_traverse) = create_map(160,120)
# mymap = transfromMap(mymap)
# start, positions, actions, evidences = generateGroundTruth(mymap)
# writeGroundTruthData('test.txt', mymap, start, positions, actions, evidences)
# maze_grid, start, positions, actions, evidences = readGroundTruthData('test.txt')
# print 1