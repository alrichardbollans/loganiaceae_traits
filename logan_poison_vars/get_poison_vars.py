import os

import pandas as pd
from cleaning import compile_hits
from pkg_resources import resource_filename
from powo_searches import search_powo

from poison_vars import output_nonpoison_csv, output_poison_csv

### Temp outputs
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_powo_search_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'powo_poisons_accepted.csv')

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_logan_poison_csv = os.path.join(_output_path, 'list_of_poisonous_plants.csv')
output_logan_nonpoison_csv = os.path.join(_output_path, 'list_of_nonpoisonous_plants.csv')


def get_powo_poisons():
    search_powo(['poison', 'poisonous', 'toxic', 'deadly'],
                _powo_search_temp_output_accepted_csv,
                families_of_interest=['Loganiaceae'],
                filters=['species', 'infraspecies']
                )


def get_nonpoison_hits():
    non_poisons = pd.read_csv(output_nonpoison_csv, index_col=0)
    non_poisons.to_csv(output_logan_nonpoison_csv)


def get_poison_hits():
    # get_powo_poisons()
    powo_hits = pd.read_csv(_powo_search_temp_output_accepted_csv)

    other_poisons = pd.read_csv(output_poison_csv)
    other_poisons.rename(columns={'Sources': 'Source'}, inplace=True)
    compile_hits(
        [other_poisons, powo_hits],
        os.path.join(_temp_outputs_path, 'output_w_mixed_powo_snippet.csv'))

    # Powo snippets aren't merged correctly, so fix that here
    hits_w_mixed_snippet = pd.read_csv(os.path.join(_temp_outputs_path, 'output_w_mixed_powo_snippet.csv'), index_col=0)
    out_df = hits_w_mixed_snippet
    out_df['powo_Snippet'] = out_df['powo_Snippet_x'].fillna('').astype(str) + out_df['powo_Snippet_y'].fillna(
        '').astype(str)
    out_df.drop(columns=['powo_Snippet_x', 'powo_Snippet_y'], inplace=True)
    out_df.to_csv(output_logan_poison_csv)


if __name__ == '__main__':
    get_poison_hits()
    get_nonpoison_hits()
