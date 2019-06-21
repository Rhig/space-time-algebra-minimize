# space-time-algebra-minimize
Python implementation of the minimization algorithm for space-time algebra


## How to use
First, create a csv input file in the "inputs" directory. It should have headers, where the first header is "name" (the name of the row, to identify in the output result), and the other headers are the delay values (d1,d2,...).

Then, change the FILE_BASE_NAME variable in ST_Optimize.py to match the name of your input file without the .csv suffix.

Finally, you can run ST_Optimize.py and an output excel file with the name as the input will appear in the "outputs" directory.
