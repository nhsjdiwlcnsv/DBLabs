DROP TABLE IF EXISTS bill;
DROP TABLE IF EXISTS announcement;
DROP TABLE IF EXISTS appointment;
DROP TABLE IF EXISTS appointment_type;
DROP TABLE IF EXISTS action;
DROP TABLE IF EXISTS action_type;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS staff_status;
DROP TABLE IF EXISTS health_card;
DROP TABLE IF EXISTS patient;
DROP TABLE IF EXISTS room;
DROP TABLE IF EXISTS building;
DROP TABLE IF EXISTS blood;
DROP TABLE IF EXISTS blood_type;



CREATE TABLE building
(
    building_id smallint PRIMARY KEY,
    address text NOT NULL,
    name varchar(64)
);

CREATE TABLE room
(
    room_id smallint PRIMARY KEY,
    building integer NOT NULL DEFAULT 0,

    CONSTRAINT fk_building_id FOREIGN KEY (building) REFERENCES building(building_id) ON DELETE SET DEFAULT
);

CREATE TABLE blood_type
(
    name varchar(3) PRIMARY KEY

    CONSTRAINT valid_name CHECK ( name in ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') )
);

CREATE TABLE blood
(
    blood_id smallint PRIMARY KEY,
    type varchar(3) NOT NULL DEFAULT 'Unspecified',
    contaminated boolean NOT NULL,

    CONSTRAINT fk_blood_type FOREIGN KEY (type) REFERENCES blood_type(name) ON DELETE SET DEFAULT
);

CREATE TABLE staff_status
(
    name varchar(8) PRIMARY KEY

    CONSTRAINT valid_name CHECK ( name in ('Admin', 'Doctor') )
);

CREATE TABLE staff
(
    staff_id integer PRIMARY KEY,
    email varchar(64) UNIQUE,
    password varchar(32) NOT NULL UNIQUE,
    first_name varchar(64) NOT NULL,
    last_name varchar(64) NOT NULL,
    phone varchar(10) UNIQUE,
    status varchar(64),

    CONSTRAINT min_password_length CHECK ( char_length(password) >= 8 ),
    CONSTRAINT phone_length CHECK ( char_length(phone) = 10 ),
    CONSTRAINT fk_staff_status FOREIGN KEY (status) REFERENCES staff_status(name) ON DELETE SET NULL,
    CONSTRAINT email_or_phone CHECK (
        CASE WHEN email IS NULL THEN 0 ELSE 1 END +
        CASE WHEN phone IS NULL THEN 0 ELSE 1 END >= 1
    )
);

CREATE TABLE patient
(
    patient_id integer PRIMARY KEY,
    email varchar(64) UNIQUE,
    username varchar(32) UNIQUE,
    password varchar(32) NOT NULL UNIQUE,
    first_name varchar(64) NOT NULL,
    last_name varchar(64) NOT NULL,
    phone varchar(10) UNIQUE,

    CONSTRAINT min_password_length CHECK ( char_length(password) >= 8 ),
    CONSTRAINT phone_length CHECK ( char_length(phone) = 10 ),
    CONSTRAINT email_or_phone CHECK (
        CASE WHEN email IS NULL THEN 0 ELSE 1 END +
        CASE WHEN phone IS NULL THEN 0 ELSE 1 END >= 1
    )
);

CREATE TABLE health_card
(
    health_card_id serial PRIMARY KEY,
    patient integer UNIQUE NOT NULL,
    description text,
    birth_date timestamp,
    height float4,
    weight float4,
    blood smallint,

    CONSTRAINT fk_patient FOREIGN KEY (patient) REFERENCES patient(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_blood FOREIGN KEY (blood) REFERENCES blood(blood_id) ON DELETE SET NULL
);

ALTER TABLE health_card
ADD bmi float4;

ALTER TABLE health_card
ADD full_name text;


CREATE TABLE appointment_type
(
    name varchar(32) PRIMARY KEY
);

CREATE TABLE appointment
(
    appointment_id integer PRIMARY KEY,
    type varchar(32) NOT NULL DEFAULT 'Unspecified',
    patient integer,
    doctor integer,
    time timestamp NOT NULL,
    room integer NOT NULL,
    description text,

    CONSTRAINT fk_type FOREIGN KEY (type) REFERENCES appointment_type(name) ON DELETE SET DEFAULT,
    CONSTRAINT fk_patient FOREIGN KEY (patient) REFERENCES patient(patient_id) ON DELETE SET NULL,
    CONSTRAINT fk_doctor FOREIGN KEY (doctor) REFERENCES staff(staff_id) ON DELETE SET NULL
);

CREATE TABLE bill
(
    bill_id serial PRIMARY KEY,
    issuer integer,
    receiver integer,
    amount float8 NOT NULL,

    CONSTRAINT fk_issuer FOREIGN KEY (issuer) REFERENCES staff(staff_id) ON DELETE SET NULL,
    CONSTRAINT fk_receiver FOREIGN KEY (receiver) REFERENCES patient(patient_id) ON DELETE SET NULL
);

CREATE TABLE announcement
(
    announcement_id integer PRIMARY KEY,
    title varchar(128) NOT NULL,
    description text,
    author integer NOT NULL,

    CONSTRAINT fk_author FOREIGN KEY (author) REFERENCES staff(staff_id) ON DELETE SET DEFAULT
);

CREATE TABLE action_type
(
    name varchar(32) PRIMARY KEY,

    CONSTRAINT valid_name CHECK ( name in ('appointment', 'announcement', 'bill', 'update', 'delete') )
);

CREATE TABLE action
(
    action_id serial8 PRIMARY KEY,
    type varchar(32) NOT NULL,
    patient_subject integer,
    patient_object integer,
    staff_subject integer,
    staff_object integer,
    time timestamp NOT NULL,

    CONSTRAINT fk_action_type FOREIGN KEY (type) REFERENCES action_type(name) ON DELETE SET NULL,
    CONSTRAINT fk_patient_subject FOREIGN KEY (patient_subject) REFERENCES patient(patient_id) ON DELETE SET NULL,
    CONSTRAINT fk_patient_object FOREIGN KEY (patient_object) REFERENCES patient(patient_id) ON DELETE SET NULL,
    CONSTRAINT fk_doctor_subject FOREIGN KEY (staff_subject) REFERENCES staff(staff_id) ON DELETE SET NULL,
    CONSTRAINT fk_doctor_object FOREIGN KEY (staff_object) REFERENCES staff(staff_id) ON DELETE SET NULL,

    CONSTRAINT le_one_patient CHECK (
        CASE WHEN patient_subject is NULL THEN 0 ELSE 1 END +
        CASE WHEN patient_object is NULL THEN 0 ELSE 1 END <= 1
    ),
    CONSTRAINT le_one_doctor CHECK (
        CASE WHEN staff_subject is NULL THEN 0 ELSE 1 END +
        CASE WHEN staff_object is NULL THEN 0 ELSE 1 END <= 1
    ),
    CONSTRAINT le_one_subject CHECK (
        CASE WHEN patient_subject is NULL THEN 0 ELSE 1 END +
        CASE WHEN staff_subject is NULL THEN 0 ELSE 1 END <= 1
    ),
    CONSTRAINT le_one_object CHECK (
        CASE WHEN patient_object is NULL THEN 0 ELSE 1 END +
        CASE WHEN staff_object is NULL THEN 0 ELSE 1 END <= 1
    )
);
