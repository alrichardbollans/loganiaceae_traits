import os

import numpy as np
import pandas as pd
from pkg_resources import resource_filename

from large_file_storage import large_folders
from climate_vars import initial_climate_vars, renaming

_inputs_path = os.path.join(large_folders, 'occ_climate_vars/')
logan_input_occurrences_with_clim_vars_csv = os.path.join(_inputs_path, 'logan_occ_with_climate_vars.csv')

_output_path = resource_filename(__name__, 'outputs')
logan_compiled_climate_vars_csv = os.path.join(_output_path, 'compiled_climate_vars.csv')

if not os.path.isdir(_output_path):
    os.mkdir(_output_path)

_climate_names = initial_climate_vars + ['koppen_geiger_mode',
                                         'koppen_geiger_all']
_climate_names.remove('Beck_KG_V1_present')


def get_climate_df():
    acc_columns = ['Accepted_Name', 'Accepted_Species', 'Accepted_Species_ID',
                   'Accepted_ID', 'Accepted_Rank']
    columns_to_import = initial_climate_vars + acc_columns

    occ_df = pd.read_csv(logan_input_occurrences_with_clim_vars_csv)[columns_to_import]

    dfs = []

    grouped = occ_df.groupby('Accepted_ID')
    for c in initial_climate_vars:
        # We take median of occurrences in order to mitigate outliers
        # This still has the possible issue of being biased towards where people take samples
        avg = pd.DataFrame(grouped[c].median())

        dfs.append(avg)

    for df in dfs:
        if len(df) != len(dfs[0]):
            print(len(df))
            print(len(dfs[0]))
            raise ValueError
    merged = pd.merge(dfs[0], dfs[1], on='Accepted_ID')
    for i in range(len(dfs)):
        if i > 1:
            merged = pd.merge(merged, dfs[i], on='Accepted_ID')

    # Get mode of koppengeiger classification.
    # In case of multiple modes, select one at random
    merged['koppen_geiger_mode'] = occ_df.groupby(['Accepted_ID'])['Beck_KG_V1_present'].agg(
        lambda x: np.random.choice(x.mode(dropna=True)))

    merged['koppen_geiger_all'] = occ_df.groupby(['Accepted_ID'])[
        'Beck_KG_V1_present'].unique().apply(
        list).values

    merged.drop(columns='Beck_KG_V1_present', inplace=True)

    # Get accepted info back from occurrences
    merged.reset_index(inplace=True)
    merged = merged.rename(columns={'index': 'Accepted_ID'})

    occ_acc_info = occ_df[acc_columns].drop_duplicates(subset=['Accepted_ID'], keep='first')
    out_df = pd.merge(occ_acc_info, merged, on='Accepted_ID')

    out_df.rename(columns=renaming, inplace=True)

    out_df.to_csv(logan_compiled_climate_vars_csv)


def main():
    get_climate_df()


if __name__ == '__main__':
    main()
