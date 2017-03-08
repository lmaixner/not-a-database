from ..load_photometry import make_folder
from ..sort_photometry import f_group
import glob
from astropy.table import Table


def test_f_group():
	# testing that the final input file is the length of the combined input
	# files

	# separately retrieve files that f_group should have for comparison
	R_filelist = glob.glob('f_group_testdata/*R.csv')
	I_filelist = glob.glob('f_group_testdata/*I.csv')
	V_filelist = glob.glob('f_group_testdata/*V.csv')
	B_filelist = glob.glob('f_group_testdata/*B.csv')

	len_R = 0
	len_I = 0
	len_V = 0
	len_B = 0

	# retrieve combined lengths of each filter color files
	for file in R_filelist:
		len_R += len(Table.read(file))
	for file in I_filelist:
		len_I += len(Table.read(file))
	for file in V_filelist:
		len_V += len(Table.read(file))
	for file in B_filelist:
		len_B += len(Table.read(file))


	# creating filename pattern that is sent to f_group that it uses for file
	# retrieval
	filters = ['I', 'R', 'V', 'B']
	f_ext = r'D:\Everything\Class\Git\tests\f_group_testdata'
	pattern = os.path.join(f_ext, '*{}.csv')
	big_file = f_group(pattern.format(filters))

	#assert something_R_output == len_R
