import os
import flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, IntegerField, SubmitField, StringField
from wtforms.validators import InputRequired, NumberRange
from flask import request
from wtforms.widgets import TableWidget, TextInput

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

Bootstrap(app)


class HealthForm(FlaskForm):
	sex = SelectField("What's your sex?", choices=[("Male", "Male"), ("Female", "Female")])
	weight = DecimalField("Weight (in kg)", places=2, validators=[InputRequired()])
	height = DecimalField("Height (in cm)", places=2, validators=[InputRequired()])
	age = IntegerField("Age", validators=[InputRequired(), NumberRange(min=12, max=99)])
	submit = SubmitField("Submit")


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


class AllFoodsForm(FlaskForm):
	update = SubmitField("Update")
	add_row = SubmitField("Add new row")

class MacrosTableForm(FlaskForm):
	food_quantity = IntegerField(validators=[InputRequired()])
	food_name = StringField(validators=[InputRequired()])

@app.route('/macros', methods=["GET", "POST"])
def macros(list_of_foods=None):
	if list_of_foods is None:
		list_of_foods = []
	all_foods: AllFoodsForm = AllFoodsForm()

	if request.method == 'POST':
		if all_foods.add_row.data:
			list_of_foods.append(MacrosTableForm())
			print(len(list_of_foods))
			all_foods.add_row.data = False

	return flask.render_template("macros.html", all_foods=all_foods, list_of_foods=list_of_foods)


if __name__ == "__main__":
	app.run(debug=True)