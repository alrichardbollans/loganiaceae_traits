import ast
import os

import pandas as pd
from automatchnames import get_accepted_info_from_ids_in_column
from getting_malarial_regions import malaria_country_codes_csv
from pkg_resources import resource_filename
from taxa_lists import get_all_taxa

from cleaning_logan_plant_occurrences import families_in_occurrences
from logan_wcsp_distributions import logan_distributions_csv

_inputs_path = resource_filename(__name__, 'inputs')

_temp_outputs_path = resource_filename(__name__, 'temp_outputs')

_output_path = resource_filename(__name__, 'outputs')
logan_taxa_in_malarial_countries_csv = os.path.join(_output_path, 'taxa_in_malarial_countries.csv')

if not os.path.isdir(_output_path):
    os.mkdir(_output_path)



def get_taxa_in_malarial_countries_from_wcsp_data():
    wcsp_dists = pd.read_csv(logan_distributions_csv)

    malaria_country_codes_df = pd.read_csv(malaria_country_codes_csv)

    ids_in_malarial_regions = []
    for idx, row in wcsp_dists.iterrows():

        if any(iso_code in malaria_country_codes_df['tdwg3_codes'].values for iso_code in
               (ast.literal_eval(row['native_tdwg3_codes']) + ast.literal_eval(
                   row['intro_tdwg3_codes']) + ast.literal_eval(row['extinct_tdwg3_codes']))):
            ids_in_malarial_regions.append(row['kew_id'])

    acc_taxa = get_all_taxa(families_of_interest=families_in_occurrences, accepted=True,
                            ranks=['Species', 'Subspecies', 'Variety'])
    family_taxa_in_malarial_regions = acc_taxa[acc_taxa['kew_id'].isin(ids_in_malarial_regions)]

    malarial_taxa_acc = get_accepted_info_from_ids_in_column(family_taxa_in_malarial_regions, 'kew_id',
                                                             families_of_interest=families_in_occurrences)
    malarial_taxa_acc.to_csv(logan_taxa_in_malarial_countries_csv)



def main():
    get_taxa_in_malarial_countries_from_wcsp_data()


if __name__ == '__main__':
    main()
