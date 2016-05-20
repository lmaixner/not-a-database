from GetGiantPileofSpreadsheets import *
from SortGiantPileofSpreadsheets import *
from AvgFlux import *
from CMD import *
import os

# Location of Source Images
sourceFilesLocation = r'C:\Users\ShakAttack\Desktop\Everything\Class\2015Fall\Phys300\2015_09_25_Reduced'

# Where to put intermediate spreadsheets
# full path or folder in current directory
pileFileLocation = r'output'

# For Filter Grouped sheets
objectName = "M71"
filteredFileLocation = r'Sorted'
filtersToUse = ['I', 'R', 'V', 'B']
AveragedLocation = r'Averaged'
AvgLocAndFilt = r'C:\Users\ShakAttack\Desktop\Everything\Class\Git\M71\Sorted\*Filt*.csv'

# CMD
LongWavelength = r'*I*.csv'
ShortWavelength = r'*R*.csv'


files = load_files(sourceFilesLocation)

print("Files are loaded... ")

next_loc = write_tables(files, pileFileLocation, objectName)
# location/name of targetdirectory can be set but has default
# inner/outer radii, gain, and read noise can be sent but have defaults

print("You are burried in a giant pile of spreadsheets... ")

next_loc = group_by_filter(next_loc, objectName, filtersToUse, filteredFileLocation, objectName)
# location/name of target directory can be set but has default
# can be sent a list of filters to go through but defaults to I,R,V,B filters

print("They are now grouped by filter... ")


next_loc = avg_flux(os.path.join(os.path.join(r'C:\Users\ShakAttack\Desktop\Everything\Class\Git', next_loc), '*Filt*'),AveragedLocation, objectName)

print("Filters have been averaged... ")

make_CMD(os.path.join(os.path.join(next_loc, ShortWavelength)), os.path.join(next_loc, LongWavelength))
