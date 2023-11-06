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