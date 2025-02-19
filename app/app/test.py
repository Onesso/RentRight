"""we'll be using the simpleTestcase since the codee does not have a database."""

from django.test import SimpleTestCase
from app import calc
from app.calc import subtract

class TestCalc(SimpleTestCase):
    """testing the calc function"""
    def test_add(self):
        responce = calc.add(3,8)
        self.assertEqual(responce, 11)

    def test_subtract(self):
       responce = calc.subtract(10, 5) 
       self.assertEqual(responce, 5)
