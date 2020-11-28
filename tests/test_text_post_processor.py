import unittest
from scripts.text_post_processor import TextPostProcessor


class TextPostProcessorTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        tp = TextPostProcessor('testdata/nltk_data/')

    def test_lowercase_first(self):
        self.assertEqual('rEP-b', TextPostProcessor.lowercase_first('REP-b'))
        self.assertEqual('bound', TextPostProcessor.lowercase_first('bound'))
        self.assertEqual('', TextPostProcessor.lowercase_first(''))

    def test_remove_stopwords(self):
        # a sentence after concept replacement
        before = ''.join(['The inhibition of binding for  NCBIGene106478911  ',
                          'and DHT by  NCBIGene106478911 ,  MESHD013739  (T),',
                          '  MESHD013196 , dehydroepiandosterone (DHEA),  ',
                          'MESHD019314  ( NCBIGene6822 ),  MESHD000735  (A) ',
                          'and 5-androstene-3beta, 17beta-diol (Adiol) was ',
                          'tested with the use of  MESHD003911 -coated charcoal',
                          ' separation of bound and free  NCBIGene106478911 , ',
                          'respectively, and  MESHD013196 .'])
        # remove_stop_words calls nltk.word_tokenize, which adds space around
        # punctuation.
        after = ''.join(['inhibition binding NCBIGene106478911 ',
                         'DHT NCBIGene106478911 , MESHD013739 ( ) ,',
                         ' MESHD013196 , dehydroepiandosterone ( DHEA ) , ',
                         'MESHD019314 ( NCBIGene6822 ) , MESHD000735 ( ) ',
                         '5-androstene-3beta , 17beta-diol ( Adiol ) ',
                         'tested use MESHD003911 coated charcoal ',
                         'separation bound free NCBIGene106478911 , ',
                         'respectively , MESHD013196 .'])
        self.assertEqual(after, TextPostProcessor.remove_stop_words(before))
        before = ''.join(['Outcomes of unrelated cord blood transplantation in ',
                          'pediatric recipients. We report results of unrelated',
                          'cord blood transplants (UCBT) in 29 pediatric ',
                          'recipients in one center and the risk factors ',
                          'associated with survival. Median age: 9 years ',
                          '(0.5-20); diagnosis: ALL (9), MESHD015470 (4), ',
                          'MESHD015464 (1), MESHD006816 (3), HLH (1), ',
                          'MESHD008228 (3), NCBIGene9253 (2); B-thal (1), ',
                          'FA (1), FEL (1), Krabbe (1), WAS (1), SAA (1).'])
        after = ''.join(['Outcomes unrelated cord blood transplantation ',
                         'pediatric recipients . report results unrelated',
                         'cord blood transplants ( UCBT ) 29 pediatric ',
                         'recipients one center risk factors ',
                         'associated survival . Median age : 9 years ',
                         '( 0.5-20 ) ; diagnosis : ALL ( 9 ) , MESHD015470 ( 4 ) , ',
                         'MESHD015464 ( 1 ) , MESHD006816 ( 3 ) , HLH ( 1 ) , ',
                         'MESHD008228 ( 3 ) , NCBIGene9253 ( 2 ) ; B-thal ( 1 ) , ',
                         'FA ( 1 ) , FEL ( 1 ) , Krabbe ( 1 ) , WAS ( 1 ) , SAA ( 1 ) .'])
        self.assertEqual(after, TextPostProcessor.remove_stop_words(before))
        before = ''.join(["A Neurologist 's Perspective on Thymectomy for ",
                          'MESHD009157 : Current Perspective and Future Trials'
                          '. The first randomized blinded study of thymectomy '
                          'in MESHD009157 was designed to answer 3 questions.'])
        after = ''.join(["Neurologist Perspective Thymectomy ",
                         'MESHD009157 : Current Perspective Future Trials '
                         '. first randomized blinded study thymectomy '
                         'MESHD009157 designed answer 3 questions .'])
        self.assertEqual(after, TextPostProcessor.remove_stop_words(before))
        before = ''.join(['A side effect of  NCBIGene1440 -mild  MESHD010146',
                          ' -was observed in one patient, but it was ',
                          'tolerable.'])
        after = ''.join(['side effect NCBIGene1440 mild MESHD010146',
                         ' observed one patient , ',
                         'tolerable .'])
        self.assertEqual(after, TextPostProcessor.remove_stop_words(before))
        before = ''.join(['RESULTS: High levels of NCBIGene4137 -A and ',
                          'NCBIGene4137 -C (above the median) in blood were ',
                          'associated with lower risk of MESHD003704 and '
                          'MESHD000544 ( NCBIGene4137 -A: MESHD003704 [95% ',
                          'CI] = 0.85[0.70-1.04]; MESHD000544 0.71[0.52-0.98]',
                          'and NCBIGene4137 -C: Dementia 0.84[0.70-1.00]; ',
                          'MESHD000544 0.78[0.60-1.03]).'])
        after = ''.join(['RESULTS : High levels NCBIGene4137 ',
                         'NCBIGene4137 ( median ) blood ',
                         'associated lower risk MESHD003704 '
                         'MESHD000544 ( NCBIGene4137 : MESHD003704 [ 95 % CI ]',
                         ' = 0.85 [ 0.70-1.04 ] ; MESHD000544 0.71 [ 0.52-0.98',
                         ' ] NCBIGene4137 : Dementia 0.84 [ 0.70-1.00 ] ; ',
                         'MESHD000544 0.78 [ 0.60-1.03 ] ) .'])
        self.assertEqual(after, TextPostProcessor.remove_stop_words(before))

    def test_remove_edge_hyphen(self):
        self.assertEqual('REP-b', TextPostProcessor.remove_edge_hyphen('-REP-b'))
        self.assertEqual('anti', TextPostProcessor.remove_edge_hyphen('anti-'))
        self.assertEqual('NO', TextPostProcessor.remove_edge_hyphen('-NO-'))
        self.assertEqual('group', TextPostProcessor.remove_edge_hyphen('group'))
        self.assertEqual('-10', TextPostProcessor.remove_edge_hyphen('-10'))


if __name__ == '__main__':
    unittest.main()
