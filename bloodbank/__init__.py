import os

import psycopg2


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


class Terminal:
    def __init__(self, connection):
        self._connection = connection
        columns, _ = os.get_terminal_size(0)

        print(SYSTEM_ENTRY_MSG.format(padding=" " * ((columns - 81) // 2)))

    @property
    def connection(self):
        return self._connection
