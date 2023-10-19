-------------------------------------------- BLOOD TYPE -------------------------------------------
-- Health cards with not contaminated and contaminated blood
SELECT description FROM health_card WHERE blood < 9;
SELECT description FROM health_card WHERE blood >= 9;

-- Average stats of patients with O+, O-, A+, A- blood types:
SELECT AVG(weight), AVG(height) FROM health_card WHERE blood in (1, 2, 5, 6, 9, 10, 13, 14);

-- Average stats of patients with B+, B-, AB+, AB- blood types:
SELECT AVG(weight), AVG(height) FROM health_card WHERE blood in (3, 4, 7, 8, 11, 12, 15, 16);

--------------------------------- ROOMS NOT HIGHER THEN 4TH FLOOR ---------------------------------
SELECT room_id FROM room WHERE room_id < 500;


------------------------------------ SORTED PATIENTS AND STAFF ------------------------------------
SELECT first_name, last_name
FROM patient
ORDER BY (first_name, last_name);

SELECT first_name, last_name
FROM staff
ORDER BY (first_name, last_name);

---------------------------- PATIENTS AND STAFF WITHOUT PHONE OR EMAIL ----------------------------
SELECT first_name, last_name, phone, email
FROM patient
WHERE email IS NULL OR phone IS NULL;

SELECT first_name, last_name, phone, email
FROM staff
WHERE email IS NULL OR phone IS NULL;

-------------------------------------- DOCTORS & ADMINS ONLY --------------------------------------
SELECT staff_id, first_name, last_name, phone, email
FROM staff
WHERE status = 'Doctor';

SELECT staff_id, first_name, last_name, phone, email
FROM staff
WHERE status = 'Admin';

-------------------------------------- COUNT DOCTORS & ADMINS --------------------------------------
SELECT COUNT(first_name)
FROM staff
WHERE status = 'Doctor';

SELECT COUNT(first_name)
FROM staff
WHERE status = 'Admin';

----------------- FIRST N PATIENTS WITH FIRST/LAST NAME STARTING/ENDING WITH SMTH -----------------
SELECT first_name, last_name
FROM patient
WHERE first_name ~~* '%A'
LIMIT 8;

SELECT first_name, last_name
FROM patient
WHERE first_name LIKE 'A%'
LIMIT 8;

------------------------------------ TOP-N RECENT APPOINTMENTS ------------------------------------
SELECT time, room, description
FROM appointment
WHERE time > '10-01-2023'
ORDER BY time DESC
LIMIT 10;

------------------------------- NUMBER OF RECENT APPOINTMENTS PER DAY -----------------------------
SELECT time, COUNT(*)
FROM appointment
WHERE time > '10-01-2023'
GROUP BY time
ORDER BY time DESC
LIMIT 10
