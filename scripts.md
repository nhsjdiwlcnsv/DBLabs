# Scripts for database manipulation

## Creating the database
```postgresql
CREATE DATABASE bloodbank
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1
```

## Creating database tables

### Building & Room
```postgresql
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
```

### Appointment & Appointment type
```postgresql
CREATE TABLE appointment_type
(
    name varchar(32) PRIMARY KEY
);

CREATE TABLE appointment
(
    appointment_id integer PRIMARY KEY,
    type varchar(32) NOT NULL DEFAULT 'Unspecified',
    patient varchar(64),
    doctor varchar(64),
    time timestamp NOT NULL,
    room integer NOT NULL,
    description text,

    CONSTRAINT fk_type FOREIGN KEY (type) REFERENCES appointment_type(name) ON DELETE SET DEFAULT,
    CONSTRAINT fk_patient FOREIGN KEY (patient) REFERENCES patient(email) ON DELETE SET NULL,
    CONSTRAINT fk_doctor FOREIGN KEY (doctor) REFERENCES staff(email) ON DELETE SET NULL
);
```

### Bill & Announcement
```postgresql
CREATE TABLE bill
(
    bill_id integer PRIMARY KEY,
    issuer varchar(64),
    receiver varchar(64),
    amount float8 NOT NULL,

    CONSTRAINT fk_issuer FOREIGN KEY (issuer) REFERENCES staff(email) ON DELETE SET NULL,
    CONSTRAINT fk_receiver FOREIGN KEY (receiver) REFERENCES patient(email) ON DELETE SET NULL
);

CREATE TABLE announcement
(
    announcement_id integer PRIMARY KEY,
    title varchar(128) NOT NULL,
    description text,
    author varchar(64) NOT NULL,

    CONSTRAINT fk_author FOREIGN KEY (author) REFERENCES staff(email)
);
```

### Action & Action type
```postgresql
CREATE TABLE action_type 
(
    name varchar(32) PRIMARY KEY
);

CREATE TABLE action 
(
    action_id integer PRIMARY KEY,
    type varchar(32) NOT NULL,

    CONSTRAINT fk_action_type FOREIGN KEY (type) REFERENCES action_type(name)
);
```

### Blood & Blood type
```postgresql
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
```

### Staff & Staff status
```postgresql
CREATE TABLE staff_status
(
    name varchar(8) PRIMARY KEY

    CONSTRAINT valid_name CHECK ( name in ('Admin', 'Doctor') )
);

CREATE TABLE staff
(
    email varchar(64) PRIMARY KEY,
    password varchar(32) NOT NULL UNIQUE,
    first_name varchar(64) NOT NULL,
    last_name varchar(64) NOT NULL,
    phone varchar(12) UNIQUE,
    status varchar(64),

    CONSTRAINT min_password_length CHECK ( char_length(password) >= 8 ),
    CONSTRAINT phone_length CHECK ( char_length(phone) >= 12 ),
    CONSTRAINT fk_staff_status FOREIGN KEY (status) REFERENCES staff_status(name) ON DELETE SET NULL
);
```

### Patient & Health card
```postgresql
CREATE TABLE patient
(
    email varchar(64) PRIMARY KEY,
    username varchar(32) UNIQUE,
    password varchar(32) NOT NULL UNIQUE,
    first_name varchar(64) NOT NULL,
    last_name varchar(64) NOT NULL,
    phone varchar(12) UNIQUE,

    CONSTRAINT min_password_length CHECK ( char_length(password) >= 8 ),
    CONSTRAINT phone_length CHECK ( char_length(phone) >= 12 )
);

CREATE TABLE health_card
(
    health_card_id integer PRIMARY KEY,
    patient varchar(64) UNIQUE NOT NULL,
    description text,
    birth_date timestamp NOT NULL,
    height float4 NOT NULL,
    weight float4 NOT NULL,
    blood smallint,

    CONSTRAINT fk_patient FOREIGN KEY (patient) REFERENCES patient(email) ON DELETE CASCADE,
    CONSTRAINT fk_blood FOREIGN KEY (blood) REFERENCES blood(blood_id) ON DELETE SET NULL
);
```