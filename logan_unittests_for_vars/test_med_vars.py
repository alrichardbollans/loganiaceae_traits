import unittest

import pandas as pd

from logan_medicinal_usage_vars import output_logan_medicinal_csv, output_logan_malarial_csv
from unit_test_methods import confirming_hits


class MyTestCase(unittest.TestCase):
    def test_medicinal_hits(self):
        p = confirming_hits()
        hits = pd.read_csv(output_logan_medicinal_csv, index_col=0)
        p.confirm_hit('Spigelia hamellioides', hits)
        p.confirm_no_hit('a', hits)
        p.confirm_powo_hit('Spigelia hamellioides', hits)


        p.confirm_hit('Spigelia palmeri', hits)
        p.confirm_hit('Strychnos congolana', hits)

    def test_antimal_hits(self):
        p = confirming_hits()
        hits = pd.read_csv(output_logan_malarial_csv, index_col=0)

        p.confirm_hit('Strychnos potatorum', hits)
        p.confirm_hit('Strychnos aculeata', hits)
        p.confirm_hit('Strychnos lucida', hits)
        p.confirm_hit('Strychnos henningsii', hits)


if __name__ == '__main__':
    unittest.main()
