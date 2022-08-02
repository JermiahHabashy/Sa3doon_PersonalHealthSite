import os
import flask
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

# config table
class Macros(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	food_name = db.Column(db.String(250), nullable=False)
	food_quantity = db.Column(db.DECIMAL(5, 2), nullable=False)
	proteins = db.Column(db.Integer)
	carbs = db.Column(db.Integer)
	fats = db.Column(db.Integer)
	calories = db.Column(db.Integer)


db.create_all()

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
			food: MacrosRow
			for food in macros_table.macro_rows.entries:
				print(food.food_name.data)
				print(food.food_quantity.data)

	return flask.render_template("macros.html", macros_table=macros_table)



if __name__ == "__main__":
	app.run(debug=True)
