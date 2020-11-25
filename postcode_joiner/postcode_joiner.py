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
        Returns numpy array with specified columns and with coerced float types if requested
        """
        return pd.read_csv(csv_path, use_cols, converter).values

    @staticmethod
    def compute_haversine_distance(arr_1, arr_2, r=6371):
        """
        Calculate the great circle distance between two points on the earth (specified in decimal degrees)
        """
        arr_1 = np.radians(arr_1)
        arr_2 = np.radians(arr_2)
    
        lat_1, long_1 = arr_1[:, 0, None], arr_1[:, 1, None]
        lat_2, long_2 = arr_2[:, 0], arr_2[:, 1]
    
        lat_diff = lat_2 - lat_1
        long_diff = long_2 - long_1
    
        a = np.sin(lat_diff * 0.5) ** 2 + np.cos(lat_1) * np.cos(lat_2) * np.sin(long_diff * 0.5) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        return c * r
    
    def stack_lat_long_pairs(self):
        coords_1 = np.stack((np.asarray(self.np_addresses[:, 2], dtype=np.float32),
                             np.asarray(self.np_addresses[:, 3], dtype=np.float32)),
                            axis=1)
        coords_2 = np.stack((np.asarray(self.np_postcodes[:, 2], dtype=np.float32),
                             np.asarray(self.np_postcodes[:, 3], dtype=np.float32)),
                            axis=1)
        return coords_1, coords_2
    
    def compute_in_chunks(self, N=5000):
        coords_1, coords_2 = self.stack_lat_long_pairs()
        min_distance_args = []
        
        for i in range(0, len(self.np_addresses), N):
            haversine_distances = self.compute_haversine_distance(coords_1[i:i + N], coords_2)
            min_distance_args.append(np.argmin(haversine_distances, axis=1))
            
        return min_distance_args

    def get_minimum_distance_postcodes(self):
        min_distance_args = self.compute_in_chunks()
        return self.np_postcodes[np.concatenate(min_distance_args), 0]
        
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
    
    postcode_joiner.get_minimum_distance_postcodes()
    # Regex pattern extract postcode from Location column
    postcode_joiner.extract_postcode_from_location()
    # Compare extracted postcode to Long/Lat inferred postcode
    postcode_joiner.validate_postcodes()
    # Export data with two additional columns as .tsv
    postcode_joiner.export_as_tsv("./data/address_list.tsv")
