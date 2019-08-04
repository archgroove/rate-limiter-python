"""
A circular _buffer for storing accesses to a rate limited Flask endpoint

version 0.2
"""

class BufferFullError(Exception):
    pass


class CircularBuffer:

    def __init__(self, maxsize):
        if _maxsize < 1:
            raise ValueError('maxsize must be positive')
        self._maxsize = maxsize
        self.size = 0
        self._start = 0
        self._buffer = [None] * self._maxsize

    def is_full(self):
        return self.size == self._maxsize

    def add_to_end(self, item):
        """Add an item to the end of the buffer"""
        if not is_full():
            index = (self._start + self.size) % self._maxsize
            self._buffer[index] = item
            self.size += 1
        else:
            raise BufferFullError("Cannot add item to a full buffer")

    def remove_from_start(self, n=1):
        """Remove n items from the start of the buffer"""
        if n < 1:
            raise ValueError(f"Must remove a positive number")
        if n > self.size:
            raise IndexError(f"There are only {self.size} items in the buffer")
        self._start = (self._start + n) % self._maxsize
        self.size -= n


    def __getitem__(self, index):
        if index >= self._maxsize:
            raise IndexError(f"Index is out of bounds")
        if index >= self.size:
            raise IndexError(f"There is no item at index {index}")
        underlying_list_index = (self._start + index) % self._maxsize
        return self._buffer[underlying_list_index]
