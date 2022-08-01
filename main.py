import os
import flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange
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


class MacrosTableForm(FlaskForm):
	table = TableWidget("test")
	food_name = TextInput("test")



@app.route('/macros', methods=["GET"])
def macros():
	macros_table: MacrosTableForm = MacrosTableForm()
	return flask.render_template("macros.html", macros_table=macros_table)


if __name__ == "__main__":
	app.run(debug=True)