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
	proteins = db.Column(db.Integer, default=0)
	carbs = db.Column(db.Integer, default=0)
	fats = db.Column(db.Integer, default=0)
	calories = db.Column(db.Integer, default=0)


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


macros_records = db.session.query(Macros).all()


@app.route('/macros', methods=["GET", "POST"])
def macros():
	macros_table: MacrosTable = MacrosTable()

	if request.method == "GET":

		for record_nr in range(len(macros_records)):
			macros_table.macro_rows.append_entry()
			macros_table.macro_rows.entries[record_nr].form.food_name.data = macros_records[record_nr].food_name
			macros_table.macro_rows.entries[record_nr].form.food_quantity.data = macros_records[record_nr].food_quantity
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
				db.session.delete(Macros.query.get(len(macros_records)))
				db.session.commit()

			macros_records.pop()


		# post data to database
		elif macros_table.btn_update.data:
			macros_table.btn_update.data = False

			def api_call(record, id):
				response = requests.request("GET", url, headers=headers, params={"ingr": record.food_name})
				response.raise_for_status()
				macros = response.json()["parsed"][0]["food"]["nutrients"]

				record.proteins = macros["PROCNT"] / 100 * record.food_quantity
				record.carbs = macros["CHOCDF"] / 100 * record.food_quantity
				record.fats = macros["FAT"] / 100 * record.food_quantity
				record.calories = macros["ENERC_KCAL"] / 100 * record.food_quantity

				if id < 0:
					db.session.add(record)

			id = 0
			for record in macros_records:
				macro_row_food_name = macros_table.macro_rows.entries[id].data["food_name"]
				macro_row_food_quantity = macros_table.macro_rows.entries[id].data["food_quantity"]
				id += 1
				if record.food_name is None:
					record.food_name = macro_row_food_name
					record.food_quantity = macro_row_food_quantity
					api_call(record, id * -1)
				else:
					if macro_row_food_name != record.food_name:
						api_call(record, id)
					elif macro_row_food_quantity != record.food_quantity:
						record.proteins = round(record.proteins / record.food_quantity * macro_row_food_quantity, 2)
						record.carbs = round(record.carbs / record.food_quantity * macro_row_food_quantity, 2)
						record.fats = round(record.fats / record.food_quantity * macro_row_food_quantity, 2)
						record.calories = round(record.calories / record.food_quantity * macro_row_food_quantity, 2)
						record.food_quantity = macro_row_food_quantity
				db.session.commit()

	return flask.render_template("macros.html", macros_table=macros_table, macros_records=macros_records)


if __name__ == "__main__":
	app.run(debug=True)
