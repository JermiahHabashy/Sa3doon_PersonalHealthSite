import os
import flask
import requests
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask import request
from static.scripts.forms import HealthForm, MacrosTable, MacrosRow

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

Bootstrap(app)
# connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/database/macros.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db: SQLAlchemy = SQLAlchemy(app)

# API config
url = "https://edamam-food-and-grocery-database.p.rapidapi.com/parser"
headers = {
	"X-RapidAPI-Key": os.environ.get("API_KEY"),
	"X-RapidAPI-Host": "edamam-food-and-grocery-database.p.rapidapi.com"
}


# config table
class Macros(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	food_name = db.Column(db.String(250), nullable=False)
	food_quantity = db.Column(db.Float(precision=2), nullable=False)
	proteins = db.Column(db.Integer)
	carbs = db.Column(db.Integer)
	fats = db.Column(db.Integer)
	calories = db.Column(db.Integer)


db.create_all()
db.session.commit()


@app.route('/', methods=["GET", "POST"])
def home():
	health_form: HealthForm = HealthForm()
	BMR = 0
	if health_form.validate_on_submit():
		# base_bmr = 10 x weight(kg) + 6.25 x height(cm) - 5 x age(y) + 5 (man) = BMR10 x weight(kg) + 6.25 x height(
		# cm) - 5 x age(y)
		# for men: +5
		# for women: -161
		BMR = 10 * float(health_form.weight.data) + 6.25 * float(health_form.height.data) - 5 * health_form.age.data
		if health_form.sex.data == "Male":
			BMR += 5
		else:
			BMR -= 161
	return flask.render_template("index.html", health_form=health_form, BMR=BMR)


@app.route('/macros', methods=["GET", "POST"])
def macros():
	macros_table: MacrosTable = MacrosTable()
	macros_records = db.session.query(Macros).all()
	# row_change = 0

	if request.method == 'POST':
		# add new table row
		if macros_table.btn_add_row.data:
			macros_table.btn_add_row.data = False
			macros_table.macro_rows.append_entry()

		# remove last row only if you more than 1 entry
		elif macros_table.btn_remove_last_row.data and len(macros_table.macro_rows.entries) > 1:
			macros_table.btn_remove_last_row.data = False
			macros_table.macro_rows.pop_entry()

		# post data to database
		# find better API
		elif macros_table.btn_update.data:
			macros_table.btn_update.data = False

			def save_to_db(food_entry, id = -1):
				response = requests.request("GET", url, headers=headers, params={"ingr": food_entry.data["food_name"]})
				response.raise_for_status()
				macros = response.json()["parsed"][0]["food"]["nutrients"]

				macros["PROCNT"] = macros["PROCNT"] / 100 * food_entry.data["food_quantity"]
				macros["CHOCDF"] = macros["CHOCDF"] / 100 * food_entry.data["food_quantity"]
				macros["FAT"] = macros["FAT"] / 100 * food_entry.data["food_quantity"]
				macros["ENERC_KCAL"] = macros["ENERC_KCAL"] / 100 * food_entry.data["food_quantity"]

				if id == -1:
					macros_record = Macros()
				else:
					macros_record = Macros.query.get(id)

				macros_record.food_name = food_entry.data["food_name"]
				macros_record.food_quantity = food_entry.data["food_quantity"]
				macros_record.proteins = macros["PROCNT"]
				macros_record.carbs = macros["CHOCDF"]
				macros_record.fats = macros["FAT"]
				macros_record.calories = macros["ENERC_KCAL"]
				db.session.add(macros_record)
				db.session.commit()

			total_entries_count = len(macros_table.macro_rows.entries)
			total_records_count = len(macros_records)
			new_entries_count = total_entries_count - total_records_count

			if new_entries_count > 0:
				# if there are more entries than records
				# make 2 lists:
				# update_entries: list of entries that exist in db, but need to be checked if food_name and food_quantity changed
				# new_entries: list of entries that are new and need to be api_call'd

				update_entries = macros_table.macro_rows.entries[0:total_records_count]
				new_entries = macros_table.macro_rows.entries[new_entries_count:]
			else:
				# if there are fewer entries than records
				# it means now new entries got made
				update_entries = macros_table.macro_rows.entries
				new_entries = 0

				if new_entries_count < 0:
					# test if entries got deleted
					# if so delete the last entries
					for entry_del in macros_records[new_entries_count:]:
						db.session.delete(entry_del)
					db.session.commit()

			id = 0
			dict_upd_food_names = {}
			for entry_upd, record_upd in zip(update_entries, macros_records):
				id += 1
				if entry_upd.data["food_name"] != record_upd.food_name:
					dict_upd_food_names[id] = entry_upd

				elif entry_upd.data["food_quantity"] != record_upd.food_quantity:
					# divide macros by food_record.food_quantity
					# multiply food_entry.food_quantity.data
					record_upd.proteins = round(record_upd.proteins / record_upd.food_quantity * entry_upd.food_quantity.data, 2)
					record_upd.carbs = round(record_upd.carbs / record_upd.food_quantity * entry_upd.food_quantity.data, 2)
					record_upd.fats = round(record_upd.fats / record_upd.food_quantity * entry_upd.food_quantity.data, 2)
					record_upd.calories = round(record_upd.calories / record_upd.food_quantity * entry_upd.food_quantity.data, 2)
					record_upd.food_quantity = entry_upd.data["food_quantity"]


			# update entries with id
			for id, entry_upd in dict_upd_food_names.items():
				save_to_db(entry_upd, id)

			if new_entries != 0:
				for new_entry in new_entries:
					save_to_db(new_entry)

	for record in range(len(macros_records) - 1):
		macros_table.macro_rows.append_entry()
	return flask.render_template("macros.html", macros_table=macros_table, macros_records=macros_records)


if __name__ == "__main__":
	app.run(debug=True)
