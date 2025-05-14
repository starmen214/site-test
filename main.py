from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from wtforms import StringField, TextAreaField, IntegerField, FormField

from data.users import User
from data.test import Tests
from data import db_session
from forms.user import LoginForm, RegisterForm
from forms.news import TestForm, TestAnswers, Answers

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title="Регистрация",
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template("register.html", title="Регистрация",
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("login.html",
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template("login.html", title="Авторизация", form=form)


@app.route("/tests/my")
@login_required
def my_tests():
    db_sess = db_session.create_session()
    my_tests = db_sess.query(Tests).filter(Tests.author_id == current_user.id).all()
    return render_template("my_tests.html", tests=my_tests, title="Мои тесты")

@app.route("/")
def index():
    db_sess = db_session.create_session()
    all_tests = db_sess.query(Tests).all()
    return render_template("index.html", tests=all_tests)


@app.route("/tests/create", methods=["GET", "POST"])
@login_required
def create_test():
    form = TestForm()
    count_conditions = []
    num = len(count_conditions) + 1
    if form.validate_on_submit():
        if form.data['submit']:
            st = ''
            for i in range(len(form.questions.data)):
                st += form.questions.data[i]['content'] + ';'
                for j in range(len(form.questions.data[i]['answer'])):
                    st += '%' + form.questions.data[i]['answer'][j] + ';'
                    st += '$' + str(form.questions.data[i]['scores'][j]) + ';'
            sp2 = []
            for i in range(len(form.res_point.data)):
                sp2.append('{}-{};&{}'.format(form.res_point.data[i], form.res_point_max.data[i], form.result.data[i]))
            st2 = ';'.join(sp2)

            db_sess = db_session.create_session()
            test = Tests()
            test.title = form.name.data
            test.questions = st
            test.author_id = current_user.get_id()
            test.result = st2
            db_sess.add(test)
            db_sess.commit()
            all_results = db_sess.query(Tests).filter(Tests.title == form.name.data,
                                                      Tests.content == form.description.data,
                                                      Tests.questions == st,
                                                      Tests.author_id == current_user.get_id(),
                                                      Tests.result == st2).first()
            db_sess.commit()

            return redirect('/')

    if form.data['submit_con']:
        form.questions.append_entry(FormField(Answers))
    elif form.data['del_con']:
        if len(form.questions) > 1:
            form.questions.pop_entry()
    elif form.data['add_res']:
        form.res_point.append_entry(IntegerField("Больше стольки очков"))
        form.res_point_max.append_entry(IntegerField("Больше стольки очков"))
        form.result.append_entry(TextAreaField("Результат"))
        form.result.entries[-1].data = None
    elif form.data['del_res']:
        if len(form.res_point) > 1:
            form.res_point.pop_entry()
            form.res_point_max.pop_entry()
            form.result.pop_entry()
    else:
        for i in range(len(form.questions.entries)):
            if form.questions.entries[i].data['add_answer']:
                form.questions.entries[i].form.answer.append_entry(StringField('ответ'))
                form.questions.entries[i].form.answer.entries[-1].data = None

                form.questions.entries[i].form.scores.append_entry(IntegerField("Количество баллов"))
                form.questions.entries[i].form.scores.entries[-1].data = None
            elif form.questions.entries[i].data['del_answer']:
                form.questions.entries[i].form.answer.pop_entry()
                form.questions.entries[i].form.scores.pop_entry()

    return render_template("test_create.html", num=num, form=form, title="Создание теста")


if __name__ == "__main__":
    main()
