from GenerateData import transfromMap,generateGroundTruth,writeGroundTruthData,readGroundTruthData
from FilterTest import *

from matplotlib import pyplot as PLT
from matplotlib import cm as CM
from matplotlib import mlab as ML
import numpy as NP

# n = 1e5
# x = y = NP.linspace(-5, 5, 100)
# X, Y = NP.meshgrid(x, y)
# Z1 = ML.bivariate_normal(X, Y, 2, 2, 0, 0)
# Z2 = ML.bivariate_normal(X, Y, 4, 1, 1, 1)
# ZD = Z2 - Z1
# x = X.ravel()
# y = Y.ravel()
# z = ZD.ravel()
# gridsize=30
# PLT.subplot(111)
#
# # if 'bins=None', then color of each hexagon corresponds directly to its count
# # 'C' is optional--it maps values to x-y coordinates; if 'C' is None (default) then
# # the result is a pure 2D histogram
#
# PLT.hexbin(x, y, C=z, gridsize=gridsize, cmap=CM.jet, bins=None)
# PLT.axis([x.min(), x.max(), y.min(), y.max()])
#
# cb = PLT.colorbar()
# cb.set_label('mean value')
# PLT.show()

def plotHeatMap(P):
    L = P[::-1]
    row = len(L)
    col = len(L[0])
    x = NP.linspace(0,col-1,col)
    y = NP.linspace(0,row-1,row)
    X,Y = NP.meshgrid(x,y)
    ZD = NP.array(L)

    x = X.ravel()
    y = Y.ravel()
    z = ZD.ravel()
    gridsize=30
    PLT.subplot(111)

    # if 'bins=None', then color of each hexagon corresponds directly to its count
    # 'C' is optional--it maps values to x-y coordinates; if 'C' is None (default) then
    # the result is a pure 2D histogram

    PLT.hexbin(x, y, C=z, gridsize=gridsize, cmap=CM.jet, bins=None)
    PLT.axis([x.min(), x.max(), y.min(), y.max()])

    cb = PLT.colorbar()
    cb.set_label('mean value')
    PLT.show()





# map = [["H","H", "T"],["N","N", "N"],["N","B","H"]]
# row = 3
# col = 3
# Actions = [[0,1],[0,1],[1,0],[1,0]]
# Evidences = ["N", "N", "H", "H"]
# Initial = [[0 for i in range(col)] for i in range(row)]
# for i in range(row):
#     for j in range(col):
#         Initial[i][j] = 1.0 / (row*col)
# P = ComputeMLSequence(map,Actions,Evidences)
# plotHeatMap(P[3])
# print 1
maze_grid, start, positions, actions, evidences = readGroundTruthData('test.txt')
row = len(maze_grid)
col = len(maze_grid[0])
Initial = [[0 for i in range(col)] for i in range(row)]
for i in range(row):
    for j in range(col):
        Initial[i][j] = 1.0 / (0.8*row*col)
P = ComputeFilterProblem(maze_grid,Initial,actions,evidences)
plotHeatMap(P[-1])