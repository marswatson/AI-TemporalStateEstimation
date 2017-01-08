import random
from CreateMap import *
from GenerateData import *
import heapq
from compiler.ast import flatten
import copy


# global movement first move up and down,,second move left and right
move = [[-1, 1, 0, 0], [0, 0, -1, 1]]

def Normalize(P):
    normal_sum = 0
    for i in range(len(P)):
        normal_sum += sum(P[i])
    for i in range(len(P)):
        for j in range(len(P[0])):
            P[i][j] = float(P[i][j])/normal_sum
    return P

def TransitionModel(map, P0, Action):
    max_row=len(P0)
    max_col=len(P0[0])
    P1 = [[0 for i in range(max_col)] for i in range(max_row)]
    for i in range(max_row):
        for j in range(max_col):
            new_i = i + Action[0]
            new_j = j + Action[1]
            #row and col requirement
            if new_i >= max_row or new_i < 0 or new_j >= max_col or new_j < 0 or map[new_i][new_j] == "B":
                P1[i][j] += P0[i][j]
            else:
                #90% move 10% stay
                P1[new_i][new_j] += 0.9*P0[i][j]
                P1[i][j] += 0.1*P0[i][j]
    return P1

def ObservationModel(map, P0, Evidence):
    max_row=len(P0)
    max_col=len(P0[0])
    P1 = [[0 for i in range(max_col)] for i in range(max_row)]
    for i in range(max_row):
        for j in range(max_col):
            if P0[i][j] <= 1e-5:#optimize
                continue
            if Evidence == map[i][j]:
                #sensor 90% right
                P1[i][j] = 0.9*P0[i][j]
            else:
                #sersor 5% make mistake
                P1[i][j] = 0.05*P0[i][j]

    P1 = Normalize(P1)
    return P1

def ComputeFilterProblem(map, initial,  Actions, Evidences):
    P = []
    P1 = initial
    for i in range(len(Actions)):
        P1 = TransitionModel(map,P1,Actions[i])
        P1 = ObservationModel(map,P1,Evidences[i])
        P.append(P1)
    return P

def ML_ComputeIntitialMaxPxe(map,evidence):
    max_row=len(map)
    max_col=len(map[0])
    Px1_e1 = [[0 for i in range(max_col)] for i in range(max_row)]
    for i in range(max_row):
        for j in range(max_col):
            if map[i][j] == "B":
                Px1_e1[i][j] = 0
            elif evidence == map[i][j]:
                Px1_e1[i][j] = 0.9
            else:
                Px1_e1[i][j] = 0.05
    Px1_e1 = Normalize(Px1_e1)
    return Px1_e1

def ML_MaxTM(map,Action,Pxpre_epre):
    max_row=len(map)
    max_col=len(map[0])
    P1 = [[0 for i in range(max_col)] for i in range(max_row)]
    ComeFrom = [[(0,0) for i in range(max_col)] for i in range(max_row)]
    for i in range(max_row):
        for j in range(max_col):
            old_i = i - Action[0]
            old_j = j - Action[1]
            #row and col requirement
            if map[i][j] == "B":
                P1[i][j] = 0
            elif old_i >= max_row or old_i < 0 or old_j >= max_col or old_j < 0 or map[old_i][old_j] == "B":
                P1[i][j] = 0.1 * Pxpre_epre[i][j]
            else:
                #90% move 10% stay
                P_frommove = 0.9*Pxpre_epre[old_i][old_j]
                P_fromstay = 0.1*Pxpre_epre[i][j]
                if(P_frommove > P_fromstay):
                    ComeFrom[i][j] = Action
                P1[i][j] = max(P_frommove,P_fromstay)
    return P1,ComeFrom

def ML_ComputeMaxPxtet(map,evidence,action,Pxpre_epre):
    P1,ComeFrom = ML_MaxTM(map,action,Pxpre_epre)
    max_row=len(map)
    max_col=len(map[0])
    Pxtet = [[0 for i in range(max_col)] for i in range(max_row)]
    for i in range(max_row):
        for j in range(max_col):
            if P1[i][j] <= 1e-5:#optimize
                continue
            if evidence == map[i][j]:
                #sensor 90% right
                Pxtet[i][j] = 0.9*P1[i][j]
            else:
                #sersor 5% make mistake
                Pxtet[i][j] = 0.05*P1[i][j]
    Pxtet = Normalize(Pxtet)
    return Pxtet,ComeFrom

def ComputeMLSequence(map,Actions, Evidences):
    P = []
    ComeFrom = []
    P1 = ML_ComputeIntitialMaxPxe(map,Evidences[0])
    P.append(P1)
    for i in range(1, len(Actions)):
        P1,cm = ML_ComputeMaxPxtet(map,Evidences[i],Actions[i],P1)
        ComeFrom.append(cm)
        P.append(P1)
    return P,ComeFrom

def ML_FindPath(k,P,ComeFrom):
    Klarge = []
    row = len(P[-1])
    col = len(P[-1][0])
    P_1d = flatten(P[-1])
    maxVal = heapq.nlargest(k, P_1d)
    maxPos = []
    a = maxVal[-1]
    for i in range(row):
        for j in range(col):
            if P[-1][i][j] >= maxVal[-1] and P[-1][i][j] != 0:
                pos = (i,j)
                maxPos.append(pos)
    Path = []
    for i in range(len(maxPos)):
        tempPath = []
        tempPath.append(maxPos[i])
        r = maxPos[i][0]
        c = maxPos[i][1]
        pathlength = len(ComeFrom)
        for j in range(pathlength):
            new_r = r - ComeFrom[pathlength-j - 1][r][c][0]
            new_c = c - ComeFrom[pathlength-j - 1][r][c][1]
            r = new_r
            c = new_c
            pos = (r,c)
            tempPath.append(pos)
        tempPath.reverse()
        Path.append(tempPath)
    return Path

def PathError(filename, Path, positions):
    error = []
    file = open(filename, 'w')
    for k in range(len(positions)):
        a_x,a_y = positions[k]
        b_x=Path[k][0]
        b_y=Path[k][1]
        err= abs(b_x-a_x) + abs(b_y-a_y)
        error.append(err)
        file.write(str(positions[k][0]) + ',' + str(positions[k][1]) + ' '
                   + str(b_x)+','+str(b_y) + ' ' + str(err)+ '\n')
    #file.write(str(err) + '\n')
    file.close()
    return error

def saveMLResults():
    error_list=[]
    pro_list = []
    kth = 10
    for it in range(10):
        for jt in range(10):
            filename = 'maps/map_' + str(it) + '_' + str(jt) + '.txt'
            maze_grid, start, positions, actions, evidences = readGroundTruthData(filename)

            P,ComeFrom = ComputeMLSequence(maze_grid,actions,evidences)
            Path = ML_FindPath(kth,P,ComeFrom)

            kPathErrors = []
            for k in range(len(Path)):
                filename2 = 'maps/ML_map_' + str(it) + '_' + str(jt)+ 'Path'+ str(k) + '.txt'
                Patherror = PathError(filename2,Path[k],positions)
                kPathErrors.append(Patherror)
            kPathAverageErrors = []
            for k in range(len(kPathErrors)):
                aError = float(sum(kPathErrors[k])) / len(kPathErrors[k])
                kPathAverageErrors.append(aError)
            kPathSmallError = 100000
            kPathSmallIndex = -1
            for k in range(len(kPathAverageErrors)):
                if kPathAverageErrors[k] < kPathSmallError:
                    kPathSmallError = kPathAverageErrors[k]
                    kPathSmallIndex = k
            error=kPathErrors[kPathSmallIndex]
            error_list.append(error)

            filename3 = 'maps/ML_map_' + str(it) + '_' + str(jt)+ 'MostLikelyPathIndex' + '.txt'
            file = open(filename3, 'w')
            file.write(str(kPathSmallIndex) + '\n')
            file.close()

    error_list_traverse= [[row[i] for row in error_list] for i in range(len(error_list[0]))]
    error_avg_list=[ sum(i)/float(len(i)) for i in error_list_traverse ]
    filename4 = 'maps/ML_error_avg_list.txt'
    file = open(filename4, 'w')
    for i in error_avg_list:
        file.write(str(i) + '\n')
    file.close()

# draw maze
def draw_sequence(maze_grid):

    # get size
    (col, row) = get_grid_size(maze_grid)

    screen = Tkinter.Tk()
    canvas = Tkinter.Canvas(screen, width=(col+2)*5, height=(row+2)*5)
    canvas.pack()

    # create initial grid world
    for c in range(1, col+2):
        canvas.create_line(c*5, 5, c*5, (row+1)*5, width=1)
    for r in range(1, row+2):
        canvas.create_line(5, r*5, (col+1)*5, r*5+1, width=1)

    # mark blocked grid as black, start state as red, goal as green
    for c in range(0, col):
        for r in range(0, row):

            # if blocked
            if maze_grid[r][c] == "B":
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="black")
            # if unblocked
            if maze_grid[r][c] == "N":
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="white")
            # if hard unblock
            if maze_grid[r][c] == "T":
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="gray")
            # if unblock highway
            if maze_grid[r][c] == "H":
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="yellow")
            # if true path
            if maze_grid[r][c] == 10:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="green")
            # if path 0
            if maze_grid[r][c] == 0:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="LightPink")
            # if path 1
            if maze_grid[r][c] == 1:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="Pink")
            # if path 2
            if maze_grid[r][c] == 2:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="Crimson")
            # if path 3
            if maze_grid[r][c] == 3:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="LavenderBlush")
            # if path 4
            if maze_grid[r][c] == 4:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="PaleVioletRed")
            # if path 5
            if maze_grid[r][c] ==5:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="HotPink")
            # if path 6
            if maze_grid[r][c] == 6:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="DeepPink")
            # if path 7
            if maze_grid[r][c] == 7:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="MediumVioletRed")
            # if path 8
            if maze_grid[r][c] == 8:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="Orchid")
            # if path 9
            if maze_grid[r][c] == 9:
                canvas.create_rectangle((c+1)*5+1, (r+1)*5+1, (c+2)*5, (r+2)*5, fill="Thistle")
    screen.mainloop()


# test
# map = [["H","H", "T"],["N","N", "N"],["N","B","H"]]
# row = 3
# col = 3
# Actions = [[0,1],[0,1],[1,0],[1,0]]
# Evidences = ["N", "N", "H", "H"]
# Initial = [[0 for i in range(col)] for i in range(row)]
# for i in range(row):
#     for j in range(col):
#         Initial[i][j] = 1.0 / 8
# Initial[2][1] = 0
# P,ComeFrom = ComputeMLSequence(map,Actions,Evidences)

# Path = []
# for i in range(len(P)):
#     tempP = []
#     tempComeFrom = []
#     for j in range(i):
#         tempP.append(P[j])
#         tempComeFrom.append(ComeFrom[j])
#     tempP.append(P[i])
#     Path.append(ML_FindPath(1,tempP,tempComeFrom))
# Path = ML_FindPath(8,P,ComeFrom)
# print Path
maze_grid, start, positions, actions, evidences = readGroundTruthData('test.txt')
row = len(maze_grid)
col = len(maze_grid[0])
P,ComeFrom = ComputeMLSequence(maze_grid,actions,evidences)
Path = ML_FindPath(10,P,ComeFrom)
print len(Path[0])
print Path


tempP = []
tempComeFrom = []
iterationNumber = 10
for i in range(iterationNumber-1):
    tempP.append(P[i])
    tempComeFrom.append(ComeFrom[i])
tempP.append(P[iterationNumber-1])
Path = ML_FindPath(10,tempP,tempComeFrom)

visulizeresults = []
for i in range(len(Path)+1):
    temp_maze = copy.deepcopy(maze_grid)
    row = len(maze_grid)
    col = len(maze_grid[0])
    if i < 10:
        for j in range(len(Path[i])):
            r = Path[i][j][0]
            c = Path[i][j][1]
            temp_maze[r][c] = i
    else:
        for j in range(len(positions)):
            r = positions[j][0]
            c = positions[j][1]
            temp_maze[r][c] = i
    visulizeresults.append(temp_maze)
for i in visulizeresults:
    draw_sequence(i)
#
#
#
#
# Errors = []
# for i in range(len(Path)):
#     file = "test_results_" + str(i) + ".txt"
#     error = PathError(file,Path[i],positions)
#     Errors.append(error)
# kPathAverageErrors = []
# for i in range(len(Errors)):
#     aError = float(sum(Errors[i])) / len(Errors[i])
#     kPathAverageErrors.append(aError)
# kPathSmallError = 100000
# kPathSmallIndex = -1
# for i in range(len(kPathAverageErrors)):
#     if kPathAverageErrors[i] < kPathSmallError:
#         kPathSmallError = kPathAverageErrors[i]
#         kPathSmallIndex = i



