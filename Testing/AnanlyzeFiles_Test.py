import unittest

import AnanlyzeFiles
from unittest.mock import Mock

class Test_AnalyzeFiles(unittest.TestCase):

    def test_empty_list(self):
        trace_values = []
        actual = AnanlyzeFiles.getfilenames(trace_values)
        self.assertEqual(actual, [])

    def test_one_element_in_list(self):
        trace_values = []
        mock_filename = Mock()
        mock_filename.name = 'test'
        trace_values.append(dict(filename=mock_filename))
        actual = AnanlyzeFiles.getfilenames(trace_values)
        self.assertEqual(actual[0], 'test')

    def test_two_elements_in_list(self):
        trace_values = []
        mock_filename1 = Mock()
        mock_filename1.name = 'test1'
        trace_values.append(dict(filename=mock_filename1))
        mock_filename2 = Mock()
        mock_filename2.name = 'test2'
        trace_values.append(dict(filename=mock_filename2))
        actual = AnanlyzeFiles.getfilenames(trace_values)
        self.assertEqual(actual[0], 'test1')
        self.assertEqual(actual[1], 'test2')
