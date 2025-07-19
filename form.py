from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, BooleanField, PasswordField, FileField, TextAreaField, validators
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100,
                                                                       message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=80,
                                                   message="Имя должно быть от 4 до 80 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100,
                                                                       message="Пароль должен быть от 4 до 100 символов")])
    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")


class AdsForm(FlaskForm):
    title = StringField("Заголовок: ", validators=[Length(min=4, max=80,
                                                          message="Заголовок должен быть от 4 до 80 символов")])
    content = TextAreaField("Объявление: ", validators=[DataRequired(), Length(min=4, max=1000,
                                                                               message="Объявление должно быть от 4 до 100 символов")])
    image = FileField("Добавить фото: ", validators=[FileAllowed(["jpg", "jpeg", "png"])])
    submit = SubmitField("Опубликовать")


class AdminForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=80, )])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100,
                                                                       message="Пароль должен быть от 4 до 100 символов")])
    submit = SubmitField("Войти")
