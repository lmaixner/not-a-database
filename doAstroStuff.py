from load_photometry import *
from sort_photometry import *
from avg_photometry import *
from make_CMD import *
import os

### VARIABLES ###
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
location_ext = r'C:\Users\ShakAttack\Desktop\Everything\Class\Git\M71\Averaged'
LongWavelength = 'I'
ShortWavelength = 'V'
membership = r'C:\Users\ShakAttack\Desktop\Everything\Class\Git\MembershipLists\M71MembershipList.csv'
# if they're something different from what they normally would be
member_col_RA = "RA"
member_col_Dec = "Dec"

"""
### MAIN ###
files = load_photometry(sourceFilesLocation)
print("Files are loaded... ")
output_loc = write_tables(files, pileFileLocation, objectName)
#print(output_loc) #I want this to be the full path name not just the extension on the PWD
# location/name of targetdirectory can be set but has default
# inner/outer radii, gain, and read noise can be sent but have defaults

print("You are burried in a giant pile of spreadsheets... ")

sorted_loc = sort_photometry('M71\output', objectName, filtersToUse, filteredFileLocation, objectName)
#print(sorted_loc)
# location/name of target directory can be set but has default
# can be sent a list of filters to go through but defaults to I,R,V,B filters

print("They are now grouped by filter... ")
"""
avged_loc = avg_photometry(os.path.join(os.path.join(r'C:\Users\ShakAttack\Desktop\Everything\Class\Git', 'M71\Sorted'), '*Filt*'), AveragedLocation, objectName)
#print(avged_loc)

print("Filters have been averaged... ")

make_CMD(location_ext, ShortWavelength, LongWavelength, cluster_members=membership, plt_nonmembers=True, object_name=objectName)  # , plot_separate=False)
