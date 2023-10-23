----------------------------------------- BLOOD TYPE ----------------------------------------
-- Health cards with not contaminated and contaminated blood
SELECT description FROM health_card WHERE blood < 9;
SELECT description FROM health_card WHERE blood >= 9;

-- Average stats of patients with O+, O-, A+, A- blood types:
SELECT AVG(weight), AVG(height) FROM health_card WHERE blood in (1, 2, 5, 6, 9, 10, 13, 14);

-- Average stats of patients with B+, B-, AB+, AB- blood types:
SELECT AVG(weight), AVG(height) FROM health_card WHERE blood in (3, 4, 7, 8, 11, 12, 15, 16);

------------------------------ ROOMS NOT HIGHER THEN 4TH FLOOR ------------------------------
SELECT room_id FROM room WHERE room_id < 500;

--------------------------------- SORTED PATIENTS AND STAFF ---------------------------------
SELECT first_name, last_name
FROM patient
ORDER BY (first_name, last_name);

SELECT first_name, last_name
FROM staff
ORDER BY (first_name, last_name);

------------------------- PATIENTS AND STAFF WITHOUT PHONE OR EMAIL -------------------------
SELECT first_name, last_name, phone, email
FROM patient
WHERE email IS NULL OR phone IS NULL;

SELECT first_name, last_name, phone, email
FROM staff
WHERE email IS NULL OR phone IS NULL;

---------------------------------- DOCTORS & ADMINS ONLY -----------------------------------
SELECT staff_id, first_name, last_name, phone, email
FROM staff
WHERE status = 'Doctor';

SELECT staff_id, first_name, last_name, phone, email
FROM staff
WHERE status = 'Admin';

----------------------------------- COUNT DOCTORS & ADMINS -----------------------------------
SELECT COUNT(first_name)
FROM staff
WHERE status = 'Doctor';

SELECT COUNT(first_name)
FROM staff
WHERE status = 'Admin';

-------------- FIRST N PATIENTS WITH FIRST/LAST NAME STARTING/ENDING WITH SMTH --------------
SELECT first_name, last_name
FROM patient
WHERE first_name ~~* '%A'
LIMIT 8;

SELECT first_name, last_name
FROM patient
WHERE first_name LIKE 'A%'
LIMIT 8;

--------------------------------- TOP-N RECENT APPOINTMENTS ---------------------------------
SELECT time, room, description
FROM appointment
WHERE time > '10-01-2023'
ORDER BY time DESC
LIMIT 10;

---------------------------- NUMBER OF RECENT APPOINTMENTS PER DAY --------------------------
SELECT time, COUNT(*) AS appointments_number
FROM appointment
WHERE time > '01-01-2023'
GROUP BY time
ORDER BY time DESC
LIMIT 10;

-------------------------------- AVERAGE BILL VALUE BY ISSUER -------------------------------
SELECT issuer, ROUND(CAST(AVG(amount) as DEC(12, 2)), 2) as avg_amount
FROM bill
GROUP BY issuer
ORDER BY issuer;

----------------------------------- THE MOST COMMON HEIGHT ----------------------------------

SELECT height, COUNT(*) as count
FROM health_card
GROUP BY height
ORDER BY count;

------------------------------ DOCTORS WITH THEIR APPOINTMENTS ------------------------------
SELECT
    s.staff_id, CONCAT(s.first_name, ' ', s.last_name) AS full_name,
    a.type, a.time, a.room
FROM staff s
LEFT OUTER JOIN appointment a ON s.staff_id = a.doctor
ORDER BY s.staff_id;

-------------------- HEALTHY PATIENT INFO WITH THEIR WEIGHT, HEIGHT, & BMI ------------------
SELECT
    p.patient_id, CONCAT(p.first_name, ' ', p.last_name) AS full_name,
    h.birth_date, h.height, h.weight,
    ROUND(CAST(h.weight * 10000 / (h.height * h.height) AS DEC(12, 2)), 2) AS bmi,
    b.type
FROM patient p
INNER JOIN health_card h ON p.patient_id = h.patient
INNER JOIN blood b on b.blood_id = h.blood
WHERE
    ROUND(h.weight * 10000 / (h.height * h.height)) > 17 AND
    ROUND(h.weight * 10000 / (h.height * h.height)) < 30 AND
    b.contaminated IS FALSE;

--------------------------------- STATISTICS FOR EACH ROOM ----------------------------------
SELECT
    a.room,
    ROUND(CAST(AVG(h.weight) AS DEC(12, 2)), 2) AS avg_weight,
    ROUND(CAST(AVG(h.height) AS DEC(12, 2)), 2) AS avg_height,
    COUNT(h.patient) AS num_patients
FROM health_card h
LEFT JOIN appointment a ON a.patient = h.patient
GROUP BY a.room
HAVING AVG(h.height) < 185
ORDER BY COUNT(h.patient);

-- ABOBA --
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS full_name,
    a.room
FROM patient p
LEFT JOIN appointment a ON a.patient = p.patient_id
ORDER BY patient_id;

----------------------------------------- ALL USERS -----------------------------------------
SELECT patient_id,
       username AS username_or_status,
       CONCAT(first_name, ' ', last_name) AS full_name,
       email
FROM patient
UNION
SELECT
    staff_id,
    status,
    CONCAT(first_name, ' ', last_name) AS full_name,
    email
FROM staff;

------------------------- PATIENTS AND DOCTORS WITH IDENTICAL NAMES -------------------------
SELECT first_name, last_name
FROM staff
WHERE EXISTS
(SELECT first_name FROM patient WHERE patient.first_name = staff.first_name);

---------------------------- INSERT INTO SELECT SYNTHETIC EXAMPLE ---------------------------
INSERT INTO staff (staff_id, email, password, first_name, last_name, phone)
SELECT
    patient_id,
    email,
    password,
    first_name,
    last_name,
    phone
FROM (
    patient
    INNER JOIN health_card ON patient.patient_id = health_card.patient
) AS pdata
WHERE
    pdata.birth_date > '01-01-2004'
    AND pdata.patient_id > 120
    AND NOT EXISTS (SELECT appointment_id FROM appointment WHERE appointment.patient = pdata.patient_id)
