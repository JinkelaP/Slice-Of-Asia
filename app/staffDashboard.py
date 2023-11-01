from app import mysql, socketio
from flask import flash, render_template, request, redirect, url_for, session, Blueprint
from flask import jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb.cursors
import bcrypt
import os
import math
from datetime import date, datetime, timedelta
from decimal import Decimal
import json

bp = Blueprint('staffDashboard', __name__, )


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


def getStaffID(userID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT staffID from branchstaffs WHERE userID = %s;', (userID,))
    return cursor.fetchone()['staffID']


def convertPizzas(pizzas_from_db, toppings_from_db):
    products = {}
    size_map = {
        'Small': 'small',
        'Medium': 'medium',
        'Large': 'large'
    }
    for pizza in pizzas_from_db:
        key = pizza['pizzaName']

        if key not in products:
            products[key] = {
                'id': pizza['pizzaID'],
                'name': key,
                'description': pizza['description'],
                'sizes': [],
                'selectedToppings': convertToppings(toppings_from_db)
            }

        products[key]['sizes'].append({
            'label': pizza['size'],
            'value': size_map[pizza['size']],
            'price': float(pizza['price'])
        })

    return list(products.values())


def convertSideOfferings(side_offerings_from_db):
    offerings = []

    for offering in side_offerings_from_db:
        offerings.append({
            'id': offering['sideOfferingID'],
            'name': offering['offeringName'],
            'description': offering['description'],
            'price': float(offering['price']),
            'preparetime': offering['preparetime']
        })

    return offerings


def convertDrinks(drinks_from_db):
    drink_list = []
    for drink in drinks_from_db:
        drink_list.append({
            'id': drink['drinkID'],
            'name': drink['drinkName'],
            'description': drink['description'],
            'price': float(drink['price']),
            'preparetime': drink['preparetime']
        })
    return drink_list


def convertToppings(toppings_from_db):
    topping_list = []
    for topping in toppings_from_db:
        topping_list.append({
            'name': topping['toppingName'],
            'description': topping['description'],
            'price': float(topping['price'],),
            'quantity': 0
        })
    return topping_list


# staff dashboard
@bp.route('/staff/home')
def staffDashboard():
    if is_authenticated():
        if session['role'] == 'branch_Staff':
            role = session['role']
            userID = session['id']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT branchstaffs.branchID FROM branchstaffs WHERE branchstaffs.userID = %s', (userID,))
            branchID = cursor.fetchone()['branchID']
            # cursor.execute('''SELECT
            #             orders.orderID, orders.customerID, orders.addressDelivery, orders.orderStatus, orders.orderDate, orders.estimatedTime, orders.deliveryOption,
            #             orders.orderJSON, orders.orderStatus, orders.totalAmount, orders.specialRequests, orders.comboID,
            #             customers.title, customers.firstName, customers.lastName, customers.phoneNumber,
            #             orderdetails.productID, orderdetails.quantity,
            #             orderdetails_toppings.toppingID, orderdetails_toppings.quantity,
            #             payment.paymentMethod
            #             FROM orders
            #             JOIN customers ON orders.customerID = customers.customerID
            #             JOIN orderdetails ON orders.orderID = orderdetails.orderID
            #             LEFT JOIN orderdetails_toppings ON orderdetails.orderDetailID = orderdetails_toppings.orderDetailID
            #             JOIN payment ON orders.orderID = payment.orderID
            #             WHERE branchID = %s
            #             ORDER BY orders.orderID, orderdetails.productID, orderdetails_toppings.toppingID''',(branchID,))

            cursor.execute('''SELECT
                                orders.orderID, 
                                orders.customerID, 
                                orders.addressDelivery,
                                orders.orderStatus,
                                orders.orderDate, 
                                orders.estimatedTime, 
                                orders.deliveryOption, 
                                orders.orderJSON, 
                                orders.orderStatus, 
                                orders.totalAmount, 
                                orders.specialRequests, 
                                orders.comboID,
                                customers.title, 
                                customers.firstName, 
                                customers.lastName, 
                                customers.phoneNumber                    
                            FROM orders
                            JOIN customers ON orders.customerID = customers.customerID 
                            WHERE branchID = %s AND orders.orderActive = TRUE''', (branchID,))
            allOrders = cursor.fetchall()
            # print(allOrders)
            return render_template('staffDashboard.html', allOrders=allOrders)
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))


@bp.route('/staff/profile')
def staffProfile():
    if is_authenticated():
        if session['role'] == 'branch_Staff':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Fetch staffinfo from the database
            cursor.execute(
                'SELECT users.userID, users.userName, users.userPassword, branchstaffs.title, branchstaffs.firstName, branchstaffs.lastName, branchstaffs.phoneNumber FROM branchstaffs JOIN users ON branchstaffs.userID = users.userID WHERE branchstaffs.userID = %s', (session['id'],))
            staffInfo = cursor.fetchone()
            return render_template('staffProfile.html', staffInfo=staffInfo)
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))


@bp.route('/staff/update_profile', methods=['GET', 'POST'])
def updateProfile():
    if is_authenticated():
        userID = request.form.get('userID')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch staffinfo from the database
        cursor.execute('''SELECT users.userID, users.userName, users.userPassword, branchstaffs.title, branchstaffs.firstName, branchstaffs.lastName, branchstaffs.phoneNumber 
                       FROM branchstaffs JOIN users 
                       ON branchstaffs.userID = users.userID 
                       WHERE branchstaffs.staffActive=True AND branchstaffs.userID = %s''', (userID,))
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
                    return redirect(url_for('staffDashboard.staffProfile'))
                else:
                    cursor.execute(
                        'UPDATE users SET userName=%s WHERE userID=%s', (userName, userID))
                    mysql.connection.commit()
                    flash('Username changed successfully!', 'success')

            # check if the password is changed by comparing the input password with the password stored in database
            if userPassword.encode('utf-8') != account['userPassword'].encode('utf-8'):
                if userPassword != "********" and not bcrypt.checkpw(userPassword.encode('utf-8'), account['userPassword'].encode('utf-8')):
                    # print(userPassword)
                    # print(account['userPassword'])

                    # if password is changed, then the new password needs to be encrypted before inserting into databse
                    hashed = passwordEncrypt(userPassword)
                    cursor.execute(
                        'UPDATE users SET userPassword=%s WHERE userID=%s', (hashed, userID))
                    mysql.connection.commit()
                    flash('Password changed successfully!', 'success')

            if 'avatar' in request.files and request.files['avatar'].filename != '':
                # print('bbbbbbbbbbb')
                avatar = request.files.get('avatar')
                avatarName = f"{userID}.jpg"
                filePath = os.path.join('app', 'static', 'avatar', avatarName)
                avatar.save(filePath)

            if firstName != account['firstName'] or lastName != account['lastName'] or phoneNumber != account['phoneNumber'] or title != account['title']:
                cursor.execute('UPDATE branchstaffs SET firstName=%s,lastName=%s,phoneNumber=%s,title=%s WHERE branchstaffs.userID = %s', (
                    firstName, lastName, phoneNumber, title, userID,))
                mysql.connection.commit()
                flash('Profile information updated successfully!', 'success')
                return redirect(url_for('staffDashboard.staffProfile'))
            else:
                return redirect(url_for('staffDashboard.staffProfile'))
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))


@bp.route('/staff/changeStatus', methods=['GET', 'POST'])
def changeStatus():
    orderID = request.json.get('orderID', [])
    newStatus = request.json.get('newStatus', [])
    # print(orderID)
    # print(newStatus)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # update orderStutas in database
        cursor.execute(
            'UPDATE orders SET orderStatus = %s WHERE orderID = %s', (newStatus, orderID))
        mysql.connection.commit()
        # print(f"Emitting data: {orderID}, {newStatus}")
        socketio.emit('statusChanged', {'orderID': orderID, 'newStatus': newStatus})
    except Exception as e:

        mysql.connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

    cursor.close()

    return jsonify({'status': 'success'})


@bp.route('/staff/deleteOrder', methods=['DELETE'])
def deleteOrder():
    orderID = request.json.get('orderID', None)
    # print(orderID)
    if orderID is not None:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'UPDATE orders SET orderActive = FALSE WHERE orderID = %s', (orderID,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid orderID'})


@bp.route('/staff/editOrder/<int:orderID>')
def editOrder(orderID):
    if is_authenticated() and session['role'] == 'branch_Staff':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(
                'SELECT * FROM orders WHERE orderID = %s;', (orderID,))
            thisOrder = cursor.fetchone()
        except:
            flash(f'Order {orderID} not found!', 'success')
            return redirect(url_for('staff.staffDashboard'))

        branchID = thisOrder['branchID']
        cart = thisOrder['orderJSON']

        # fetch branch info
        cursor.execute(
            'SELECT * FROM branches WHERE branchID = %s;', (branchID,))
        branches = cursor.fetchone()

        # fetch toppings
        cursor.execute(
            'SELECT toppingName, description, price FROM toppings WHERE toppingActive = TRUE;')
        toppings_db = cursor.fetchall()
        toppings = convertToppings(toppings_db)

        # fetch national pizzas
        cursor.execute(
            'SELECT pizzaID, pizzaName, description, size, price, preparetime FROM pizzas WHERE pizzaActive = TRUE AND branchID IS NULL;')
        national_pizzas_db = cursor.fetchall()
        national_pizzas = convertPizzas(national_pizzas_db, toppings_db)

        # fetch branch pizzas
        cursor.execute(
            'SELECT pizzaID, pizzaName, description, size, price, preparetime FROM pizzas WHERE pizzaActive = TRUE AND branchID = %s;', (branchID,))
        branch_pizzas_db = cursor.fetchall()
        branch_pizzas = convertPizzas(branch_pizzas_db, toppings_db)

        # fetch national side offerings
        cursor.execute(
            'SELECT sideOfferingID, offeringName, description, price, preparetime FROM sideOfferings WHERE sideOfferingActive = TRUE AND branchID IS NULL;')
        national_side_offerings_db = cursor.fetchall()
        national_side_offerings = convertSideOfferings(
            national_side_offerings_db)

        # fetch branch side offerings
        cursor.execute(
            'SELECT sideOfferingID, offeringName, description, price, preparetime FROM sideOfferings WHERE sideOfferingActive = TRUE AND branchID = %s;', (branchID,))
        branch_side_offerings_db = cursor.fetchall()
        branch_side_offerings = convertSideOfferings(branch_side_offerings_db)

        # fetch national drinks
        cursor.execute(
            'SELECT drinkID, drinkName, description, price, preparetime FROM drinks WHERE drinkActive = TRUE AND branchID IS NULL;')
        national_drinks_db = cursor.fetchall()
        national_drinks = convertDrinks(national_drinks_db)

        # fetch branch drinks
        cursor.execute(
            'SELECT drinkID, drinkName, description, price, preparetime FROM drinks WHERE drinkActive = TRUE AND branchID = %s;', (branchID,))
        branch_drinks_db = cursor.fetchall()
        branch_drinks = convertDrinks(branch_drinks_db)

        return render_template('menuStaffEdit.html', orderID=orderID, cartSession=cart, isCartString=True, branches=branches, session=session, national_pizzas=national_pizzas, branch_pizzas=branch_pizzas, national_side_offerings=national_side_offerings, branch_side_offerings=branch_side_offerings, national_drinks=national_drinks, branch_drinks=branch_drinks, toppings=toppings, voucherApplied=None)

    else:
        flash('Error', 'success')
        return redirect(url_for('/'))


@bp.route('/staff/editingOrder', methods=['POST'])
def editingOrder():
    if is_authenticated() and session['role'] == 'branch_Staff':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cartData = request.json.get('cart', [])
        orderID = request.json.get('orderID', 0)
        responseData = {
            'result': False,
            'msg': []
        }

        for i in cartData:
            if type(i) == dict:
                if i['id'] < 200:
                    cursor.execute("SELECT pizzaActive AS 'available', pizzaName AS 'name' FROM pizzas WHERE pizzaID = %s;", (i['id'],))
                elif i['id'] < 300:
                    cursor.execute("SELECT sideOfferingActive AS 'available', offeringName AS 'name' FROM sideOfferings WHERE sideOfferingID = %s;", (i['id'],))
                else:
                    cursor.execute("SELECT drinkActive AS 'available', drinkName AS 'name' FROM drinks WHERE drinkID = %s;", (i['id'],))
                
                resultAvailable = cursor.fetchone()
                if resultAvailable['available'] != True:
                    responseData['msg'].append(f'{resultAvailable["name"]} is not available now.\n')

        if responseData['msg'] != []:
            responseData['result'] = True
        else:
            cursor.execute('UPDATE orders SET orderJSON=%s WHERE orderID=%s',(json.dumps(cartData), orderID))
            mysql.connection.commit()


        return jsonify(responseData)

    else:
        flash('Error', 'success')
        return redirect(url_for('/'))


