from app import mysql
from flask import flash, render_template, request, redirect, url_for, session, Blueprint
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb.cursors
import bcrypt
import os
import math
from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import jsonify
from itertools import groupby
from operator import itemgetter
import simplejson

bp = Blueprint('adminDashboard2', __name__, )


def is_authenticated():
    return 'loggedin' in session

def userNameCrash(userName):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT * FROM users WHERE userActive = True and userName = %s', (userName,))
    exist_account = cursor.fetchone()
    if exist_account:
        return 1
    else:
        return 0

# encapsulate the passwordEncrypt function
def passwordEncrypt(userPassword):
    bytes = userPassword.encode('utf-8')
    salt = bcrypt.gensalt()
    hashedPsw = bcrypt.hashpw(bytes, salt)
    return hashedPsw

@bp.route('/adminDashboard2', methods=['GET'])
def adminDashboard2():
    if 'loggedin' in session and session['role'] == 'branch_Admin':

        branchAdminID = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch the branchID based on branchAdminID
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch_data = cursor.fetchone()
        branchID = branch_data['branchID']

        cursor.execute('SELECT COUNT(staffID) FROM branchStaffs WHERE branchID=%s AND staffActive = 1',(branchID,))
        staff_count = cursor.fetchone()

        cursor.execute('''
            SELECT
                DATE(orderDate) AS orderDay,
                COUNT(orderID) AS totalOrders,
                SUM(totalAmount) AS totalSales
            FROM orders
            WHERE
                orderDate >= DATE_SUB(NOW(), INTERVAL 1 WEEK)
                AND orderActive = 1
            GROUP BY orderDay
            ORDER BY orderDay;''')
        order_data = cursor.fetchall()

        cursor.execute('SELECT COUNT(promoID) FROM simplepromotions WHERE branchID IS NULL')
        nationalPromotionsNum = cursor.fetchone()

        cursor.execute('SELECT COUNT(promoID) FROM simplepromotions WHERE branchID = %s', (branchID,))
        branchPromotionsNum = cursor.fetchone()

        cursor.execute('SELECT COUNT(pizzaName) FROM pizzas WHERE branchID = %s',(branchID,))
        pizzaNum = cursor.fetchone()

        cursor.execute('SELECT COUNT(sideOfferingID) FROM sideOfferings WHERE branchID = %s',(branchID,))
        sideOfferingNum = cursor.fetchone()

        cursor.execute('SELECT COUNT(drinkID) FROM drinks WHERE branchID = %s',(branchID,))
        drinkNum = cursor.fetchone()

        cursor.close()
        return render_template('adminDashboard2.html', staff_count=staff_count['COUNT(staffID)'], order_data=order_data, nationalPromotionsNum=nationalPromotionsNum['COUNT(promoID)'], branchPromotionsNum=branchPromotionsNum['COUNT(promoID)'], pizzaNum=pizzaNum['COUNT(pizzaName)'], sideOfferingNum=sideOfferingNum['COUNT(sideOfferingID)'], drinkNum=drinkNum['COUNT(drinkID)'])
    else:
        flash('Please login as branch admin!')
        return redirect(url_for('login.login'))

@bp.route('/adminDashboard2/reports', methods=['GET'])
def reports():
    if not 'loggedin' in session or session['role'] != 'branch_Admin':
        return redirect(url_for('login.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    branchAdminID = session['id']


    # Fetch the branchID based on branchAdminID
    cursor.execute(
        'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
    branch_data = cursor.fetchone()
    branchID = branch_data['branchID']
    # Fetch info from the database

    branch = {}

    cursor.execute('SELECT * FROM simplepromotions WHERE sPromoActive = TRUE AND branchID = %s;', (branchID,))
    branch['simplePromo'] = cursor.fetchall()

    for i in branch['simplePromo']:
        i['startDate'] = i['startDate'].isoformat()
        i['endDate'] = i['endDate'].isoformat()

    cursor.execute('SELECT * FROM comboPromotions WHERE cPromoActive = TRUE AND branchID = %s;', (branchID,))
    branch['comboPromo'] = cursor.fetchall()

    for i in branch['comboPromo']:
        i['startDate'] = i['startDate'].isoformat()
        i['endDate'] = i['endDate'].isoformat()

    cursor.execute('SELECT SUM(totalAmount) AS total FROM orders WHERE orderActive = TRUE AND branchID = %s;', (branchID,))
    totalAmount = cursor.fetchone()

    cursor.execute('SELECT COUNT(orderID) AS total FROM orders WHERE orderActive = TRUE AND branchID = %s;', (branchID,))
    totalOrder = cursor.fetchone()

    cursor.execute('SELECT orderDate, totalAmount, branchID, deliveryOption FROM orders WHERE orderDate BETWEEN NOW() - INTERVAL 30 DAY AND NOW() AND branchID = %s ORDER BY orderDate DESC;', (branchID,))
    orders30Days = cursor.fetchall()

    for i in orders30Days:
        i['orderDate'] = i['orderDate'].isoformat()

    cursor.execute('SELECT COUNT(customerID) AS total FROM customers WHERE customerActive = TRUE')
    totalCustomer = cursor.fetchone()

    cursor.execute('SELECT od.productID, COUNT(od.productID) as count FROM orderDetails od\
    JOIN orders o ON od.orderID = o.orderID\
    WHERE  o.orderDate BETWEEN NOW() - INTERVAL 30 DAY AND NOW() AND branchID = %s\
    GROUP BY od.productID ORDER BY count DESC;', (branchID,))
    topProducts30 = cursor.fetchall()

    cursor.execute('SELECT od.productID, COUNT(od.productID) as count FROM orderDetails od\
    JOIN orders o ON od.orderID = o.orderID\
    WHERE branchID = %s\
    GROUP BY od.productID ORDER BY count DESC;', (branchID,))
    topProductsAll = cursor.fetchall()

    for i in topProducts30:
        if i['productID'] < 200:
            cursor.execute("SELECT * FROM pizzas WHERE pizzaID = %s;", (i['productID'],))
            productName = cursor.fetchone()
            i['productID'] = productName['pizzaName']

        elif i['productID'] < 300:
            cursor.execute("SELECT * FROM sideOfferings WHERE sideOfferingID = %s;", (i['productID'],))
            productName = cursor.fetchone()
            i['productID'] = productName['offeringName']

        else:
            cursor.execute("SELECT * FROM drinks WHERE drinkID = %s;", (i['productID'],))
            productName = cursor.fetchone()
            i['productID'] = productName['drinkName']

    for i in topProductsAll:
        if i['productID'] < 200:
            cursor.execute("SELECT * FROM pizzas WHERE pizzaID = %s;", (i['productID'],))
            productName = cursor.fetchone()
            i['productID'] = productName['pizzaName']

        elif i['productID'] < 300:
            cursor.execute("SELECT * FROM sideOfferings WHERE sideOfferingID = %s;", (i['productID'],))
            productName = cursor.fetchone()
            i['productID'] = productName['offeringName']

        else:
            cursor.execute("SELECT * FROM drinks WHERE drinkID = %s;", (i['productID'],))
            productName = cursor.fetchone()
            i['productID'] = productName['drinkName']

    branch['totalAmounts'] = totalAmount
    branch['totalOrder'] = totalOrder
    branch['totalCustomer'] = totalCustomer
    branch['orders30Days'] = orders30Days
    branch['topProducts30'] = topProducts30
    branch['topProductsAll'] = topProductsAll

    return render_template('branchReports.html', branchInfo=simplejson.dumps(branch, use_decimal=True))



@bp.route('/edit_staff/<int:staff_id>', methods=['POST'])
def edit_staff(staff_id):
    # Ensure the user is logged in and is a branch admin
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        # Retrieve form data
        title = request.form['title']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        position = request.form['position']
        phone_number = request.form['phoneNumber']

        # Database operation to update the staff info
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            UPDATE branchStaffs
            SET title = %s, firstName = %s, lastName = %s, position = %s, phoneNumber = %s
            WHERE staffID = %s
        ''', (title, first_name, last_name, position, phone_number, staff_id))
        mysql.connection.commit()
        cursor.close()

        flash('Staff info updated successfully!')
        return redirect(url_for('adminDashboard2.adminDashboard2'))
    else:
        flash('Please login as branch admin!')
        return redirect(url_for('login.login'))

@bp.route('/add_staff', methods=['POST'])
def add_staff():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch_data = cursor.fetchone()
        branchID = branch_data['branchID']

        # Step 1: Register the user
        username = request.form.get('username')
        password = request.form.get('userPassword')
        cursor.execute('SELECT * FROM users WHERE userName = %s', (username,))
        account = cursor.fetchone()

        if account:
            flash('Username already exists! Choose a different one.')
            return redirect(url_for('adminDashboard2.adminDashboard2'))

        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('INSERT INTO users (userRole, userName, userPassword, userActive) VALUES (%s, %s, %s, %s)',
                       ('branch_Staff', username, hashed_password, True))
        mysql.connection.commit()

        # Step 2: Add as branch staff
        userID = cursor.lastrowid
        title = request.form.get('title')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        position = request.form.get('position')
        phoneNumber = request.form.get('phoneNumber')
        cursor.execute('''
            INSERT INTO branchStaffs (branchID, userID, title, firstName, lastName, position, phoneNumber)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (branchID, userID, title, firstName, lastName, position, phoneNumber))
        mysql.connection.commit()

        cursor.close()
        flash('New staff added successfully!')
        return redirect(url_for('adminDashboard2.adminDashboard2'))
    else:
        flash('Please login as branch admin!')
        return redirect(url_for('login.login'))

@bp.route('/adminDashboard2/delete_staff/<int:staffID>', methods=['GET'])
def delete_staff(staffID):
    if 'loggedin' in session and session['role'] == 'branch_Admin':

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Set the staffActive field to 0 for the corresponding staff
        cursor.execute(
            'UPDATE branchStaffs SET staffActive = 0 WHERE staffID = %s', (staffID,))

        # Get the userID associated with the staff to update the users table
        cursor.execute(
            'SELECT userID FROM branchStaffs WHERE staffID = %s', (staffID,))
        user_data = cursor.fetchone()

        # Set the userActive field to 0 for the corresponding user
        cursor.execute(
            'UPDATE users SET userActive = 0 WHERE userID = %s', (user_data['userID'],))

        mysql.connection.commit()
        cursor.close()

        flash('Staff has been successfully deleted!')
        return redirect(url_for('adminDashboard2.adminDashboard2'))

    else:
        flash('Please login as branch admin!')
        return redirect(url_for('login.login'))

@bp.route('/branchadmin/profile')
def branchadminProfile():
    if is_authenticated():
        if session['role'] == 'branch_Admin':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Fetch admininfo from the database
            cursor.execute(
                'SELECT users.userID, users.userName, users.userPassword, admininfo.title, admininfo.firstName, admininfo.lastName, admininfo.phoneNumber FROM admininfo JOIN users ON admininfo.userID = users.userID WHERE admininfo.userID = %s', (session['id'],))
            branchadminInfo = cursor.fetchone()
            return render_template('branchadminProfile.html', branchadminInfo=branchadminInfo)
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))

@bp.route('/branchadmin/update_profile', methods=['GET', 'POST'])
def updateProfile():
    if is_authenticated():
        userID = request.form.get('userID')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch admininfo from the database
        cursor.execute('''SELECT users.userID, users.userName, users.userPassword, admininfo.title, admininfo.firstName, admininfo.lastName, admininfo.phoneNumber
                       FROM admininfo JOIN users
                       ON admininfo.userID = users.userID
                       WHERE admininfo.adminActive=True AND admininfo.userID = %s''', (userID,))
        account = cursor.fetchone()

        if account:
            userName = request.form.get('userName')
            title = request.form.get('title')
            firstName = request.form.get('firstName')
            lastName = request.form.get('lastName')
            phoneNumber = request.form.get('phoneNumber')
            userPassword = request.form.get('userPassword')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # if username is changed:
            if userName != account['userName']:
                # check if username already exists in database
                if userNameCrash(userName):
                    flash(
                        'Failed. Username already exists. Please choose a different username.', 'error')
                    return redirect(url_for('adminDashboard2.branchadminProfile'))
                else:
                    cursor.execute(
                        'UPDATE users SET userName=%s WHERE userID=%s', (userName, userID))
                    mysql.connection.commit()
                    flash('Username changed successfully!', 'success')

            # check if the password is changed by comparing the input password with the password stored in database
            if userPassword.encode('utf-8') != account['userPassword'].encode('utf-8'):
                if userPassword != "********" and not bcrypt.checkpw(userPassword.encode('utf-8'), account['userPassword'].encode('utf-8')):
                    # if password is changed, then the new password needs to be encrypted before inserting into databse
                    hashed = passwordEncrypt(userPassword)
                    cursor.execute(
                        'UPDATE users SET userPassword=%s WHERE userID=%s', (hashed, userID))
                    mysql.connection.commit()
                    flash('Password changed successfully!', 'success')

            if 'avatar' in request.files and request.files['avatar'].filename != '':
                avatar = request.files.get('avatar')
                avatarName = f"{userID}.jpg"
                filePath = os.path.join('app', 'static', 'avatar', avatarName)
                avatar.save(filePath)

            if firstName != account['firstName'] or lastName != account['lastName'] or phoneNumber != account['phoneNumber'] or title != account['title']:
                cursor.execute('UPDATE admininfo SET firstName=%s,lastName=%s,phoneNumber=%s,title=%s WHERE admininfo.userID = %s', (
                    firstName, lastName, phoneNumber, title, userID,))
                mysql.connection.commit()
                flash('Profile information updated successfully!', 'success')
                return redirect(url_for('adminDashboard2.branchadminProfile'))
            else:
                return redirect(url_for('adminDashboard2.branchadminProfile'))
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))

@bp.route('/branchStaffs', methods=['GET'])
def branchStaffs():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch_data = cursor.fetchone()
        branchID = branch_data['branchID']
        # Fetch staff data for the given branchID, only where staffActive is true and userActive is true
        query = '''
        SELECT bs.*
        FROM branchStaffs bs
        JOIN users u ON bs.userID = u.userID
        WHERE bs.branchID = %s AND bs.staffActive = 1 AND u.userActive = 1
        '''
        cursor.execute(query, (branchID,))
        staff_data = cursor.fetchall()

        return render_template('branchStaffs.html', staffs=staff_data)
    return redirect(url_for('login.login'))

@bp.route('/branchProducts', methods=['GET'])
def branchProducts():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # fetch the branchID based on branchAdminID
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch = cursor.fetchone()
        branchID = branch['branchID']

        # fetch the pizzas, side offerings and drinks for the given branchID         # AND pizzaActive = TRUE
        cursor.execute(
            'SELECT * FROM pizzas WHERE branchID = %s ORDER BY pizzaName', (branchID,))
        pizzas = cursor.fetchall()

        # Group the pizzas by their name
        pizzas = [list(g) for k, g in groupby(
            pizzas, key=itemgetter('pizzaName'))]

        cursor.execute(
            'SELECT * FROM sideOfferings WHERE branchID = %s AND sideOfferingActive = TRUE', (branchID,))
        side_offerings = cursor.fetchall()

        cursor.execute(
            'SELECT * FROM drinks WHERE branchID = %s AND drinkActive = TRUE', (branchID,))
        drinks = cursor.fetchall()

        cursor.execute('SELECT * FROM toppings WHERE toppingActive = TRUE')
        toppings = cursor.fetchall()

        cursor.close()

        return render_template('branchProducts.html',
                               branch_pizzas=pizzas,
                               branch_sideOfferings=side_offerings,
                               branch_drinks=drinks,
                               toppings=toppings)

    return redirect(url_for('login.login'))

@bp.route('/branchAddSideOffering', methods=['POST'])
def branchAddSideOffering():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # fetch the branchID based on branchAdminID
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch = cursor.fetchone()
        branchID = branch['branchID']

        offeringName = request.form['offeringName']
        description = request.form['description']
        price = request.form['price']
        preparetime = request.form['preparetime']

        # INSERT into the database
        cursor.execute('INSERT INTO sideOfferings (offeringName, description, price, branchID, preparetime, sideOfferingActive) VALUES (%s, %s, %s, %s, %s, TRUE)',
                       (offeringName, description, price, branchID, preparetime))

        # fetch the id of the side offering that was just inserted
        sideOfferingId = cursor.lastrowid

        # Handle image file upload
        if 'image' in request.files and request.files['image'].filename != '':
            image = request.files.get('image')
            imageName = f"{sideOfferingId}.jpg"
            filePath = os.path.join('app', 'static', 'image', imageName)
            image.save(filePath)

        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return redirect(url_for('login.login'))

@bp.route('/branchUpdateSideOffering', methods=['POST'])
def branchUpdateSideOffering():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # fetch the branchID based on branchAdminID
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch = cursor.fetchone()
        branchID = branch['branchID']

        sideOfferingId = request.form['sideOfferingID']
        offeringName = request.form['offeringName']
        description = request.form['description']
        price = request.form['price']
        preparetime = request.form['preparetime']

        # Check if the sideOffering to be updated belongs to this branch
        cursor.execute(
            'SELECT branchID FROM sideOfferings WHERE sideOfferingID = %s', (sideOfferingId,))
        offeringBranch = cursor.fetchone()
        if not offeringBranch or offeringBranch['branchID'] != branchID:
            return jsonify(success=False, message="Unauthorized action.")

        cursor.execute('UPDATE sideOfferings SET offeringName = %s, description = %s, price = %s, preparetime = %s WHERE sideOfferingID = %s',
                       (offeringName, description, price, preparetime, sideOfferingId))

        if 'image' in request.files and request.files['image'].filename != '':
            image = request.files.get('image')
            imageName = f"{sideOfferingId}.jpg"
            filePath = os.path.join('app', 'static', 'image', imageName)
            image.save(filePath)

        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, message="Login required or invalid access.")

@bp.route('/branchDeleteSideOffering', methods=['POST'])
def branchDeleteSideOffering():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        sideOfferingID = request.json['sideOfferingID']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Soft delete the sideOffering by setting its sideOfferingActive attribute to false
        cursor.execute('UPDATE sideOfferings SET sideOfferingActive = FALSE WHERE sideOfferingID = %s', [
                       sideOfferingID])
        mysql.connection.commit()

        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False)

@bp.route('/branchDeactivateSingleSizePizza', methods=['POST'])
def branchDeactivateSingleSizePizza():
    pizzaID = request.json.get('pizzaID')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'UPDATE pizzas SET pizzaActive = FALSE WHERE pizzaID = %s', (pizzaID,))
    mysql.connection.commit()
    cursor.close()
    return jsonify(success=True)

@bp.route('/branchActivateSingleSizePizza', methods=['POST'])
def branchActivateSingleSizePizza():
    pizzaID = request.json.get('pizzaID')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'UPDATE pizzas SET pizzaActive = TRUE WHERE pizzaID = %s', (pizzaID,))
    mysql.connection.commit()
    cursor.close()
    return jsonify(success=True)

@bp.route('/branchDeactivateEntirePizza', methods=['POST'])
def branchDeactivateEntirePizza():
    pizzaName = request.json.get('pizzaName')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'UPDATE pizzas SET pizzaActive = FALSE WHERE pizzaName = %s', (pizzaName,))
    mysql.connection.commit()
    cursor.close()
    return jsonify(success=True)

@bp.route('/branchAddPizza', methods=['POST'])
def branchAddPizza():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # fetch the branchID based on branchAdminID
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch = cursor.fetchone()
        branchID = branch['branchID']

        pizzaName = request.form['pizzaName']
        description = request.form['pizzaDescription']
        sizes = ['Small', 'Medium', 'Large']
        prices = [request.form['smallPrice'],
                  request.form['mediumPrice'], request.form['largePrice']]
        preparetimes = [request.form['smallPrepareTime'],
                        request.form['mediumPrepareTime'], request.form['largePrepareTime']]

        for size, price, preparetime in zip(sizes, prices, preparetimes):
            cursor.execute("""
                INSERT INTO pizzas (pizzaName, description, size, price, branchID, preparetime)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (pizzaName, description, size, price, branchID, preparetime))

        if 'pizzaImage' in request.files and request.files['pizzaImage'].filename != '':
            image = request.files.get('pizzaImage')
            # fetch the id of the pizza that was just inserted
            first_pizzaId = cursor.lastrowid

            for offset in range(3):
                pizzaId = first_pizzaId - offset
                imageName = f"{pizzaId}.jpg"
                filePath = os.path.join('app', 'static', 'image', imageName)
                with open(filePath, 'wb') as f:
                    f.write(image.read())
                    # reset the file pointer to the beginning of the file
                    image.seek(0)

        mysql.connection.commit()
        cursor.close()
        return jsonify(success=True)

    return jsonify(success=False, message="Unauthorized access.")

@bp.route('/branchUpdatePizza', methods=['POST'])
def branchUpdatePizza():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # fetch the branchID based on branchAdminID
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch = cursor.fetchone()
        branchID = branch['branchID']

        pizzaOriginalName = request.form['pizzaOriginalName']
        pizzaNewName = request.form['pizzaName']
        description = request.form['description']

        # Fetch the existing sizes for the given pizza name
        cursor.execute('SELECT size FROM pizzas WHERE pizzaName = %s AND branchID = %s AND pizzaActive = TRUE',
                       (pizzaOriginalName, branchID))
        existing_sizes = [row['size'] for row in cursor.fetchall()]

        for existing_size in existing_sizes:
            # Only update if we have data for this size
            if request.form.get(f'{existing_size.lower()}Price') and request.form.get(f'{existing_size.lower()}PrepareTime'):
                price = request.form[f'{existing_size.lower()}Price']
                preparetime = request.form[f'{existing_size.lower()}PrepareTime']

                cursor.execute("""
                    UPDATE pizzas SET pizzaName = %s, description = %s, price = %s, preparetime = %s
                    WHERE pizzaName = %s AND size = %s AND branchID = %s
                """, (pizzaNewName, description, price, preparetime, pizzaOriginalName, existing_size, branchID))

        if 'pizzaImage' in request.files and request.files['pizzaImage'].filename != '':
            image = request.files.get('pizzaImage')
            for size in existing_sizes:
                cursor.execute(
                    'SELECT pizzaID FROM pizzas WHERE pizzaName = %s AND size = %s AND branchID = %s', (pizzaNewName, size, branchID))
                pizza = cursor.fetchone()
                # Only update if we have data for this size
                # data like {'pizzaID': 166}
                if pizza:
                    imageName = f"{pizza['pizzaID']}.jpg"
                    filePath = os.path.join(
                        'app', 'static', 'image', imageName)
                    with open(filePath, 'wb') as f:
                        f.write(image.read())
                    # reset the file pointer to the beginning of the file
                    image.seek(0)

        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, message="Unauthorized access.")

@bp.route('/branchPromotions')
def branchPromotions():
     if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch = cursor.fetchone()
        branchID = branch['branchID']
        cursor.execute('SELECT * FROM simplepromotions WHERE branchID = %s AND sPromoActive = TRUE', (branchID,))
        branchPromotions = cursor.fetchall()

        cursor.execute('SELECT * FROM simplepromotions WHERE branchID IS NULL AND sPromoActive = TRUE')
        nationalPromotions = cursor.fetchall()

        return render_template('branchPromotions.html', branchPromotions=branchPromotions, nationalPromotions=nationalPromotions)


@bp.route('/branchAddPromotion', methods=['POST'])
def branchAddPromotion():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # fetch the branchID based on branchAdminID
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch = cursor.fetchone()
        branchID = branch['branchID']

        promoType = request.form['promoType']
        startDate = request.form['startDate']
        endDate = request.form['endDate']
        thresholdAmount = request.form['thresholdAmount']
        discountAmount = request.form['discountAmount']
        code = request.form['code']
        description = request.form['description']

        cursor.execute('INSERT INTO simplepromotions (promoType, branchID, description, startDate, endDate, thresholdAmount, discountAmount, code, sPromoActive) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)', (promoType, branchID, description, startDate, endDate, thresholdAmount,discountAmount, code))

        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, message="Unauthorized access.")

@bp.route('/branchUpdatePromotion', methods=['POST'])
def branchUpdatePromotion():
    if 'loggedin' in session and session['role'] == 'branch_Admin':
        branchAdminID = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # fetch the branchID based on branchAdminID
        cursor.execute(
            'SELECT branchID FROM branches WHERE branchAdminID = %s', (branchAdminID,))
        branch = cursor.fetchone()
        branchID = branch['branchID']

        promoID = request.form['promoID']
        promoType = request.form['promoType']
        startDate = request.form['startDate']
        endDate = request.form['endDate']
        thresholdAmount = request.form['thresholdAmount']
        discountAmount = request.form['discountAmount']
        code = request.form['code']
        description = request.form['description']
        # print('111111111')
        # print(code)

        if promoType:
            cursor.execute("""
                UPDATE simplepromotions SET promoType = %s, startDate = %s, endDate = %s, thresholdAmount = %s, discountAmount = %s,  code = %s, description = %s
                WHERE promoID = %s  AND branchID = %s
            """, (promoType, startDate, endDate, thresholdAmount, discountAmount, code, description, promoID, branchID))



        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, message="Unauthorized access.")


@bp.route('/branchDeactivatePromotion', methods=['POST'])
def branchDeactivatePromotion():
    promoID = request.json.get('promoID')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'UPDATE simplepromotions SET sPromoActive = FALSE WHERE promoID = %s', (promoID,))
    mysql.connection.commit()
    cursor.close()
    return jsonify(success=True)

@bp.route('/reviews/<branchID>', methods=['GET'])
def checkReviews(branchID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT reviewID, reviews.customerID, reviews.orderID, reviewDate, rating, review, branchID FROM reviews JOIN orders ON orders.orderID = reviews.orderID WHERE branchID = %s', (branchID,))
    branchReviews = cursor.fetchall()
    # print(branchReviews)
    return render_template('branchReviews.html', branchReviews=branchReviews)
