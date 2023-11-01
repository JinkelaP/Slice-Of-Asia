from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, flash
from flask_mysqldb import MySQL
import bcrypt
from app import mysql


bp = Blueprint('logout', __name__, )

@bp.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('role',None)
   session.pop('branch',None)
   session.pop('cart',None)

   flash('Log out successful!', 'success'), 
   # Redirect to login page
   return redirect('/')