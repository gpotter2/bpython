from code import compile_command as compiler
from functools import partial
import difflib
import inspect
import re
import unittest

try:
    import unittest2 as unittest
except ImportError:
    import unittest
skip = unittest.skip

from bpython.curtsiesfrontend.interpreter import code_finished_will_parse
from bpython.curtsiesfrontend.preprocess import indent_empty_lines

from bpython.test.fodder import original as original, processed

indent_empty = partial(indent_empty_lines, compiler=compiler)


def get_fodder_source(test_name):
    pattern = r'#StartTest-%s\n(.*?)#EndTest' % (test_name,)
    orig, xformed = [re.search(pattern, inspect.getsource(module), re.DOTALL)
                     for module in [original, processed]]

    if not orig:
        raise ValueError("Can't locate test %s in original fodder file" % (test_name,))
    if not xformed:
        raise ValueError("Can't locate test %s in processed fodder file" % (test_name,))
    return orig.group(1), xformed.group(1)


class TestPreprocessing(unittest.TestCase):

    def assertCompiles(self, source):
        finished, parsable = code_finished_will_parse(source, compiler)
        return finished and parsable

    def test_indent_empty_lines_nops(self):
        self.assertEqual(indent_empty('hello'), 'hello')
        self.assertEqual(indent_empty('hello\ngoodbye'), 'hello\ngoodbye')
        self.assertEqual(indent_empty('a\n    b\nc\n'), 'a\n    b\nc\n')

    def assertShowWhitespaceEqual(self, a, b):
        self.assertEqual(
            a, b,
            ''.join(difflib.context_diff(a.replace(' ', '~').splitlines(True),
                                         b.replace(' ', '~').splitlines(True),
                                         fromfile='actual',
                                         tofile='expected',
                                         n=5)))

    def assertDefinitionIndented(self, obj):
        name = obj.__name__
        obj2 = getattr(processed, name)
        orig = inspect.getsource(obj)
        xformed = inspect.getsource(obj2)
        self.assertShowWhitespaceEqual(indent_empty(orig), xformed)
        self.assertCompiles(xformed)

    def assertLinesIndented(self, test_name):
        orig, xformed = get_fodder_source(test_name)
        self.assertShowWhitespaceEqual(indent_empty(orig), xformed)
        self.assertCompiles(xformed)

    def assertIndented(self, obj_or_name):
        if isinstance(obj_or_name, str):
            self.assertLinesIndented(obj_or_name)
        else:
            self.assertDefinitionIndented(obj_or_name)

    def test_empty_line_between_methods(self):
        self.assertIndented(original.BlankLineBetweenMethods)

    def test_empty_line_within_class(self):
        self.assertIndented(original.BlankLineInFunction)

    def test_blank_lines_in_for_loop(self):
        self.assertIndented('blank_lines_in_for_loop')

    @skip("More advanced technique required: need to try compiling and backtracking")
    def test_blank_line_in_try_catch(self):
        self.assertIndented('blank_line_in_try_catch')

    @skip("More advanced technique required: need to try compiling and backtracking")
    def test_blank_line_in_try_catch_else(self):
        self.assertIndented('blank_line_in_try_catch_else')

    def test_blank_trailing_line(self):
        self.assertIndented('blank_trailing_line')