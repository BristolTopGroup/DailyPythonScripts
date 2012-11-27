
inputs = [(1,2),(3,4)]
widths = [1,2,3,4]

for measurement, width in zip(inputs, widths):
    value, error = measurement
    print value, error, width