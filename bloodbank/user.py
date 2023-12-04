import enum
from collections import namedtuple

import psycopg2
from psycopg2.extras import NamedTupleCursor

from bloodbank import Terminal


class UserStatus(enum.Enum):
    USER = 0
    PATIENT = 1
    STAFF = 2
    ADMIN = 3


class UserCommand(enum.Enum):
    AUTHENTICATE = 'g0'


UserCreds = namedtuple('UserCreds', 'email password status')


class User:
    QUERY_MSG: str = """
    ================================== BLOOD BANK HELP ==================================
    User:
        - Authenticate                                                                 g0
    Staff:
        - Create appointment                                                           s0
        - Delete appointment                                                           s1
        - Update appointment                                                           s2
    Patient:
        - Get your medical record                                                      p0
    =====================================================================================
    """
    AUTH_MSG: str = "Enter user's email and password separated by space: "
    WELCOME_MSG: str = "Welcome back, {email}!"
    SIGN_UP_MSG: str = "Looks like there's no such user. Would you like to sign up? [y/*]"

    def __init__(self, terminal: Terminal):
        self._email: str | None = None
        self._password: str | None = None
        self._status: UserStatus = UserStatus.USER
        self._terminal = terminal

    @staticmethod
    def commit(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            args[0].term.connection.commit()

        return wrapper

    @property
    def term(self):
        return self._terminal

    def interact(self):
        query: str = input(self.QUERY_MSG)

        if query == UserCommand.AUTHENTICATE.value:
            response = input(self.AUTH_MSG).split()

            if self._authenticate(*response):
                print(self.WELCOME_MSG.format(email=self._email))
            elif (
                    input(self.SIGN_UP_MSG) == 'y' and
                    self._sign_up(*input("Email, username, password, first_name, last_name, phone: ").split())
            ):
                print("Hey, hi, hello, yo, what's up?")

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
                self._status = (UserStatus.STAFF, UserStatus.ADMIN)[staff_resp.status == 'Admin']
            elif patient_resp:
                self._email = patient_resp.email
                self._password = patient_resp.password
                self._status = UserStatus.PATIENT

        return self._status is not UserStatus.USER

    @commit
    def _sign_up(
            self, email: str, username: str | None,
            password: str, first_name: str,
            last_name: str, phone: str | None
    ) -> bool:
        with self.term.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute("SELECT patient_id from patient ORDER BY patient_id DESC")
            last_id = cursor.fetchone().patient_id

        query: str = """
        INSERT INTO patient (patient_id, email, username, password, first_name, last_name, phone)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        with self.term.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(query, (last_id + 1, email, username, password, first_name, last_name, phone))
            cursor.execute("SELECT * FROM patient WHERE email=%s AND password=%s", (email, password))

            response: UserCreds = cursor.fetchone()

        if not response:
            return False

        self._email = email
        self._password = password
        self._status = UserStatus.PATIENT

        return True
