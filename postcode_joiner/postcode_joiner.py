import csv
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

class PostCodeJoiner:
    def __init__(self, address_path, postcode_path):
        self.np_postcodes = self.set_arrays(postcode_path).values
        self.np_addresses = self.set_arrays(address_path,
                                            use_cols=[0,1,2,3,4],
                                            type_converter={"Latitude": self.coerce_as_float})
        self.column_names = list(self.np_addresses.columns)
        self.np_addresses = self.np_addresses.values
    
    @staticmethod
    def coerce_as_float(x):
        try:
            return np.float32(x)
        except ValueError:
            return np.nan
    
    @staticmethod
    def set_arrays(csv_path, use_cols=None, type_converter=None):
        """
        Use pandas to read the csv (faster than numpy's read_txt and gen_txt cannot handle commas inside comma delimited file)
        Returns dataframe with specified columns and with coerced float types if requested
        """
        return pd.read_csv(csv_path, usecols=use_cols, converters=type_converter)
        
    def filter_invalid_postcodes(self):
        np_is_active_postcode = np.isnan(np.asarray(self.np_postcodes[:,2], dtype=np.float32))
        self.np_postcodes = self.np_postcodes[np_is_active_postcode]

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

    @staticmethod
    def compute_euclidean_distance(arr_1, arr_2):
        return cdist(arr_1, arr_2, metric='euclidean')
    
    def stack_lat_long_pairs(self):
        coords_1 = np.stack((np.asarray(self.np_addresses[:, 2], dtype=np.float32),
                             np.asarray(self.np_addresses[:, 3], dtype=np.float32)),
                            axis=1)
        coords_2 = np.stack((np.asarray(self.np_postcodes[:, 3], dtype=np.float32),
                             np.asarray(self.np_postcodes[:, 4], dtype=np.float32)),
                            axis=1)
        return coords_1, coords_2
    
    def compute_in_chunks(self, tradeoff, N=5000):
        
        if tradeoff not in ["accuracy", "speed"]:
            raise ValueError("Trade-off must be either speed or accuracy")
        
        coords_1, coords_2 = self.stack_lat_long_pairs()
        min_distance_args = []
        
        for i in range(0, len(self.np_addresses), N):
            if tradeoff == "accuracy":
                # Using Haversine distance formula (slower but higher accuracy)
                distances = self.compute_haversine_distance(coords_1[i:i + N], coords_2)
            else:
                distances = self.compute_euclidean_distance(coords_1[i:i + N], coords_2)

            min_distance_args.append(np.argmin(distances, axis=1))
            
        return min_distance_args

    def get_minimum_distance_postcodes(self, tradeoff):
        min_distance_args = self.compute_in_chunks(tradeoff)
        return self.np_postcodes[np.concatenate(min_distance_args), 0]
        
    def extract_postcode_from_location(self):
        """
        Uses the UK postcode regex pattern to extract postcode from Location column
        Postcode regex (un-anchored) https://stackoverflow.com/a/51885364/5437165
        Returns numpy array of postcodes matched from Location column (index=4), NaN values if not matched
        """
        POSTCODE_REGEX_PATTERN = "([A-Z][A-HJ-Y]?[0-9][A-Z0-9]? ?[0-9][A-Z]{2}|GIR ?0A{2})"
        return pd.Series(self.np_addresses[:, 4]).str.extract(POSTCODE_REGEX_PATTERN, expand=False).values
    
    @staticmethod
    def validate_postcodes(extracted_postcodes, min_distance_postcodes):
        """
        Returns numpy array of True/False values where regex extracted postcode matches min distance computed postcodes
        """
        return extracted_postcodes == min_distance_postcodes
        
    def export_as_tsv(self, export_path, np_min_distance_postcodes, np_valid_postcodes):
        
        np_address_extra_cols = np.concatenate([self.np_addresses,
                                                np_min_distance_postcodes[:, None],
                                                np_valid_postcodes[:, None]],
                                               axis=1)

        with open(export_path, 'w', newline='') as tsv_file:
            csv.writer(tsv_file, delimiter="\t").writerow(self.column_names + ["Postcode (nearest match)", "Validated"])
            csv.writer(tsv_file, delimiter="\t").writerows(np_address_extra_cols)

        print(".tsv file successfully exported to " + export_path)

if __name__ == '__main__':
    # Constant paths
    ADDRESS_FILE_PATH = "./data/address_list.csv"
    POSTCODE_FILE_PATH = "./data/postcode_reference.csv"
    
    # Instantiate class
    postcode_joiner = PostCodeJoiner(ADDRESS_FILE_PATH, POSTCODE_FILE_PATH)

    postcode_joiner.filter_invalid_postcodes()
    
    min_distance_postcodes = postcode_joiner.get_minimum_distance_postcodes(tradeoff="speed")
    # Regex pattern extract postcode from Location column
    extracted_postcodes = postcode_joiner.extract_postcode_from_location()
    # Compare extracted postcode to Long/Lat inferred postcode
    valid_postcodes = postcode_joiner.validate_postcodes(extracted_postcodes, min_distance_postcodes)
    # Export data with two additional columns as .tsv
    postcode_joiner.export_as_tsv("./data/address_list.tsv", min_distance_postcodes, valid_postcodes)
