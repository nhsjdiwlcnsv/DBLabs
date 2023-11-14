CREATE OR REPLACE PROCEDURE update_health_record(
    patient_id integer,
    new_desc text,
    new_blood smallint,
    new_weight real,
    new_height real,
    new_birth_date timestamp with time zone
)
AS
    $$
        BEGIN
            UPDATE health_card
            SET
                description = COALESCE(new_desc, description),
                blood = COALESCE(new_blood, blood),
                weight = COALESCE(new_weight, weight),
                height = COALESCE(new_height, height),
                birth_date = COALESCE(new_birth_date, birth_date)
            WHERE patient = patient_id;
            COMMIT;
        END;
    $$
LANGUAGE plpgsql;
