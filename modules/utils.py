from datetime import datetime

class Utils:
	# Gets the elapsed minutes from 'inputTime' until now
	def timeDiff(self, inputTime: datetime) -> int:
		date = inputTime.replace(tzinfo=None)
		now = datetime.utcnow()
		return (now - date).total_seconds() / 60

	def __init__(self):
		pass
