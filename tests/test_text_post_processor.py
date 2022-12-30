import unittest
from scripts.text_post_processor import TextPostProcessor


class TextPostProcessorTestCase(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     tp = TextPostProcessor('testdata/nltk_data/')

    def test_lowercase_first(self):
        self.assertEqual('rEP-b', TextPostProcessor.lowercase_first('REP-b'))
        self.assertEqual('bound', TextPostProcessor.lowercase_first('bound'))
        self.assertEqual('', TextPostProcessor.lowercase_first(''))

    def test_process_phrase_report_lexicon(self):
        tp = TextPostProcessor('testdata/nltk_data/')
        # a sentence after concept replacement
        before = ''.join(['The inhibition of binding for  NCBIGene106478911  ',
                          'and DHT by  NCBIGene106478911 ,  MESHD013739  (T),',
                          '  MESHD013196 , dehydroepiandosterone (DHEA),  ',
                          'MESHD019314  ( NCBIGene6822 ),  MESHD000735  (A) ',
                          'and 5-androstene-3beta, 17beta-diol (Adiol) was ',
                          'tested with the use of  MESHD003911 -coated charcoal',
                          ' separation of bound and free  NCBIGene106478911 , ',
                          'respectively, and  MESHD013196 .'])
        after = ''.join(['inhibition binding ncbigene106478911 ',
                         'dht ncbigene106478911 meshd013739',
                         ' meshd013196 dehydroepiandosterone dhea ',
                         'meshd019314 ncbigene6822 meshd000735 ',
                         '5 androstene diol adiol ',
                         'test use meshd003911 coat charcoal ',
                         'separation bound free ncbigene106478911 ',
                         'respectively meshd013196'])
        self.assertEqual(after, tp.process_phrase(before))
        before = ''.join(['Outcomes of unrelated cord blood transplantation in ',
                          'pediatric recipient. We report results of unrelated',
                          ' cord blood transplants (UCBT) in 29 pediatric ',
                          'recipients in one center and the risk factors ',
                          'associated with survival. Median age: 9 years ',
                          '(0.5-20); diagnosis: ALL (9),  MESHD015470  (4),  ',
                          'MESHD015464  (1),  MESHD006816  (3), HLH (1),  ',
                          'MESHD008228  (3),  NCBIGene9253  (2); B-thal (1), ',
                          'FA (1), FEL (1), Krabbe (1), WAS (1), SAA (1).'])
        after = ''.join(['outcome unrelated cord blood transplantation ',
                         'pediatric recipient report result unrelated',
                         ' cord blood transplant ucbt pediatric ',
                         'recipient one center risk factor ',
                         'associate survival median age 9 year ',
                         '0 5 diagnosis all 9 meshd015470 4 ',
                         'meshd015464 1 meshd006816 3 hlh 1 ',
                         'meshd008228 3 ncbigene9253 2 thal 1 ',
                         'fa 1 fel 1 krabbe 1 was 1 saa 1'])
        self.assertEqual(after, tp.process_phrase(before))
        before = ''.join(["A Neurologist's Perspective on Thymectomy for  ",
                          'MESHD009157 : Current Perspective and Future Trials'
                          '. The first randomized blinded study of thymectomy '
                          'in  MESHD009157  was designed to answer 3 '
                          'questions.'])
        after = ''.join(["neurologist perspective thymectomy ",
                         'meshd009157 current perspective future trial '
                         'first randomize blind study thymectomy '
                         'meshd009157 design answer 3 '
                         'question'])
        self.assertEqual(after, tp.process_phrase(before))
        before = ''.join(['A side effect of  NCBIGene1440 -mild  MESHD010146',
                          ' -was observed in one patient, but it was assess ',
                          'tolerable.'])
        after = ''.join(['side effect ncbigene1440 mild meshd010146',
                         ' observe one patient ass ',
                         'tolerable'])
        self.assertEqual(after, tp.process_phrase(before))
        before = ''.join(['RESULTS: High levels of  NCBIGene4137 -A and  ',
                          'NCBIGene4137 -C (above the median) in blood were ',
                          'associates with lower risk of  MESHD003704  and  '
                          'MESHD000544  ( NCBIGene4137 -A:  MESHD003704 [95% ',
                          'CI] = 0.85[0.70-1.04];  MESHD000544  0.71[0.52-0.98]',
                          ' and  NCBIGene4137 -C: Dementia 0.84[0.70-1.00];  ',
                          'MESHD000544  0.78[0.60-1.03]).'])
        after = ''.join(['results high level ncbigene4137 ',
                         'ncbigene4137 median blood ',
                         'associate low risk meshd003704 '
                         'meshd000544 ncbigene4137 meshd003704 95 ',
                         'ci 0 0 1 meshd000544 0 0 0 ',
                         'ncbigene4137 dementia 0 0 1 ',
                         'meshd000544 0 0 1'])
        self.assertEqual(after, tp.process_phrase(before))
        tp.report_lexicon("testdata/lexicons")


if __name__ == '__main__':
    unittest.main()
