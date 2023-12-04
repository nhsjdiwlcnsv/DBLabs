from dotenv import load_dotenv, dotenv_values
import psycopg2
import bloodbank
import bloodbank.user


def main():
    config: dict = dotenv_values('.env')

    connection = psycopg2.connect(
        dbname=config.get('DB_NAME'),
        user=config.get('USER'),
        password=config.get('PASSWORD')
    )

    terminal = bloodbank.Terminal(connection)
    user = bloodbank.user.User(terminal)

    while True:
        user.interact()


if __name__ == '__main__':
    load_dotenv()
    main()
