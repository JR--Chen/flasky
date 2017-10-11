from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    account = StringField('教务网账号', validators=[DataRequired(), Length(10, 10)])
    passwd = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('绑定')
