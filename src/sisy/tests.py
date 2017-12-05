from django.test import TestCase as DjangoTestCase
from unittest import TestCase as PythonTestCase
from sisy.models import func_from_string, Task

class TestFuncFromString(DjangoTestCase):
    def test_real_single_module(self):
        with self.assertRaises(ValueError, msg="Need full dotted path to task function"):
            func_from_string('sisy')

    def test_bogus_single_module(self):
        with self.assertRaises(ValueError, msg='Need full dotted path to task function'):
            func_from_string('bogus')

    def test_bogus_dual_module(self):
        with self.assertRaisesRegex(ValueError, r'Module .*? not found'):
            func_from_string('bogus.foo')

    def test_real_dual_module(self):
        with self.assertRaises(ValueError, msg="Cannot call module directly"):
            func_from_string('sisy.models')

    def test_bare_class(self):
        with self.assertRaises(ValueError, msg="Cannot call class directly"):
            func_from_string('sisy.models.Task')

    def test_wrong_sig(self):
        with self.assertRaises(ValueError, msg="Improper signature for task function(needs only \'message\')"):
            func_from_string('sisy.models.Task.run_once')

    def test_instance_method(self):
        with self.assertRaises(ValueError, msg="Cannot call module directly"):
            func_from_string('sisy.models.Task.calc_next_run')

    def test_non_function(self):
        with self.assertRaisesRegex(ValueError, r'.*? \(.*?\) is not a callable object'):
            func_from_string('sisy.models.Task.created_at')


