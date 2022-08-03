# slice at: 4
new_entries_count = 5 - 4

rows = [0, 1, 2, 3, 4]
collumns = ["a", "b", "c", "d", "e"]

update_entries = rows[:4]
new_entries = rows[-new_entries_count:]

print("these are new: old")
print(update_entries)
print("these are new: ")
print(new_entries)

for e, j in zip(rows, collumns):
	print(e)
	print(j)