from flask import flash, render_template, request, redirect, url_for, session, Blueprint
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb.cursors
import bcrypt
import os
import math
from datetime import date, datetime, timedelta
from decimal import Decimal


#The index page of the web app

#Now, any customer and guest will be able to see the menu.

bp = Blueprint('index', __name__, )
@bp.route("/", methods=['GET'])
def indexPage():
    if 'loggedin' in session:
        if session['role'] == 'HQ_Admin':
            return redirect(url_for('adminDashboard1.adminDashboard1'))
        elif session['role'] == 'branch_Admin':
            return redirect(url_for('adminDashboard2.adminDashboard2'))
        elif session['role'] == 'branch_Staff':
            return redirect(url_for('staffDashboard.staffDashboard'))
        elif session['role'] == 'Customer':
            return redirect(url_for('customerDashboard.customerDashboard'))
    else:
        return render_template('index.html')