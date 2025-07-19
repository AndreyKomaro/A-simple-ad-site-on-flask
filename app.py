from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from dbase import User, Ads, db
from form import LoginForm, RegisterForm, AdsForm, AdminForm

# MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e07d545ec92181206e19e1551f35604896a1b906'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///my.db'

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route('/')
def index():
    ads = db.session.execute(db.select(Ads).order_by(db.desc(Ads.date_created))).scalars()
    return render_template('index.html', title='Сайт на Flask', ads=ads)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).filter_by(email=form.email.data)).scalar()
        if user and check_password_hash(user.password, form.psw.data):
            rm = form.remember.data
            login_user(user, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", title="Авторизация", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    ads = db.session.execute(
        db.select(Ads).filter_by(user_id=current_user.id).order_by(db.desc(Ads.date_created))).scalars()
    if request.method == "POST":
        ad = db.get_or_404(Ads, request.form['ad_id'])
        db.session.delete(ad)
        db.session.commit()
        flash("Объявление удалено", "success")
        return redirect(url_for('profile'))
    return render_template('profile.html', title='Профиль', ads=ads)


@app.route('/kart')
def kart():
    im_id = request.args.get('im_id')
    ad_img = db.session.execute(db.select(Ads.image).filter_by(id=im_id)).scalar()
    return ad_img


@app.route('/addadv', methods=['GET', 'POST'])
@login_required
def addadv():
    form = AdsForm()
    if form.validate_on_submit():
        try:
            if form.image.data:
                ads_img = form.image.data.read()
            else:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), "rb") as f:
                    ads_img = f.read()
            ads = Ads(title=form.title.data, content=form.content.data,
                      image=ads_img, user_id=current_user.id)
            db.session.add(ads)
            db.session.commit()
            flash("Объявление опубликовано", "success")
            return redirect(url_for('profile'))
        except:
            db.session.rollback()
            flash("Ошибка при добавлении в БД", "error")
    return render_template('addadv.html', title='Добавить объявление', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.email.data in db.session.execute(db.select(User.email)).scalars():
        flash('Пользователь с таким email уже существует', "error")
    else:
        if form.validate_on_submit():
            try:
                hash = generate_password_hash(request.form['psw'])
                u = User(username=form.name.data, email=form.email.data, password=hash)
                db.session.add(u)
                db.session.commit()
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash("Ошибка при добавлении в БД", "error")

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = AdminForm()
    if form.validate_on_submit():
        if form.name.data == 'admin' == form.psw.data:
            login_admin()
            return redirect(url_for("administration"))
        flash("Неверная пара логин/пароль", "error")
    return render_template("admin.html", title="Админ", form=form)


@app.route('/administration', methods=['GET', 'POST'])
def administration():
    if not is_logged():
        return redirect(url_for('admin'))
    users = db.session.execute(db.select(User).order_by(User.email)).scalars()
    if request.method == "POST":
        try:
            user_id = request.form.get('user_id')
            ad_id = request.form.get('ad_id')
            if user_id:
                ads = db.session.execute(db.select(Ads).filter_by(user_id=user_id)).scalars()
                for ad in ads:
                    db.session.delete(ad)
                user = db.get_or_404(User, user_id)
                db.session.delete(user)
                db.session.commit()
                flash("Пользователь удалён", "success")
                return redirect(url_for('administration'))
            if ad_id:
                ad = db.get_or_404(Ads, ad_id)
                db.session.delete(ad)
                db.session.commit()
                flash("Объявление удалено", "success")
                return redirect(url_for('administration'))
        except:
            db.session.rollback()
            flash("Ошибка при удалении из БД", "error")

    def aduser(user_id):
        user_ads = db.session.execute(db.select(Ads).filter_by(user_id=user_id)).scalars()
        return user_ads
    return render_template('administration.html', title='Админ-панель', users=users, aduser=aduser)

@app.route('/aduser')
def aduser():
    user_id = request.args.get('user_id')
    user_ads = db.session.execute(db.select(Ads).filter_by(user_id=user_id)).scalars()
    return user_ads


@app.route('/logout_admin', methods=["POST", "GET"])
def logout_admin():
    if not is_logged():
        return redirect(url_for('.login'))
    session.pop('admin_logged', None)
    return redirect(url_for('admin'))

def login_admin():
    session['admin_logged'] = 1


def is_logged():
    return True if session.get('admin_logged') else False




if __name__ == '__main__':
    app.run(debug=True)
