import enum
import os
from collections import namedtuple

import psycopg2
from psycopg2.extras import NamedTupleCursor

import bloodbank

def _commit(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        args[0].term.connection.commit()

    return wrapper

def _requires_auth(func):
    def wrapper(*args, **kwargs):
        if args[0].status == UserStatus.GUEST:
            raise PermissionError(f'Access denied to a guest user! Did you forget to authenticate?')
        else:
            return func(*args, **kwargs)

    return wrapper


class UserStatus(enum.Enum):
    GUEST = 0
    PATIENT = 1
    STAFF = 2
    ADMIN = 3


class UserCommand(enum.Enum):
    AUTHENTICATE = 'g0'

    GET_MEDICAL_RECORD = 'p0'


UserCreds = namedtuple('UserCreds', 'email password status')
MedicalRecord = namedtuple(
    'MedicalRecord',
    'record_id patient_id info birth_date height weight bmi'
)


class User:
    QUERY_MSG: str = """
    {padding} ▄▄ • ▄• ▄▌▄▄▄ ..▄▄ · ▄▄▄▄▄    Authenticate                                    g0
    {padding}▐█ ▀ ▪█▪██▌▀▄.▀·▐█ ▀. •██   
    {padding}▄█ ▀█▄█▌▐█▌▐▀▀▪▄▄▀▀▀█▄ ▐█.▪
    {padding}▐█▄▪▐█▐█▄█▌▐█▄▄▌▐█▄▪▐█ ▐█▌·
    {padding}·▀▀▀▀  ▀▀▀  ▀▀▀  ▀▀▀▀  ▀▀▀ 
    
    
    {padding}.▄▄ · ▄▄▄▄▄ ▄▄▄· ·▄▄▄·▄▄▄      Create appointment                              s0
    {padding}▐█ ▀. •██  ▐█ ▀█ ▐▄▄·▐▄▄·      View appointment                                s1
    {padding}▄▀▀▀█▄ ▐█.▪▄█▀▀█ ██▪ ██▪       View appointments                               s2
    {padding}▐█▄▪▐█ ▐█▌·▐█ ▪▐▌██▌.██▌.      Delete appointment                              s3
    {padding} ▀▀▀▀  ▀▀▀  ▀  ▀ ▀▀▀ ▀▀▀       Update appointment                              s4
    
    
    {padding} ▄▄▄· ▄▄▄· ▄▄▄▄▄▪  ▄▄▄ . ▐ ▄ ▄▄▄▄▄   Get medical record                        p0
    {padding}▐█ ▄█▐█ ▀█ •██  ██ ▀▄.▀·•█▌▐█•██     View appointments                         p1
    {padding} ██▀·▄█▀▀█  ▐█.▪▐█·▐▀▀▪▄▐█▐▐▌ ▐█.▪   
    {padding}▐█▪·•▐█ ▪▐▌ ▐█▌·▐█▌▐█▄▄▌██▐█▌ ▐█▌·   
    {padding}.▀    ▀  ▀  ▀▀▀ ▀▀▀ ▀▀▀ ▀▀ █▪ ▀▀▀    
    
    
    """
    AUTH_MSG: str = "\tEnter user's email and password separated by space: "
    WELCOME_BACK_MSG: str = "\tWelcome back, {name}!"
    WELCOME_MSG: str = "\tWelcome, {name}!"
    SIGN_UP_MSG: str = "\tLooks like there's no such user. Would you like to sign up? [y/*]"

    def __init__(self, terminal: bloodbank.Terminal):
        self._email: str | None = None
        self._password: str | None = None
        self._status: UserStatus = UserStatus.GUEST
        self._terminal: bloodbank.Terminal = terminal

        columns, _ = os.get_terminal_size(0)

        self.QUERY_MSG = self.QUERY_MSG.format(padding=' ' * ((columns - 81) // 2 - 4))

    @property
    def term(self) -> bloodbank.Terminal:
        return self._terminal

    @property
    def email(self) -> str:
        return self._email

    @property
    def password(self) -> str:
        return self._password

    @property
    def status(self) -> UserStatus:
        return self._status

    @_requires_auth
    def full_name(self) -> str:
        query: str = f"""
        SELECT CONCAT(first_name, ' ', last_name) as full_name
        FROM {'patient' if self.status == UserStatus.PATIENT else 'staff'}
        WHERE email=%s AND password=%s
        """

        with self.term.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(query, (self.email, self.password))
            response = cursor.fetchone()

        return response.full_name

    def id(self) -> int:
        query: str = f"""
        SELECT {'patient_id' if self.status == UserStatus.PATIENT else 'staff_id'}
        FROM {'patient' if self.status == UserStatus.PATIENT else 'staff'}
        WHERE email=%s AND password=%s
        """

        with self.term.connection.cursor() as cursor:
            cursor.execute(query, (self.email, self.password))
            response = cursor.fetchone()

        return int(response[0])

    def interact(self):
        query: str = input(self.QUERY_MSG)

        if query == UserCommand.AUTHENTICATE.value:
            response = input(self.AUTH_MSG).split()

            if self._authenticate(*response):
                print(self.WELCOME_BACK_MSG.format(name=self.full_name()))
            elif (
                    input(self.SIGN_UP_MSG) == 'y' and
                    self._sign_up(*input("Email, username, password, first_name, last_name, phone: ").split())
            ):
                print(self.WELCOME_MSG.format(name=self.full_name()))

        elif query == UserCommand.GET_MEDICAL_RECORD.value:
            self._get_medical_record()

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

        return self._status is not UserStatus.GUEST

    @_commit
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

    @_requires_auth
    def _get_medical_record(self):
        query: str = f"""
        SELECT
            health_card_id AS record_id, 
            patient AS patient_id, 
            description AS info, 
            birth_date, 
            height, 
            weight,
            bmi
        FROM health_card
        WHERE patient={self.id()}
        """

        with self.term.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(query)
            response: MedicalRecord = cursor.fetchone()

        print(f"""
        RECORD ID:          {response.record_id}
        PATIENT ID:         {response.patient_id}
        INFO:               {response.info}
        BIRTH DATE:         {response.birth_date}
        WEIGHT:             {response.weight}
        HEIGHT:             {response.height}
        BODY MASS INDEX:    {response.bmi}""")