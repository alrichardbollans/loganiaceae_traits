import os
import pandas as pd
from pkg_resources import resource_filename

from cleaning import compile_hits, output_summary_of_hit_csv
from automatchnames import get_accepted_info_from_names_in_column
from powo_searches import search_powo

### Inputs
from logan_manually_collected_data import logan_encoded_traits_csv

_inputs_path = resource_filename(__name__, 'inputs')
# Refs citing plant sheet saved
_initial_MPNS_csv = os.path.join(_inputs_path, 'MPNSv11 Loganiaceae + Gentianaceae + Gelsemiaceae.csv')

### Temp outputs
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_powo_search_medicinal_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'powo_medicinal_accepted.csv')

_cleaned_MPNS_accepted_csv = os.path.join(_temp_outputs_path, 'MPNS Data_accepted.csv')

_powo_search_malarial_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'powo_malarial_accepted.csv')
_manual_hit_antimal_temp_output = os.path.join(_temp_outputs_path, '_manual_hit_antimal_temp_output.csv')
_manual_hit_fever_temp_output = os.path.join(_temp_outputs_path, '_manual_hit_fever_temp_output.csv')

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_logan_medicinal_csv = os.path.join(_output_path, 'list_plants_medicinal_usage.csv')
output_logan_malarial_csv = os.path.join(_output_path, 'list_plants_malarial_usage.csv')

logan_fams_of_interest = ['Loganiaceae']


def get_powo_medicinal_usage():
    search_powo(
        ['medicinal', 'medication', 'medicine'],
        _powo_search_medicinal_temp_output_accepted_csv,
        characteristics_to_search=['use'],
        families_of_interest=logan_fams_of_interest,
        filters=['species', 'infraspecies']
    )


def prepare_MPNS_hits(families_of_interest=None) -> pd.DataFrame:
    # Requested from MPNS
    mpns_df = pd.read_csv(_initial_MPNS_csv)
    mpns_df.drop(columns=['refstand', 'ref_short', 'ID'], inplace=True)

    mpns_df = mpns_df.dropna(subset=['taxon_name'])
    if families_of_interest is not None:
        mpns_df = mpns_df[mpns_df['family'].str.contains('|'.join(families_of_interest))]

    mpns_df = mpns_df.drop_duplicates(subset=['taxon_name'])
    accepted_mpns_df = get_accepted_info_from_names_in_column(mpns_df, 'taxon_name')

    accepted_mpns_df = accepted_mpns_df.dropna(subset=['Accepted_Name'])
    accepted_mpns_df['Source'] = 'MPNS'

    accepted_mpns_df.to_csv(_cleaned_MPNS_accepted_csv)

    return accepted_mpns_df


def get_powo_antimalarial_usage():
    try:
        search_powo(['antimalarial', 'malaria'],
                    _powo_search_malarial_temp_output_accepted_csv,
                    characteristics_to_search=['use'],
                    families_of_interest=logan_fams_of_interest,
                    filters=['species', 'infraspecies']
                    )
    except KeyError as e:
        print(f'KeyError: {e}')
        print('Key error likely raised due to no matches being found')


def get_manual_hits():
    trait_table = pd.read_csv(logan_encoded_traits_csv)
    antimal_hits = trait_table[trait_table['Antimalarial_Use'] == 1]
    antimal_hits = antimal_hits[[
        'Antimalarial_Use', 'Accepted_Name', 'Accepted_Species', 'Accepted_Species_ID', 'Accepted_ID',
        'Accepted_Rank',
        'Family']]
    antimal_hits['Source'] = 'Manual'
    antimal_hits.to_csv(_manual_hit_antimal_temp_output)

    fever_hits = trait_table[trait_table['History_Fever'] == 1]
    fever_hits = fever_hits[[
        'History_Fever', 'Accepted_Name', 'Accepted_Species', 'Accepted_Species_ID', 'Accepted_ID',
        'Accepted_Rank',
        'Family']]
    fever_hits['Source'] = 'Manual'
    fever_hits.to_csv(_manual_hit_fever_temp_output)


def prepare_data():
    # Antimal
    get_powo_antimalarial_usage()
    get_manual_hits()

    # Medicinal
    get_powo_medicinal_usage()
    prepare_MPNS_hits(families_of_interest=logan_fams_of_interest)


def main():
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if not os.path.isdir(_output_path):
        os.mkdir(_output_path)

    prepare_data()

    manual_antimal_hits = pd.read_csv(_manual_hit_antimal_temp_output)
    manual_fever_hits = pd.read_csv(_manual_hit_fever_temp_output)
    powo_medicinal_hits = pd.read_csv(_powo_search_medicinal_temp_output_accepted_csv)
    mpns_medicinal_hits = pd.read_csv(_cleaned_MPNS_accepted_csv)

    compile_hits([powo_medicinal_hits, mpns_medicinal_hits, manual_antimal_hits, manual_fever_hits],
                 output_logan_medicinal_csv)

    try:
        powo_antimalarial_hits = pd.read_csv(_powo_search_malarial_temp_output_accepted_csv)
        compile_hits([powo_antimalarial_hits, manual_antimal_hits], output_logan_malarial_csv)

    except FileNotFoundError:
        compile_hits([manual_antimal_hits], output_logan_malarial_csv)

    output_source_summaries()


def output_source_summaries():
    output_summary_of_hit_csv(
        output_logan_medicinal_csv,
        os.path.join(_output_path, 'source_summaries', 'medicinal_source_summary'),
        families=['Loganiaceae'],
        source_translations={'POWO': 'POWO pages'}, ranks=['Species'])

    output_summary_of_hit_csv(
        output_logan_malarial_csv,
        os.path.join(_output_path, 'source_summaries', 'malarial_source_summary'),
        families=['Loganiaceae'],
        source_translations={'POWO': 'POWO pages'}, ranks=['Species'])


if __name__ == '__main__':
    main()
