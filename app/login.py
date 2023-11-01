from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
from app import mysql

bp = Blueprint('login', __name__, )

def is_authenticated():
    return 'loggedin' in session

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # logged in user cannot enter the page
    if 'loggedin' in session:
        return redirect("/")
    # Check if "username" and "password" POST requests exist (user submitted form)
    elif request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        user_password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE userName = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            password = account['userPassword']
            if bcrypt.checkpw(user_password.encode('utf-8'), password.encode('utf-8')):
                # If account exists in users table in our database
                # Create session data
                session['loggedin'] = True
                session['role'] = account['userRole']
                session['id'] = account['userID']

                # Redirect to respective dashboard based on role
                if session['role'] == 'HQ_Admin':
                    return redirect(url_for('adminDashboard1.adminDashboard1'))
                elif session['role'] == 'branch_Admin':
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT branchID FROM branches WHERE branchAdminID = %s',(session['id'],))
                    branchID = cursor.fetchone()
                    session['branchID'] = branchID['branchID']
                    return redirect(url_for('adminDashboard2.adminDashboard2'))
                elif session['role'] == 'branch_Staff':
                    return redirect(url_for('staffDashboard.staffDashboard'))
                else:
                    return redirect(url_for('customerDashboard.customerDashboard'))
            else:
                # Password incorrect
                msg = 'Incorrect password!'
                return render_template('login.html', msg=msg, loginUsername=username)
        else:
            # Account doesn't exist or username incorrect
            msg = 'Incorrect username'
            return render_template('login.html', msg=msg, loginUsername=username)
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)


@bp.route('/chooseBranch', methods=['GET', 'POST'])
def chooseBranch():
    branchChoosed = request.form.get('branchChoosed')

    if branchChoosed:
        session['branch'] = branchChoosed
        session.pop('cart',None)
        return redirect(url_for('customerDashboard.menu'))
    
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM branches;',)
        branchList = cursor.fetchall()
        return render_template('chooseBranch.html',branchList = branchList)




# def is_authenticated():
#     return 'loggedin' in session

# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     msg = ''
#     if 'loggedin' in session:
#         return redirect("/")
#     elif request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         username = request.form['username']
#         user_password = request.form['password']
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM users WHERE userName = %s', (username,))
#         account = cursor.fetchone()
#         if account:
#             password = account['userPassword']
#             if bcrypt.checkpw(user_password.encode('utf-8'), password.encode('utf-8')):
#                 session['loggedin'] = True
#                 session['role'] = account['userRole']
#                 session['id'] = account['userID']
#                 if session['role'] == 'HQ_Admin':
#                     return redirect(url_for('adminDashboard1.adminDashboard1'))
#                 elif session['role'] == 'branch_Admin':
#                     return redirect(url_for('adminDashboard2.adminDashboard2'))
#                 elif session['role'] == 'branch_Staff':
#                     return redirect(url_for('staffDashboard.staffDashboard'))
#                 else:
#                     return redirect(url_for('customerDashboard.customerDashboard'))
#             else:
#                 msg = 'Incorrect password!'
#                 return render_template('login.html', msg=msg, loginUsername=username)
#         else:
#             msg = 'Incorrect username'
#             return render_template('login.html', msg=msg, loginUsername=username)
#     return render_template('login.html', msg=msg)
