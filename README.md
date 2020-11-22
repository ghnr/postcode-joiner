# Postcode Lat/Long Joiner

This script inserts a postcode column and a validated column to `address_list.csv` by merging postcode data from `postcode_reference.csv` file by using the latitude and longitude existing in both sets of data.

## Running

The script is written for python3.6+ and requires the packages numpy and pandas to be installed:
```
$ cd ./postcode_joiner/postcode_joiner/
$ python postcode_joiner.py
```

## Testing

```
$ cd ./postcode_joiner/postcode_joiner/tests/
$ python -m pytest
```

## Design choices

- Handling erroneous values in the Latitude column: Values in this column are all converted to a numpy `float64` dtype and any errors in conversion are "coerced" into an appropriate value. In the case of a string existing in an expected float column, that string will be parsed as a `NaN` value ([docs](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_numeric.html)). A harsher method would have been to immediately raise an error, but this does not seem practical in the introductory steps of data cleaning.
- Latitude and longitude precision: Given that our only point of reference are the provided lat/long values in both files, these common values must be used to determine the matching postcode (if any) given the geographical indicators. The postcode reference does not provide a range of longitudes and latitudes that it spans but instead a single point corresponding to the postcode. On the other hand, the address file provides lat/long pairs of the address to a degree of precision that is not necessary for this task. The best approach then would be to round the lat/long down to a less precise but more easily matchable value, which as a result of the rounding would cover a larger geographical area. Through exploratory data analysis, 3 decimal points of precision were found to maximise the number of matched and validated postcodes between the two sets. It is also a logically grounded value as 3 dp. is enough to determine one street from another as it is accurate to approximately 111 metres.
- Fuzziness and multiple matches: Given the decision choice above to optimise the number of matches and the accuracy of matches coupling, after the merge stage where the dataframes are left joined together, the resultant dataframe is much larger than the original as it has matched multiple postcodes per address. This is an unavoidable downside of the fuzzy matching above and the decision was made to simply drop the duplicate postcodes for each address (keeping the first matching row only, the default behaviour of panda's function).
- Extracting postcodes from location: This seems like a classical problem where regex is suited. *"Some people, when confronted with a problem, think "I know, I'll use regular expressions." Now they have two problems."* Luckily, a regex pattern for matching UK postcodes exists online and was created by a StackOverflow user who upgraded the pattern provided by Government Data Standards.
- Testing framework: `pytest` was chosen as it is more popular than the built-in `unittests` module, while also allowing greater control over testing via features like fixtures that are commonplace in integration testing suites across languages.


## Potential improvements

- Given that a location column exists for the vast majority of rows in the dataset, a far more accurate postcode can be obtained by using Google's Geolocation API which would take the location data (as well as the provided lat/long data) and return the best location object match from Google's servers including a postcode.
