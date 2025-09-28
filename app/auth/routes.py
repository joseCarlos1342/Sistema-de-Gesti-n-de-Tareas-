from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.forms import RegistrationForm, LoginForm, ProfileForm, ChangePasswordForm
from app.services.auth_service import AuthService
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Validar fortaleza de contraseña
        is_valid, message = AuthService.validate_password_strength(form.password.data)
        if not is_valid:
            flash(message, 'error')
            return render_template('auth/register.html', form=form)

        # Crear usuario
        user, error = AuthService.create_user(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data
        )

        if user:
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(error, 'error')

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = AuthService.validate_user_credentials(form.email.data, form.password.data)

        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            session.permanent = True

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Email o contraseña incorrectos.', 'error')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(session['user_id'])
    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        success, message = AuthService.update_user_profile(
            user=user,
            name=form.name.data,
            email=form.email.data
        )

        if success:
            session['user_name'] = user.name  # Actualizar sesión
            flash(message, 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash(message, 'error')

    return render_template('auth/profile.html', form=form, user=user)

@auth_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(session['user_id'])
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Validar fortaleza de nueva contraseña
        is_valid, message = AuthService.validate_password_strength(form.new_password.data)
        if not is_valid:
            flash(message, 'error')
            return render_template('auth/change_password.html', form=form)

        success, message = AuthService.change_password(
            user=user,
            current_password=form.current_password.data,
            new_password=form.new_password.data
        )

        if success:
            flash(message, 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash(message, 'error')

    return render_template('auth/change_password.html', form=form)