from wtforms.validators import Required
from flask_wtf import Form
from wtforms import SubmitField, StringField


class InputForm(Form):
    tag_names = StringField('标签名(如marathon，用逗号分隔)',
                            validators=[Required()], default='marathon')
    submit = SubmitField("提交")


class GetClusterResourceForm(Form):
    url = StringField('Mesos-master链接', validators=[Required()])
    submit = SubmitField("提交")
