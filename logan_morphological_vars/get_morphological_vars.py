import os
import pandas as pd
from pkg_resources import resource_filename

from logan_manually_collected_data import manual_habit_data_output

temp_outputs_path = resource_filename(__name__, 'temp_outputs')
_spine_powo_search_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'spines_powo' + '_accepted.csv')
_hairs_powo_search_temp_output_accepted_csv = os.path.join(temp_outputs_path, 'hairs_powo' + '_accepted.csv')

### Outputs
output_path = resource_filename(__name__, 'outputs')
logan_spines_output_csv = os.path.join(output_path, 'spines_hits.csv')
logan_no_spines_output_csv = os.path.join(output_path, 'no_spines_hits.csv')

logan_hairy_output_csv = os.path.join(output_path, 'hairy_hits.csv')
logan_non_coloured_latex_output_csv = os.path.join(output_path, 'non_coloured_latex.csv')
logan_coloured_latex_output_csv = os.path.join(output_path, 'coloured_latex.csv')
logan_left_corollas_latex_output_csv = os.path.join(output_path, 'left_corollas.csv')
logan_right_corollas_latex_output_csv = os.path.join(output_path, 'right_corollas.csv')
logan_habits_output_csv = os.path.join(output_path, 'habits.csv')

logan_family_list = ['Loganiaceae']


def get_powo_hairs_and_spines():
    from powo_searches import search_powo
    # Get spine powo hits
    search_powo(['spine', 'thorn', 'spikes'],
                _spine_powo_search_temp_output_accepted_csv,
                characteristics_to_search=['leaf', 'inflorescence', 'appearance', 'fruit'],
                families_of_interest=logan_family_list, filters=['genera', 'species', 'infraspecies'])

    # Get powo hair hits
    search_powo(['hairs', 'hairy', 'pubescent'],
                _hairs_powo_search_temp_output_accepted_csv,
                characteristics_to_search=['leaf', 'inflorescence', 'appearance'],
                families_of_interest=logan_family_list, filters=['genera', 'species', 'infraspecies'])


def output_compiled_data():
    from morphological_vars import try_spine_temp_output_accepted_csv, try_no_spine_temp_output_accepted_csv, \
        try_hair_temp_output_accepted_csv
    from powo_searches import create_presence_absence_data
    from cleaning import compile_hits

    # Spines
    powo_spine_hits = pd.read_csv(_spine_powo_search_temp_output_accepted_csv)

    # Spines are often reported as 'absent'
    # List accepted ids of such cases to remove
    spine_ids_for_absence = ['50426037-2', '547225-1', '547073-1', '547572-1'
                             ]
    powo_presence_spine_hits, powo_absence_spine_hits = create_presence_absence_data(powo_spine_hits,
                                                                                     accepted_ids_of_absence=spine_ids_for_absence)

    try_spine_hits = pd.read_csv(try_spine_temp_output_accepted_csv)
    all_spine_dfs = [try_spine_hits, powo_presence_spine_hits]
    compile_hits(all_spine_dfs, logan_spines_output_csv)

    taxa_with_spines = []
    for d in all_spine_dfs:
        taxa_with_spines += d["Accepted_Name"].unique().tolist()

    # No spines
    try_no_spine_hits = pd.read_csv(try_no_spine_temp_output_accepted_csv)

    # Remove no spines hits which are in spines hits as we consider spines on any plant part
    # and no spines may indicate no spine on particular part
    powo_absence_spine_hits = powo_absence_spine_hits[~powo_absence_spine_hits["Accepted_Name"].isin(taxa_with_spines)]
    try_no_spine_hits = try_no_spine_hits[~try_no_spine_hits["Accepted_Name"].isin(taxa_with_spines)]

    compile_hits([powo_absence_spine_hits, try_no_spine_hits], logan_no_spines_output_csv)

    # Hairs
    powo_hair_hits = pd.read_csv(_hairs_powo_search_temp_output_accepted_csv)
    try_hair_hits = pd.read_csv(try_hair_temp_output_accepted_csv)

    all_hair_hits = [powo_hair_hits, try_hair_hits]
    compile_hits(all_hair_hits, logan_hairy_output_csv)

    # Habit
    habits = pd.read_csv(manual_habit_data_output)
    habits.to_csv(logan_habits_output_csv)


def main():
    if not os.path.isdir(temp_outputs_path):
        os.mkdir(temp_outputs_path)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    get_powo_hairs_and_spines()
    output_compiled_data()


if __name__ == '__main__':
    main()
