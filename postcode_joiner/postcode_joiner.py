import pandas as pd

class PostCodeJoiner:
    def __init__(self, address_path, postcode_path):
        self.df_address_list = self.set_dataframe(address_path)
        self.df_postcode_ref = self.set_dataframe(postcode_path)
        
    def set_dataframe(self, csv_path):
        # Read the csv files into a pandas dataframe
        return pd.read_csv(csv_path)
    
    def convert_address_col_to_float(self, col_name):
        # Address list latitude is an object/str, cast it to a float
        # Errors in conversion will change the stored value to NaN (coerce)
        self.df_address_list[col_name] = pd.to_numeric(self.df_address_list[col_name],
                                                       errors="coerce")
        
    def rename_postcode_ref_column(self, rename_mapping):
        # Rename the columns in the postcode reference to match the names in df_address_list
        self.df_postcode_ref.rename(columns=rename_mapping,
                                    inplace=True)
        
    def round_column_floats(self, col_name, decimal_places):
        # Rounds floats to N number of decimal places
        self.df_address_list[f"{col_name} (rounded)"] = self.df_address_list[col_name].round(decimal_places)
        self.df_postcode_ref[f"{col_name} (rounded)"] = self.df_postcode_ref[col_name].round(decimal_places)
        
    def merge_postcode_reference(self):
        # Left merges the postcode data and the address data on Latitude and Longitude
        original_columns = list(self.df_address_list.columns)

        df_postcode_ref_trimmed = self.df_postcode_ref[["postcode", "Latitude (rounded)", "Longitude (rounded)"]]
        
        self.df_address_list = self.df_address_list.merge(df_postcode_ref_trimmed,
                                                          on=["Latitude (rounded)", "Longitude (rounded)"],
                                                          how="left")
        
        # Dropping dupes based on original columns to remove multiple postcode matches due to the rounding fuzziness
        self.df_address_list.drop_duplicates(original_columns,
                                             keep="first",
                                             inplace=True)
        
    def extract_postcode_from_location(self):
        # Uses the UK postcode regex pattern to extract postcode from Location column
        # Postcode regex (un-anchored) https://stackoverflow.com/a/51885364/5437165
        POSTCODE_REGEX_PATTERN = "([A-Z][A-HJ-Y]?[0-9][A-Z0-9]? ?[0-9][A-Z]{2}|GIR ?0A{2})"
        self.df_address_list["Postcode in Location"] = self.df_address_list["Location"].str.extract(POSTCODE_REGEX_PATTERN)
    
    def validate_postcodes(self):
        # Creates new column called validated with comparison of extracted postcode and inferred postcode
        self.df_address_list.loc[self.df_address_list["postcode"] == self.df_address_list["Postcode in Location"], "validated"] = True
        self.df_address_list.loc[self.df_address_list["postcode"] != self.df_address_list["Postcode in Location"], "validated"] = False
        
    def misc_clean_output_data(self):
        # Pandas quirk of reading a csv without a defined column name, rename back to original name
        self.df_address_list.rename(columns={"Unnamed: 5": ""},
                                    inplace=True)
        # Removes extra columns created during the intermediary steps
        self.df_address_list.drop(["Postcode in Location", "Latitude (rounded)", "Longitude (rounded)"],
                                  axis=1,
                                  inplace=True)
        
    def export_as_tsv(self, export_path):
        # Exports to csv with tab \t separator
        self.df_address_list.to_csv(export_path,
                                    sep="\t",
                                    index=False)
        print(".tsv file successfully exported to " + export_path)

if __name__ == '__main__':
    # Constant paths
    ADDRESS_FILE_PATH = "./data/address_list.csv"
    POSTCODE_FILE_PATH = "./data/postcode_reference.csv"
    
    # Instantiate class
    postcode_joiner = PostCodeJoiner(ADDRESS_FILE_PATH, POSTCODE_FILE_PATH)
    
    # Squash strings in latitude to floats
    postcode_joiner.convert_address_col_to_float("Latitude")
    # Regex pattern extract postcode from Location column
    postcode_joiner.extract_postcode_from_location()
    # Compare extracted postcode to Long/Lat inferred postcode
    postcode_joiner.validate_postcodes()
    # Remove additional columns created in preparation for export
    postcode_joiner.misc_clean_output_data()
    # Export data with two additional columns as .tsv
    postcode_joiner.export_as_tsv("./data/address_list.tsv")
