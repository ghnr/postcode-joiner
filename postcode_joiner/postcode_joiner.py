import numpy as np
import pandas as pd

class PostCodeJoiner:
    def __init__(self, address_path, postcode_path):
        self.np_postcodes = self.set_arrays(postcode_path)
        self.np_addresses = self.set_arrays(address_path,
                                            use_cols=[0,1,2,3,4],
                                            converter={"Latitude": self.coerce_as_float})
    
    @staticmethod
    def coerce_as_float(x):
        try:
            return np.float32(x)
        except ValueError:
            return np.nan
    
    @staticmethod
    def set_arrays(csv_path, use_cols=None, converter=None):
        """
        Use pandas to read the csv (faster than numpy's read_txt and gen_txt cannot handle commas inside comma delimited file)
        Returns numpy array with specified columns and coerced float types if requested
        """
        return pd.read_csv(csv_path, use_cols, converter).values
        
    def extract_postcode_from_location(self):
        # Uses the UK postcode regex pattern to extract postcode from Location column
        # Postcode regex (un-anchored) https://stackoverflow.com/a/51885364/5437165
        POSTCODE_REGEX_PATTERN = "([A-Z][A-HJ-Y]?[0-9][A-Z0-9]? ?[0-9][A-Z]{2}|GIR ?0A{2})"
        self.df_address_list["Postcode in Location"] = self.df_address_list["Location"].str.extract(POSTCODE_REGEX_PATTERN)
    
    def validate_postcodes(self):
        # Creates new column called validated with comparison of extracted postcode and inferred postcode
        self.df_address_list.loc[self.df_address_list["postcode"] == self.df_address_list["Postcode in Location"], "validated"] = True
        self.df_address_list.loc[self.df_address_list["postcode"] != self.df_address_list["Postcode in Location"], "validated"] = False
        
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
    
    # Regex pattern extract postcode from Location column
    postcode_joiner.extract_postcode_from_location()
    # Compare extracted postcode to Long/Lat inferred postcode
    postcode_joiner.validate_postcodes()
    # Export data with two additional columns as .tsv
    postcode_joiner.export_as_tsv("./data/address_list.tsv")
