from datetime import datetime

class Utils:
	# Gets the elapsed minutes from 'inputTime' until now
	def timeDiff(self, inputTime: datetime) -> int:
		date = inputTime.replace(tzinfo=None)
		now = datetime.utcnow()
		return (now - date).total_seconds() / 60

	# Returns the value of the symbol
	def getSymbol(self, text: str) -> str:
		# Splits the input text "/stock baba" --> ["/stock", "baba"]
		words = text.split()

		# Symbols must be requested as a lowercase string without $ sign
		# "$BABA" bad, "baba" good
		assert len(words) == 2, "Bad command syntax"
		return words[-1].replace('$','').lower()

	def __init__(self):
		pass
