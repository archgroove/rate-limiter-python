"""
A circular buffer for storing accesses to a rate limited Flask endpoint

version 0.1
"""
import datetime


class BufferFullError(Exception):
    pass


class CircularBuffer:

    # TODO make period a datetime.timedelta object
    def __init__(self, rate: int, period):
        """
        :rate: int rate limit
        :period: datetime.timedelta period over which rate limit applies
        """
        self.size = rate
        self.buffer = [None] * size
        self.start = 0
        self.end = 0
        self.n_entries = 0
        self.period = period

    def is_empty(self):
        return self.n_entries == 0

    def is_full(self):
        return self.n_entries == self.size()

    def put(self, timestamp):
        """
        Add an item to the end of the buffer if the rate limit would not
        be exceeded
        """
        if not isinstance(timestamp, datetime.datetime):
            raise ValueError("Buffer only accepts timestamps")

        if timestamp < self.newest:
            raise ValueError("New entry must not be earlier than the newest entry")

        if self.start == self.end:
            # Examples
            # [None(S,E), None, None, None, None, None, None, None]
            assert self.n_entries + 1 <= self.size, 'n_entries cannot be greater than size'
            self.buffer[self.start] = timestamp
            self.n_entries += 1
        elif not self.is_full():
            # Examples
            # [0m (S), 1m, 2m, 3m, 4m, 5m, 6m (E), None]
            # [8m, 9m (E), None, 3m (S), 4m, 5m, 6m]
            # [None, 8m (S), 9m, 10m, 11m, 12m, 13m (E)]
            # Put the next entry at the end of the buffer
            assert self.n_entries + 1 <= self.size, 'n_entries cannot be greater than size'
            next_position = self.end + 1 % self.size
            self.buffer[next_position] = timestamp
            self.end = next_position
            self.n_entries += 1
        else:
            # Examples
            # [0m (S), 1m, 2m, 3m, 4m, 5m, 6m, 7m (E)]
            # [8m, 9m (E), 2m (S), 3m, 4m, 5m, 6m, 7m]
            # Replace the oldest entry with the new entry if the oldest is expired
            if not self.oldest < timestamp - self.period:
                s = self.seconds_remaining()
                raise BufferFullError(f"Rate limit exceeded, cannot add timestamp to buffer. {s} seconds remaining")
            self.oldest = timestamp
            self.end = next_position
            self.start += 1  # the index of the oldest entry

    @property
    def oldest(self):
        if self.is_empty():
            return None
        return self.buffer[self.start]

    @property
    def newest(self):
        if self.is_empty():
            return None
        return self.buffer[self.end]

    def seconds_remaining(self):
        """
        Return the number of seconds remaining until the endpoint can be accessed
        again.
        """
        if not self.is_full():
            return 0

        # Buffer is full but oldest access is outside the rate limited period
        # One could also add a cleanup step here that removes stale entries
        # from the buffer. This would slow things down slightly but make the
        # buffer more useful for analytics.
        if self.oldest < datetime.datetime.now() - self.period:
            return 0

        # Buffer is full and oldest access is within the rate limited period
        else:
            time_remaining = (self.oldest + self.period) - datetime.datetime.now()
            return time_remaining.total_seconds()
