import enum
import os
from collections import namedtuple

from psycopg2.extras import NamedTupleCursor

SYSTEM_ENTRY_MSG: str = """


{padding} ▄▄▄▄    ██▓     ▒█████   ▒█████  ▓█████▄     ▄▄▄▄    ▄▄▄       ███▄    █  ██ ▄█▀
{padding}▓█████▄ ▓██▒    ▒██▒  ██▒▒██▒  ██▒▒██▀ ██▌   ▓█████▄ ▒████▄     ██ ▀█   █  ██▄█▒ 
{padding}▒██▒ ▄██▒██░    ▒██░  ██▒▒██░  ██▒░██   █▌   ▒██▒ ▄██▒██  ▀█▄  ▓██  ▀█ ██▒▓███▄░ 
{padding}▒██░█▀  ▒██░    ▒██   ██░▒██   ██░░▓█▄   ▌   ▒██░█▀  ░██▄▄▄▄██ ▓██▒  ▐▌██▒▓██ █▄ 
{padding}░▓█  ▀█▓░██████▒░ ████▓▒░░ ████▓▒░░▒████▓    ░▓█  ▀█▓ ▓█   ▓██▒▒██░   ▓██░▒██▒ █▄
{padding}░▒▓███▀▒░ ▒░▓  ░░ ▒░▒░▒░ ░ ▒░▒░▒░  ▒▒▓  ▒    ░▒▓███▀▒ ▒▒   ▓▒█░░ ▒░   ▒ ▒ ▒ ▒▒ ▓▒
{padding}▒░▒   ░ ░ ░ ▒  ░  ░ ▒ ▒░   ░ ▒ ▒░  ░ ▒  ▒    ▒░▒   ░   ▒   ▒▒ ░░ ░░   ░ ▒░░ ░▒ ▒░
{padding} ░    ░   ░ ░   ░ ░ ░ ▒  ░ ░ ░ ▒   ░ ░  ░     ░    ░   ░   ▒      ░   ░ ░ ░ ░░ ░ 
{padding} ░          ░  ░    ░ ░      ░ ░     ░        ░            ░  ░         ░ ░  ░   
{padding}      ░                            ░               ░                             
"""

HELP_MSG: str = """
    
    
    {padding} ▄▄ • ▄• ▄▌▄▄▄ ..▄▄ · ▄▄▄▄▄    Authenticate .................................. g0
    {padding}▐█ ▀ ▪█▪██▌▀▄.▀·▐█ ▀. •██      Help .......................................... g1
    {padding}▄█ ▀█▄█▌▐█▌▐▀▀▪▄▄▀▀▀█▄ ▐█.▪
    {padding}▐█▄▪▐█▐█▄█▌▐█▄▄▌▐█▄▪▐█ ▐█▌·
    {padding}·▀▀▀▀  ▀▀▀  ▀▀▀  ▀▀▀▀  ▀▀▀ 


    {padding}.▄▄ · ▄▄▄▄▄ ▄▄▄· ·▄▄▄·▄▄▄    View medical record by patient's id ............. s0
    {padding}▐█ ▀. •██  ▐█ ▀█ ▐▄▄·▐▄▄·    Create appointment .............................. s1
    {padding}▄▀▀▀█▄ ▐█.▪▄█▀▀█ ██▪ ██▪     View appointments ............................... s2 (p2)
    {padding}▐█▄▪▐█ ▐█▌·▐█ ▪▐▌██▌.██▌.    Delete appointment .............................. s3
    {padding} ▀▀▀▀  ▀▀▀  ▀  ▀ ▀▀▀ ▀▀▀     Update appointment .............................. s4  
    {padding}Create announcement .......................................................... s5
    {padding}View announcements ........................................................... s6
    {padding}Delete announcement (Admin) .................................................. s7
    {padding}Update announcement (Admin) .................................................. s8
    {padding}Create bill .................................................................. s9
    {padding}View bills ................................................................... s10
    {padding}Delete bill (Admin) .......................................................... s11


    {padding} ▄▄▄· ▄▄▄· ▄▄▄▄▄▪  ▄▄▄ . ▐ ▄ ▄▄▄▄▄   Get medical record ...................... p0
    {padding}▐█ ▄█▐█ ▀█ •██  ██ ▀▄.▀·•█▌▐█•██     Update medical record ................... p1
    {padding} ██▀·▄█▀▀█  ▐█.▪▐█·▐▀▀▪▄▐█▐▐▌ ▐█.▪   View appointments ....................... p2 (s2)
    {padding}▐█▪·•▐█ ▪▐▌ ▐█▌·▐█▌▐█▄▄▌██▐█▌ ▐█▌·   
    {padding}.▀    ▀  ▀  ▀▀▀ ▀▀▀ ▀▀▀ ▀▀ █▪ ▀▀▀    
    
    
    """
MEDICAL_RECORD_MSG: str = """        {info}
        +-----------------------------------------+
        | RECORD ID:          {record_id:<19} |
        | PATIENT ID:         {patient_id:<19} |
        | FULL NAME:          {full_name:<19} |
        | BIRTH DATE:         {birth_date} |
        | WEIGHT:             {weight:<16.2f} kg |
        | HEIGHT:             {height:<16.2f} cm |
        | BODY MASS INDEX:    {bmi:<13.2f}       |
        +-----------------------------------------+"""

APPOINTMENT_MSG: str = """        {info}
        +------------------------------------------------------+
        | APPOINTMENT ID:       {appointment_id:<30} |
        | TYPE:                 {type:<30} |
        | PATIENT:              {patient_id:<30} |
        | DOCTOR:               {doctor_id:<30} |
        | TIME:                 {time:<30} |
        | ROOM:                 {room:<30} |
        +------------------------------------------------------+"""

ANNOUNCEMENT_MSG: str = """
        +---------------------------------------------------+
        | ID     | {announcement_id:<40} |
        +---------------------------------------------------+
        | Title  | {title:<40} |
        +---------------------------------------------------+
        | Author | {author:<40} |
        +---------------------------------------------------+
        {description}"""

class FetchMode(enum.Enum):
    ONE = 0
    ALL = 1
    MANY = 2
    NONE = 3


class Terminal:
    def __init__(self, connection):
        self._connection = connection
        columns, _ = os.get_terminal_size(0)

        print(SYSTEM_ENTRY_MSG.format(padding=" " * ((columns - 81) // 2)))

    @property
    def connection(self):
        return self._connection

    def execute_query(self, query, mode: FetchMode, *values) -> namedtuple:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(query, values)

            if mode == FetchMode.ONE:
                return cursor.fetchone()
            elif mode == FetchMode.ALL:
                return cursor.fetchall()
            elif mode == FetchMode.NONE:
                return

UserCreds = namedtuple('UserCreds', 'email password status')
MedicalRecord = namedtuple('MedicalRecord', 'record_id patient_id full_name info birth_date height weight bmi')
Appointment = namedtuple('Appointment', 'appointment_id type patient doctor time room description')
Announcement = namedtuple('Announcement', 'announcement_id title author description')

