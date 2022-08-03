from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, IntegerField, SubmitField, StringField, FieldList, FormField, Label
from wtforms.validators import InputRequired, NumberRange


class HealthForm(FlaskForm):
	sex = SelectField("What's your sex?", choices=[("Male", "Male"), ("Female", "Female")])
	weight = DecimalField("Weight (in kg)", places=2, validators=[InputRequired()])
	height = DecimalField("Height (in cm)", places=2, validators=[InputRequired()])
	age = IntegerField("Age", validators=[InputRequired(), NumberRange(min=12, max=99)])
	submit = SubmitField("Submit")




class MacrosRow(FlaskForm):
	food_name = StringField()
	food_quantity = DecimalField()
	macros = (0, 0, 0, 0)


class MacrosTable(FlaskForm):
	macro_rows = FieldList(FormField(MacrosRow), min_entries=1)
	btn_update = SubmitField("Update")
	btn_add_row = SubmitField("Add new row")
	btn_remove_last_row = SubmitField("Remove last row")