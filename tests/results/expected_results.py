from pandas import read_csv

# Expected results to assert that output results are equal to this
# Relative path of results needed for pytest call
result_postcode_renamed = read_csv("./results/test_postcode_reference_renamed.csv")
result_address_rounded = read_csv("./results/test_address_list_rounded.csv")
result_postcode_rounded = read_csv("./results/test_postcode_reference_rounded.csv")
result_address_merged = read_csv("./results/test_address_list_merged.csv")
result_address_extracted = read_csv("./results/test_address_list_extracted.csv")
result_address_validated = read_csv("./results/test_address_list_validated.csv")
result_address_cleaned = read_csv("./results/test_address_list_cleaned.csv")
result_address_cleaned.rename(columns={"Unnamed: 5": ""}, inplace=True) # fixing pandas read_csv on unnamed col
result_export = read_csv("./results/result.tsv")
