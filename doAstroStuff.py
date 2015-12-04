from GetGiantPileofSpreadsheets import *
from SortGiantPileofSpreadsheets import *

# Location of Source Images
sourceFilesLocation = r'C:\Users\ShakAttack\Desktop\Everything\Class\2015Fall\Phys300\2015_09_25_Reduced'

# Where to put intermediate spreadsheets
# full path or folder in current directory
pileFileLocation = r'C:\Users\ShakAttack\Desktop\Everything\Class\2015Fall\Phys300\garbage'

# For Filter Grouped sheets
objectName = "M71"
filteredFileLocation = r'C:\Users\ShakAttack\Desktop\Everything\Class\2015Fall\Phys300\output'
filtersToUse = ['I', 'R', 'V', 'B']
targetDirectory = 'output'

files = loadFiles(sourceFilesLocation)

print("Files are loaded... ")

writeTables(files, pileFileLocation)
# location/name of target directory can be set but has default
# inner/outer radii, gain, and read noise can be sent but have defaults

print("You are burried in a giant pile of spreadsheets... ")

GroupByFilter(filteredFileLocation, objectName, filtersToUse, targetDirectory)
# location/name of target directory can be set but has default
# can be sent a list of filters to go through but defaults to I,R,V,B filters

print("They are now grouped by filter... ")
