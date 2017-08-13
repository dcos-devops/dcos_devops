from flask_wtf import Form
from wtforms import SelectField, SubmitField


class ChooseForm(Form):
    warning_level = SelectField(
        '告警级别',
        choices=[('确认', '确认'), ('警报', '警报'), ('紧急', '紧急')]
    )
    submit = SubmitField("提交")
