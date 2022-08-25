# pyslib
My library `slib` written in python. The library is used to load, plot, process, and save data for space physics research.

NOTE: it's still under development.

## Load data files for missions
The `mission` directory contains subdirectories for each mission. For example, the `rbsp` subdirectory contains modules that load the data files for each instrument. We typically request these data files by simply specifying the wanted time range, probe (if multi-spacecaft missions), and the type of data for the given instrument.

For example, to load the EFW L2 Vsvy data, we do
```
import mission

time_range = ['2013-06-01','2013-06-02']
probe = 'a'
id = 'l2%vsvy'
files = mission.rbsp.efw.load_file(time_range, probe, id)
```

To simply read and plot the data out of the files, we can use the `pytplot` package.
```
import pytplot
pytplot.cdf_to_tplot(files)
pytplot.tplot(['vsvy','orbit_num'])
```

Modules in the `mission` directory are simply the "drivers" for a certain mission and instrument. In most cases, general users do not need to call them directly because there are higher-level "drivers" to read data out of these data files, which is explained in the next section.


## Read data from the loaded files
The `read` directory contains modules to read specific data from the data files loaded by the mission-based modules and to store the data in memory to be processed, plotted, and saved.

The modules in the `read` directory play a central role in the `slib` package. The key idea here is that these modules handle the mission and instrument specific details and return physics variables that can be further processed uniformly.

For example, although GOES and THEMIS both measure the magnetic field, the data loading and calibration are mission and instrument specific. Ideally, we, the general users, do not need to know these details. We simply want to load magnetic field data for the related missions, with simple commands like
```

# Settings for loading B field.
time_range = ['2013-06-01','2013-06-02']
coord = 'sm'
goes_probes = ['g13']
themis_probes = ['a','d','e']

# Load the B field data to memory.
bfield_vars = list()
for probe in goes_probes:
    bfield_vars.append(read.goes.bfield(time_range, probe=probe, coord=coord))
for probe in themis_probes:
    bfield_vars.append(read.themis.bfield(time_range, probe=probe, coord=coord))

# Process the data uniformly.
for var in bfield_vars:
    libs.math.detrend(var)

# Plot the data to a file.
plot_file = '~/test_bfield.pdf'
fig_size = (8,6)
slib.open_plot(plot_file, fig_size=fig_size)
slib.plot(bfield_vars)
slib.close_plot()

# Save the data to a file.
data_file = '~/test_bfield.cdf'
slib.save(bfield_vars, data_file)
```

This is essentially what the `pyspedas` and `pytplot` allow us to do. But the `slib` package allows us to read and process the data more flexibily.

NOTE: this is a framework to be filled as need. Please join me to fill in the mission and instrument you are familiar with.

## The variable management system
I call the data that are read by the modules in the `read` directory as **variables**. There needs to be a system that manage the variables.

For example, we can get (and set) the actual data, time, depending data, and settings of a variable. We can rename, save, and plot a variable. We can merge multiple variables to one or split one to multiple variables.

This is essentially achieving the same functionality as part of the `pytplot` package. However, there are some technical details to improve the memory management.


## The libraries
There are several modules in the `libs` directory to provide low-level modules, for example, on time conversion among different formats, on input/output for different file formats, on coordinate transformations, etc. I will not go through the details in this overview document.