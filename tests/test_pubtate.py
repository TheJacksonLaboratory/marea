import unittest
from click.testing import CliRunner
from scripts.pubtate import REPLACED_FILENAME
from scripts.pubtate import fix_concept_ids, main


class PubtateTestCase(unittest.TestCase):

    def test_fix_concept_ids(self):
        self.assertEqual(' NCBIGene1019  NCBIGene1021 ',
                         fix_concept_ids('Gene', '1019;1021'),
                         'Unexpected result for multiple gene ids separated by semicolon.')
        self.assertEqual(' MESHD012175 ', fix_concept_ids('Disease', 'MESH:D012175'),
                         'Unexpected result for MeSH id.')

    def test_selective_replacement(self):
        cset_path = 'testdata/pubtator_test_csets/conceptSet.tsv'
        input_dir = 'testdata/pubtator_test_csets/'
        desired_file = 'bioconcepts2pubtatorcentral.target'
        runner = CliRunner()
        result = runner.invoke(main, ['-i', input_dir, '-o', None, '-c', cset_path])
        self.assertEqual(0, result.exit_code, f"Exit code is {result.exit_code}.")
        with open(input_dir + desired_file,'r') as target:
            target_lines = target.readlines()
            with open(input_dir + REPLACED_FILENAME,'r') as actual:
                actual_lines = actual.readlines()
                target_len = len(target_lines)
                actual_len = len(actual_lines)
                self.assertEqual(target_len, actual_len,
                                 'Output file length does not match expected')
                lines_match = True
                for i in range(target_len):
                    if actual_lines[i] != target_lines[i]:
                        lines_match = False
                        print(f"Target and actual output differ at line {i + 1}")
                        print('Target: ' + target_lines[i])
                        print('Actual: ' + actual_lines[i])
                self.assertTrue(lines_match)


if __name__ == '__main__':
    unittest.main()
