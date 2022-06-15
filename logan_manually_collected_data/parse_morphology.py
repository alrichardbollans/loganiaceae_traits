import os

import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column
from pkg_resources import resource_filename

from logan_manually_collected_data import logan_trait_parsing_output_path

_inputs_path = resource_filename(__name__, 'inputs')
_manual_habit_data_csv = os.path.join(_inputs_path, 'manual_habits.csv')

manual_habit_data_output = os.path.join(logan_trait_parsing_output_path, 'manual_habit_data.csv')


def prepare_habits():
    habits = pd.read_csv(_manual_habit_data_csv)
    acc_manual_data = get_accepted_info_from_names_in_column(habits, 'genus')

    acc_manual_data.to_csv(manual_habit_data_output)


def main():
    prepare_habits()


if __name__ == '__main__':
    main()
