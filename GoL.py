import argparse
import pathlib
from typing import Optional

INT64_MAX = (2 ** 63) - 1
INT64_MIN = (-2 ** 63)

class Point:
    def __init__(self, x: int, y: int):
        if (x > INT64_MAX or x < INT64_MIN or
            y > INT64_MAX or y < INT64_MIN):
            raise Exception("X and Y coordinates must be within the 64-bit signed integer range.")
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "X: {x}, Y: {y}".format(x = self.x, y = self.y)

    def __repr__(self):
        return "({x},{y})".format(x = self.x, y = self.y)

    def __hash__(self):
        return hash((self.x, self.y))

class Cell:
    def __init__(self, point: Point, isNextGenAlive: Optional[bool] = None):
        self.point = point
        self.isNextGenAlive = isNextGenAlive

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.point == other
        if not isinstance(other, Cell):
            return False
        return self.point == other.point

    def __str__(self):
        return "X: {x}, Y: {y}, isNextGenAlive: {isNextGenAlive}".format(x = self.point.x, y = self.point.y, isNextGenAlive = self.isNextGenAlive)

    def __repr__(self):
        return "({x},{y},{isNextGenAlive})".format(x = self.point.x, y = self.point.y, isNextGenAlive = self.isNextGenAlive)

    def __hash__(self):
        return hash(self.point)

class GameOfLife:
    def __init__(self, initialLiveCells: set[Cell], numOfGenerations: int):
        if numOfGenerations < 0:
            raise Exception("Number of generations to run through must be zero or positive.")

        # To keep track of all live cells via a set of Cells
        self.liveCells = initialLiveCells.copy()
        # To keep track of all dead cell points and how many live neighbors they have
        self.deadCellNeighborCounts: dict[Point, int] = dict()
        self.numOfGenerations = numOfGenerations
        self.currentGeneration: int = 0

    def __str__(self):
        lcStr = "#Life 1.06\n"
        for lc in self.liveCells:
            lcStr += str(lc.point.x) + " " + str(lc.point.y) + "\n"
        return lcStr

    def runGenerations(self) -> None:
        while self.currentGeneration < self.numOfGenerations:
            self.runNextGeneration()

    def runNextGeneration(self) -> None:
        self.calculateNextGen()
        self.removeDeadCells()
        self.createNewCells()
        self.resetNextGen()
        self.currentGeneration += 1
    
    def calculateNextGen(self) -> None:
        # Run through each live cell
        for lc in self.liveCells:
            numLiveNeighbors = self.getLiveNeighbors(lc.point)
            lc.isNextGenAlive = numLiveNeighbors in {2,3}
    
    def getLiveNeighbors(self, point: Point) -> int:
        # Get all 8 possible directions for neighbors
        directions = [
            Point(1,0),
            Point(1,1),
            Point(0,1),
            Point(-1,1),
            Point(-1,0),
            Point(-1,-1),
            Point(0,-1),
            Point(1,-1),
        ]

        liveCount = 0

        for d in directions:
            x = point.x + d.x
            y = point.y + d.y
            if (x <= INT64_MAX and x >= INT64_MIN and
                y <= INT64_MAX and y >= INT64_MIN):

                neighbor = Point(x, y)

                if neighbor in self.liveCells:
                    liveCount += 1
                else:
                    if neighbor in self.deadCellNeighborCounts:
                        self.deadCellNeighborCounts[neighbor] += 1
                    else:
                        self.deadCellNeighborCounts[neighbor] = 1

        return liveCount
    
    def createNewCells(self) -> None:
        for k, v in self.deadCellNeighborCounts.items():
            if v == 3:
                self.liveCells.add(Cell(k, True))
        
        self.deadCellNeighborCounts.clear()
    
    def removeDeadCells(self) -> None:
        deadCells: set[Cell] = set()
        for c in self.liveCells:
            if c.isNextGenAlive == False:
                deadCells.add(c)
        
        self.liveCells -= deadCells
    
    def resetNextGen(self) -> None:
        for lc in self.liveCells:
            lc.isNextGenAlive = None

def getCommandLineArgs() -> tuple[Optional[str], Optional[int], Optional[str]]:
    argParser = argparse.ArgumentParser(
        prog="Conway's Game of Life",
        description="A program to run simulations of Conway's Game of Life"
    )

    argParser.add_argument("-f", "--filename", dest="filename", default=None)
    argParser.add_argument("-n", "--numberOfGens", dest="numberOfGens", default=None)
    argParser.add_argument("-s", "--solutionFilename", dest="solutionFilename", default=None)

    args = argParser.parse_args()

    filename: Optional[str] = None
    numberOfGens: Optional[int] = None
    solutionFilename: Optional[str] = None

    if args.filename:
        filename = str(args.filename)
    if args.numberOfGens:
        numberOfGens = int(args.numberOfGens)
    if args.solutionFilename:
        solutionFilename = str(args.solutionFilename)

    return (filename, numberOfGens, solutionFilename)

def readLiveCellFile(filename: str) -> set[Cell]:
    headerLine = "#Life 1.06"
    liveCells: set[Cell] = set()

    lifeFile = open(file=filename, mode="r")
    lines = lifeFile.readlines()
    
    if lines[0].strip() != headerLine:
        raise Exception("Life files must be in Life 1.06 format and contain the ""{headerLine}"" header".format(headerLine=headerLine))
    
    i = 1
    while i < len(lines):
        coords = lines[i].split(" ")
        liveCells.add(Cell(Point(int(coords[0]), int(coords[1]))))
        i += 1

    lifeFile.close()

    return liveCells

def writeLiveCellResultFile(filename: str, gol: GameOfLife, numOfGens: int):
    fullPath = filename + "-Result" + str(numOfGens) + ".life"
    with open(fullPath, "w") as f:
        f.write(str(gol))

    print("Wrote final board to file: {fullPath}".format(fullPath=fullPath))


def getLiveCellsFromConsole() -> set[Cell]:
    liveCells: set[Cell] = set()

    line = input()
    while line.strip():
        coords = line.split(" ")
        liveCells.add(Cell(Point(int(coords[0]), int(coords[1]))))
        line = input()

    return liveCells

def runGameOfLife():
    (filename, numOfGens, solutionFilename) = getCommandLineArgs()
    liveCells: set[Cell]
    if filename:
        print("Reading live cells from #Life 1.06 file: {filename}".format(filename=filename))
        liveCells = readLiveCellFile(filename)
    else:
        print("Reading live cells from console input:")
        liveCells = getLiveCellsFromConsole()
    
    if not numOfGens:
        numOfGens = 10

    print("Running Game of Live through {numOfGens} generation(s)...".format(numOfGens=numOfGens))
    game = GameOfLife(liveCells, numOfGens)
    game.runGenerations()

    if filename:
        writeLiveCellResultFile(pathlib.Path(filename).stem, game, numOfGens)
    else:
        print(game)

    if solutionFilename:
        solution = readLiveCellFile(solutionFilename)
        if solution == game.liveCells:
            print("Test Passed: Final board matches expected solution.")
        else:
            print("Test Failed: Final board does not match expected solution.")

# Test Cases
# 1. Standard Case
# 2. Large Coordinates, Offsetting Coordinates
# 3. Out of Bound Coordinates
# 4. Large Number of Coordinates

def main():
    runGameOfLife()

if __name__ == "__main__":
    main()
