import csv
from soupclass8 import r_csv, w_csv

def new_find(new, old):
	new_f = r_csv(new)
	old_f = r_csv(old)
	new_entries = [new_f[0]]
	check = ''

	for i in range(1, len(new_f)):
		check = True
		for i_2 in range(1, len(old_f)):
			if new_f[i][0] == old_f[i_2][0]:
				check = False
		if check:
			new_entries.append(new_f[i])
	w_csv(new_entries)
	return new_entries
