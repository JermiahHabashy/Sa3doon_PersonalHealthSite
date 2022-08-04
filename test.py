import requests

# slice at: 2
list_entries = [0, 1, 2, 3]
list_records = [0]

total_entries_count = len(list_entries)
total_records_count = len(list_records)
new_entries_count = total_entries_count - total_records_count


update_entries = list_entries[0:total_records_count]
new_entries = list_entries[total_records_count:]


print("these are new: old")
print(update_entries)
print("these are new: ")
print(new_entries)



# # API config
# url = "https://edamam-food-and-grocery-database.p.rapidapi.com/parser"
# headers = {
# 	"X-RapidAPI-Key": "542e6db5bbmsh4d71ec3335b847fp1df863jsne3b51f1dc049",
# 	"X-RapidAPI-Host": "edamam-food-and-grocery-database.p.rapidapi.com"
# }
# response = requests.request("GET", url, headers=headers, params={"ingr": "banana, pie"})
# response.raise_for_status()
# print(response.json())
# print(response.json()["parsed"][0]["food"]["nutrients"])