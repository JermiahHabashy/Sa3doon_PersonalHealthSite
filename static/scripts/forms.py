from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, IntegerField, SubmitField, StringField, FieldList, FormField, Label
from wtforms.validators import InputRequired, NumberRange


class HealthForm(FlaskForm):
	sex = SelectField("What's your sex?", choices=[("Male", "Male"), ("Female", "Female")])
	weight = FloatField("Weight (in kg)", validators=[InputRequired()])
	height = FloatField("Height (in cm)", validators=[InputRequired()])
	age = IntegerField("Age", validators=[InputRequired(), NumberRange(min=12, max=99)])
	submit = SubmitField("Submit")




class MacrosRow(FlaskForm):
	food_name = StringField(default="")
	food_quantity = FloatField()


class MacrosTable(FlaskForm):
	macro_rows = FieldList(FormField(MacrosRow), min_entries=1)
	btn_update = SubmitField("Update")
	btn_add_row = SubmitField("Add new row")
	btn_remove_last_row = SubmitField("Remove last row")