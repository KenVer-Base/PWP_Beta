from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql
# 1. IMPORT LIBRARY HASHING
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cur.fetchone()
        cur.close()
        
        # 0:id, 1:username, 2:full_name, 3:email, 4:password_hash
        if user:
            # 2. CEK PASSWORD DENGAN HASH
            # user[4] adalah password terenkripsi dari database
            # password_input adalah password yang diketik user
            if check_password_hash(user[4], password_input):
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('main.index'))
            else:
                flash('Password salah!', 'danger')
        else:
            flash('Email tidak ditemukan!', 'danger')
            
    return render_template('auth/auth.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cur.fetchone()
        
        if existing_user:
            flash('Username atau Email sudah dipakai!', 'danger')
        else:
            # 3. ENKRIPSI PASSWORD SEBELUM DISIMPAN
            hashed_password = generate_password_hash(password)

            cur.execute("INSERT INTO users (username, full_name, email, password) VALUES (%s, %s, %s, %s)", 
                        (username, full_name, email, hashed_password))
            mysql.connection.commit()
            flash('Akun berhasil dibuat! Silakan login.', 'success')
            return redirect(url_for('auth.login'))
            
        cur.close()
        
    return render_template('auth/auth.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))