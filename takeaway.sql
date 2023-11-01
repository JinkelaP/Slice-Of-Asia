DROP DATABASE IF EXISTS takeaway;
CREATE DATABASE takeaway;
USE takeaway;

CREATE TABLE IF NOT EXISTS users
(
    userID INT auto_increment PRIMARY KEY NOT NULL,
    userRole ENUM('HQ_Admin', 'branch_Admin', 'branch_Staff', 'Customer') NOT NULL DEFAULT 'Customer',
    userName VARCHAR(255) NOT NULL UNIQUE,
    userPassword VARCHAR(255) NOT NULL,
    userActive BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE IF NOT EXISTS AdminInfo
(
    userID INT PRIMARY KEY NOT NULL,
    title VARCHAR(10) NOT NULL,
    position ENUM('HQ_Admin', 'branch_Admin') NOT NULL,
    firstName VARCHAR(20) NOT NULL,
    lastName VARCHAR(20) NOT NULL,
    phoneNumber VARCHAR(15) NOT NULL,
    adminActive BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY (userID) REFERENCES users(userID)
        ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS branches
(
    branchID INT auto_increment PRIMARY KEY NOT NULL,
    branchAdminID INT,
    branchName VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL, 
    address VARCHAR(255) NOT NULL, 
    phoneNumber VARCHAR(15) NOT NULL, 
    email VARCHAR(40) NOT NULL,
    startTime TIME NOT NULL,
    endTime TIME NOT NULL,
    branchActive BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY (branchAdminID) REFERENCES users(userID)
        ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS branchStaffs
(
    staffID INT auto_increment PRIMARY KEY NOT NULL,
    branchID INT NOT NULL,
    userID INT NOT NULL,
    title VARCHAR(10) NOT NULL,
    firstName VARCHAR(20) NOT NULL,
    lastName VARCHAR(20) NOT NULL,
    position VARCHAR(20) NOT NULL,
    phoneNumber VARCHAR(15) NOT NULL,
    staffActive BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY (branchID) REFERENCES branches(branchID)
        ON UPDATE CASCADE,
    FOREIGN KEY (userID) REFERENCES users(userID)
        ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS customers
(
    customerID INT auto_increment PRIMARY KEY NOT NULL,
    userID INT NOT NULL,
    title VARCHAR(10) NOT NULL,
    firstName VARCHAR(20) NOT NULL,
    lastName VARCHAR(20) NOT NULL,
    email VARCHAR(40) NOT NULL,
    phoneNumber VARCHAR(15) NOT NULL,
    Address VARCHAR(200) NOT NULL,
    dateOfBirth DATE,
    Preferences VARCHAR(200),
    customerActive BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY (userID) REFERENCES users(userID)
        ON UPDATE CASCADE
);


CREATE TABLE simplePromotions (
    promoID INT PRIMARY KEY AUTO_INCREMENT,
    promoType ENUM('Code', 'fullReduction'),
    branchID INT,  -- If it's a branch-specific promotion, it has a branch ID; otherwise, it's NULL
    description TEXT,
    startDate DATE,
    endDate DATE,
    thresholdAmount DECIMAL(10,2),  -- Minimum amount to use the promotion
    discountAmount DECIMAL(10,2),  -- Amount to be discounted
    code TEXT,
    sPromoActive BOOLEAN DEFAULT TRUE,

    FOREIGN KEY(branchID) REFERENCES branches(branchID)
);


CREATE TABLE comboPromotions (
    comboID INT PRIMARY KEY AUTO_INCREMENT,
    branchID INT,  -- If it's a branch-specific promotion, it has a branch ID; otherwise, it's NULL 
    description TEXT,
    startDate DATE,
    endDate DATE,
    requiredItems TEXT,  -- Represents items required for the promotion. E.g., '{"pizza":2, "sideOffering":1}'
    freeItem TEXT,        -- Represents the free item. E.g., '{"drink":1}'
    cPromoActive BOOLEAN DEFAULT TRUE,

    FOREIGN KEY(branchID) REFERENCES branches(branchID)
);


CREATE TABLE IF NOT EXISTS products 
(
    productID INT AUTO_INCREMENT PRIMARY KEY,
    productType ENUM('Pizza', 'Drink', 'SideOffering') NOT NULL,
    originalID INT NOT NULL
);


CREATE TABLE IF NOT EXISTS pizzas 
(
    pizzaID INT AUTO_INCREMENT PRIMARY KEY,
    pizzaName VARCHAR(100) NOT NULL,
    description TEXT,
    size ENUM('Small', 'Medium', 'Large') NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    branchID INT, -- If it's a specialty pizza, it has a branch ID; otherwise, it's NULL
    preparetime INT NOT NULL,
    pizzaActive BOOLEAN DEFAULT TRUE,

    FOREIGN KEY(branchID) REFERENCES branches(branchID)
) AUTO_INCREMENT = 100;


Create TABLE IF NOT EXISTS toppings
(
    toppingID INT AUTO_INCREMENT PRIMARY KEY,
    toppingName VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,

    toppingActive BOOLEAN DEFAULT TRUE
) AUTO_INCREMENT = 400;


CREATE TABLE IF NOT EXISTS pizza_toppings 
(
    pizzaID INT,
    toppingID INT,
    quantity INT DEFAULT 1,


    FOREIGN KEY(pizzaID) REFERENCES pizzas(pizzaID),
    FOREIGN KEY(toppingID) REFERENCES toppings(toppingID),

    PRIMARY KEY(pizzaID, toppingID)  -- A pizza can have multiple toppings. A topping can be on multiple pizzas. 
);


CREATE TABLE IF NOT EXISTS sideOfferings 
(
    sideOfferingID INT AUTO_INCREMENT PRIMARY KEY,
    offeringName VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    branchID INT, -- If it's a specialty side offering, it has a branch ID; otherwise, it's NULL
    preparetime INT NOT NULL,
    sideOfferingActive BOOLEAN DEFAULT TRUE,

    FOREIGN KEY(branchID) REFERENCES branches(branchID)
) AUTO_INCREMENT = 200;


CREATE TABLE IF NOT EXISTS drinks 
(
    drinkID INT AUTO_INCREMENT PRIMARY KEY,
    drinkName VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    branchID INT, -- If it's a specialty drink, it has a branch ID; otherwise, it's NULL
    preparetime INT DEFAULT 1,
    drinkActive BOOLEAN DEFAULT TRUE,

    FOREIGN KEY(branchID) REFERENCES branches(branchID)
) AUTO_INCREMENT = 300;


CREATE TABLE IF NOT EXISTS orders 
(
    orderID INT AUTO_INCREMENT PRIMARY KEY,
    customerID INT,
    branchID INT,
    addressDelivery VARCHAR(200),
    orderStatus ENUM('Unpaid', 'Paid', 'Processing', 'In Oven', 'Quality Checking', 'Ready In Store', 'On The Way', 'Delivered','Done') DEFAULT 'Unpaid',
    totalAmount DECIMAL(10,2),
    orderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deliveryOption ENUM('Pick Up', 'Delivery'),
    estimatedTime TIMESTAMP,
    promoID INT,
    comboID INT,
    specialRequests TEXT,
    orderActive BOOLEAN DEFAULT TRUE,
    orderJSON JSON,

    FOREIGN KEY(customerID) REFERENCES customers(customerID),
    FOREIGN KEY(branchID) REFERENCES branches(branchID),
    FOREIGN KEY(promoID) REFERENCES simplePromotions(promoID),
    FOREIGN KEY(comboID) REFERENCES comboPromotions(comboID)
);

CREATE TABLE IF NOT EXISTS orderDetails 
(
    orderDetailID INT AUTO_INCREMENT PRIMARY KEY,
    orderID INT,
    productID INT,
    productType ENUM('Pizza', 'Drink', 'SideOffering'),
    price DECIMAL(10,2),
    quantity INT DEFAULT 1,
    orderDetailActive BOOLEAN DEFAULT TRUE,

    FOREIGN KEY(orderID) REFERENCES orders(orderID)
);


CREATE TABLE IF NOT EXISTS orderDetails_toppings
(
    orderDetailID INT,
    toppingID INT,
    quantity INT DEFAULT 1,

    FOREIGN KEY(orderDetailID) REFERENCES orderDetails(orderDetailID),
    FOREIGN KEY(toppingID) REFERENCES toppings(toppingID),

    PRIMARY KEY(orderDetailID, toppingID) 
);


CREATE TABLE IF NOT EXISTS carts 
(
    cartID INT AUTO_INCREMENT PRIMARY KEY,
    customerID INT,
    branchID INT,

    FOREIGN KEY(customerID) REFERENCES customers(customerID),
    FOREIGN KEY(branchID) REFERENCES branches(branchID)
);


CREATE TABLE IF NOT EXISTS cartDetails 
(
    cartDetailID INT AUTO_INCREMENT PRIMARY KEY,
    cartID INT,
    productID INT,
    productType ENUM('Pizza', 'Drink', 'SideOffering'),
    price DECIMAL(10,2),
    quantity INT DEFAULT 1,

    FOREIGN KEY(cartID) REFERENCES carts(cartID),
    FOREIGN KEY(productID) REFERENCES products(productID)
);


CREATE TABLE IF NOT EXISTS cartDetails_toppings 
(
    cartDetailID INT,
    toppingID INT,
    quantity INT DEFAULT 1,

    FOREIGN KEY(cartDetailID) REFERENCES cartDetails(cartDetailID),
    FOREIGN KEY(toppingID) REFERENCES toppings(toppingID),

    PRIMARY KEY(cartDetailID, toppingID)
);


CREATE TABLE IF NOT EXISTS reviews 
-- Customers can only review the whole orders that are delivered, not individual products
(
    reviewID INT AUTO_INCREMENT PRIMARY KEY,
    customerID INT,
    orderID INT,
    reviewDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    rating INT,
    review TEXT,
    reviewActive BOOLEAN DEFAULT TRUE,

    FOREIGN KEY(customerID) REFERENCES customers(customerID),
    FOREIGN KEY(orderID) REFERENCES orders(orderID)
);


CREATE TABLE IF NOT EXISTS notifications 
(
    notificationID INT AUTO_INCREMENT PRIMARY KEY,
    customerID INT DEFAULT NULL,
    branchID INT DEFAULT NULL,
    title VARCHAR(100),
    content TEXT,
    notificationType ENUM('General', 'Order-related') NOT NULL,
    relatedOrderID INT,
    dateSent DATETIME DEFAULT CURRENT_TIMESTAMP,
    notificationActive BOOLEAN DEFAULT TRUE,

    FOREIGN KEY(customerID) REFERENCES customers(customerID),
    FOREIGN KEY(relatedOrderID) REFERENCES orders(orderID)
);


CREATE TABLE IF NOT EXISTS payment
(
    paymentID INT auto_increment PRIMARY KEY NOT NULL,
    customerID INT NOT NULL,
    orderID INT NOT NULL,
    paymentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    paymentMethod ENUM('Cash', 'Credit Card', 'Debit Card', 'PayPal') DEFAULT 'Credit Card',
    paymentActive BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (customerID) REFERENCES customers(customerID),
    FOREIGN KEY (orderID) REFERENCES orders(orderID)
);


INSERT INTO users (userID, userRole, userName, userPassword) VALUES
-- password : Password 
('1','HQ_Admin','headAdmin','$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
('2','branch_Admin','branchAdminA','$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
('3','branch_Admin','branchAdminB','$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
('4','branch_Admin','branchAdminC','$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
('5','branch_Admin','branchAdminD','$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
('6','Customer','customer01','$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
('7','branch_Staff','AbranchStaffA','$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
-- BranchB staff
(8, 'branch_Staff', 'BbranchStaffA', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(9, 'branch_Staff', 'BbranchStaffB', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(10, 'branch_Staff', 'BbranchStaffC', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(11, 'branch_Staff', 'BbranchStaffD', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(12, 'branch_Staff', 'BbranchStaffE', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
-- BranchC staff
(13, 'branch_Staff', 'CbranchStaffA', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(14, 'branch_Staff', 'CbranchStaffB', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(15, 'branch_Staff', 'CbranchStaffC', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(16, 'branch_Staff', 'CbranchStaffD', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(17, 'branch_Staff', 'CbranchStaffE', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
-- BranchD staff
(18, 'branch_Staff', 'DbranchStaffA', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(19, 'branch_Staff', 'DbranchStaffB', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(20, 'branch_Staff', 'DbranchStaffC', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(21, 'branch_Staff', 'DbranchStaffD', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(22, 'branch_Staff', 'DbranchStaffE', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
-- BranchA staff
(23, 'branch_Staff', 'AbranchStaffB', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(24, 'branch_Staff', 'AbranchStaffC', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(25, 'branch_Staff', 'AbranchStaffD', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.'),
(26, 'branch_Staff', 'AbranchStaffE', '$2b$12$du3wTHLJ1ctJSdenpzWEuu3AJJwBL/CrHvW2lsbGgDKvDo6kVTe4.');



INSERT INTO admininfo (userID, title, position, firstName, lastName, phoneNumber) VALUES
('1', 'Mr', 'HQ_Admin', 'Head', 'Admin', '0228888888'),
('2', 'Mr', 'branch_Admin', 'BranchA', 'Admin', '0228888881'),
('3', 'Mr', 'branch_Admin', 'BranchB', 'Admin', '0228888882'),
('4', 'Mr', 'branch_Admin', 'BranchC', 'Admin', '0228888883'),
('5', 'Mr', 'branch_Admin', 'BranchD', 'Admin', '0228888885');

INSERT INTO branches (branchAdminID, branchName, city, address, phoneNumber, email, startTime, endTime) VALUES
('2', 'Flavorful Haven', 'Auckland', '1 Queen Street, Auckland', '0228888886', 'branchA@gmail.com', '11:00:00', '21:00:00'),
('3', 'Asian Fusion Delights', 'Christchurch', '1 High Street, Christchurch', '0228888889', 'branchB@gmail.com', '11:00:00', '21:00:00'),
('4', 'Taste Trails Asia', 'Wellington', '1 Willis Street, Wellington', '0228888890', 'branchC@gmail.com', '11:00:00', '21:00:00'),
('5', 'Culinary Voyage', 'Queenstown', '1 Lakeview Road, Queenstown', '0228888891', 'branchD@gmail.com', '11:00:00', '21:00:00');


INSERT INTO branchStaffs (branchID, userID, title, firstName, lastName, position, phoneNumber) VALUES
('1', '7', 'Mr', 'BranchA', 'Staff', 'branch_Staff', '0228888887'),
-- BranchB staff
(2, 8, 'Mr', 'StaffB', 'A', 'branch_Staff', '0228888892'),
(2, 9, 'Ms', 'StaffB', 'B', 'branch_Staff', '0228888893'),
(2, 10, 'Mr', 'StaffB', 'C', 'branch_Staff', '0228888894'),
(2, 11, 'Ms', 'StaffB', 'D', 'branch_Staff', '0228888895'),
(2, 12, 'Mr', 'StaffB', 'E', 'branch_Staff', '0228888896'),
-- BranchC staff
(3, 13, 'Mr', 'StaffC', 'A', 'branch_Staff', '0228888897'),
(3, 14, 'Ms', 'StaffC', 'B', 'branch_Staff', '0228888898'),
(3, 15, 'Mr', 'StaffC', 'C', 'branch_Staff', '0228888899'),
(3, 16, 'Ms', 'StaffC', 'D', 'branch_Staff', '0228888800'),
(3, 17, 'Mr', 'StaffC', 'E', 'branch_Staff', '0228888801'),
-- BranchD staff
(4, 18, 'Mr', 'StaffD', 'A', 'branch_Staff', '0228888802'),
(4, 19, 'Ms', 'StaffD', 'B', 'branch_Staff', '0228888803'),
(4, 20, 'Mr', 'StaffD', 'C', 'branch_Staff', '0228888804'),
(4, 21, 'Ms', 'StaffD', 'D', 'branch_Staff', '0228888805'),
(4, 22, 'Mr', 'StaffD', 'E', 'branch_Staff', '0228888806'),
-- BranchA staff
(1, 23, 'Ms', 'StaffA', 'B', 'branch_Staff', '0228888807'),
(1, 24, 'Mr', 'StaffA', 'C', 'branch_Staff', '0228888808'),
(1, 25, 'Ms', 'StaffA', 'D', 'branch_Staff', '0228888809'),
(1, 26, 'Mr', 'StaffA', 'E', 'branch_Staff', '0228888810');

INSERT INTO customers (userID, title, firstName, lastName, email, phoneNumber, Address, dateOfBirth, Preferences) VALUES
('6', 'Mr', 'John', 'Smith', 'customer@gmail.com', '0228888886', '1 Queen Street, Auckland', '1990-01-01', 'I like to eat meat.');


INSERT INTO pizzas (pizzaName, description, size, price, preparetime) VALUES
('Teriyaki Chicken', 'Tender chicken with teriyaki sauce and mozzarella cheese', 'Small', 10.99, 10),
('Teriyaki Chicken', 'Tender chicken with teriyaki sauce and mozzarella cheese', 'Medium', 12.99, 15),
('Teriyaki Chicken', 'Tender chicken with teriyaki sauce and mozzarella cheese', 'Large', 14.99, 20),

('Spicy Tuna', 'Tuna mixed with spicy mayo, topped with green onions', 'Small', 11.99, 10),
('Spicy Tuna', 'Tuna mixed with spicy mayo, topped with green onions', 'Medium', 14.99, 15),
('Spicy Tuna', 'Tuna mixed with spicy mayo, topped with green onions', 'Large', 16.99, 20),

('Peking Duck', 'Roasted duck slices with hoisin sauce and green onions', 'Small', 11.99, 10),
('Peking Duck', 'Roasted duck slices with hoisin sauce and green onions', 'Medium', 13.99, 15),
('Peking Duck', 'Roasted duck slices with hoisin sauce and green onions', 'Large', 16.99, 20),

('Thai Basil Veggie', 'Fresh veggies with Thai basil pesto sauce', 'Small', 8.99, 10),
('Thai Basil Veggie', 'Fresh veggies with Thai basil pesto sauce', 'Medium', 10.99, 15),
('Thai Basil Veggie', 'Fresh veggies with Thai basil pesto sauce', 'Large', 12.99, 20),

('Kimchi Beef', 'Spicy kimchi with seasoned beef and mozzarella cheese', 'Small', 10.99, 10),
('Kimchi Beef', 'Spicy kimchi with seasoned beef and mozzarella cheese', 'Medium', 13.99, 15),
('Kimchi Beef', 'Spicy kimchi with seasoned beef and mozzarella cheese', 'Large', 15.99, 20),

('Banh Mi Pork', 'Slices of Vietnamese-style pork with pickled veggies', 'Small', 11.99, 10),
('Banh Mi Pork', 'Slices of Vietnamese-style pork with pickled veggies', 'Medium', 13.99, 15),
('Banh Mi Pork', 'Slices of Vietnamese-style pork with pickled veggies', 'Large', 15.99, 20),

('Miso Mushroom', 'Mushrooms sautéed in miso butter with mozzarella cheese', 'Small', 9.99, 10),
('Miso Mushroom', 'Mushrooms sautéed in miso butter with mozzarella cheese', 'Medium', 12.99, 15),
('Miso Mushroom', 'Mushrooms sautéed in miso butter with mozzarella cheese', 'Large', 14.99, 20),

('Sweet and Sour Pork', 'Pork with sweet and sour sauce, pineapples, and bell peppers', 'Small', 10.99, 10),
('Sweet and Sour Pork', 'Pork with sweet and sour sauce, pineapples, and bell peppers', 'Medium', 13.99, 15),
('Sweet and Sour Pork', 'Pork with sweet and sour sauce, pineapples, and bell peppers', 'Large', 15.99, 20),

('Curry Chicken', 'Chicken pieces in a rich curry sauce with cheese', 'Small', 10.99, 10),
('Curry Chicken', 'Chicken pieces in a rich curry sauce with cheese', 'Medium', 12.99, 15),
('Curry Chicken', 'Chicken pieces in a rich curry sauce with cheese', 'Large', 15.99, 20),

('Szechuan Veggie', 'Mixed veggies with Szechuan pepper sauce and mozzarella cheese', 'Small', 8.99, 10),
('Szechuan Veggie', 'Mixed veggies with Szechuan pepper sauce and mozzarella cheese', 'Medium', 10.99, 15),
('Szechuan Veggie', 'Mixed veggies with Szechuan pepper sauce and mozzarella cheese', 'Large', 12.99, 20);

-- For branchID 1
INSERT INTO pizzas (pizzaName, description, size, price, branchID, preparetime) VALUES
('Bamboo Shoot Delight', 'Fresh bamboo shoots with tangy sauce, green peppers, and mozzarella cheese', 'Small', 11.99, 1, 10),
('Bamboo Shoot Delight', 'Fresh bamboo shoots with tangy sauce, green peppers, and mozzarella cheese', 'Medium', 14.99, 1, 12),
('Bamboo Shoot Delight', 'Fresh bamboo shoots with tangy sauce, green peppers, and mozzarella cheese', 'Large', 17.99, 1, 15),
('Oriental Tofu Feast', 'Tofu cubes with sesame oil, cherry tomatoes, and a hint of chili', 'Small', 10.99, 1, 10),
('Oriental Tofu Feast', 'Tofu cubes with sesame oil, cherry tomatoes, and a hint of chili', 'Medium', 13.99, 1, 12),
('Oriental Tofu Feast', 'Tofu cubes with sesame oil, cherry tomatoes, and a hint of chili', 'Large', 16.99, 1, 15),
('Prawn Dragon', 'Juicy prawns with dragon fruit slices and zesty lime dressing', 'Small', 13.99, 1, 10),
('Prawn Dragon', 'Juicy prawns with dragon fruit slices and zesty lime dressing', 'Medium', 16.99, 1, 12),
('Prawn Dragon', 'Juicy prawns with dragon fruit slices and zesty lime dressing', 'Large', 19.99, 1, 15);

-- For branchID 2
INSERT INTO pizzas (pizzaName, description, size, price, branchID, preparetime) VALUES
('Mango Chicken Fusion', 'Tender chicken pieces with mango slices and a hint of mint', 'Small', 11.99, 2, 10),
('Mango Chicken Fusion', 'Tender chicken pieces with mango slices and a hint of mint', 'Medium', 14.99, 2, 12),
('Mango Chicken Fusion', 'Tender chicken pieces with mango slices and a hint of mint', 'Large', 17.99, 2, 15),
('Lotus Veggie Crunch', 'Lotus stem with a mix of veggies in a tangy sauce', 'Small', 9.99, 2, 10),
('Lotus Veggie Crunch', 'Lotus stem with a mix of veggies in a tangy sauce', 'Medium', 12.99, 2, 12),
('Lotus Veggie Crunch', 'Lotus stem with a mix of veggies in a tangy sauce', 'Large', 15.99, 2, 15),
('Beef Rendang Bliss', 'Indonesian-style beef rendang with cheese', 'Small', 12.99, 2, 10),
('Beef Rendang Bliss', 'Indonesian-style beef rendang with cheese', 'Medium', 15.99, 2, 12),
('Beef Rendang Bliss', 'Indonesian-style beef rendang with cheese', 'Large', 18.99, 2, 15);

-- For branchID 3
INSERT INTO pizzas (pizzaName, description, size, price, branchID, preparetime) VALUES
('Pineapple Pork Punch', 'Pork slices with pineapple chunks in a spicy sauce', 'Small', 11.99, 3, 10),
('Pineapple Pork Punch', 'Pork slices with pineapple chunks in a spicy sauce', 'Medium', 14.99, 3, 12),
('Pineapple Pork Punch', 'Pork slices with pineapple chunks in a spicy sauce', 'Large', 17.99, 3, 15),
('Eggplant Emperor', 'Roasted eggplant with mozzarella and a hint of garlic', 'Small', 9.99, 3, 10),
('Eggplant Emperor', 'Roasted eggplant with mozzarella and a hint of garlic', 'Medium', 12.99, 3, 12),
('Eggplant Emperor', 'Roasted eggplant with mozzarella and a hint of garlic', 'Large', 15.99, 3, 15),
('Fiery Fish Fiesta', 'Fish slices with hot chilies and mozzarella cheese', 'Small', 12.99, 3, 10),
('Fiery Fish Fiesta', 'Fish slices with hot chilies and mozzarella cheese', 'Medium', 15.99, 3, 12),
('Fiery Fish Fiesta', 'Fish slices with hot chilies and mozzarella cheese', 'Large', 18.99, 3, 15);

-- For branchID 4
INSERT INTO pizzas (pizzaName, description, size, price, branchID, preparetime) VALUES
('Lamb Lush', 'Juicy lamb pieces with rosemary and thyme', 'Small', 11.99, 4, 10),
('Lamb Lush', 'Juicy lamb pieces with rosemary and thyme', 'Medium', 14.99, 4, 12),
('Lamb Lush', 'Juicy lamb pieces with rosemary and thyme', 'Large', 17.99, 4, 15),
('Cherry Tomato Tingle', 'Cherry tomatoes with feta cheese and olives', 'Small', 9.99, 4, 10),
('Cherry Tomato Tingle', 'Cherry tomatoes with feta cheese and olives', 'Medium', 12.99, 4, 12),
('Cherry Tomato Tingle', 'Cherry tomatoes with feta cheese and olives', 'Large', 15.99, 4, 15),
('Ocean Octopus', 'Octopus slices with a tangy marinara sauce', 'Small', 12.99, 4, 10),
('Ocean Octopus', 'Octopus slices with a tangy marinara sauce', 'Medium', 15.99, 4, 12),
('Ocean Octopus', 'Octopus slices with a tangy marinara sauce', 'Large', 18.99, 4, 15);


INSERT INTO sideOfferings (offeringName, description, price, preparetime) VALUES
('Spring Roll', 'Crispy spring rolls filled with veggies', 5.99, 10),
('Edamame', 'Steamed edamame beans with sea salt', 4.99, 5),
('Garlic Knots', 'Knots of bread topped with garlic butter', 3.99, 8),
('Kimchi Salad', 'Spicy kimchi mixed with fresh lettuce', 6.99, 5),
('Tempura Veggies', 'Mixed veggies fried in tempura batter', 7.99, 12),
('Asian Bruschetta', 'Crispy bread with Thai basil, tomatoes, and onions', 6.99, 10),
('Sesame Wings', 'Chicken wings tossed in a sesame sauce', 8.99, 15),
('Tofu Bites', 'Deep-fried tofu pieces with a dipping sauce', 6.99, 10),
('Yuzu Caesar Salad', 'Traditional Caesar salad with a touch of yuzu citrus', 7.99, 5),
('Spicy Mayo Fries', 'Crispy fries served with spicy mayo', 5.99, 12);

-- For branchID 1
INSERT INTO sideOfferings (offeringName, description, price, branchID, preparetime) VALUES
('Chili Lime Prawn Skewers', 'Juicy prawns skewered and drizzled with chili lime sauce', 9.99, 1, 12),
('Bamboo Shoots Salad', 'Crunchy bamboo shoots mixed with fresh veggies in a tangy dressing', 6.99, 1, 10),
('Prawn Crackers', 'Crispy prawn-flavored crackers served with sweet chili dip', 4.99, 1, 8),
('Sweet Corn Soup', 'Creamy soup made with sweet corn and chicken pieces', 5.99, 1, 10),
('Lettuce Cups', 'Minced chicken served in lettuce cups with hoisin sauce', 7.99, 1, 15);

-- For branchID 2
INSERT INTO sideOfferings (offeringName, description, price, branchID, preparetime) VALUES
('Szechuan Peppercorn Wings', 'Wings tossed in a spicy Szechuan peppercorn sauce', 9.99, 2, 15),
('Asian Guacamole', 'Creamy guacamole with a hint of wasabi and soy sauce', 5.99, 2, 8),
('Nori Wrapped Tempura', 'Mixed veggies wrapped in nori and fried in tempura batter', 8.99, 2, 12),
('Wasabi Peas', 'Crunchy peas coated with spicy wasabi', 4.99, 2, 5),
('Miso Soup', 'Traditional miso soup with tofu and seaweed', 5.99, 2, 10);

-- For branchID 3
INSERT INTO sideOfferings (offeringName, description, price, branchID, preparetime) VALUES
('Lotus Chips', 'Thinly sliced lotus stem fried to perfection', 6.99, 3, 10),
('Dragon Fruit Salad', 'Refreshing salad made with dragon fruit and cucumber', 7.99, 3, 10),
('Red Curry Hummus', 'Creamy hummus flavored with Thai red curry paste', 5.99, 3, 8),
('Bao Buns', 'Fluffy buns filled with BBQ pork', 8.99, 3, 12),
('Crispy Calamari', 'Deep-fried calamari rings served with a tangy dip', 9.99, 3, 12);

-- For branchID 4
INSERT INTO sideOfferings (offeringName, description, price, branchID, preparetime) VALUES
('Jasmine Rice Pilaf', 'Jasmine rice cooked with veggies and mild spices', 5.99, 4, 10),
('Mango Sticky Rice', 'Sweet sticky rice topped with fresh mango slices and drizzled with coconut sauce', 7.99, 4, 12),
('Thai Spring Roll', 'Delicate spring rolls filled with glass noodles and veggies', 6.99, 4, 10),
('Chili Tofu', 'Soft tofu pieces stir-fried in a spicy chili sauce', 7.99, 4, 12),
('Dim Sum Platter', 'An assortment of steamed dim sums', 9.99, 4, 15);


INSERT INTO drinks (drinkName, description, price, preparetime) VALUES
('Coca-Cola', 'Classic carbonated soft drink', 2.49, 1),
('Sprite', 'Lemon-lime flavored soft drink', 2.49, 1),
('Pepsi', 'Popular carbonated cola drink', 2.49, 1),
('Diet Coke', 'Low-calorie version of classic Coca-Cola', 2.49, 1),
('Mountain Dew', 'Citrus-flavored carbonated soft drink', 2.49, 1),
('Dr Pepper', 'Unique blend of 23 flavors in a soft drink', 2.49, 1),
('Orange Juice', 'Freshly squeezed orange juice', 2.99, 1),
('Apple Juice', 'Sweet apple juice made from fresh apples', 2.99, 1),
('Water Bottle', 'Purified drinking water', 1.49, 1),
('Green Tea Bottle', 'Bottled green tea beverage', 2.99, 1);


INSERT INTO toppings (toppingName, description, price) VALUES
('Mozzarella Cheese', 'Creamy and soft mozzarella cheese', 1.50),
('Pepperoni', 'Sliced spicy pepperoni', 1.70),
('Vegetables', 'Mixed fresh vegetables', 1.30),
('Meat', 'Assorted meat chunks', 1.90),
('Olives', 'Sliced black olives', 1.20);

INSERT INTO orders VALUES 
(1,1,1,'1 Queen Street, Auckland ','Paid',35.44,'2022-11-11 03:49:15','Pick Up','2022-11-11 04:19:00',NULL,NULL,'',1,'[{\"id\": 136, \"name\": \"Prawn Dragon\", \"size\": {\"label\": \"Large\", \"price\": 19.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 2, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Juicy prawns with dragon fruit slices and zesty lime dressing\", \"toppingPrice\": 3}, {\"id\": 304, \"name\": \"Mountain Dew\", \"price\": 2.49, \"number\": 1, \"description\": \"Citrus-flavored carbonated soft drink\", \"toppingPrice\": 0}, {\"id\": 303, \"name\": \"Diet Coke\", \"price\": 2.49, \"number\": 1, \"description\": \"Low-calorie version of classic Coca-Cola\", \"toppingPrice\": 0}, {\"id\": 305, \"name\": \"Dr Pepper\", \"price\": 2.49, \"number\": 3, \"description\": \"Unique blend of 23 flavors in a soft drink\", \"toppingPrice\": 0}]'),
(2,1,1,'1 Queen Street, Auckland ','Paid',33.37,'2023-10-01 03:49:34','Pick Up','2023-10-11 04:19:00',NULL,NULL,'',1,'[{\"id\": 211, \"name\": \"Bamboo Shoots Salad\", \"price\": 6.99, \"number\": 1, \"description\": \"Crunchy bamboo shoots mixed with fresh veggies in a tangy dressing\", \"toppingPrice\": 0}, {\"id\": 214, \"name\": \"Lettuce Cups\", \"price\": 7.99, \"number\": 1, \"description\": \"Minced chicken served in lettuce cups with hoisin sauce\", \"toppingPrice\": 0}, {\"id\": 112, \"name\": \"Kimchi Beef\", \"size\": {\"label\": \"Medium\", \"price\": 13.99, \"value\": \"medium\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 1, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 1, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 1, \"description\": \"Sliced black olives\"}], \"description\": \"Spicy kimchi with seasoned beef and mozzarella cheese\", \"toppingPrice\": 4.4}]'),
(3,1,2,'1 Queen Street, Auckland ','Paid',29.96,'2022-11-11 03:51:39','Pick Up','2022-11-11 04:21:00',NULL,NULL,'',1,'[{\"id\": 206, \"name\": \"Sesame Wings\", \"price\": 8.99, \"number\": 1, \"description\": \"Chicken wings tossed in a sesame sauce\", \"toppingPrice\": 0}, {\"id\": 207, \"name\": \"Tofu Bites\", \"price\": 6.99, \"number\": 1, \"description\": \"Deep-fried tofu pieces with a dipping sauce\", \"toppingPrice\": 0}, {\"id\": 208, \"name\": \"Yuzu Caesar Salad\", \"price\": 7.99, \"number\": 1, \"description\": \"Traditional Caesar salad with a touch of yuzu citrus\", \"toppingPrice\": 0}, {\"id\": 209, \"name\": \"Spicy Mayo Fries\", \"price\": 5.99, \"number\": 1, \"description\": \"Crispy fries served with spicy mayo\", \"toppingPrice\": 0}]'),
(4,1,2,'1 Queen Street, Auckland ','Paid',38.96,'2023-10-01 03:51:59','Pick Up','2023-10-11 04:21:00',NULL,NULL,'',1,'[{\"id\": 103, \"name\": \"Spicy Tuna\", \"size\": {\"label\": \"Large\", \"price\": 16.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Tuna mixed with spicy mayo, topped with green onions\", \"toppingPrice\": 0}, {\"id\": 121, \"name\": \"Sweet and Sour Pork\", \"size\": {\"label\": \"Large\", \"price\": 15.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Pork with sweet and sour sauce, pineapples, and bell peppers\", \"toppingPrice\": 0}, {\"id\": 307, \"name\": \"Apple Juice\", \"price\": 2.99, \"number\": 1, \"description\": \"Sweet apple juice made from fresh apples\", \"toppingPrice\": 0}, {\"id\": 306, \"name\": \"Orange Juice\", \"price\": 2.99, \"number\": 1, \"description\": \"Freshly squeezed orange juice\", \"toppingPrice\": 0}]'),
(5,1,3,'1 Queen Street, Auckland ','Paid',42.66,'2022-11-11 03:52:25','Pick Up','2022-11-11 04:22:00',NULL,NULL,'',1,'[{\"id\": 121, \"name\": \"Sweet and Sour Pork\", \"size\": {\"label\": \"Large\", \"price\": 15.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 1, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 1, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Pork with sweet and sour sauce, pineapples, and bell peppers\", \"toppingPrice\": 3.2}, {\"id\": 148, \"name\": \"Pineapple Pork Punch\", \"size\": {\"label\": \"Large\", \"price\": 17.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Pork slices with pineapple chunks in a spicy sauce\", \"toppingPrice\": 0}, {\"id\": 307, \"name\": \"Apple Juice\", \"price\": 2.99, \"number\": 1, \"description\": \"Sweet apple juice made from fresh apples\", \"toppingPrice\": 0}, {\"id\": 304, \"name\": \"Mountain Dew\", \"price\": 2.49, \"number\": 1, \"description\": \"Citrus-flavored carbonated soft drink\", \"toppingPrice\": 0}]'),
(6,1,3,'1 Queen Street, Auckland ','Paid',27.96,'2023-10-01 03:52:39','Pick Up','2023-10-01 04:22:00',NULL,NULL,'',1,'[{\"id\": 127, \"name\": \"Szechuan Veggie\", \"size\": {\"label\": \"Small\", \"price\": 8.99, \"value\": \"small\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Mixed veggies with Szechuan pepper sauce and mozzarella cheese\", \"toppingPrice\": 0}, {\"id\": 201, \"name\": \"Edamame\", \"price\": 4.99, \"number\": 1, \"description\": \"Steamed edamame beans with sea salt\", \"toppingPrice\": 0}, {\"id\": 203, \"name\": \"Kimchi Salad\", \"price\": 6.99, \"number\": 1, \"description\": \"Spicy kimchi mixed with fresh lettuce\", \"toppingPrice\": 0}, {\"id\": 205, \"name\": \"Asian Bruschetta\", \"price\": 6.99, \"number\": 1, \"description\": \"Crispy bread with Thai basil, tomatoes, and onions\", \"toppingPrice\": 0}]'),
(7,1,3,'1 Queen Street, Auckland ','Paid',19.96,'2023-10-11 03:53:28','Pick Up','2023-10-11 04:23:00',NULL,NULL,'',1,'[{\"id\": 301, \"name\": \"Sprite\", \"price\": 2.49, \"number\": 1, \"description\": \"Lemon-lime flavored soft drink\", \"toppingPrice\": 0}, {\"id\": 300, \"name\": \"Coca-Cola\", \"price\": 2.49, \"number\": 1, \"description\": \"Classic carbonated soft drink\", \"toppingPrice\": 0}, {\"id\": 204, \"name\": \"Tempura Veggies\", \"price\": 7.99, \"number\": 1, \"description\": \"Mixed veggies fried in tempura batter\", \"toppingPrice\": 0}, {\"id\": 203, \"name\": \"Kimchi Salad\", \"price\": 6.99, \"number\": 1, \"description\": \"Spicy kimchi mixed with fresh lettuce\", \"toppingPrice\": 0}]'),
(8,1,1,'1 Queen Street, Auckland ','Paid',22.96,'2023-10-11 03:53:52','Pick Up','2023-10-11 04:23:00',NULL,NULL,'',1,'[{\"id\": 304, \"name\": \"Mountain Dew\", \"price\": 2.49, \"number\": 1, \"description\": \"Citrus-flavored carbonated soft drink\", \"toppingPrice\": 0}, {\"id\": 301, \"name\": \"Sprite\", \"price\": 2.49, \"number\": 1, \"description\": \"Lemon-lime flavored soft drink\", \"toppingPrice\": 0}, {\"id\": 210, \"name\": \"Chili Lime Prawn Skewers\", \"price\": 9.99, \"number\": 1, \"description\": \"Juicy prawns skewered and drizzled with chili lime sauce\", \"toppingPrice\": 0}, {\"id\": 204, \"name\": \"Tempura Veggies\", \"price\": 7.99, \"number\": 1, \"description\": \"Mixed veggies fried in tempura batter\", \"toppingPrice\": 0}]'),
(9,1,2,'1 Queen Street, Auckland ','Paid',29.98,'2023-10-11 03:54:03','Pick Up','2023-10-11 04:24:00',NULL,NULL,'',1,'[{\"id\": 103, \"name\": \"Spicy Tuna\", \"size\": {\"label\": \"Large\", \"price\": 16.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Tuna mixed with spicy mayo, topped with green onions\", \"toppingPrice\": 0}, {\"id\": 127, \"name\": \"Szechuan Veggie\", \"size\": {\"label\": \"Large\", \"price\": 12.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Mixed veggies with Szechuan pepper sauce and mozzarella cheese\", \"toppingPrice\": 0}]'),
(10,1,4,'1 Queen Street, Auckland ','Paid',49.27,'2022-12-11 03:54:25','Pick Up','2022-12-11 04:24:00',NULL,NULL,'',1,'[{\"id\": 103, \"name\": \"Spicy Tuna\", \"size\": {\"label\": \"Large\", \"price\": 16.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Tuna mixed with spicy mayo, topped with green onions\", \"toppingPrice\": 0}, {\"id\": 106, \"name\": \"Peking Duck\", \"size\": {\"label\": \"Small\", \"price\": 11.99, \"value\": \"small\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 1, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Roasted duck slices with hoisin sauce and green onions\", \"toppingPrice\": 1.3}, {\"id\": 163, \"name\": \"Ocean Octopus\", \"size\": {\"label\": \"Large\", \"price\": 18.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Octopus slices with a tangy marinara sauce\", \"toppingPrice\": 0}]'),
(11,1,4,'1 Queen Street, Auckland ','Paid',37.97,'2023-10-01 03:54:36','Pick Up','2023-10-01 04:24:00',NULL,NULL,'',1,'[{\"id\": 121, \"name\": \"Sweet and Sour Pork\", \"size\": {\"label\": \"Large\", \"price\": 15.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Pork with sweet and sour sauce, pineapples, and bell peppers\", \"toppingPrice\": 0}, {\"id\": 118, \"name\": \"Miso Mushroom\", \"size\": {\"label\": \"Large\", \"price\": 14.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Mushrooms sautéed in miso butter with mozzarella cheese\", \"toppingPrice\": 0}, {\"id\": 227, \"name\": \"Thai Spring Roll\", \"price\": 6.99, \"number\": 1, \"description\": \"Delicate spring rolls filled with glass noodles and veggies\", \"toppingPrice\": 0}]'),
(12,1,4,'1 Queen Street, Auckland ','Paid',39.96,'2023-10-11 03:54:50','Pick Up','2023-10-11 04:24:00',NULL,NULL,'',1,'[{\"id\": 127, \"name\": \"Szechuan Veggie\", \"size\": {\"label\": \"Large\", \"price\": 12.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Mixed veggies with Szechuan pepper sauce and mozzarella cheese\", \"toppingPrice\": 0}, {\"id\": 121, \"name\": \"Sweet and Sour Pork\", \"size\": {\"label\": \"Large\", \"price\": 15.99, \"value\": \"large\"}, \"number\": 1, \"toppings\": [{\"name\": \"Mozzarella Cheese\", \"price\": 1.5, \"quantity\": 0, \"description\": \"Creamy and soft mozzarella cheese\"}, {\"name\": \"Pepperoni\", \"price\": 1.7, \"quantity\": 0, \"description\": \"Sliced spicy pepperoni\"}, {\"name\": \"Vegetables\", \"price\": 1.3, \"quantity\": 0, \"description\": \"Mixed fresh vegetables\"}, {\"name\": \"Meat\", \"price\": 1.9, \"quantity\": 0, \"description\": \"Assorted meat chunks\"}, {\"name\": \"Olives\", \"price\": 1.2, \"quantity\": 0, \"description\": \"Sliced black olives\"}], \"description\": \"Pork with sweet and sour sauce, pineapples, and bell peppers\", \"toppingPrice\": 0}, {\"id\": 201, \"name\": \"Edamame\", \"price\": 4.99, \"number\": 1, \"description\": \"Steamed edamame beans with sea salt\", \"toppingPrice\": 0}, {\"id\": 200, \"name\": \"Spring Roll\", \"price\": 5.99, \"number\": 1, \"description\": \"Crispy spring rolls filled with veggies\", \"toppingPrice\": 0}]');

INSERT INTO payment VALUES 
(1,1,1,'2023-10-12 03:49:15','PayPal',1),
(2,1,2,'2023-10-12 03:49:34','PayPal',1),
(3,1,3,'2023-10-12 03:51:38','PayPal',1),
(4,1,4,'2023-10-12 03:51:59','PayPal',1),
(5,1,5,'2023-10-12 03:52:24','PayPal',1),
(6,1,6,'2023-10-12 03:52:39','PayPal',1),
(7,1,7,'2023-10-12 03:53:27','PayPal',1),
(8,1,8,'2023-10-12 03:53:52','PayPal',1),
(9,1,9,'2023-10-12 03:54:02','PayPal',1),
(10,1,10,'2023-10-12 03:54:24','PayPal',1),
(11,1,11,'2023-10-12 03:54:36','PayPal',1),
(12,1,12,'2023-10-12 03:54:50','PayPal',1);


INSERT INTO orderdetails VALUES (1,1,136,'Pizza',19.99,1,1),(2,1,304,'Drink',2.49,1,1),(3,1,303,'Drink',2.49,1,1),
(4,1,305,'Drink',2.49,3,1),(5,2,211,'SideOffering',6.99,1,1),(6,2,214,'SideOffering',7.99,1,1),
(7,2,112,'Pizza',13.99,1,1),(8,3,206,'SideOffering',8.99,1,1),(9,3,207,'SideOffering',6.99,1,1),
(10,3,208,'SideOffering',7.99,1,1),(11,3,209,'SideOffering',5.99,1,1),(12,4,103,'Pizza',16.99,1,1),
(13,4,121,'Pizza',15.99,1,1),(14,4,307,'Drink',2.99,1,1),(15,4,306,'Drink',2.99,1,1),(16,5,121,'Pizza',15.99,1,1),
(17,5,148,'Pizza',17.99,1,1),(18,5,307,'Drink',2.99,1,1),(19,5,304,'Drink',2.49,1,1),(20,6,127,'Pizza',8.99,1,1),
(21,6,201,'SideOffering',4.99,1,1),(22,6,203,'SideOffering',6.99,1,1),(23,6,205,'SideOffering',6.99,1,1),
(24,7,301,'Drink',2.49,1,1),(25,7,300,'Drink',2.49,1,1),(26,7,204,'SideOffering',7.99,1,1),
(27,7,203,'SideOffering',6.99,1,1),(28,8,304,'Drink',2.49,1,1),(29,8,301,'Drink',2.49,1,1),
(30,8,210,'SideOffering',9.99,1,1),(31,8,204,'SideOffering',7.99,1,1),(32,9,103,'Pizza',16.99,1,1),
(33,9,127,'Pizza',12.99,1,1),(34,10,103,'Pizza',16.99,1,1),(35,10,106,'Pizza',11.99,1,1),(36,10,163,'Pizza',18.99,1,1),
(37,11,121,'Pizza',15.99,1,1),(38,11,118,'Pizza',14.99,1,1),(39,11,227,'SideOffering',6.99,1,1),
(40,12,127,'Pizza',12.99,1,1),(41,12,121,'Pizza',15.99,1,1),(42,12,201,'SideOffering',4.99,1,1),
(43,12,200,'SideOffering',5.99,1,1);

INSERT INTO orderdetails_toppings VALUES 
(1,400,1),(7,402,1),(7,403,1),(7,404,1),(16,402,1),(16,403,1),(35,402,1);

INSERT INTO notifications VALUES 
(1,1,1,'Order received!','Your order #1 has been received!','Order-related',1,'2023-10-12 16:49:15',1),
(2,1,1,'Order received!','Your order #2 has been received!','Order-related',2,'2023-10-12 16:49:34',1),
(3,1,2,'Order received!','Your order #3 has been received!','Order-related',3,'2023-10-12 16:51:38',1),
(4,1,2,'Order received!','Your order #4 has been received!','Order-related',4,'2023-10-12 16:51:59',1),
(5,1,3,'Order received!','Your order #5 has been received!','Order-related',5,'2023-10-12 16:52:24',1),
(6,1,3,'Order received!','Your order #6 has been received!','Order-related',6,'2023-10-12 16:52:39',1),
(7,1,3,'Order received!','Your order #7 has been received!','Order-related',7,'2023-10-12 16:53:27',1),
(8,1,1,'Order received!','Your order #8 has been received!','Order-related',8,'2023-10-12 16:53:52',1),
(9,1,2,'Order received!','Your order #9 has been received!','Order-related',9,'2023-10-12 16:54:02',1),
(10,1,4,'Order received!','Your order #10 has been received!','Order-related',10,'2023-10-12 16:54:24',1),
(11,1,4,'Order received!','Your order #11 has been received!','Order-related',11,'2023-10-12 16:54:36',1),
(12,1,4,'Order received!','Your order #12 has been received!','Order-related',12,'2023-10-12 16:54:50',1);

INSERT INTO `simplepromotions` VALUES 
(1,'fullReduction',1,'Get a 10% discount on purchases over $50','2023-10-30','2024-10-01',50.00,0.90,'',1),
(2,'Code',NULL,'Enjoy a 10% discount when you spend over $50','2023-10-30','2024-05-01',50.00,0.90,'promo123',1),
(3,'fullReduction',2,'Get a 15% discount on purchases over $40','2023-10-30','2024-09-01',40.00,0.85,'',1),
(4,'Code',2,'Get a 10% discount on purchases over $50','2023-10-30','2024-05-01',50.00,0.90,'promo1',1),
(5,'Code',2,'Get a 20% discount on purchases over $100','2023-10-30','2024-09-01',100.00,0.80,'promo2',1),
(6,'Code',1,'Get a 10% discount on purchases over $50','2023-10-30','2024-05-01',50.00,0.90,'promoa1',1),
(7,'Code',1,'Get a 15% discount on purchases over $100','2023-10-30','2024-05-02',100.00,0.85,'promoa2',1),
(8,'fullReduction',3,'Get a 15% discount on purchases over $50','2023-10-30','2024-05-01',50.00,0.85,'',1),
(9,'Code',3,'Get a 10% discount on purchases over $50','2023-10-31','2024-01-01',50.00,0.90,'promoc1',1),
(10,'Code',3,'Get a 20% discount on purchases over $100','2023-10-30','2024-05-01',100.00,0.80,'promoc2',1),
(11,'Code',4,'Get a 10% discount on purchases over $50','2023-10-31','2024-05-01',50.00,0.90,'promod1',1),
(12,'Code',4,'Get a 20% discount on purchases over $100','2023-11-01','2024-05-01',100.00,0.80,'promod2',1),
(13,'fullReduction',4,'Get a 10% discount on purchases over $50','2023-11-01','2024-01-01',50.00,0.90,'',1),
(14,'Code',NULL,'Get a 20% discount on purchases over $100','2023-11-01','2024-01-01',100.00,0.80,'promon1',1);