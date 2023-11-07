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
        VALUES ('announcement', NULL, NULL, NEW.doctor, NULL, NOW());
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

CREATE OR REPLACE TRIGGER recalculate_bmi
    AFTER UPDATE OF weight, height
    ON health_card
    FOR EACH ROW
    EXECUTE FUNCTION recalculate_bmi();