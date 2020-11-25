import pytest
import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal
from pandas import read_csv
from pandas.testing import assert_frame_equal
from postcode_joiner import postcode_joiner
from results import expected_results

# pytest module scoped, same instance reused for each test
@pytest.fixture(scope="module")
def postcode_joiner_obj():
    return postcode_joiner.PostCodeJoiner("./data/test_address_list_raw.csv",
                                          "./data/test_postcode_reference_raw.csv")

@pytest.fixture(scope="module")
def array_samples():
    return np.array([[51.6155, 0.032659]]), np.array([[51.5717, 0.052316]])

def test_column_names_extracted(postcode_joiner_obj):
    assert len(postcode_joiner_obj.np_addresses) > 0, "List of column names are empty"

def test_type_coercion(postcode_joiner_obj):
    assert np.asarray(postcode_joiner_obj.np_addresses[:,2], dtype=np.float32).dtype == np.float32, \
        "Latitude column dtype is not castable as np.float"
    
def test_invalid_postcode_filtering(postcode_joiner_obj):
    postcode_joiner_obj.filter_invalid_postcodes()
    assert np.all(np.isnan(np.asarray(postcode_joiner_obj.np_postcodes[:, 2], dtype=np.float32))), \
        "Postcodes with non-null terminated_postcode column remains"

def test_haversine_computation(postcode_joiner_obj, array_samples):
    haversine_output = postcode_joiner_obj.compute_haversine_distance(array_samples[0], array_samples[1])
    assert_array_almost_equal(haversine_output, expected_results.haversine_result, decimal=8,
                              err_msg="Haversine computation results do not match")
    
def test_euclidean_computation(postcode_joiner_obj, array_samples):
    euclidean_output = postcode_joiner_obj.compute_euclidean_distance(array_samples[0], array_samples[1])
    assert_array_almost_equal(euclidean_output, expected_results.euclidean_result, decimal=8,
                              err_msg="Euclidean computation results do not match")
    
def test_stack_pairs(postcode_joiner_obj):
    assert_array_almost_equal(postcode_joiner_obj.stack_lat_long_pairs()[0], expected_results.coords_result[0], decimal=8)
    assert_array_almost_equal(postcode_joiner_obj.stack_lat_long_pairs()[1], expected_results.coords_result[1], decimal=8)

def test_tradeoff_bad_value_raise(postcode_joiner_obj):
    with pytest.raises(ValueError):
        postcode_joiner_obj.compute_in_chunks("bad-tradeoff-arg")

def test_minimum_distance_accuracy(postcode_joiner_obj):
    assert list(postcode_joiner_obj.get_minimum_distance_postcodes("accuracy")) == expected_results.accuracy_result

def test_minimum_distance_speed(postcode_joiner_obj):
    assert list(postcode_joiner_obj.get_minimum_distance_postcodes("speed")) == expected_results.speed_result
    
def test_extract_postcode(postcode_joiner_obj):
    assert list(postcode_joiner_obj.extract_postcode_from_location()) == expected_results.extract_result, \
        "Extracted postcodes do not match"

def test_export_tsv(postcode_joiner_obj):
    
    postcode_joiner_obj.export_as_tsv("./data/export.tsv",
                                      np.array(expected_results.accuracy_result),
                                      np.array(expected_results.valid_result))

    assert_frame_equal(read_csv("./data/export.tsv"), expected_results.result_export)

if __name__ == '__main__':
    pytest.main()
