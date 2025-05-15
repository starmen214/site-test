import flask_wtf
import wtforms


class RegisterForm(flask_wtf.FlaskForm):
    email = wtforms.EmailField('Почта', validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField('Пароль', validators=[wtforms.validators.DataRequired()])
    password_again = wtforms.PasswordField('Повторите пароль', validators=[wtforms.validators.DataRequired()])
    name = wtforms.StringField('Имя пользователя', validators=[wtforms.validators.DataRequired()])
    detail = wtforms.TextAreaField('Детальнее о вас')
    submit = wtforms.SubmitField('Войти')


class LoginForm(flask_wtf.FlaskForm):
    email = wtforms.EmailField('Почта', validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField('Пароль', validators=[wtforms.validators.DataRequired()])
    remember_me = wtforms.BooleanField('Запомнить меня')
    submit = wtforms.SubmitField('Войти')
