import os.path

from automatchnames import get_accepted_info_from_names_in_column, remove_whitespace_at_beginning_and_end

import os

import pandas as pd
from pkg_resources import resource_filename

_inputs_path = resource_filename(__name__, 'inputs')

logan_trait_parsing_output_path = resource_filename(__name__, 'outputs')
if not os.path.isdir(_inputs_path):
    os.mkdir(_inputs_path)

if not os.path.isdir(logan_trait_parsing_output_path):
    os.mkdir(logan_trait_parsing_output_path)

NEW_HEADINGS = [
    "Genus",
    "Species",
    "Tested_for_Alkaloids",
    "Ref_Alks",
    "Alkaloids_test_notes",
    "Alkaloids",
    "Alk_classes_tested_for",
    "Alkaloid_classes",
    "Alkaloid_class_absences",
    "Alkaloid_mainclass(conal)",
    "Alkaloid_otherclasses",
    "Alkaloid_class_notes",
    "Antimalarial_Use",
    "Ref_H_Mal",
    "History_Fever",
    "Ref_H_Fever",
    "Tested_Antimalarial",
    "Extraction_Method",
    "Type_of_Test",
    "Activity_Antimalarial",
    "Authors_Activity_Label",
    "Positive_Control_Used",
    "Given_Activities",
    "Ref_Activity",
    "General_notes",
    "MPNS_notes",
    "Details",
    "Cardenolides",
    "Cardenolides_Ref",
    "Steroids",
    "Steroids_Ref"
]
if any('source' in x.lower() for x in NEW_HEADINGS):
    raise ValueError('Unwanted Source included in columns')
logan_accepted_trait_csv = os.path.join(logan_trait_parsing_output_path, "logan_accepted_traits.csv")
ACCEPTED_NAME_COLUMN = "Accepted_Name"


class Family:
    def __init__(self, name, tag, unclean_trait_csv):
        self.name = name
        self.tag = tag
        self.unclean_trait_csv = unclean_trait_csv
        self.clean_trait_csv = os.path.join(logan_trait_parsing_output_path, "clean_" + tag + "_trait_data.csv")
        self.species_name_list = os.path.join(logan_trait_parsing_output_path, tag + "_species_names.txt")


LOG = Family("Loganiaceae", "log",
             os.path.join(_inputs_path, 'Loganiaceae, alkaloids, steroids and antimalarial activity.xlsx'))


def strip_leading_trailing_whitespace(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df[column] = df[column].apply(remove_whitespace_at_beginning_and_end)
    return df


def create_single_name(df: pd.DataFrame):
    df['Name'] = df['Genus'] + " " + df['Species']

    # Remove NBSPs
    def remove_nbsp(value: str):
        try:
            v = value.replace("\xa0", " ")

            return v
        except AttributeError:
            return value

    df['Name'] = df['Name'].apply(remove_nbsp)
    df.set_index('Name', inplace=True)


def rename_headings(df: pd.DataFrame):
    # First the tables are saved to csv

    df.set_axis(NEW_HEADINGS, axis=1, inplace=True)


def do_initial_clean(fam: Family):
    # Load family traits into dataframe
    trait_df = pd.read_excel(fam.unclean_trait_csv, sheet_name='Data')
    rename_headings(trait_df)

    # Remove empty genus or species
    trait_df = trait_df.drop(trait_df[trait_df.Genus.isna()].index, inplace=False)
    trait_df = trait_df.drop(trait_df[trait_df.Species.isna()].index, inplace=False)

    # Create Name column
    trait_df = strip_leading_trailing_whitespace(trait_df, 'Genus')
    trait_df = strip_leading_trailing_whitespace(trait_df, 'Species')
    create_single_name(trait_df)

    trait_df.sort_values(by=['Name'], inplace=True)

    # Add family name
    trait_df['Family'] = fam.name

    # Output to csv
    trait_df.to_csv(fam.clean_trait_csv)


def create_order_csv(fams):
    dfs = []
    for f in fams:
        df = pd.read_csv(f.clean_trait_csv)
        dfs.append(df)

    order_df = pd.concat(dfs)

    accepted_order = get_accepted_info_from_names_in_column(order_df, 'Name',
                                                            families_of_interest=['Loganiaceae'])

    duplicateRows = accepted_order[accepted_order.duplicated([ACCEPTED_NAME_COLUMN])]
    if len(duplicateRows.index) > 0:
        raise ValueError('Repeated accepted names (likely from use of synonyms in names). Fix before continuing.')

    print(accepted_order.columns)
    accepted_order.to_csv(logan_accepted_trait_csv)


def main():
    fams = [LOG]
    for f in fams:
        do_initial_clean(f)
    create_order_csv(fams)


if __name__ == '__main__':
    main()
