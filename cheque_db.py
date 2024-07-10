import sqlite3
class ChequeGiveawayRecord:
    def __init__(self, chat_id, type_link, link):
        self.chat_id = chat_id
        self.type_link = type_link
        self.link = link
class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.create_table_if_not_exists()
    def create_table_if_not_exists(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ChequeGiveaway (
                            chat_id INTEGER,
                            type_link TEXT,
                            link TEXT UNIQUE
                          )''')
        self.conn.commit()
    def add_cheque_giveaway_record(self, item) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM ChequeGiveaway WHERE link=? LIMIT 1", (item.link,))
        existing_link = cursor.fetchone()
        if existing_link is None:
            cursor.execute('''INSERT INTO ChequeGiveaway (chat_id, type_link, link)
                                  VALUES (?, ?, ?)''', (item.chat_id, item.type_link, item.link))
            self.conn.commit()
            return True
        else:
            return False

    def get_all_links(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT link FROM ChequeGiveaway")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    def close_connection(self):
        self.conn.close()



if __name__ == "__main__":
    # Example usage
    db_manager = DatabaseManager("cheque.db")
    record = ChequeGiveawayRecord(123, 'example', 'http://example.com')
    db_manager.add_cheque_giveaway_record(record)
    db_manager.close_connection()