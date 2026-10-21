CREATE DATABASE IF NOT EXISTS hotel_system_db CHARACTER SET utf8mb4;
USE hotel_system_db;

CREATE TABLE Guest (
  Guest_ID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(100) NOT NULL,
  Email VARCHAR(100) NOT NULL UNIQUE,
  Phone VARCHAR(20) NOT NULL,
  Password_Hash VARCHAR(255) NOT NULL,
  SSN VARCHAR(20) UNIQUE,
  Guest_Type ENUM('New','Return') NOT NULL DEFAULT 'New'
);

CREATE TABLE Admin (
  Admin_ID INT AUTO_INCREMENT PRIMARY KEY,
  Admin_Name VARCHAR(100) NOT NULL UNIQUE,
  Password_Hash VARCHAR(255) NOT NULL
);

CREATE TABLE Room (
  Room_ID INT AUTO_INCREMENT PRIMARY KEY,
  Room_Number VARCHAR(10) NOT NULL UNIQUE,
  Room_Type ENUM('Standard','Suite') NOT NULL,
  Price_Night DECIMAL(10,2) NOT NULL,
  Status ENUM('Available','Booked','Maintenance') NOT NULL DEFAULT 'Available'
);

CREATE TABLE Booking (
  Booking_ID INT AUTO_INCREMENT PRIMARY KEY,
  Guest_ID INT NOT NULL,
  Room_ID INT NOT NULL,
  Check_In DATE NOT NULL,
  Check_Out DATE NOT NULL,
  Total_Amount DECIMAL(10,2) NOT NULL DEFAULT 0,
  Booking_Status ENUM('Pending','Confirmed','Cancelled') NOT NULL DEFAULT 'Pending',
  Confirmed_By INT NULL,
  FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID),
  FOREIGN KEY (Room_ID) REFERENCES Room(Room_ID),
  FOREIGN KEY (Confirmed_By) REFERENCES Admin(Admin_ID)
);

CREATE TABLE Payment (
  Payment_ID INT AUTO_INCREMENT PRIMARY KEY,
  Booking_ID INT NOT NULL UNIQUE,
  Amount DECIMAL(10,2) NOT NULL,
  Payment_Method ENUM('Credit Card','Cash') NOT NULL,
  Card_Last4 CHAR(4) NULL,
  Payment_Status ENUM('Pending','Paid','Rejected') NOT NULL DEFAULT 'Pending',
  Payment_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID) ON DELETE CASCADE
);

INSERT INTO Room (Room_Number, Room_Type, Price_Night) VALUES
('101','Standard',50),('102','Standard',50),('201','Suite',120);
