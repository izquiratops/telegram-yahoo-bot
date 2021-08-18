from datetime import time
from pytz import timezone

MADRID = timezone('Europe/Madrid')

# Early Trading Session: 7:00 a.m. to 9:30 a.m. ET
# Open 11:00 UTC (13:00 GMT+2)
EARLY_OPEN_MARKET = time(hour=11, minute=00, second=00, tzinfo=MADRID)
# Close 13:30 UTC (15:30 GMT+2)
EARLY_CLOSE_MARKET = time(hour=13, minute=30, second=00, tzinfo=MADRID)

# Core Trading Session: 9:30 a.m. to 4:00 p.m. ET
# Open 13:30 UTC (15:30 GMT+2)
CORE_OPEN_MARKET = time(hour=13, minute=30, second=00, tzinfo=MADRID)
# Close 20:00 UTC (22:00 GMT+2)
CORE_CLOSE_MARKET = time(hour=20, minute=00, second=00, tzinfo=MADRID)

# Late Trading Session: 4:00 p.m. to 8:00 p.m. ET
# Open 20:00 UTC (22:00 GMT+2)
LATE_OPEN_MARKET = time(hour=20, minute=00, second=00, tzinfo=MADRID)
# Close 00:00 UTC (02:00 GMT+2)
LATE_CLOSE_MARKET = time(hour=00, minute=00, second=00, tzinfo=MADRID)
