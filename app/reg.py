from flask import flash, render_template, request, redirect, url_for, session, Blueprint
from flask_mysqldb import MySQL
from datetime import datetime,date, timedelta
import MySQLdb.cursors
import bcrypt
from app import mysql
import re

bp = Blueprint('reg', __name__)

@bp.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('userPassword')
        title = request.form.get('title')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        phoneNumber = request.form.get('phoneNumber')
        email = request.form.get('userEmail')
        address = request.form.get('userAddress')
        dateOfBirth = request.form.get('dateedit')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE userName = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
            return render_template('register.html', msg=msg)

        # Encrypt the password before saving it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new user with role "Customer"
        cursor.execute('INSERT INTO users (userRole, userName, userPassword, userActive) VALUES (%s, %s, %s, %s)', ('Customer', username, hashed_password, True))
        mysql.connection.commit()
        
        # Get user_ID, then insert into table customer
        user_ID = cursor.lastrowid
        cursor.execute('INSERT INTO customers (userID, title, firstName, lastName, email, phoneNumber, Address, dateOfBirth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (user_ID, title, firstName, lastName, email, phoneNumber, address, dateOfBirth))
        mysql.connection.commit()
        cursor.close()
        
        # Successful registration
        flash('Registration succeeded!', 'success')
        return redirect(url_for('login.login'))

    return render_template('register.html')