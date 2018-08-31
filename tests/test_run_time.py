
import os
import unittest

class MyTest(unittest.TestCase):
    def test(self):
        os.system('./runAll.sh spark')


unittest.main()
