import datetime
import enum
import os

from psycopg2.extras import NamedTupleCursor

from bloodbank import FetchMode, Announcement
from bloodbank import Terminal
from bloodbank import UserCreds, MedicalRecord, Appointment
from bloodbank import HELP_MSG, MEDICAL_RECORD_MSG, APPOINTMENT_MSG, ANNOUNCEMENT_MSG


class Status(enum.Enum):
    GUEST = 'guest'
    PATIENT = 'patient'
    STAFF = 'staff'
    ADMIN = 'admin'


class Command(enum.Enum):
    AUTHENTICATE = 'g0'
    HELP = 'g1'
    P_VIEW_MEDICAL_RECORD = 'p0'
    P_UPDATE_MEDICAL_RECORD = 'p1'
    S_VIEW_MEDICAL_RECORD = 's0'
    S_CREATE_APPOINTMENT = 's1'
    VIEW_APPOINTMENTS = ('s2', 'p2')
    S_DELETE_APPOINTMENT = 's3'
    S_UPDATE_APPOINTMENT = 's4'
    S_CREATE_ANNOUNCEMENT = 's5'
    S_VIEW_ANNOUNCEMENTS = 's6'
    S_DELETE_ANNOUNCEMENT = 's7'
    S_UPDATE_ANNOUNCEMENT = 's8'


def _commit(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        args[0].term.connection.commit()

    return wrapper


def _requires_auth(statuses: tuple):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if args[0].status not in statuses:
                raise PermissionError(f'Access denied to {args[0].status.value} user!')
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


class User:
    AUTH_MSG: str = "\tEnter user's email and password separated by space: "
    WELCOME_BACK_MSG: str = "\tWelcome back, {name}!"
    WELCOME_MSG: str = "\tWelcome, {name}!"
    SIGN_UP_MSG: str = "\tLooks like there's no such user. Would you like to sign up? [y/*]"

    def __init__(self, terminal: Terminal):
        self._queries: int = 0
        self._email: str | None = None
        self._password: str | None = None
        self._status: Status = Status.GUEST
        self._terminal: Terminal = terminal

        columns, _ = os.get_terminal_size(0)
        self.HELP_MSG = HELP_MSG.format(padding=' ' * ((columns - 81) // 2 - 4))

        print(self.HELP_MSG)

    @property
    def term(self) -> Terminal:
        return self._terminal

    @property
    def email(self) -> str:
        return self._email

    @property
    def password(self) -> str:
        return self._password

    @property
    def status(self) -> Status:
        return self._status

    @_requires_auth(statuses=(Status.PATIENT, Status.STAFF, Status.ADMIN))
    def full_name(self) -> str:
        query: str = f"""
        SELECT CONCAT(first_name, ' ', last_name) as full_name
        FROM {self.status.value}
        WHERE email=%s AND password=%s
        """

        with self.term.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(query, (self.email, self.password))
            response = cursor.fetchone()

        return response.full_name

    def id(self) -> int:
        query: str = f"""
        SELECT {self.status.value}_id
        FROM {'patient' if self.status == Status.PATIENT else 'staff'}
        WHERE email=%s AND password=%s
        """

        with self.term.connection.cursor() as cursor:
            cursor.execute(query, (self.email, self.password))
            response = cursor.fetchone()

        return int(response[0])

    def interact(self):
        query: str = input(f"    ~ ({self.email if self.status != Status.GUEST else 'Guest'}): ")

        # Authorize into system
        if query == Command.AUTHENTICATE.value:
            if self._authenticate(*input(self.AUTH_MSG).split()):
                print(self.WELCOME_BACK_MSG.format(name=self.full_name()))
            elif (input(self.SIGN_UP_MSG) == 'y' and self._sign_up(*input("\tEmail, username, password, first_name, "
                                                                          "last_name, phone: ").split())):
                print(self.WELCOME_MSG.format(name=self.full_name()))

        # Print help message
        elif query == Command.HELP.value:
            print(self.HELP_MSG)

        # View your medical record
        elif query == Command.P_VIEW_MEDICAL_RECORD.value and self.status == Status.PATIENT:
            self._get_medical_record()

        # View patient's medical record
        elif query == Command.S_VIEW_MEDICAL_RECORD.value and self.status in (Status.STAFF, Status.ADMIN):
            self._get_medical_record(int(input("    Patient's ID: ")))

        # Create appointment
        elif query == Command.S_CREATE_APPOINTMENT.value:
            app_type = input("\tType of the appointment (refer to help if needed): ")
            desc = input("\tDescription: ")
            patient_id, room_id = input("\tPatient ID, Room: ").split()
            timestamp = datetime.datetime.strptime(input("\tDate & time (dd-mm-yyyy HH:MM): "), '%d-%m-%Y %H:%M')

            self._create_appointment(app_type, patient_id, timestamp, room_id, desc)

        # View appointments
        elif query in Command.VIEW_APPOINTMENTS.value:
            self._get_appointments()

        # Delete a specific appointment
        elif query == Command.S_DELETE_APPOINTMENT.value:
            self._delete_appointment(input("    Appointment ID: "))

        # Update a specific appointment
        elif query == Command.S_UPDATE_APPOINTMENT.value:
            app_id = input("\tAppointment ID: ")
            desc = input("\tDescription: ")
            room_id = input("\tRoom: ")
            timestamp = datetime.datetime.strptime(input("\tDate & time (dd-mm-yyyy HH:MM): "), '%d-%m-%Y %H:%M')

            self._update_appointment(app_id, desc, room_id, timestamp)

        elif query == Command.S_CREATE_ANNOUNCEMENT.value:
            title = input("\tTitle: ")
            desc = input("\tDescription: ")

            self._create_announcement(title, desc)

        elif query == Command.S_VIEW_ANNOUNCEMENTS.value:
            self._get_announcements()

        elif query == Command.S_DELETE_ANNOUNCEMENT.value:
            self._delete_announcement(input("    Announcement ID: "))

        elif query == Command.S_UPDATE_ANNOUNCEMENT.value:
            app_id = input("\tAnnouncement ID: ")
            title = input("\tTitle: ")
            desc = input("\tDescription: ")
            
            self._update_announcement(app_id, title, desc)

    def _authenticate(self, email: str, password: str) -> bool:
        staff_query: str = """
        SELECT email, password, status FROM staff
        WHERE email=%s AND password=%s"""

        patient_query: str = """
        SELECT email, password FROM patient
        WHERE email=%s AND password=%s"""

        with self.term.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(staff_query, (email, password))
            staff_resp: UserCreds = cursor.fetchone()

            cursor.execute(patient_query, (email, password))
            patient_resp: UserCreds = cursor.fetchone()

            if staff_resp:
                self._email = staff_resp.email
                self._password = staff_resp.password
                self._status = (Status.STAFF, Status.ADMIN)[staff_resp.status == 'Admin']
            elif patient_resp:
                self._email = patient_resp.email
                self._password = patient_resp.password
                self._status = Status.PATIENT

        return self._status is not Status.GUEST

    @_commit
    def _sign_up(
            self, email: str, username: str | None,
            password: str, first_name: str,
            last_name: str, phone: str | None
    ) -> bool:
        last_id = self.term.execute_query(
            "SELECT patient_id from patient ORDER BY patient_id DESC",
            mode=FetchMode.ONE
        ).patient_id

        query: str = """
        INSERT INTO patient (patient_id, email, username, password, first_name, last_name, phone)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        response: UserCreds = self.term.execute_query(
            query, FetchMode.ONE,
            last_id + 1, email, username, password, first_name, last_name, phone)

        if not response:
            return False

        self._email = email
        self._password = password
        self._status = Status.PATIENT

        return True

    @_requires_auth(statuses=(Status.PATIENT, Status.STAFF, Status.ADMIN))
    def _get_medical_record(self, patient_id: int | None = None):
        query: str = f"""
        SELECT
            health_card_id AS record_id,
            patient AS patient_id,
            CONCAT(sup.first_name, ' ', sup.last_name) AS full_name,
            description AS info,
            birth_date, height, weight, bmi
        FROM health_card
        JOIN patient AS sup
        ON patient_id=patient
        WHERE patient={self.id() if not patient_id else patient_id}"""

        resp: MedicalRecord = self.term.execute_query(query, FetchMode.ONE)

        print(MEDICAL_RECORD_MSG.format(
            record_id=str(resp.record_id).zfill(4),
            patient_id=str(resp.patient_id).zfill(4),
            full_name=resp.full_name,
            birth_date=resp.birth_date,
            weight=resp.weight,
            height=resp.height,
            bmi=resp.bmi,
            info=resp.info
        ))

    @_requires_auth(statuses=(Status.PATIENT, Status.STAFF, Status.ADMIN))
    def _get_appointments(self):
        query: str = f"""
        SELECT 
            a.appointment_id,
            a.time,
            a.description,
            a.room,
            a.type,
            CONCAT(p.first_name, ' ', p.last_name) AS patient,
            CONCAT(s.first_name, ' ', s.last_name) AS doctor
        FROM appointment  a
        JOIN staff s ON s.staff_id = a.doctor
        JOIN patient p ON a.patient = p.patient_id
        WHERE {self.status.value if self.status != Status.STAFF else 'doctor'}={self.id()}
        ORDER BY a.time"""

        with self.term.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(query)
            responses: list[Appointment] = cursor.fetchall()

        for resp in responses:
            print(APPOINTMENT_MSG.format(
                appointment_id=str(resp.appointment_id).zfill(5),
                type=resp.type,
                patient_id=str(resp.patient).zfill(4),
                doctor_id=str(resp.doctor).zfill(4),
                time=str(resp.time),
                room=resp.room,
                info=resp.description
            ))
            print()

    @_commit
    @_requires_auth((Status.STAFF, Status.ADMIN))
    def _create_appointment(
            self,
            appointment_type,
            patient_id,
            time,
            room,
            description=None
    ):
        last_id = self.term.execute_query(
            "SELECT appointment_id from appointment ORDER BY appointment_id DESC",
            mode=FetchMode.ONE
        ).appointment_id

        query: str = """
        INSERT INTO appointment (appointment_id, type, patient, doctor, time, room, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        self.term.execute_query(
            query, FetchMode.NONE,
            last_id + 1, appointment_type, patient_id, self.id(), time, room, description
        )

    @_commit
    @_requires_auth((Status.STAFF, Status.ADMIN))
    def _delete_appointment(self, appointment_id: int):
        query: str = """
        DELETE FROM appointment
        WHERE appointment_id=%s"""

        self.term.execute_query(query, FetchMode.NONE, appointment_id)

    def _update_appointment(self, app_id, desc, room_id, timestamp):
        query: str = "CALL update_appointment(%s::integer, %s::text, %s::integer, %s::timestamp without time zone)"
        self.term.execute_query(query, FetchMode.NONE, app_id, desc, room_id, timestamp, )

    @_requires_auth((Status.STAFF, Status.ADMIN))
    def _create_announcement(self, title, description):
        last_id = self.term.execute_query(
            "SELECT announcement_id from announcement ORDER BY announcement_id DESC",
            mode=FetchMode.ONE
        ).announcement_id

        query: str = """
        INSERT INTO announcement (announcement_id, title, description, author)
        VALUES (%s, %s, %s, %s)"""

        self.term.execute_query(
            query, FetchMode.NONE,
            last_id + 1, title, description, self.id()
        )

    @_requires_auth(statuses=(Status.PATIENT, Status.STAFF, Status.ADMIN))
    def _get_announcements(self):
        query: str = f"""
        SELECT 
            announcement_id,
            title,
            email AS author,
            description
        FROM announcement
        JOIN staff ON staff_id = author
        WHERE author=%s"""

        responses: list[Announcement] = self.term.execute_query(query, FetchMode.ALL, self.id())

        for resp in responses:
            print(ANNOUNCEMENT_MSG.format(
                announcement_id=str(resp.announcement_id).zfill(5),
                title=resp.title,
                author=resp.author,
                description=resp.description
            ))
            print()

    @_commit
    @_requires_auth((Status.ADMIN,))
    def _delete_announcement(self, announcement_id: int):
        query: str = """DELETE FROM announcement WHERE announcement_id=%s"""

        self.term.execute_query(query, FetchMode.NONE, announcement_id)

    @_requires_auth((Status.ADMIN,))
    def _update_announcement(self, announcement_id, title, desc):
        query: str = "CALL update_appointment(%s::integer, %s::text, %s::text)"
        self.term.execute_query(query, FetchMode.NONE, announcement_id, title, desc)
