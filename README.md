# Conway's Game of Life

Conway's **Game of Life** implemented in Python for the 64-bit signed integer space.

## Command-Line Arguments

You can run `GoL.py` with various command-line arguments to control its behavior. The file format expected for the coordinates of live cells is the [#Life 1.06](https://conwaylife.com/wiki/Life_1.06) format. If the `--filename` argument is not specified, you can input the coordinates via command-line. It will accept coordinates until a blank line is read.

* `--numberOfGens <number>`, `-n <number>`: Specify the number of generations to run. Defaults to `10` if not specified.
* `--filename <path>`, `-f <path>`: Specify the path to the file of coordinates.
* `--solutionFilename <path>`, `-s <path>`: Specify the path to the solution file. This is used to debug and verify the simulations are running correctly.
