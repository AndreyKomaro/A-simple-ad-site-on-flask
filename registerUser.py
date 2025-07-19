from email_validator import validate_email, EmailNotValidError


def is_valid_email(email):
    try:
        valid = validate_email(email)
        return True
    except EmailNotValidError:
        return False
def register_user(email, password):
    if request.method == "POST":
        if (len(request.form['name']) > 4 and len(request.form['email']) > 4
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']):
            if request.form['email'] in list(db.session.execute(db.select(User.email)).scalars()):
                flash('Пользователь с таким email уже существует', "error")

            try:
                hash = generate_password_hash(request.form['psw'])
                u = User(username=request.form['name'], email=request.form['email'], password=hash)
                db.session.add(u)
                print('add')
                db.session.commit()
                print('commit')
                flash("Вы успешно зарегистрированы", "success")
            except:
                db.session.rollback()
                flash("Ошибка при добавлении в БД", "error")
            return redirect(url_for('login'))
        else:
            flash("Неверно заполнены поля", "error")
