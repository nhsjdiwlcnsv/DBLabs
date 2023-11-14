--------------------------------------- LOG NEW BILL ----------------------------------------
CREATE OR REPLACE FUNCTION log_new_bill()
RETURNS TRIGGER AS
    $$
    BEGIN
        INSERT INTO action (type, patient_subject, patient_object, staff_subject, staff_object, time)
        VALUES ('bill', NULL, NEW.receiver, NEW.issuer, NULL, NOW());
        RETURN NEW;
    END
    $$
LANGUAGE 'plpgsql';

CREATE OR REPLACE TRIGGER log_new_bill
    AFTER INSERT ON bill
    FOR EACH ROW
    EXECUTE FUNCTION log_new_bill();

------------------------------------ LOG NEW APPOINTMENT ------------------------------------
CREATE OR REPLACE FUNCTION log_new_appointment()
RETURNS TRIGGER AS
    $$
    BEGIN
        INSERT INTO action (type, patient_subject, patient_object, staff_subject, staff_object, time)
        VALUES ('appointment', NULL, NEW.patient, NEW.doctor, NULL, NOW());
        RETURN NEW;
    END
    $$
LANGUAGE 'plpgsql';

CREATE OR REPLACE TRIGGER log_new_appointment
    AFTER INSERT ON appointment
    FOR EACH ROW
    EXECUTE FUNCTION log_new_appointment();

----------------------------------- LOG NEW ANNOUNCEMENT ------------------------------------
CREATE OR REPLACE FUNCTION log_new_announcement()
RETURNS TRIGGER AS
    $$
    BEGIN
        INSERT INTO action (type, patient_subject, patient_object, staff_subject, staff_object, time)
        VALUES ('announcement', NULL, NULL, NEW.author, NULL, NOW());
        RETURN NEW;
    END
    $$
LANGUAGE 'plpgsql';

CREATE OR REPLACE TRIGGER log_new_announcement
    AFTER INSERT ON announcement
    FOR EACH ROW
    EXECUTE FUNCTION log_new_announcement();

--------------------------------- RECALCULATE PATIENT'S BMI ---------------------------------
CREATE OR REPLACE FUNCTION recalculate_bmi()
RETURNS TRIGGER AS
    $$
        BEGIN
            UPDATE health_card
            SET bmi = NEW.weight * 10000 / (NEW.height * NEW.height)
            WHERE NEW.patient = patient;
            RETURN NEW;
        END;
    $$
LANGUAGE 'plpgsql';

CREATE OR REPLACE TRIGGER recalculate_bmi_on_update
    AFTER UPDATE OF weight, height
    ON health_card
    FOR EACH ROW WHEN
        (
            CASE WHEN (NEW.height != OLD.height) THEN 1 ELSE 0 END +
            CASE WHEN (NEW.weight != OLD.weight) THEN 1 ELSE 0 END +
            CASE WHEN (OlD.height IS NULL) THEN 1 ELSE 0 END +
            CASE WHEN (OlD.weight IS NULL) THEN 1 ELSE 0 END >= 1
        )
    EXECUTE FUNCTION recalculate_bmi();

CREATE OR REPLACE TRIGGER calculate_bmi_on_insert
    AFTER INSERT ON health_card
    FOR EACH ROW
    EXECUTE FUNCTION recalculate_bmi();

------------------------- CREATE NEW HEALTH RECORD FOR NEW PATIENT --------------------------
CREATE OR REPLACE FUNCTION assign_new_record()
RETURNS trigger AS
    $$
        BEGIN
            INSERT INTO health_card (patient, description, full_name)
            VALUES (NEW.patient_id, 'Blank health card', CONCAT(NEW.first_name, ' ', NEW.last_name));
            RETURN NEW;
        END
    $$
LANGUAGE 'plpgsql';

CREATE OR REPLACE TRIGGER create_health_card_for_new_patient
    AFTER INSERT ON patient
    FOR EACH ROW
    EXECUTE FUNCTION assign_new_record();

-------------------------- CREATE EMPTY BILL FOR NEW APPOINTMENT ----------------------------
CREATE OR REPLACE FUNCTION add_bill()
RETURNS trigger AS
    $$
        BEGIN
            INSERT INTO bill (issuer, receiver, amount)
            VALUES (NEW.doctor, NEW.patient, 0);
            RETURN NEW;
        END
    $$
LANGUAGE 'plpgsql';

CREATE OR REPLACE TRIGGER add_bill_to_new_appointment
    AFTER INSERT ON appointment
    FOR EACH ROW
    EXECUTE FUNCTION add_bill();