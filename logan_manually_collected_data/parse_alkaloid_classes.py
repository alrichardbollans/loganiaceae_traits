import os
from typing import List

import pandas as pd

from logan_manually_collected_data import logan_trait_parsing_output_path, logan_encoded_traits_csv

logan_parsed_alkaloid_classes_csv = os.path.join(logan_trait_parsing_output_path, 'parsed_alkaloid_classes.csv')


def remove_whitespace_at_beginning_and_end(value: str):
    try:
        v = value.rstrip()
        out = v.lstrip()
        return out
    except AttributeError:
        return value


def remove_reference_in_string(val: str):
    import re
    return re.sub("[\[].*?[\]]", "", val)


def lower_case_string(val: str):
    return val.lower()


def OHE_alks(df: pd.DataFrame) -> pd.DataFrame:
    import numpy as np
    # OHE alks
    def convert_alks_to_lists(hab: str) -> List[str]:

        if hab == '?':
            raise ValueError
        try:
            if ';' not in hab:
                alk_list = [hab]
            else:
                alk_list = hab.split(';')
        except TypeError:
            raise ValueError
        else:
            out_list = list(map(remove_reference_in_string, alk_list))
            out_list = list(map(remove_whitespace_at_beginning_and_end, out_list))

            out_list = list(map(lower_case_string, out_list))

            return out_list

    df['Alkaloid_mainclass'] = df['Alkaloid_mainclass'].apply(convert_alks_to_lists)

    multilabels = df['Alkaloid_mainclass'].str.join('|').str.get_dummies()
    multilabels = multilabels.add_prefix('alk_')
    df = df.join(multilabels)

    return df


def parse_alkaloid_data():
    input_alks = pd.read_csv(logan_encoded_traits_csv, index_col=0)

    input_alks.dropna(subset=['Alkaloid_mainclass'], inplace=True)

    # OHE
    encoded = OHE_alks(input_alks)
    alk_cols_to_use = [c for c in encoded.columns.tolist() if 'alk_' in c]
    encoded = encoded[['Accepted_Name', 'Genus', 'Accepted_ID'] + alk_cols_to_use]
    encoded.to_csv(logan_parsed_alkaloid_classes_csv)
    encoded.describe().to_csv(os.path.join(logan_trait_parsing_output_path, 'alks summary.csv'))

    cols = [x for x in encoded.columns.tolist() if 'alk_' in x]

    def rmv_prefix(given_value: str):
        out = given_value[given_value.rindex('alk_') + len('alk_'):]
        return out

    cols_to_use = list(map(rmv_prefix, cols))

    pd.DataFrame(cols_to_use).to_csv('alks_to_parse.csv')


def main():
    parse_alkaloid_data()


if __name__ == '__main__':
    main()
