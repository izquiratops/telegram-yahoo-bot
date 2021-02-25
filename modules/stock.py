class Stock:
	def __str__(self):
		return  f"Price: {self.intradayPrice}$\n" \
				f"Change Point: {self.intradayChangePoint}$ " \
				f"({self.intradayChangePercent})"

	def __init__(self, intradayPrice, intradayChangePoint, intradayChangePercent):
		self.intradayPrice         = intradayPrice
		self.intradayChangePoint   = intradayChangePoint
		self.intradayChangePercent = intradayChangePercent
