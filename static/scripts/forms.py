from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, IntegerField, SubmitField, StringField, FieldList, FormField, RadioField
from wtforms.validators import InputRequired, NumberRange


# home forms
class HealthForm(FlaskForm):
	sex = SelectField("What's your sex?", choices=[("Male", "Male"), ("Female", "Female")])
	weight = FloatField("Weight (in kg)", validators=[InputRequired()])
	height = FloatField("Height (in cm)", validators=[InputRequired()])
	age = IntegerField("Age", validators=[InputRequired(), NumberRange(min=12, max=99)])
	submit_info = SubmitField("Submit info")
	diet_select = RadioField("Choose your diet", choices=[])
	submit_diet = SubmitField("Submit diet")




# macros forms
class MacrosRow(FlaskForm):
	food_name = StringField(default="")
	food_quantity = FloatField()


class MacrosTable(FlaskForm):
	macro_rows = FieldList(FormField(MacrosRow), min_entries=1)
	btn_update = SubmitField("Update")
	btn_add_row = SubmitField("Add new row")
	btn_remove_last_row = SubmitField("Remove last row")