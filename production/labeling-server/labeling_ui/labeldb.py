from typing import Union
import psycopg2
from psycopg2 import OperationalError


class Labeling:
    def __init__(self, db_name, db_user, db_password, db_host, db_port) -> None:
        super(Labeling, self).__init__()
        # Connect to the postgresql server
        try:
            self.db = psycopg2.connect(
                database=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
            )
        except OperationalError as e:
            print(f"The error '{e}' occurred")

    def login_user(self, username: str, passwd: str) -> bool:
        user_query: str = "SELECT username FROM accounts WHERE username=%s"
        passwd_query: str = "SELECT password FROM accounts WHERE username=%s"
        login_successfully = False
        try:
            cursor = self.db.cursor()
            cursor.execute(user_query, (username,))
            usernamedata = cursor.fetchone()
            cursor.execute(passwd_query, (username,))
            passworddata = cursor.fetchone()

            usernamedata = next(iter(usernamedata)) if usernamedata else None
            passworddata = next(iter(passworddata)) if passworddata else None
            if usernamedata == username and passwd == passworddata:
                login_successfully = True
        finally:
            cursor.close()

        return login_successfully

    def give_record(self, username: str):
        article_query = "select articles.article \
from articles, summarization as summ \
where not articles.highlights=summ.summary and not summ.user_name=%s"

        highlights_query = "select articles.highlights \
from articles, summarization as summ \
where not articles.highlights=summ.summary and not summ.user_name=%s"
        try:
            cursor = self.db.cursor()
            cursor.execute(article_query, (username,))
            article = cursor.fetchone()
            cursor.execute(highlights_query, (username,))
            highlights = cursor.fetchone()
            article = next(iter(article)) if article else ""
            highlights = next(iter(highlights)) if article else ""

            return article, highlights
        finally:
            cursor.close()

    def write_record(self, username: str, summary: str, feedback: bool, user_summary: Union[str, None]):
        query = "insert into summarization (user_name, summary, feedback, user_summary) \
VALUES(%s, %s, %s, %s)"
        try:
            cursor = self.db.cursor()
            cursor.execute(query, (username, summary, feedback, user_summary))
        finally:
            cursor.close()
