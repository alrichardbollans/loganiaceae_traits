import unittest

import pandas as pd

from logan_common_name_vars import output_logan_common_names_csv
from unittests import confirming_hits


class MyTestCase(unittest.TestCase):
    def test_hits(self):
        p = confirming_hits()
        hits = pd.read_csv(output_logan_common_names_csv, index_col=0)
        p.confirm_hit('Strychnos nux-vomica', hits)
        p.confirm_hit('Canscora diffusa', hits)
        p.confirm_hit('Canscora alata', hits)


        p.confirm_no_hit('Gentianella quinquefolia', hits)
        p.confirm_no_hit('Bonyunia antoniifolia', hits)



if __name__ == '__main__':
    unittest.main()
