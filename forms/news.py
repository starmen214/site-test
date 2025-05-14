from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, FieldList, FormField, RadioField
from wtforms.validators import DataRequired


class Answers(FlaskForm):
    content = TextAreaField("Вопрос")
    answer = FieldList(StringField("ответ"), min_entries=1)
    scores = FieldList(IntegerField("Количество баллов"), min_entries=1)
    add_answer = SubmitField("Создать ответ")
    del_answer = SubmitField("Удалить ответ")


class TestForm(FlaskForm):
    name = StringField("Название теста", validators=[DataRequired()])
    description = TextAreaField("Описание")
    questions = FieldList(FormField(Answers), "Вопросы", min_entries=1)
    submit_con = SubmitField("Создать вопрос")
    del_con = SubmitField("Удалить вопрос")
    res_point = FieldList(IntegerField("От стольки очков"), min_entries=1)
    res_point_max = FieldList(IntegerField("До стольки очков"), min_entries=1)
    result = FieldList(TextAreaField("Результат"), min_entries=1)
    add_res = SubmitField("Создать результат")
    del_res = SubmitField("Удалить результат")
    submit = SubmitField("Сохранить тест")
    run_test = SubmitField("Пройти тест")
    add_picture = SubmitField("Добавить изображение")
    but_answer = SubmitField("Выбрать")


class AccountSubmit(FlaskForm):
    ac_id = IntegerField("Введите id аккаунта")
    ac_name = TextAreaField("Введите имя аккаунта")
    submit = SubmitField("Найти аккаунт")


class TestId(FlaskForm):
    ar_id = IntegerField("Введите id теста")
    submit = SubmitField("Найти тест")


class TestNameSubmit(FlaskForm):
    ar_name = TextAreaField("Введите название теста")
    submit = SubmitField("Найти тест")


class TestAnswers(FlaskForm):
    answers = RadioField("Ответы", choices=[])
    submit = SubmitField("Отправить ответ")
