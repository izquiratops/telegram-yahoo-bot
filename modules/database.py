import sqlite3

class Database:
	def insertFavorite(self, userId: int, sym: str) -> None:
		with sqlite3.connect('dbname.db') as conn:
			cur = conn.cursor()
			try:
				cur.execute(f"INSERT INTO favorites VALUES('{userId}', '{sym}')")
			except:
				raise AssertionError('There\'s already added')

			# Save state
			conn.commit()

	def deleteFavorite(self, userId: int, sym: str) -> None:
		with sqlite3.connect('dbname.db') as conn:
			cur = conn.cursor()
			try:
				cur.execute(f"DELETE FROM favorites WHERE userId={userId} AND sym='{sym}'")
			except:
				raise

			# Save state
			conn.commit()

	def getFavorites(self, userId: int) -> list:
		with sqlite3.connect('dbname.db') as conn:
			cur = conn.cursor()
			cur.execute(f"SELECT sym FROM favorites WHERE userId='{userId}'")
			fetch = cur.fetchall()
			assert len(fetch) > 0, 'Empty list'

			return fetch

	def __init__(self):
		with sqlite3.connect('dbname.db') as conn:
			cur = conn.cursor()
			cur.execute('CREATE TABLE IF NOT EXISTS favorites (userId real, sym text, UNIQUE(userId, sym))')
			conn.commit()
