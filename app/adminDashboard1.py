from app import mysql
from flask import flash, render_template, request, redirect, url_for, session, Blueprint
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
import os
import math
from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import jsonify
from itertools import groupby
from operator import itemgetter
import json
import simplejson

bp = Blueprint('adminDashboard1', __name__, )

def is_authenticated():
    return 'loggedin' in session

def userNameCrash(userName):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE userActive = True and userName = %s', (userName,))
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

@bp.route('/hqAdmin/home')
def adminDashboard1():
    if not 'loggedin' in session or session['role'] != 'HQ_Admin':
        return redirect(url_for('login.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch branches from the database
    cursor.execute('SELECT * FROM branches WHERE branchActive = TRUE;')
    branches = cursor.fetchall()


    # Fetch additional information for each branch.
    for branch in branches:
        cursor.execute('SELECT * FROM pizzas WHERE branchID = %s AND pizzaActive = TRUE', (branch['branchID'],))
        branch['specialty_pizzas'] = cursor.fetchall()

        cursor.execute('SELECT * FROM sideOfferings WHERE branchID = %s AND sideOfferingActive = TRUE', (branch['branchID'],))
        branch['specialty_sides'] = cursor.fetchall()

        cursor.execute('SELECT * FROM drinks WHERE branchID = %s AND drinkActive = TRUE', (branch['branchID'],))
        branch['specialty_drinks'] = cursor.fetchall()

        cursor.execute('SELECT * FROM AdminInfo WHERE userID = %s;', (branch['branchAdminID'],))
        branch['branchAdminInfo'] = cursor.fetchone()

        cursor.execute('SELECT * FROM simplepromotions WHERE branchID = %s AND sPromoActive = TRUE', (branch['branchID'],))
        branch['simplePromo'] = cursor.fetchall()

        cursor.execute('SELECT * FROM comboPromotions WHERE branchID = %s AND cPromoActive = TRUE', (branch['branchID'],))
        branch['comboPromo'] = cursor.fetchall()

        cursor.execute('SELECT * FROM orders WHERE branchID = %s AND orderActive = TRUE', (branch['branchID'],))
        totalAmountOrders = cursor.fetchall()

        cursor.execute('SELECT orderDate, totalAmount FROM orders WHERE branchID = %s AND orderDate BETWEEN NOW() - INTERVAL 30 DAY AND NOW() ORDER BY orderDate DESC;', (branch['branchID'],))
        orders30Days = cursor.fetchall()

        totalAmount = 0
        totalCustomer = 0
        customerIDTemp = 0
        for i in totalAmountOrders:
            totalAmount += i['totalAmount']
            if i['customerID'] != customerIDTemp:
                totalCustomer += 1
                customerIDTemp = i['customerID']

        cursor.execute('SELECT od.productID, COUNT(od.productID) as count FROM orderDetails od\
        JOIN orders o ON od.orderID = o.orderID\
        WHERE o.branchID = %s AND o.orderDate BETWEEN NOW() - INTERVAL 30 DAY AND NOW()\
        GROUP BY od.productID ORDER BY count DESC', (branch['branchID'],))
        topProducts = cursor.fetchall()

        for i in topProducts:
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
        branch['orderAmounts'] = len(totalAmountOrders)
        branch['totalCustomer'] = customerIDTemp
        branch['orders30Days'] = orders30Days
        branch['topProducts'] = topProducts

    return render_template('adminDashboard1.html', branches=branches)

@bp.route('/hqAdmin/reports')
def reports():
    if not 'loggedin' in session or session['role'] != 'HQ_Admin':
        return redirect(url_for('login.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch info from the database

    branch = {}

    cursor.execute('SELECT * FROM simplepromotions WHERE sPromoActive = TRUE')
    branch['simplePromo'] = cursor.fetchall()

    for i in branch['simplePromo']:
        i['startDate'] = i['startDate'].isoformat()
        i['endDate'] = i['endDate'].isoformat()

    cursor.execute('SELECT * FROM comboPromotions WHERE cPromoActive = TRUE')
    branch['comboPromo'] = cursor.fetchall()

    for i in branch['comboPromo']:
        i['startDate'] = i['startDate'].isoformat()
        i['endDate'] = i['endDate'].isoformat()

    cursor.execute('SELECT SUM(totalAmount) AS total FROM orders WHERE orderActive = TRUE')
    totalAmount = cursor.fetchone()

    cursor.execute('SELECT COUNT(orderID) AS total FROM orders WHERE orderActive = TRUE')
    totalOrder = cursor.fetchone()

    cursor.execute('SELECT orderDate, totalAmount, branchID, deliveryOption FROM orders WHERE orderDate BETWEEN NOW() - INTERVAL 30 DAY AND NOW() ORDER BY orderDate DESC;')
    orders30Days = cursor.fetchall()

    for i in orders30Days:
        i['orderDate'] = i['orderDate'].isoformat()

    cursor.execute('SELECT COUNT(customerID) AS total FROM customers WHERE customerActive = TRUE')
    totalCustomer = cursor.fetchone()

    cursor.execute('SELECT od.productID, COUNT(od.productID) as count FROM orderDetails od\
    JOIN orders o ON od.orderID = o.orderID\
    WHERE  o.orderDate BETWEEN NOW() - INTERVAL 30 DAY AND NOW()\
    GROUP BY od.productID ORDER BY count DESC')
    topProducts30 = cursor.fetchall()

    cursor.execute('SELECT od.productID, COUNT(od.productID) as count FROM orderDetails od\
    JOIN orders o ON od.orderID = o.orderID\
    GROUP BY od.productID ORDER BY count DESC')
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

    return render_template('nationalReports.html', nationalInfo=simplejson.dumps(branch, use_decimal=True))

@bp.route('/hqadmin/profile')
def hqadminProfile():
    if is_authenticated():
        if session['role'] == 'HQ_Admin':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Fetch admininfo from the database
            cursor.execute('SELECT users.userID, users.userName, users.userPassword, admininfo.title, admininfo.firstName, admininfo.lastName, admininfo.phoneNumber FROM admininfo JOIN users ON admininfo.userID = users.userID WHERE admininfo.userID = %s',(session['id'],))
            hqadminInfo = cursor.fetchone()
            return render_template('hqadminProfile.html', hqadminInfo=hqadminInfo)
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))

@bp.route('/hqadmin/update_profile', methods=['GET', 'POST'])
def updateProfile():
    if is_authenticated():
        userID = request.form.get('userID')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch admininfo from the database
        cursor.execute('''SELECT users.userID, users.userName, users.userPassword, admininfo.title, admininfo.firstName, admininfo.lastName, admininfo.phoneNumber
                       FROM admininfo JOIN users
                       ON admininfo.userID = users.userID
                       WHERE admininfo.adminActive=True AND admininfo.userID = %s''',(userID,))
        account = cursor.fetchone()

        if account:
            userName = request.form.get('userName')
            title = request.form.get('title')
            firstName = request.form.get('firstName')
            lastName = request.form.get('lastName')
            phoneNumber = request.form.get('phoneNumber')
            userPassword = request.form.get('userPassword')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            #if username is changed:
            if userName != account['userName']:
                #check if username already exists in database
                if userNameCrash(userName):
                    flash('Failed. Username already exists. Please choose a different username.','error')
                    return redirect(url_for('adminDashboard1.hqadminProfile'))
                else:
                    cursor.execute('UPDATE users SET userName=%s WHERE userID=%s',(userName, userID))
                    mysql.connection.commit()
                    flash('Username changed successfully!','success')

            # check if the password is changed by comparing the input password with the password stored in database
            if userPassword.encode('utf-8') !=  account['userPassword'].encode('utf-8'):
                if userPassword != "********" and not bcrypt.checkpw(userPassword.encode('utf-8'), account['userPassword'].encode('utf-8')):
                    # if password is changed, then the new password needs to be encrypted before inserting into databse
                    hashed = passwordEncrypt(userPassword)
                    cursor.execute('UPDATE users SET userPassword=%s WHERE userID=%s',(hashed, userID))
                    mysql.connection.commit()
                    flash('Password changed successfully!','success')

            if 'avatar' in request.files and request.files['avatar'].filename != '':
                avatar = request.files.get('avatar')
                avatarName = f"{userID}.jpg"
                filePath = os.path.join('app', 'static', 'avatar', avatarName)
                avatar.save(filePath)

            if firstName != account['firstName'] or lastName != account['lastName'] or phoneNumber != account['phoneNumber'] or title != account['title']:
                    cursor.execute('UPDATE admininfo SET firstName=%s,lastName=%s,phoneNumber=%s,title=%s WHERE admininfo.userID = %s', (firstName,lastName,phoneNumber,title,userID,))
                    mysql.connection.commit()
                    flash('Profile information updated successfully!','success')
                    return redirect(url_for('adminDashboard1.hqadminProfile'))
            else:
                return redirect(url_for('adminDashboard1.hqadminProfile'))
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))


@bp.route('/nationalProducts', methods=['GET'])
def nationalProducts():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch the pizzas, side offerings, and drinks that are national (branchID is NULL) and active
        cursor.execute('SELECT * FROM pizzas WHERE branchID IS NULL AND pizzaActive = TRUE ORDER BY pizzaName')
        pizzas = cursor.fetchall()

        # Group the pizzas by their name
        pizzas = [list(g) for k, g in groupby(pizzas, key=itemgetter('pizzaName'))]

        cursor.execute('SELECT * FROM sideOfferings WHERE branchID IS NULL AND sideOfferingActive = TRUE')
        side_offerings = cursor.fetchall()

        cursor.execute('SELECT * FROM drinks WHERE branchID IS NULL AND drinkActive = TRUE')
        drinks = cursor.fetchall()

        cursor.execute('SELECT * FROM toppings WHERE toppingActive = TRUE')
        toppings = cursor.fetchall()

        cursor.close()

        return render_template('nationalProducts.html', pizzas=pizzas, side_offerings=side_offerings, drinks=drinks, toppings=toppings)

    return redirect(url_for('login.login'))


@bp.route('/addABranch', methods=['POST'])
def addABranch():
    if is_authenticated():
        if session['role'] == 'HQ_Admin':
            # Extracting data from the form
            branchName = request.form.get('branchName')
            city = request.form.get('city')
            address = request.form.get('address')
            phoneNumber = request.form.get('phoneNumber')
            email = request.form.get('email')
            startTime = request.form.get('startTime')
            endTime = request.form.get('endTime')

            # Insert into the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = '''
            INSERT INTO branches (branchName, city, address, phoneNumber, email, startTime, endTime)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(query, (branchName, city, address, phoneNumber, email, startTime, endTime))
            mysql.connection.commit()
            cursor.close()

            flash('Branch added successfully!', 'success')
            return redirect(url_for('login.login'))
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))


@bp.route('/addPizza', methods=['POST'])
def addPizza():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        pizzaName = request.form['pizzaName']
        description = request.form['description']

        sizes = ['Small', 'Medium', 'Large']
        prices = [request.form['smallPrice'], request.form['mediumPrice'], request.form['largePrice']]
        preparetimes = [request.form['smallPrepareTime'], request.form['mediumPrepareTime'], request.form['largePrepareTime']]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        for size, price, preparetime in zip(sizes, prices, preparetimes):
            cursor.execute("""
                INSERT INTO pizzas (pizzaName, description, size, price, preparetime)
                VALUES (%s, %s, %s, %s, %s)
            """, (pizzaName, description, size, price, preparetime))

        if 'pizzaImage' in request.files and request.files['pizzaImage'].filename != '':
            image = request.files.get('pizzaImage')
            # fetch the id of the pizza that was just inserted
            first_pizzaId = cursor.lastrowid

            for offset in range(3):
                pizzaId = first_pizzaId - offset
                imageName = f"{pizzaId}.jpg"
                filePath = os.path.join('app', 'static', 'image', imageName)
                # save the image to the file system
                with open(filePath, 'wb') as f:
                    f.write(image.read())
                    # reset the file pointer to the beginning of the file
                    image.seek(0)

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('adminDashboard1.nationalProducts'))
    return redirect(url_for('login.login'))


@bp.route('/editPizzaMain', methods=['POST'])
def editPizzaMain():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        pizzaOriginalName = request.form['pizzaOriginalName']
        pizzaNewName = request.form['pizzaName']
        description = request.form['description']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch all pizzaIDs that match the original pizza name
        cursor.execute('SELECT pizzaID FROM pizzas WHERE pizzaName = %s', (pizzaOriginalName,))
        all_pizzaIDs = [row['pizzaID'] for row in cursor.fetchall()]

        # Update the pizzaName and description for all pizzaIDs that match the original pizza name
        for pizzaID in all_pizzaIDs:
            cursor.execute('UPDATE pizzas SET pizzaName = %s, description = %s WHERE pizzaID = %s',
                           (pizzaNewName, description, pizzaID))

            if 'pizzaImage' in request.files and request.files['pizzaImage'].filename != '':
                image = request.files.get('pizzaImage')
                imageName = f"{pizzaID}.jpg"
                filePath = os.path.join('app', 'static', 'image', imageName)
                with open(filePath, 'wb') as f:
                    f.write(image.read())
                # reset the file pointer to the beginning of the file
                image.seek(0)

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('adminDashboard1.nationalProducts'))

    return redirect(url_for('login.login'))




@bp.route('/editPizzaSize', methods=['POST'])
def editPizzaSize():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        pizzaID = request.form['pizzaID']
        price = request.form['price']
        preparetime = request.form['preparetime']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('UPDATE pizzas SET price = %s, preparetime = %s WHERE pizzaID = %s', (price, preparetime, pizzaID))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('adminDashboard1.nationalProducts'))

    return redirect(url_for('login.login'))


@bp.route('/deletePizzas', methods=['POST'])
def deletePizzas():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        pizzaNames = request.json.get('pizzaNames', [])
        pizzaIds = request.json.get('pizzaIds', [])

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if pizzaNames:  # Check if pizzaNames is not empty
            query_names = "UPDATE pizzas SET pizzaActive = FALSE WHERE pizzaName IN (%s)" % ', '.join(['%s'] * len(pizzaNames))
            cursor.execute(query_names, tuple(pizzaNames))

        if pizzaIds:  # Check if pizzaIds is not empty
            query_ids = "UPDATE pizzas SET pizzaActive = FALSE WHERE pizzaID IN (%s)" % ', '.join(['%s'] * len(pizzaIds))
            cursor.execute(query_ids, tuple(pizzaIds))

        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, error="Unauthorized access")

@bp.errorhandler(500)
def server_error(e):
    return jsonify(success=False, error="Internal server error"), 500

@bp.route('/addSideOffering', methods=['POST'])
def addSideOffering():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        offeringName = request.form['offeringName']
        description = request.form['description']
        price = request.form['price']
        preparetime = request.form['preparetime']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO sideOfferings (offeringName, description, price, preparetime) VALUES (%s, %s, %s, %s)', (offeringName, description, price, preparetime))
        # fetch the id of the side offering that was just inserted
        sideOfferingId = cursor.lastrowid

        if 'image' in request.files and request.files['image'].filename != '':
            image = request.files.get('image')
            imageName = f"{sideOfferingId}.jpg"
            filePath = os.path.join('app', 'static', 'image', imageName)
            image.save(filePath)

        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('adminDashboard1.nationalProducts'))
    return redirect(url_for('login.login'))

@bp.route('/editSideOffering', methods=['POST'])
def editSideOffering():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        sideOfferingId = request.form['sideOfferingId']
        editOfferingName = request.form['editOfferingName']
        editDescription = request.form['editDescription']
        editPrice = request.form['editPrice']
        editPrepareTime = request.form['editPrepareTime']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if 'editImage' in request.files and request.files['editImage'].filename != '':
            image = request.files.get('editImage')
            imageName = f"{sideOfferingId}.jpg"
            filePath = os.path.join('app', 'static', 'image', imageName)
            image.save(filePath)

        cursor.execute('UPDATE sideOfferings SET offeringName=%s, description=%s, price=%s, preparetime=%s WHERE sideOfferingID=%s', (editOfferingName, editDescription, editPrice, editPrepareTime, sideOfferingId))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('adminDashboard1.nationalProducts'))
    return redirect(url_for('login.login'))

@bp.route('/deleteSideOffering', methods=['POST'])
def deleteSideOffering():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        sideOfferingId = request.form['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Soft delete the sideOffering by setting its sideOfferingActive attribute to false
        cursor.execute('UPDATE sideOfferings SET sideOfferingActive = FALSE WHERE sideOfferingID = %s', [sideOfferingId])
        mysql.connection.commit()
        cursor.close()
        return jsonify(success=True)
    return jsonify(success=False, error="Authentication failed.")

@bp.route('/addDrink', methods=['POST'])
def addDrink():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        drinkName = request.form['drinkName']
        description = request.form['description']
        price = request.form['price']
        preparetime = request.form['preparetime']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('INSERT INTO drinks (drinkName, description, price, preparetime) VALUES (%s, %s, %s, %s)', (drinkName, description, price, preparetime))
        drinkID = cursor.lastrowid  # fetch the id of the drink that was just inserted

        if 'drinkImage' in request.files and request.files['drinkImage'].filename != '':
            drinkImage = request.files.get('drinkImage')
            imageName = f"{drinkID}.jpg"
            filePath = os.path.join('app', 'static', 'image', imageName)
            drinkImage.save(filePath)

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('adminDashboard1.nationalProducts'))

    return redirect(url_for('login.login'))

@bp.route('/editDrink', methods=['POST'])
def editDrink():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        # Fetching the form data
        drinkId = request.form['drinkId']
        drinkName = request.form['drinkName']
        description = request.form['description']
        price = request.form['price']
        preparetime = request.form['preparetime']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Updating the drink's data in the database
        cursor.execute('UPDATE drinks SET drinkName = %s, description = %s, price = %s, preparetime = %s WHERE drinkID = %s', (drinkName, description, price, preparetime, drinkId))

        # If a new image is uploaded, save it
        if 'drinkImage' in request.files and request.files['drinkImage'].filename != '':
            drinkImage = request.files.get('drinkImage')
            imageName = f"{drinkId}.jpg"
            filePath = os.path.join('app', 'static', 'image', imageName)
            drinkImage.save(filePath)

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('adminDashboard1.nationalProducts'))

    return redirect(url_for('login.login'))


@bp.route('/deleteDrink', methods=['POST'])
def deleteDrink():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        drinkId = request.form['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('UPDATE drinks SET drinkActive = FALSE WHERE drinkID = %s', [drinkId])

        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, error="Authentication failed.")


@bp.route('/addTopping', methods=['POST'])
def addTopping():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        toppingName = request.form['toppingName']
        description = request.form['toppingDescription']
        price = request.form['toppingPrice']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO toppings (toppingName, description, price) VALUES (%s, %s, %s)', (toppingName, description, price))

        toppingId = cursor.lastrowid

        if 'toppingImage' in request.files and request.files['toppingImage'].filename != '':
            toppingImage = request.files.get('toppingImage')
            imageName = f"{toppingId}.jpg"
            filePath = os.path.join('app', 'static', 'image', imageName)
            toppingImage.save(filePath)

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('adminDashboard1.nationalProducts'))

    return redirect(url_for('login.login'))

@bp.route('/editTopping', methods=['POST'])
def editTopping():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        # fetch the form data
        toppingId = request.form['toppingId']
        toppingName = request.form['toppingName']
        description = request.form['description']
        price = request.form['price']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # update the topping's data in the database
        cursor.execute('UPDATE toppings SET toppingName = %s, description = %s, price = %s WHERE toppingID = %s', (toppingName, description, price, toppingId))

        # if a new image is uploaded, save it
        if 'toppingImage' in request.files and request.files['toppingImage'].filename != '':
            toppingImage = request.files.get('toppingImage')
            imageName = f"{toppingId}.jpg"
            filePath = os.path.join('app', 'static', 'image', imageName)
            toppingImage.save(filePath)

        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, error="Authentication failed.")


@bp.route('/deleteTopping', methods=['POST'])
def deleteTopping():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        toppingId = request.form['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('UPDATE toppings SET toppingActive = FALSE WHERE toppingID = %s', [toppingId])

        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, error="Authentication failed.")


@bp.route('/nationalPromotions')
def nationalPromotions():
     if 'loggedin' in session and session['role'] == 'HQ_Admin':
        branchAdminID = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM simplepromotions WHERE branchID IS NOT NULL AND sPromoActive = TRUE')
        branchPromotions = cursor.fetchall()

        cursor.execute('SELECT * FROM simplepromotions WHERE branchID IS NULL AND sPromoActive = TRUE')
        nationalPromotions = cursor.fetchall()

        return render_template('nationalPromotions.html', branchPromotions=branchPromotions, nationalPromotions=nationalPromotions)


@bp.route('/nationalAddPromotion', methods=['POST'])
def nationalAddPromotion():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        branchAdminID = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        promoType = request.form['promoType']
        startDate = request.form['startDate']
        endDate = request.form['endDate']
        thresholdAmount = request.form['thresholdAmount']
        discountAmount = request.form['discountAmount']
        code = request.form['code']
        description = request.form['description']

        cursor.execute('INSERT INTO simplepromotions (promoType,  description, startDate, endDate, thresholdAmount, discountAmount, code, sPromoActive) VALUES (%s,  %s, %s, %s, %s, %s, %s, TRUE)', (promoType, description, startDate, endDate, thresholdAmount,discountAmount, code))

        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, message="Unauthorized access.")

@bp.route('/nationalUpdatePromotion', methods=['POST'])
def nationalUpdatePromotion():
    if 'loggedin' in session and session['role'] == 'HQ_Admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        promoID = request.form['promoID']
        promoType = request.form['promoType']
        startDate = request.form['startDate']
        endDate = request.form['endDate']
        thresholdAmount = request.form['thresholdAmount']
        discountAmount = request.form['discountAmount']
        code = request.form['code']
        description = request.form['description']
        if promoType:
            cursor.execute("""
                UPDATE simplepromotions SET promoType = %s, startDate = %s, endDate = %s, thresholdAmount = %s, discountAmount = %s,  code = %s, description = %s
                WHERE promoID = %s
            """, (promoType, startDate, endDate, thresholdAmount, discountAmount, code, description, promoID))
        mysql.connection.commit()
        cursor.close()

        return jsonify(success=True)

    return jsonify(success=False, message="Unauthorized access.")


@bp.route('/nationalDeactivatePromotion', methods=['POST'])
def nationalDeactivatePromotion():
    promoID = request.json.get('promoID')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'UPDATE simplepromotions SET sPromoActive = FALSE WHERE promoID = %s', (promoID,))
    mysql.connection.commit()
    cursor.close()
    return jsonify(success=True)