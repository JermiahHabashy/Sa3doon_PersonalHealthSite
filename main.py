import os
import flask
from flask import url_for, redirect
import requests
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask import request
from static.scripts.forms import HealthForm, MacrosTable

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

Bootstrap(app)
# connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/database/database.db'
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
	food_quantity = db.Column(db.Integer, nullable=False)
	proteins = db.Column(db.Integer, default=0)
	carbs = db.Column(db.Integer, default=0)
	fats = db.Column(db.Integer, default=0)
	calories = db.Column(db.Integer, default=0)


class Diet(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	proteins = db.Column(db.Integer)
	carbs = db.Column(db.Integer)
	fats = db.Column(db.Integer)
	calories = db.Column(db.Integer)


db.create_all()
db.session.commit()


@app.route('/', methods=["GET", "POST"])
def home():
	health_form: HealthForm = HealthForm()
	bmr = 0
	diet: Diet = Diet()
	if request.method == "POST":
		if health_form.submit_info.data:
			# base_bmr = 10 x weight(kg) + 6.25 x height(cm) - 5 x age(y) + 5 (man) = BMR10 x weight(kg) + 6.25 x height(
			# cm) - 5 x age(y)
			# for men: +5
			# for women: -161
			bmr = int(10 * int(health_form.weight.data) + 6.25 * int(health_form.height.data) - 5 * health_form.age.data)
			if health_form.sex.data == "Male":
				bmr += 5
			else:
				bmr -= 161
			health_form.diet_select.choices = [(bmr, f"BMR: {bmr}"), (bmr+300, f"Bulk: {bmr+300}"), (bmr-300, f"Cut: {bmr-300}")]

		elif health_form.submit_diet.data:
			chosen_diet = int(health_form.diet_select.data)
			diet.proteins = round(chosen_diet * 0.4 / 4, 2)
			diet.carbs = round(chosen_diet * 0.2 / 4, 2)
			diet.fats = round(chosen_diet * 0.3 / 9, 2)
			diet.calories = round(chosen_diet, 2)

			dup_diet = Diet()
			dup_diet.proteins = round(chosen_diet * 0.4 / 4, 2)
			dup_diet.carbs = round(chosen_diet * 0.2 / 4, 2)
			dup_diet.fats = round(chosen_diet * 0.3 / 9, 2)
			dup_diet.calories = round(chosen_diet, 2)

			db.session.add(diet)
			db.session.add(dup_diet)
			db.session.commit()
			diets = db.session.query(Diet).all()
			return redirect("/macros")

	return flask.render_template("index.html", health_form=health_form)


macros_records = db.session.query(Macros).all()
remaining_macros = []

@app.route('/macros', methods=["GET", "POST"])
def macros():
	macros_table: MacrosTable = MacrosTable()
	diets = db.session.query(Diet).all()


	if request.method == "GET":
		for record_nr in range(len(macros_records)):
			macros_table.macro_rows.append_entry()
			macros_table.macro_rows.entries[record_nr].form.food_name.data = macros_records[record_nr].food_name
			macros_table.macro_rows.entries[record_nr].form.food_quantity.data = macros_records[record_nr].food_quantity
			diets[0].proteins -= macros_records[record_nr].proteins
			diets[0].carbs -= macros_records[record_nr].carbs
			diets[0].fats -= macros_records[record_nr].fats
			diets[0].calories -= macros_records[record_nr].calories
			db.session.commit()

	elif request.method == 'POST':
		# add new table row
		if macros_table.btn_add_row.data:
			macros_table.btn_add_row.data = False

			# new entry to MacroRows
			macros_table.macro_rows.append_entry()

			new_macros_record = Macros()
			new_macros_record.id = len(macros_records) + 1
			new_macros_record.proteins = 0
			new_macros_record.carbs = 0
			new_macros_record.fats = 0
			new_macros_record.calories = 0
			macros_records.append(new_macros_record)

		# remove last row only if you more than 1 entry
		elif macros_table.btn_remove_last_row.data and len(macros_records) > 1:
			macros_table.btn_remove_last_row.data = False

			# delete last entry from MacroRows
			macros_table.macro_rows.pop_entry()

			# delete last record from db
			if len(db.session.query(Macros).all()) >= len(macros_records):
				record_del = Macros.query.get(len(macros_records))
				diets[0].proteins += record_del.proteins
				diets[0].carbs += record_del.carbs
				diets[0].fats += record_del.fats
				diets[0].calories += record_del.calories
				db.session.delete(record_del)
				db.session.commit()

			macros_records.pop()


		# post data to database
		elif macros_table.btn_update.data:
			macros_table.btn_update.data = False

			def api_call(record, id):
				response = requests.request("GET", url, headers=headers, params={"ingr": record.food_name})
				response.raise_for_status()
				macros = response.json()["parsed"][0]["food"]["nutrients"]

				record.proteins = round(int(macros["PROCNT"] / 100 * record.food_quantity), 2)
				record.carbs = round(int(macros["CHOCDF"] / 100 * record.food_quantity), 2)
				record.fats = round(int(macros["FAT"] / 100 * record.food_quantity), 2)
				record.calories = round(int(macros["ENERC_KCAL"] / 100 * record.food_quantity), 2)

				if id < 0:
					db.session.add(record)

				subtract_diet(record)

			def subtract_diet(record):
				diets[0].proteins -= record.proteins
				diets[0].carbs -= record.carbs
				diets[0].fats -= record.fats
				diets[0].calories -= record.calories

			id = 0
			for record in macros_records:
				macro_row_food_name = macros_table.macro_rows.entries[id].data["food_name"]
				macro_row_food_quantity = int(macros_table.macro_rows.entries[id].data["food_quantity"])
				id += 1
				if record.food_name is None:
					record.food_name = macro_row_food_name
					record.food_quantity = macro_row_food_quantity
					api_call(record, id * -1)
				else:
					if macro_row_food_name != record.food_name:
						api_call(record, id)
					elif macro_row_food_quantity != record.food_quantity:
						record.proteins = round(int(record.proteins / record.food_quantity * macro_row_food_quantity), 2)
						record.carbs = round(int(record.carbs / record.food_quantity * macro_row_food_quantity), 2)
						record.fats = round(int(record.fats / record.food_quantity * macro_row_food_quantity), 2)
						record.calories = round(int(record.calories / record.food_quantity * macro_row_food_quantity), 2)
						record.food_quantity = macro_row_food_quantity
						subtract_diet(record)
				db.session.commit()

	return flask.render_template("macros.html", macros_table=macros_table, macros_records=macros_records, diets=diets)


if __name__ == "__main__":
	app.run(debug=True)
