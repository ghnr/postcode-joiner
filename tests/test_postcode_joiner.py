import pytest
import numpy as np
from pandas import read_csv
from pandas.testing import assert_frame_equal
from postcode_joiner import postcode_joiner
from results import expected_results

# pytest module scoped, same instance reused for each test
@pytest.fixture(scope="module")
def postcode_joiner_obj():
    return postcode_joiner.PostCodeJoiner("./data/test_address_list_raw.csv",
                                          "./data/test_postcode_reference_raw.csv")

def test_col_conversion(postcode_joiner_obj):
    print(postcode_joiner_obj.df_address_list["Latitude"])
    postcode_joiner_obj.convert_address_col_to_float("Latitude")
    
    assert postcode_joiner_obj.df_address_list["Latitude"].dtypes == np.dtype('float64')

def test_distance_computation(postcode_joiner_obj):
    assert True

def test_extract_postcode(postcode_joiner_obj):
    postcode_joiner_obj.extract_postcode_from_location()
    assert_frame_equal(postcode_joiner_obj.df_address_list, expected_results.result_address_extracted)
    
def test_validate_postcodes(postcode_joiner_obj):
    postcode_joiner_obj.validate_postcodes()
    assert_frame_equal(postcode_joiner_obj.df_address_list, expected_results.result_address_validated)
    
def test_misc_clean_data(postcode_joiner_obj):
    postcode_joiner_obj.misc_clean_output_data()
    assert_frame_equal(postcode_joiner_obj.df_address_list, expected_results.result_address_cleaned)

def test_export_tsv(postcode_joiner_obj):
    postcode_joiner_obj.export_as_tsv("./data/export.tsv")
    
    assert_frame_equal(read_csv("./data/export.tsv"), expected_results.result_export)

if __name__ == '__main__':
    pytest.main()
