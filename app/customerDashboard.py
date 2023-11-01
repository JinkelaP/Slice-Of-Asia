from app import mysql
from flask import flash, render_template, request, redirect, url_for, session, Blueprint, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
import json
import os
from decimal import Decimal
from datetime import datetime, timezone
import pytz

bp = Blueprint('customerDashboard', __name__, )

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

def convertPizzas(pizzas_from_db,toppings_from_db):
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

def convertPromotions(branch_promotions_db):
    promotion_list = []
    today = datetime.now().date()
    
    for promotion in branch_promotions_db:
        if promotion['startDate'] <= today <= promotion['endDate']:
            promotion_list.append({
                'id': promotion['promoID'],
                'description': promotion['description'],
                'startDate': promotion['startDate'],
                'endDate': promotion['endDate'],
                'thresholdAmount': float(promotion['thresholdAmount']),
                'discountAmount':float(promotion['discountAmount'])
            })
    return promotion_list

# encapsulate the passwordEncrypt function
def passwordEncrypt(userPassword):
    bytes = userPassword.encode('utf-8')
    salt = bcrypt.gensalt()
    hashedPsw = bcrypt.hashpw(bytes, salt)
    return hashedPsw

def getCustomerID(userID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT customerID from customers WHERE userID = %s;', (userID,))
    return cursor.fetchone()['customerID']

@bp.route('/menu')
def menu():
    if 'branch' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # fetch branch info
        cursor.execute('SELECT * FROM branches WHERE branchID = %s;', (session['branch'],))
        branches = cursor.fetchone()

         # fetch toppings
        cursor.execute('SELECT toppingName, description, price FROM toppings WHERE toppingActive = TRUE;')
        toppings_db = cursor.fetchall()
        toppings = convertToppings(toppings_db)

        # fetch national pizzas
        cursor.execute('SELECT pizzaID, pizzaName, description, size, price, preparetime FROM pizzas WHERE pizzaActive = TRUE AND branchID IS NULL;')
        national_pizzas_db = cursor.fetchall()
        national_pizzas = convertPizzas(national_pizzas_db, toppings_db)

        # fetch branch pizzas
        cursor.execute('SELECT pizzaID, pizzaName, description, size, price, preparetime FROM pizzas WHERE pizzaActive = TRUE AND branchID = %s;', (session['branch'],))
        branch_pizzas_db = cursor.fetchall()
        branch_pizzas = convertPizzas(branch_pizzas_db, toppings_db)

        # fetch national side offerings
        cursor.execute('SELECT sideOfferingID, offeringName, description, price, preparetime FROM sideOfferings WHERE sideOfferingActive = TRUE AND branchID IS NULL;')
        national_side_offerings_db = cursor.fetchall()
        national_side_offerings = convertSideOfferings(national_side_offerings_db)

        # fetch branch side offerings
        cursor.execute('SELECT sideOfferingID, offeringName, description, price, preparetime FROM sideOfferings WHERE sideOfferingActive = TRUE AND branchID = %s;', (session['branch'],))
        branch_side_offerings_db = cursor.fetchall()
        branch_side_offerings = convertSideOfferings(branch_side_offerings_db)

        # fetch national drinks
        cursor.execute('SELECT drinkID, drinkName, description, price, preparetime FROM drinks WHERE drinkActive = TRUE AND branchID IS NULL;')
        national_drinks_db = cursor.fetchall()
        national_drinks = convertDrinks(national_drinks_db)

        # fetch branch drinks
        cursor.execute('SELECT drinkID, drinkName, description, price, preparetime FROM drinks WHERE drinkActive = TRUE AND branchID = %s;', (session['branch'],))
        branch_drinks_db = cursor.fetchall()
        branch_drinks = convertDrinks(branch_drinks_db)

        # fetch promotions
        cursor.execute('SELECT promoID, description, startDate, endDate, thresholdAmount, discountAmount FROM simplepromotions WHERE sPromoActive = TRUE AND promoType = "fullReduction" AND  (branchID = %s OR branchID IS NULL);', (session['branch'],))
        branch_promotions_db = cursor.fetchall()
        branch_promotions = convertPromotions(branch_promotions_db)
        
        if 'cart' in session:
            cart = session['cart']
            if cart:
                voucherApplied = cart[-2]                      
                if type(cart[-1]) == int or type(cart[-1]) == str:
                    cart.pop(-1)
                    cart.pop(-1)
            else:
                voucherApplied = None
            return render_template('menu.html',cartSession = json.dumps(cart), isCartString = True, branches=branches, session=session, national_pizzas=national_pizzas, branch_pizzas=branch_pizzas, national_side_offerings=national_side_offerings, branch_side_offerings=branch_side_offerings, national_drinks=national_drinks, branch_drinks=branch_drinks, toppings=toppings, branch_promotions=branch_promotions, voucherApplied = voucherApplied)
        else:
            return render_template('menu.html', cartSession = None, branches=branches, session=session, national_pizzas=national_pizzas, branch_pizzas=branch_pizzas, national_side_offerings=national_side_offerings, branch_side_offerings=branch_side_offerings, national_drinks=national_drinks, branch_drinks=branch_drinks, toppings=toppings, branch_promotions=branch_promotions, voucherApplied = False)

    else:
        flash('You need to choose a branch before ordering!', 'success')
        return redirect(url_for('login.chooseBranch'))


@bp.route('/customer')
def customerDashboard():
    if not is_authenticated():
        flash('You did not login!', 'success')
        return redirect(url_for('login.login'))
    else:
        return redirect(url_for('customerDashboard.menu'))
    
@bp.route('/checkout', methods=['POST'])
def checkout():

    cartData = request.json.get('cart', [])
    cartTotal = request.json.get('total', 0)
    voucherApplied = request.json.get('voucherApplied', False)
          
    if cartData and not isinstance(cartData[-1], str):
        cartData.append(voucherApplied)
        cartData.append(cartTotal)
    session['cart'] = cartData

# check if items are available
    responseData = {
        'result': False,
        'msg': []
    }
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
 

    # return a json
    return jsonify(responseData)

# Hey! This is a legacy function, not recommend to use.
@bp.route('/checkoutUpdate')
def checkoutUpdate():
    session.pop('cart',None)
    return redirect(url_for('customerDashboard.menu'))

@bp.route('/payment')
def payment():
    if not is_authenticated():
        flash('You did not login!', 'success')
        return redirect(url_for('login.login'))
    elif 'cart' not in session:
        return redirect(url_for('customerDashboard.menu'))
    else:
        cart = session['cart']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
        cursor.execute('SELECT users.userName, customers.firstName, customers.lastName, customers.email, customers.phoneNumber, customers.Address FROM customers JOIN users ON customers.userID = users.userID WHERE customers.userID = %s',(session['id'],))
        customerInfo = cursor.fetchone()     
        return render_template('payment.html', cartJs = json.dumps(cart), cart = cart, customerInfo = customerInfo)
    
@bp.route('/order', methods=['POST'])
def order():
    totalAmount = Decimal(session['cart'][-1])
    cart = session['cart'][:-2]
    branchID = session['branch']
    userID = session['id']
    addressDelivery = f"{request.form.get('Address')} {request.form.get('zip')}"
    orderStatus = 'Paid'

    orderMethod = request.form.get('orderMethod')
    if orderMethod == "delivery":
        deliveryOption = 'Delivery'
        totalAmount += 7
    elif orderMethod == "takeaway":
        deliveryOption = 'Pick Up'
    
    estimatedTime = request.form.get('estimatedTime')
    dtFormat = "%Y-%m-%dT%H:%M"
    naiveDt = datetime.strptime(estimatedTime, dtFormat)
    aucklandTime = pytz.timezone('Pacific/Auckland')
    localisedDt = aucklandTime.localize(naiveDt)
    estimatedTime = localisedDt.strftime('%Y-%m-%d %H:%M:%S')

    estimatedTimedMysql = localisedDt.astimezone(pytz.utc)

    currentUTC = datetime.utcnow()
    formattedUTC = currentUTC.strftime('%Y-%m-%d %H:%M:%S')
    orderSubmitTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  
    specialRequests = request.form.get('specialRequests')


    customerID = getCustomerID(userID)
    # create orders
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO orders (customerID, branchID, addressDelivery, orderStatus,\
                  totalAmount, deliveryOption, estimatedTime, specialRequests, orderJSON, orderDate) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s);',\

                      (customerID, branchID, addressDelivery, orderStatus, totalAmount, deliveryOption, estimatedTimedMysql, specialRequests, json.dumps(cart), formattedUTC))

    mysql.connection.commit()
    orderID = cursor.lastrowid
    # create payments
    paymentMethod = request.form.get('paymentMethod')
    if paymentMethod == "debit":
        paymentMethod = 'Debit Card'
    elif paymentMethod == "credit":
        paymentMethod = 'Credit Card'
    elif paymentMethod == "paypal":
        paymentMethod = 'Paypal'

    # cursor.execute('SELECT orderID from orders WHERE customerID = %s;', (customerID,))
    # orderID = cursor.fetchall()[-1]['orderID']
    cursor.execute('INSERT INTO payment (customerID, orderID, paymentMethod) VALUES (%s, %s, %s);',\
                      (customerID, orderID, paymentMethod))
    mysql.connection.commit()

    # create order details
    # create order-topping details
    
    for i in cart:
        if type(i) == dict:
            productID = i['id']
            if i['id'] < 200:
                productType = 'Pizza'
            elif i['id'] < 300:
                productType = 'SideOffering'
            else:
                productType = 'Drink'
            
            if 'price' in i:
                price = i['price']
            else:
                price = i['size']['price']
            
            quantity = i['number']
            
            cursor.execute('INSERT INTO orderDetails (orderID, productID, productType, price, quantity) VALUES (%s, %s, %s, %s, %s);',\
                      (orderID, productID, productType, price, quantity))
            mysql.connection.commit()

            cursor.execute('SELECT orderDetailID FROM orderDetails WHERE orderID = %s', (orderID,))
            orderDetailID = cursor.fetchall()[-1]['orderDetailID']
            

            if 'toppings' in i:
                toppingID = 400
                for t in i['toppings']:
                    if t['quantity'] > 0:
                        cursor.execute('INSERT INTO orderdetails_toppings (orderDetailID, toppingID, quantity) VALUES (%s, %s, %s);', \
                                       (orderDetailID, toppingID, quantity))
                    mysql.connection.commit()
                    toppingID += 1
            

    # create notification

    title = 'Order received!'
    content = f'Your order #{orderID} has been received!'
    cursor.execute('INSERT INTO notifications (customerID, branchID, title, content, notificationType, relatedOrderID) VALUES (%s, %s, %s, %s, %s, %s);',\
                      (customerID, branchID, title, content, 'Order-related', orderID))
    mysql.connection.commit()

    session.pop('cart')

    flash('Your order has been placed successfully!', 'success')

    return redirect(url_for('customerDashboard.trackOrder', orderID=orderID))

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

@bp.route('/customer/trackOrder/<orderID>')
def trackOrder(orderID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # preparing data for tracking order page

    # get cart item's preparation time from database

    cursor.execute('SELECT * from orders WHERE orderID = %s;', (orderID,))
    orderInfo = cursor.fetchone()

    branchID = orderInfo['branchID']

    cart = json.loads(orderInfo['orderJSON'])
    for item in cart:
        if item['id'] < 200:
            cursor.execute('SELECT preparetime from pizzas WHERE pizzaID = %s;', (item['id'],))
            result = cursor.fetchone()
            preparetime = result['preparetime']
            if item['size']['value'] == 'medium':
                preparetime += 5
            if item['size']['value'] == 'large':
                preparetime += 10
            item['preparetime'] = preparetime
        elif item['id'] < 300:
            cursor.execute('SELECT preparetime from sideOfferings WHERE sideOfferingID = %s;', (item['id'],))
            result = cursor.fetchone()
            item['preparetime'] = result['preparetime']
        else:
            item['preparetime'] = 0

    cursor.execute('SELECT * from branches WHERE branchID = %s and branchActive = 1;', (branchID,))
    branchInfo = cursor.fetchone()

    cursor.execute('SELECT * from customers WHERE customerID = %s and customerActive = 1;',(orderInfo['customerID'],))
    customerInfo = cursor.fetchone()

    startTimeDuration = branchInfo['startTime']
    totalSeconds = startTimeDuration.total_seconds()
    hours = int(totalSeconds // 3600)
    minutes = int((totalSeconds % 3600) // 60)
    seconds = int(totalSeconds % 60)
    formattedStartTime = f"{hours:02}:{minutes:02}:{seconds:02}"
    branchInfo['startTime'] = formattedStartTime

    endTimeDuration = branchInfo['endTime']
    totalSeconds = endTimeDuration.total_seconds()
    hours = int(totalSeconds // 3600)
    minutes = int((totalSeconds % 3600) // 60)
    seconds = int(totalSeconds % 60)
    formattedEndTime = f"{hours:02}:{minutes:02}:{seconds:02}"
    branchInfo['endTime'] = formattedEndTime

    if branchID == 1 or branchID == '1' :
        branchInfo['GPS'] = [-36.843326, 174.766817]
    elif branchID == 2 or branchID ==  '2':
        branchInfo['GPS'] = [50.735544, -1.778984]
    elif branchID == 3 or branchID == '3':
        branchInfo['GPS'] = [-41.286790, 174.776222]
    elif branchID == 4 or branchID == '4':
        branchInfo['GPS'] = [-45.033108, 168.656930]

    estimatedTime = utc_to_local(orderInfo['estimatedTime'])
    orderSubmitTime = utc_to_local(orderInfo['orderDate'])

    cursor.execute('SELECT * from reviews WHERE orderID = %s;', (orderID,))
    reviewInfo = cursor.fetchone()

    order = {
        'orderID': orderID,
        'cart': cart,
        'totalAmount': orderInfo['totalAmount'],
        'orderMethod': orderInfo['deliveryOption'],
        'orderStatus': orderInfo['orderStatus'],
        'specifiedPickupOrDeliveryTime': estimatedTime,
        'orderSubmitTime': orderSubmitTime,
        'branchInfo': branchInfo,
        'customerInfo': customerInfo,
        'specialRequests': orderInfo['specialRequests'],
        'reviewInfo': reviewInfo
    }

    return render_template('trackOrder.html', order=order)
    

@bp.route('/customer/myOrder')
def myOrder():
    if is_authenticated():
        role = session['role']
        customerID = getCustomerID(session['id'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
        # Fetch customerinfo from the database

        # Since I cannot jsonserialise the date object in Js, I can only write this longggggg SQL.
        cursor.execute('SELECT orders.orderID, orders.orderDate, orders.estimatedTime, orders.deliveryOption, orders.orderJSON,  \
                       orders.orderStatus, orders.totalAmount, orders.specialRequests, branches.branchName, branches.branchID\
                       ,payment.paymentMethod\
                       FROM orders JOIN branches ON branches.branchID = orders.branchID \
                       JOIN payment ON orders.orderID = payment.orderID\
                       WHERE orders.customerID = %s',(customerID,))
        allOrders = cursor.fetchall()

        allOrders = sorted(allOrders, key=lambda x: x['orderDate'])

        cursor.execute('SELECT branchName from branches;')
        allBranch = cursor.fetchall()
        
        return render_template('myOrder.html', allOrders = allOrders, allBranch = allBranch)
    else:
        return redirect(url_for('login.login'))  

@bp.route('/customer/reorder', methods=['POST'])
def reOrder():
    cartData = request.json.get('orderData', [])
    branchID = request.json.get('branchID', '')
    cartData.append(False)
    cartData.append(0)
    session['cart'] = cartData
    session['branch'] = branchID
    return '233'

@bp.route('/customer/msg', methods=['GET'])
def msg():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
    cursor.execute('SELECT * FROM notifications WHERE customerID = %s',(getCustomerID(session['id']),))
    allMsg = cursor.fetchall()
    return render_template('displayMsg.html', allMsg = reversed(allMsg))

@bp.route('/customer/profile')
def customerProfile():    
    if is_authenticated():
        if session['role'] == 'Customer':    
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
            # Fetch customerinfo from the database
            cursor.execute('SELECT users.userID, users.userName, users.userPassword, customers.title, customers.firstName, customers.lastName, customers.email, customers.phoneNumber, customers.Address, customers.dateOfBirth, customers.Preferences FROM customers JOIN users ON customers.userID = users.userID WHERE customers.userID = %s',(session['id'],))
            customerInfo = cursor.fetchone()           
            return render_template('customerProfile.html', customerInfo=customerInfo)
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))    
    
@bp.route('/customer/update_profile', methods=['GET', 'POST'])
def updateProfile():
    if is_authenticated():
        userID = request.form.get('userID')        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
        # Fetch customers from the database
        cursor.execute('''SELECT users.userID, users.userName, users.userPassword, customers.title, customers.firstName, customers.lastName, customers.email, customers.phoneNumber, customers.Address, customers.dateOfBirth, customers.Preferences
                       FROM customers JOIN users 
                       ON customers.userID = users.userID 
                       WHERE customers.customerActive=True AND customers.userID = %s''',(userID,))
        account = cursor.fetchone()        
             
        if account:

            userName = request.form.get('userName')
            title = request.form.get('title')
            firstName = request.form.get('firstName')
            lastName = request.form.get('lastName')

            email = request.form.get('email')
            phoneNumber = request.form.get('phoneNumber')
            Address = request.form.get('Address')
            dateOfBirth = request.form.get('dateOfBirth')
            Preferences = request.form.get('Preferences')
            userPassword = request.form.get('userPassword')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)            
            #if username is changed:
            if userName != account['userName']:
                #check if username already exists in database                
                if userNameCrash(userName):
                    flash('Failed. Username already exists. Please choose a different username.','error')
                    return redirect(url_for('customerDashboard.customerProfile'))
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

            if firstName != account['firstName'] or lastName != account['lastName'] or phoneNumber != account['phoneNumber'] or title != account['title'] or email != account['email'] or Address != account['Address'] or dateOfBirth != account['dateOfBirth'] or Preferences != account['Preferences']:
                    cursor.execute('UPDATE customers SET title=%s,firstName=%s,lastName=%s,email=%s,phoneNumber=%s,Address=%s,dateOfBirth=%s,Preferences=%s WHERE customers.userID = %s', (title,firstName,lastName,email,phoneNumber,Address,dateOfBirth,Preferences,userID,))
                    mysql.connection.commit()
                    flash('Profile information updated successfully!','success')
                    return redirect(url_for('customerDashboard.customerProfile'))           
            else:                
                return redirect(url_for('customerDashboard.customerProfile'))
        else:
            return "unauthorized"
    else:
        return redirect(url_for('login.login'))
    

@bp.route('/customer/review', methods=['POST'])
def reviewOrder():
    data = request.json
    customerID = data['customerID']
    orderID = data['orderID']
    reviewDate = datetime.now()
    rating = data['rating']
    review = data['review']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * from reviews WHERE orderID = %s;', (orderID,))
    existingReview = cursor.fetchone()
    if existingReview:
        cursor.execute("UPDATE reviews SET rating = %s, review = %s WHERE orderID = %s;",(rating, review, orderID))
    else:
        cursor.execute("INSERT INTO reviews (customerID, orderID, reviewDate, rating, review) VALUES (%s, %s, %s, %s, %s)",(customerID,orderID, reviewDate, rating, review))
    mysql.connection.commit()
    return jsonify(success=True, message="Thank you for your feedback!")

    