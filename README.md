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

- Handling erroneous values in the Latitude column: Values in this column are all converted to a numpy `float64` dtype and any errors in conversion are "coerced" into an appropriate value. In the case of a string existing in an expected float column, that string will be parsed as a `NaN` value. This all happens in the custom converter function that is called when reading the csv file.
- Filtering invalid postcodes: Postcodes with a termination date in the postcode lookup are removed so that the search does not match invalid postcodes.
- Distance computation, Haversine vs Euclidean: Give the latitude and longitude value pairs, distances from each address to each location in the postcode lookup can be computed. The decision lies in which distance approximation algorithm to use. The Haversine formula is a more accurate approximation of distances between geographical points as it accounts for the Earth's curvature given a mean Earth radius. Whereas, the Euclidean distance formula operates on the assumption that the two points of interest exist on a flat plane; an approximation with minimal error when calculating distances on the scale of a single city. The Haversine computation is roughly 7-10x slower than the Euclidean computation and has a larger memory footprint. 
- Minimising memory footprint: As the above distance approximations use NxM matrices, it is imperative that unnecessary memory overhead be minimised. In this case, a 32 bit float is capable of storing 8 significant digits, which is precise enough for postcode matching with latitudes and longitudes, and is half the bits required for 64 bit floats. Additionally, the addresses dataset is chunked to a size of N when carrying out the distance computation. This limits the maximum memory required for a single iteration of distance calculations. 
- Extracting postcodes from location: This is a classic problem where regex is suited. *"Some people, when confronted with a problem, think "I know, I'll use regular expressions." Now they have two problems."* Luckily, a regex pattern for matching UK postcodes exists online and was created by a StackOverflow user who upgraded the pattern provided by Government Data Standards.
- Testing framework: `pytest` was chosen as it is more popular than the built-in `unittests` module, while also allowing greater control over testing via features like fixtures that are commonplace in integration testing suites across languages.


## Potential improvements

- Given that a location column exists for the vast majority of rows in the dataset, a far more accurate postcode can be obtained by using Google's Geolocation API which would take the location data (as well as the provided lat/long data) and return the best location object match from Google's servers including a postcode.
