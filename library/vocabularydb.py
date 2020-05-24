import pg8000
import slackbot_settings as conf


class VocabularyDatabase:
    """パワーワードを扱うDBを操作するためのクラス"""

    def __init__(self):
        try:
            pg8000.paramstyle = 'qmark'
            self.conn = pg8000.connect(
                host=conf.DB_HOST,
                user=conf.DB_USER,
                password=conf.DB_PASSWORD,
                port=conf.DB_PORT,
                ssl_context=conf.DB_SSL,
                database=conf.DB_NAME
            )
        except:
            print('Can not connect to database.')

    def __enter__(self):
        return self

    def get_word_list(self):
        """パワーワードの一覧をDBから取得する"""
        with self.conn.cursor() as cursor:
            try:
                cursor.execute("SELECT no, word FROM vocabulary ORDER BY no;")
                results = cursor.fetchall()
            except:
                print('Can not execute sql(select_list).')

        return results

    def get_random_word(self):
        """パワーワードをDBからランダムで取得する"""

        with self.conn.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT word FROM vocabulary ORDER BY random() LIMIT 1;")
                results = cursor.fetchone()
            except:
                print('Can not execute sql(select_random).')

        return results

    def add_word(self, word) -> None:
        """パワーワードをDBに登録する"""

        with self.conn.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO vocabulary(word) VALUES(?);", (word,))
                self.conn.commit()
            except:
                print('Can not execute sql(add).')

    def delete_word(self, id) -> None:
        """指定したidのパワーワードをDBから削除する"""

        with self.conn.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM vocabulary WHERE no = ?;", (id,))
                self.conn.commit()
            except:
                print('Can not execute sql(delete).')

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()


def get_vocabularys():
    """一覧を表示する"""

    with VocabularyDatabase() as z:
        result = z.get_word_list()

    if 0 < len(result):
        slack_msg = "```"

        # SELECTした順に連番を振る。
        cnt = 1
        for row in result:
            no, text = row
            slack_msg = slack_msg + '\n {0}. {1}'.format(cnt, text)
            cnt += 1

        slack_msg = slack_msg + "```"

        return slack_msg
    else:
        return "登録されている単語はないっぽ！"


def add_vocabulary(msg) -> None:
    """追加する"""

    with VocabularyDatabase() as vd:
        vd.add_word(msg)


def show_vocabulary(id) -> str:
    """指定したものを表示する"""

    slack_msg = "該当する番号は見つからなかったっぽ!"

    with VocabularyDatabase() as vd:
        result = vd.get_word_list()

    cnt = 1
    for row in result:
        no, text = row
        if cnt == id:
            slack_msg = '{}'.format(text)
        cnt += 1

    return slack_msg


def show_random_vocabulary() -> str:
    """ランダムに一つ表示する"""

    slack_msg = "鳩は唐揚げ！！"

    with VocabularyDatabase() as vd:
        result = vd.get_random_word()

    if result is not None and len(result) > 0:
        slack_msg = '{}'.format(result[0])

    return slack_msg


def delete_vocabulary(id) -> str:
    """削除する"""

    slack_msg = "該当する番号は見つからなかったっぽ!"

    with VocabularyDatabase() as vd:
        result = vd.get_word_list()
        cnt = 1
        for row in result:
            no, text = row
            if cnt == id:
                delete_id = no
                vd.delete_word(delete_id)
                slack_msg = "忘れたっぽ!"
                break
            cnt += 1

    return slack_msg
