import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, rate_limit: int, time_window: int):
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.user_access_times = defaultdict(list)

    def is_rate_limited(self, user_id: int) -> bool:
        now = time.time()
        access_times = self.user_access_times[user_id]

        # Remove access times outside the time window
        access_times = [t for t in access_times if now - t < self.time_window]
        self.user_access_times[user_id] = access_times

        # Check if user is rate limited
        if len(access_times) >= self.rate_limit:
            return True

        # Add current access time
        self.user_access_times[user_id].append(now)
        return False
