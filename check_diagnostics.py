from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("./diags/hdf5")

print("Iterations:")
print(ts.iterations)

print("\nAvailable fields:")
print(ts.avail_fields)

print("\nAvailable species:")
print(ts.avail_species)
