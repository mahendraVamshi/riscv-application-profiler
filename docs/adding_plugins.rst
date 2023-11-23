How to Add Plugins to the Profiler
==================================

Plugins can be added to the profiler to extend its functionality and analyze program behavior. This guide explains the steps to create and integrate a new plugin into the profiler.

Creating a New Plugin
----------------------

To create a new plugin, follow these steps:

1. Create a New File:

   Create a new Python file in the ``plugins`` folder of the project.

2. Define Inputs:

   Your plugin should accept the following inputs:

   - ``master_inst_list``: A list of all instructions in the program, represented as a list of ``Instruction`` objects.
   - ``ops_dict``: A dictionary containing all operations in the program. Keys represent operation names, and values are operation objects.
   - ``extension_used``: A boolean value indicating whether the program uses an extension. This is used to determine whether to include extension-specific operations in the analysis.

   Any custom inputs must be defined in the configuration YAML file. These will be treated as keyword args to the function.

3. Define Outputs:

   Your plugin should return a dictionary containing the results of your analysis. The keys of this dictionary should be operation names, and the values are metrics that were computed in the plugin itself. All returned values will be tabulated. Eventually, this will become a custom class.

Adding a Plugin to the YAML File
--------------------------------

To execute your plugin, you must add it to the configuration YAML file. To do this, follow these steps:

1. Add ``plugin_name``:

   Add the plugin file name to your YAML file, under `profiles:config:metric`. Under that add your plugin function name along with a header name as `plugin_file_name:`.

2. Execute the Plugin:

   Sit back and run the profiler as usual. Your plugin will be executed along with the rest of the analysis.
