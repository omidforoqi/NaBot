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
        articles_id_query = "select id from articles"
        articles_user_seen_query = "select article_id from summarization where user_name=%s"
        article_return_query = "select article from articles where id=%s"
        summary_return_query = "select highlights from articles where id=%s"
        article, highlights, article_id = "", "", ""
        try:
            cursor = self.db.cursor()

            cursor.execute(articles_id_query)
            articles_id = cursor.fetchall()
            articles_id = set([item[0] for item in articles_id])
            cursor.execute(articles_user_seen_query, (username,))
            user_seen_article_id = cursor.fetchall()
            user_seen_article_id = set([item[0] for item in user_seen_article_id])
            article_id = tuple(articles_id.difference(user_seen_article_id))
            if len(article_id) > 0:
                article_id = article_id[0]
                cursor.execute(article_return_query, (article_id,))
                article = cursor.fetchone()
                article = next(iter(article)) if article else ""
                cursor.execute(summary_return_query, (article_id,))
                highlights = cursor.fetchone()
                highlights = next(iter(highlights)) if article else ""            
        finally:
            cursor.close()
        return article, highlights, article_id

    def write_record(self, username: str, feedback: bool, user_summary: Union[str, None], article_id: str):
        query = "insert into summarization (user_name, feedback, user_summary, article_id) \
VALUES(%s, %s, %s, %s)"
        try:
            cursor = self.db.cursor()
            cursor.execute(query, (username, feedback, user_summary, article_id))
            self.db.commit()
        finally:
            cursor.close()
