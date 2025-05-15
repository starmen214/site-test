from flask import Flask, render_template, redirect, request
from flask_admin import Admin
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from wtforms import StringField, TextAreaField, IntegerField, FormField

from admin.tests import TestAdminView
from admin.users import UserAdminView
from data.users import User
from data.tests import Tests
from data import db_session
from forms.users import LoginForm, RegisterForm
from forms.tests import TestForm, TestAnswers, Answers, TestNameSubmit, TestId

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
admin = Admin(app, name='testing', template_mode='bootstrap3')
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/tests.db")
    db_sess = db_session.create_session()
    admin.add_view(UserAdminView(User, db_sess))
    admin.add_view(TestAdminView(Tests, db_sess))
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
        if user and user.check_password(password=form.password.data):
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
        if form.data["submit"]:
            st = ''
            for i in range(len(form.questions.data)):
                st += form.questions.data[i]["content"] + ";"
                for j in range(len(form.questions.data[i]["answer"])):
                    st += "%" + form.questions.data[i]["answer"][j] + ";"
                    st += "$" + str(form.questions.data[i]["scores"][j]) + ";"
            sp2 = []
            for i in range(len(form.res_point.data)):
                sp2.append("{}-{};&{}".format(
                    form.res_point.data[i], form.res_point_max.data[i], form.result.data[i]))
            st2 = ";".join(sp2)

            db_sess = db_session.create_session()
            test = Tests()
            test.title = form.name.data
            test.content = form.description.data
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
            return redirect("/")

    if form.data["submit_con"]:
        form.questions.append_entry(FormField(Answers))
    elif form.data["del_con"]:
        if len(form.questions) > 1:
            form.questions.pop_entry()
    elif form.data["add_res"]:
        form.res_point.append_entry(IntegerField("Больше стольки очков"))
        form.res_point_max.append_entry(IntegerField("Больше стольки очков"))
        form.result.append_entry(TextAreaField("Результат"))
        form.result.entries[-1].data = None
    elif form.data["del_res"]:
        if len(form.res_point) > 1:
            form.res_point.pop_entry()
            form.res_point_max.pop_entry()
            form.result.pop_entry()
    else:
        for i in range(len(form.questions.entries)):
            if form.questions.entries[i].data["add_answer"]:
                form.questions.entries[i].form.answer.append_entry(StringField("ответ"))
                form.questions.entries[i].form.answer.entries[-1].data = None

                form.questions.entries[i].form.scores.append_entry(IntegerField("Количество баллов"))
                form.questions.entries[i].form.scores.entries[-1].data = None
            elif form.questions.entries[i].data["del_answer"]:
                form.questions.entries[i].form.answer.pop_entry()
                form.questions.entries[i].form.scores.pop_entry()

    return render_template("test_create.html", num=num, form=form, title="Создание теста")


@app.errorhandler(404)
def page_not_found(exception):
    page_user_asking_for = request.base_url.split('/')[-1]
    return render_template("404.html", page=page_user_asking_for), 404


@app.errorhandler(401)
def unauthorized(exception):
    page_user_asking_for = request.base_url.split('/')[-1]
    return render_template("401.html", page=page_user_asking_for), 401


@app.route("/tests/<int:num>", methods=["GET", "POST"])
def run_news(num):
    score = 0
    num_of_question = 0
    if request.args.get("score"):
        score = int(request.args.get("score"))
    if request.args.get("question"):
        num_of_question = int(request.args.get("question"))
    form = TestAnswers()
    if form.data["submit"] and form.data["answers"]:
        score += int(form.data["answers"])
        num_of_question += 1
        return redirect("/tests/{}?score={}&question={}".format(num, str(score), str(num_of_question)))
    db_sess = db_session.create_session()
    all_values = db_sess.query(Tests).filter(Tests.id == num).first()
    title = all_values.title
    cycle = 0
    question = ''
    answers = []
    scores = []
    parsed_quest = all_values.questions.split(";")
    del parsed_quest[-1]
    num_q = len(list(filter(lambda x: x[0] != "$" and x[0] != "%", parsed_quest)))
    if num_q <= num_of_question:
        s = score
        TestAnswers.sp = []
        return redirect("/tests/{}/finish/{}".format(num, s))
    else:
        for i in range(len(parsed_quest)):
            if parsed_quest[i][0] == "%":
                if cycle - 1 == num_of_question:
                    answers.append(parsed_quest[i][1::])
            elif parsed_quest[i][0] == "$":
                if cycle - 1 == num_of_question:
                    scores.append(parsed_quest[i][1::])
            else:
                cycle += 1
                if cycle - 1 == num_of_question:
                    question = parsed_quest[i]
            if cycle > num_of_question + 1:
                break
        for i in range(len(answers)):
            form.answers.choices.append((int(scores[i]), answers[i]))
        return render_template(
            "run_test.html", title=title, num=num_of_question + 1, form=form, question=question)


@app.route("/tests/<int:num>/finish/<int:score>")
def finish_test(num, score):
    sum_ans = score
    db_sess = db_session.create_session()
    all_results = db_sess.query(Tests).filter(Tests.id == num).first()
    parsed_res = all_results.result.split(";")
    test_result = ''
    results = []
    scrs = []
    for i in range(len(parsed_res)):
        if parsed_res[i][0] == "&":
            results.append(parsed_res[i][1::])
        else:
            scrs.append(parsed_res[i].split("-"))
    for i in range(len(scrs)):
        if int(scrs[i][0]) <= sum_ans <= int(scrs[i][1]):
            test_result = results[i]

    return render_template("test_end.html", test_result=test_result)


@app.route("/tests/view/<int:num>", methods=["GET", "POST"])
def view_test(num):
    crashed = 0
    test_id = 0
    content = "К сожалению, описания нет :("
    author_id = 0
    creation_date = 0
    title = 0
    try:
        content = ''
        form = TestForm()
        db_sess = db_session.create_session()
        needed_test = db_sess.query(Tests).filter(Tests.id == num).first()
        title = needed_test.title
        test_id = needed_test.id
        author_id = needed_test.author_id
        creation_date = needed_test.created_date
        if needed_test.content:
            content = needed_test.content
        if form.data["run_test"]:
            return redirect("/tests/{}?score={}&question={}".format(test_id, "0", "0"))
    except Exception as e:
        crashed = 1
    return render_template("test.html", name=title, content=content, id_t=test_id, user_id=author_id,
                           date=creation_date,
                           crashed=crashed, form=form)


@app.route("/search_by_name", methods=["GET", "POST"])
def search_by_name():
    form = TestNameSubmit()
    form_valid = form.validate_on_submit()
    db_sess = db_session.create_session()
    if form_valid:
        try:
            needed_test = db_sess.query(Tests.id).filter(Tests.title == form.ar_name.data).first()
            for i in needed_test:
                name = i
            test_url = "/tests/view/" + str(name)
            return redirect(test_url)
        except Exception:
            return redirect("/")
    return render_template("search_by_name.html", form=form)


@app.route("/search_by_id", methods=["GET", "POST"])
def search_by_id():
    form = TestId()
    is_valid = form.validate_on_submit()
    if is_valid:
        needed_test = "/tests/view/" + str(form.ar_id.data)
        return redirect(needed_test)
    return render_template("search_by_id.html", form=form)


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/users/<int:num>")
def view_user(num):
    db_sess = db_session.create_session()
    needed_user = db_sess.query(User).filter(User.id == num).first()
    users_test = None
    found = False
    if needed_user:
        found = True
        users_test = db_sess.query(Tests).filter(Tests.author_id == needed_user.id).all()
    return render_template("user_detail.html", user=needed_user, tests=users_test, found=found)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    main()
