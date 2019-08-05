import unittest
from circular_buffer import CircularBuffer, BufferFullError

class TestCircularBuffer(unittest.TestCase):

    def _nearly_full_buffer(self):
        cb = CircularBuffer(5)
        cb.add_to_end('a')
        cb.add_to_end('b')
        cb.add_to_end('c')
        cb.add_to_end('d')
        return cb

    def _full_buffer(self):
        cb = CircularBuffer(5)
        cb.add_to_end('a')
        cb.add_to_end('b')
        cb.add_to_end('c')
        cb.add_to_end('d')
        cb.add_to_end('e')
        return cb

    def test_init_zero_length_buffer_fails(self):
        self.assertRaises(ValueError, CircularBuffer, 0)

    def test_add_to_empty_succeeds(self):
        cb = CircularBuffer(1)
        cb.add_to_end('a')
        self.assertEqual('a', cb[0])
        self.assertEqual(1, cb.size)

    def test_add_to_not_full_succeeds(self):
        cb = self._nearly_full_buffer()
        cb.add_to_end('e')
        self.assertEqual('e', cb[4])
        self.assertEqual(5, cb.size)

    def test_add_to_not_full_wrapped_succeeds(self):
        cb = self._full_buffer()
        cb.remove_from_start(1)
        cb.add_to_end('f')
        self.assertEqual('f', cb[4])

    def test_add_to_full_fails(self):
        cb = self._full_buffer()
        self.assertRaises(BufferFullError, cb.add_to_end, 'f')
        self.assertEqual(5, cb.size)

    def test_remove_too_many_fails(self):
        cb = self._full_buffer()
        self.assertRaises(IndexError, cb.remove_from_start, 6)
        self.assertEqual(5, cb.size)

    def test_remove_negatory_fails(self):
        cb = self._full_buffer()
        self.assertRaises(ValueError, cb.remove_from_start, -1)
        self.assertEqual(5, cb.size)

    def test_remove_from_existing_succeeds(self):
        cb = self._full_buffer()
        cb.remove_from_start(1)
        self.assertEqual(4, cb.size)

    def test_is_full_when_full(self):
        cb = self._full_buffer()
        self.assertTrue(cb.is_full())

    def test_not_is_full_when_not_full(self):
        cb = self._nearly_full_buffer()
        self.assertFalse(cb.is_full())

    def test_getitem_wrapped(self):
        cb = self._full_buffer()
        cb.remove_from_start()
        cb.add_to_end('f')
        self.assertEqual('f', cb[4])

    def test_getitem_not_wrapped(self):
        cb = self._full_buffer()
        self.assertEqual('e', cb[4])

    def test_getitem_negative_fails(self):
        cb = self._full_buffer()
        self.assertRaises(IndexError, cb.__getitem__, -1)

    def test_getitem_out_of_bounds_fails(self):
        cb = self._full_buffer()
        self.assertRaises(IndexError, cb.__getitem__, 5)
