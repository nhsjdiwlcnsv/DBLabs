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

CREATE OR REPLACE PROCEDURE update_announcement(
    id integer,
    new_title text,
    new_desc text
)
AS
    $$
        BEGIN
            UPDATE announcement
            SET
                title = COALESCE(new_title, title),
                description = COALESCE(new_desc, description)
            WHERE announcement_id = id;
            COMMIT;
        END;
    $$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE update_appointment(
    id integer,
    new_desc text,
    new_room integer,
    new_time timestamp without time zone
)
AS
    $$
        BEGIN
            UPDATE appointment
            SET
                description = COALESCE(new_desc, description),
                room = COALESCE(new_room, room),
                time = COALESCE(new_time, time)
            WHERE appointment_id = id;
--             COMMIT;
        END;
    $$
LANGUAGE plpgsql;
