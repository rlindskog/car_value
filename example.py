from car_value import comparisons

query = {
    'region': 'sfbay',
    'make': 'honda',
    'model': 'accord'
}

comparisons = Comparisons(query)

for comparison in comparisons():
    print(comparison)
