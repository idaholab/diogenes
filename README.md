# AVC - Livewire

## Our Branching Strategy

* `develop` - Used for work-in-progress, primarily for tools and processes that are under development. There can be feature- or developer-specfic branches from this, as needed. When tools and processes are ready for use in processing data "for real", this branch can be merged to...
* `master` - Used for processing datasets to generate low-level metadata JSON files, generate the data quality assessments, produce dictionaries from low-level metadata, etc. When files are ready to be published or released (e.g., migrated to the Github NREL/livewire repositor that drives the Liveware Data Platform site), this branch can be merged to...
* `release` - This branch exists primarily to represent the version of products like JSON files, PDF dictionaries, content such as FAQ entries which either currently exists on the LDP site or which is ready to be migrated to the LDP site (e.g., we're done with it).

# Running the Diogenes

## Commands and Arguments

**Recommend using VS Code**

python generate_metadata.py -id/--identifier <dataset_identifier> 

The above command encompasses all the required arguments to run the Diogenes. The dataset identifier can be found in the project metadata (which is necessary to run Diogenes). There are a few optional arguments that may or may not be necessary:

* -id - The dataset identifier lookup in the partial metadata
* -ext/--file_extension <ext> -  Describes the extension of the data files so the sytem knows how to read them
* -i/--input_path - The path to the input directory containing `data` and `descriptive_information`
* -o/--output_path - The path to the output directory
* -files_exist_error - If the output directory exists then an error will be thrown when trying to erase the output directory
* -ignore_chars - If there are characters not valid in the UTF-8 standard they will be ignored and printed to stdout
* -n/--n_rows - The max number of rows to sample during metadata/data quality creation
* -p/--processes - The number of processes to spawn for sampling
* -d/--delimiter <delim> - The delimiter used in the data files (tab, comma, etc)
* -to_veritas/--skip_to_veritas <true/false> - Ignores the initial low level metadata (LLMD) creation and moves directly to data quality processing (NOTE: The system assumes the requisite files are in the right place)
* -to_schema/--skip_to_schema_validation <true/false> - Ignores LLMD creation and data quality processing and checks the JSON against the current accepted schema (NOTE: The system assumes the requisite files are in the right place)
* -to_pdf/--skip_to_pdf_generation <true/false> - Ignores LLMD creation, data quality, and schema validation to go to PDF generation (NOTE: The system assumes the requisite files are in the right place)
* -files_exist_error <true/false> - When true, if output files currently exist, instead of erasing them, the system will throw an error
* -a/--annotations - When true, uses the manual annotations as specified in the annotations document instead of trying to infer the relationships between tables (required when multiple tables have columns with the same named primary key)

***Repo Example for Included ds2 Input Files***
* Create input folder (**example already exists in this repo** *diogenes/example_input/*)
   - Requires data files to be in the data folder
   - For most datassets, this requires annotations file in the descriptive_information folder. This is a file that INL creates
   - Requires json file to be placed in the descriptive_information folder. This file comes from the meta repo on the NREL drive. It's under meta/meta and isn't called project metadata (we rename it that). 

* clone [diogenes repo](https://github.inl.gov/Advanced-Transportation/diogenes) (use Github Desktop or git CLI)
* change directory to where you cloned the repo `cd /to/where/you/cloned/to/`
* create virtual environtment (only needed the first time) `python -m venv .venv` or follow these steps for [vs code](https://code.visualstudio.com/docs/python/environments)
* activate the venv (need to do this everytime you reopen the project if vscode doesn't do this automagically)
  - Windows `.\.venv\Scripts\activate`
  - Mac `source ./.venv/bin/activate`
* install required packages in the venv (only needed the first time) `pip install -r requirements.txt`
* [install playwright](https://playwright.dev/python/docs/intro)
  - `playwright install`
* Create an input folder (need to do this for every Livewire dataset. Currently you can only do one project at a time.)
  - For reference there is the 'example_input' folder you can use these files to test
* Run Diogenes:
- Option 1: Command line.
    Change to the metadata folder. `cd metadata`
    Paste this into the terminal. `python generate_metadata.py -id "ds2" -a "true" -i "../example_input/ds2"`
- Option 2: Run the example_main.py script
***Notes:*** 
*You have to remove the output folder before running each time* 
*You can point to differnt input folders by adding the relative or absolute path to a new folder (it doesn't need to be called input)*

## Required Packages

This software was developed using Python 3.12. It uses the following packages from `requirements.txt`:

Core deps:
* numpy
* pandas
* scikit-learn
* scipy
* KDEpy
* openpyxl
* nltk
* jsonschema
* [playwright](https://playwright.dev/python/docs/intro)
* tqdm
* xlsxwriter

Extras / transitive deps (pulled in by core deps; pinned in `requirements.txt`):
* attrs
* click
* joblib
* jsonschema-specifications
* python-dateutil
* pytz
* referencing
* regex
* rpds-py
* six
* typing_extensions
* tzdata

## Architecture (Quick Flow)

Five-line flow:
1) Ingest inputs (annotations + project metadata + data files)
2) Build LLMD via Insight
3) Run data quality via Veritas
4) Validate JSON schema
5) Generate PDF + final metadata outputs

Key modules:
* `metadata/generate_metadata.py` orchestrator and CLI
* `metadata/metadata_generation/insight/` LLMD creation
* `metadata/metadata_generation/veritas/` data quality analysis
* `metadata/metadata_generation/json_schema_validation/` schema checks
* `metadata/metadata_generation/pdf_generation/` PDF dictionary output
* `metadata/metadata_generation/utils/` shared IO and helpers

## Required Inputs

The sub-directory "metadata_generation" in the git repo is assumed to be root for all required inputs

### Configuration Files

Configuration files come prepackaged with the git repo (values are at the discretion of the user)

* `configuration/veritas/general_constraints.csv`: This file defines some of the statistical metrics used by various rule executions in Veritas
* `configuration/veritas/unit_constraints.csv`: This file defines the upper and lower bounds of the values for values of specific units
* `configuration/json_schema/dictionary.json`: This defines the current JSON schema and the final metadata must conform to these specifications

### Input Files

* `input/data/<data files>`: This directory should contain the raw tabular data in csv format from the dataset you wish to analyze. The filenames _must_ be a one-to-one match for the table names in the low-level metadata (LLMD) file.
* `input/descriptive_information/annotations.xlxs`: This file describes the data types, data quality types, descriptions, units, and relationships between different columns and tables
* `input/descriptive_information/project_metadata.json`: This file is obtained from the Livewire repo hosted by PNNL, and it contains titles and descriptions necessary for the software to work
* `input/descriptive_information/table_descriptions.json`: (OPTIONAL) This file is generated by the users and follows a basic JSON format, it is only used if table descriptions are provided by the project authors

# Pipeline - Insight

Insight is a tool designed to generate the initial LLMD for the metadata generation process. It generates everything for the LLMD besides the data quality scores produces by Veritas later in the pipeline. An intermediate file is produced and can be analyzed for correctness. 

## Pipeline Overview (Code Map)

```
CLI / example_main.py
  -> run_metadata_generation(...)  (metadata/generate_metadata.py)
     -> MetadataGenerationSettings + DefaultFileLocations + *FilePaths init
     -> MetadataGenerationInput(settings)

     Insight (LLMD creation)
       metadata/metadata_generation/insight/factory/llmd_factory.py
       inputs: annotations.xlsx, project_metadata.json, optional table_descriptions.json
       output: LLMD JSON (output/insight/<id>.json)

     Veritas (data quality)
       metadata/metadata_generation/veritas/api/drivers.py
       inputs: LLMD JSON + raw data files + constraints CSVs
       outputs: error catalogs, scorecard distillations, quality annotations

     JSON Schema Validation
       metadata/metadata_generation/json_schema_validation/json_schema_validator.py
       input: LLMD + quality output
       uses: metadata/configuration/json_schema/dictionary.json

     PDF Generation
       metadata/metadata_generation/pdf_generation/api/api.py
       input: validated metadata JSON
       output: PDF dictionary

     Final Writers
       metadata/metadata_generation/utils/file_writer.py
       outputs: final metadata JSON + data quality excerpts
```

## Insight Files

* `annotations.xlxs` - The file is comprised of various "sheets" with each sheet representing a different table's information
    * Name: The name of the column in the table
    * Type: The data type for the data within the column. 
    * Data Quality Class: A label for the column that determines what analysis will be executed for the column data. (the various types are described in Veritas)
    * Description: (OPTIONAL) A description of the column data specifying what real-world attribute the column data attempt to record. Descriptions are provided by the data authors.
    * Units: (OPTIONAL) The standard units (SI or Imperial) the column data is measured in.
    * Notes: (OPTIONAL) Any manual notation left by human annotators to remember certain irregularities with the data.
    * Manual Annotations: This specifies the foreign key relationships to other tables. Due to the nature of composite keys, a foreign key can map back to mutiple tables/primary keys. The format to specify is a JSON dictionary formatted as follows: {"foreign_key_references":[{"table":<primary_key_table_name>,"key":<primary_key_attribute_name>},..."table":<primary_key_table_name>,"key":<primary_key_attribute_name>}]}
* `project_metadata.json` - This file is obtained from the PNNL-mandated Livewire repository and has a defined format that must be followed
* `table_descriptions.json` - This is an optional file generated by the user (if table descriptions are present) that follows a very simple JSON format by declaring a dictionary at the JSON root level and writing and entry for each table with a mapping from <table_name> to <description>, e.g.: 

```
{
    "travel_patterns" : "The travel patterns of various individuals in the survey",
    "individuals_in_survey" : "A (redacted) list of all individuals in the survey"
}
```

## Data Types (Typical Data Quality Classes)

* string (typically some form of key, categorical, or none)
* integer (typically some form of key, categorical, numerical, or sequence)
* float (typically numerical or sequence)
* boolean (typically categorical)
* date (typically date)
* time (type time) 
* date-time (typically date-time)
* json (none)
* xml (none)
* blob (none)
* (redacted) (none)
* (none) (none)

## Insight Output

* `output/insight/<dataset_identifier.json>` - This is the intermediate LLMD file that is the input to Veritas, and thus it does not contain data quality information

# Pipeline - Veritas

Veritas is a tool designed to perform data quality analysis on tabular data. While designed for DOE's Livewire Data Platform (LDP) project, the data does not have to originate from the LDP but will be more efficiently analyzed if it is mobility data.

## Constraint Files

In each constraint file, each constraint is given a name, a lower bound, an upper bound, and a description. "n/a" is an acceptable value for the lower or upper bound but will be treated as infinity when considering comparisons within the system. Descriptions have no specified format but serve as a comment system. 

* `general_constraints.csv` - Constraints that are more related to how the software runs rather than applying constraints to any specific domain: 
    * Kurtosis & Skewness: When analyzing numeric columns of data, Veritas checks to see if the data conforms to the normal distribution. Skewness defines the symmetry of the distribution while Kurtosis defines the 'tails' of the distribution. Both statistical bounds are currently set to check whether or not the data conforms to values expected in the normal distribution. You can be more flexible with this value but avoid changing it so much that it no longer applies to a normal distribution
    * Date: This defines the upper and lower bound years a date must fall within to be considered correct
    * Frequency: When analyzing categorical data, each categorical value must be present in a percentage threshold to qualify as correct. The upper bound for this constraint should always be set to "n/a" while the lower bound can be manipulated. It is expressed as a percentage so if you were to specify 0.1 as the lower bound then for each categorical value it must be present in at least 0.1% of the data rows to be considered correct

* `unit_constraints.csv` - There are no dedicated unit constraints within Veritas. Veritas will cross reference the units that are present in the LLMD with the units that are in the unit_constraints.csv file. If the units specified in the LLMD have a matching unit constraint within the unit_constraints.csv file (in the name column) a rule will be created to analyze the column based on that unit constraint. This means that the units in the LLMD must be identical to the units in the 'unit' category if you wish to perform data quality unit analysis. You _can_ have a lower bound and upper bound as "n/a" and "n/a", respectively, but in doing so you aren't really establishing any bounds and are slowing down the processing.

## Data Quality Classes (Data Quality Metrics Listed)

Veritas current supports the following data quality classes:

* `primary_key`: a single-attribute value that is presumed to be unique
* `composite_primary_key`: specifies the column as a partial attribute in a multi-attribute key that forms a unique primary key when other `composite_primary_key` attributes are combined into a single value
* `foreign_key`: a single-attribute value that references an anttribute in another table
* `composite_foreign_key`: specifies the column as a partial attribute in a multi-attribute key that forms a unique foreign key when other `composite_foreign_key` attributes are combined into a single value
* `composite_primary_key_foreign_key`: specifies the column as a partial attribute in a multi-attribute key that forms a unique primary key when other composite_primary_key attributes are combined into a single value. The column also represent a _singular_ foreign key reference (a `composite_primary_key` where a subset of the key is also a `composite_foreign_key` is not yet supported)
* `sequence`: a column that follows a chronological pattern of progression (usually encompasses date or date-time)
* `categorical`: discrete values or descriptors (e.g. car models)
* `numerical`: numerical data (e.g. mileage driven, distance from home)
* `date`: a column that follows a standard date format and has no time
* `date-time`: a column that follows a standard date-time format
* `time`: a column that follows a standard time value has no date
* `none`: no discernable data quality class (no analysis performed) 

## Data Quality Rules

Veritas currently implements the following data quality rules:

* Any `primary_key` data quality type must be unique
* Any `foreign_key` data quality type must have an existing referenced value in the primary key table
* Categorical value must appear a certain (%) threshold in the data with the threshold being specified in the general_constraints.csv file
* Numerical values must be within a certain number of standard deviations from the mean
* Values with units must be within the bounds specified in the unit constraint if a unit constraint exists
* Dates and date-times must be within the year bounds specified in the general_constraints.csv file and be formatted correctly and consistently
* Sequence types must be monotonic (either increasing or decreasing)
* Times must be formatted correctly and contain valid values

When a record is considered erroneous, it can be grouped with other records as the same error. Depending on certain criteria, each error is assigned a group tag and an erroneous/missing record is added to the list of missing or erroneous records. The errors are assigned group IDs and the records are assigned location IDs. When combined the group ID and location ID give us the probability that a specific record is actually in error. It is possible that not all records that have been 'affected' by an error are actually erroneous. Thus, the IDs are necessary.

Group tags serve to identify how an _error_ affects the records it corresponds to. In some cases the records might affect a significant percentage of records in a table, or it might affect multiple records in multiple tables. These groups help give the system perspective on the error and its potential erroneous nature. 

Locations serve to show how a _record_ is in error. Unlike groups that describe the error, the location serves to describe a singular record. Somewhat contrary to its name, a record's location has much less to do with _where_ the record is, and more of how it is in error. You may notice that a lot of the groups have 'soft' language such as 'many' or 'some.' The actual values that determine group ID's can be modified in veritas/error_catalog_generation/group_id_generation.py. Locations don't necessarily have such subjectively determined criterion. **The combination of each group-location pair, and their corresponding probability of error, can be modified in veritas/error_catalog_generation/error_probabilities.py**

## Group & Location Codes

### Identifier Groups

* AFFECTS_MANY_RECORDS: the error affects a significant number of records
* AFFECTS_SOME_RECORDS: the error affects a modest number of records
* AFFECTS_FEW_RECORDS: the error affects a small number of records

### Key Groups

* MULTI_RECORD: the error affects multiple records in a table
* MULTI_TABLE: the error affects multiple records across multiple tables
* SINGLE_RECORD: the error affects a single record

### Numerical Groups

* AFFECTS_MANY_RECORDS: as above
* AFFECTS_SOME_RECORDS: as above
* AFFECTS_FEW_RECORDS: as above

### Categorical Groups

* MULTIPLE_SUB_THRESHOLD: the error affects a significant number of categorical values
* FEW_SUB_THRESHOLD: the error affects a modest number of categorical values
* SINGLE_SUB_THRESHOLD: the error affects a single categorical value

### Date Groups

* AFFECTS_MANY_RECORDS: as above
* AFFECTS_SOME_RECORDS: as above
* AFFECTS_FEW_RECORDS: as above

### Identifier Locations

* UNIQUENESS_VIOLATION: the record is in violation of a uniqueness rule

### Key Location:

* MISSING_PRIMARY_KEY: the record is a missing identifier record
* ORPHAN_FOREIGN_KEY: the record is a key without an identifier

### Categorical Location

* PLAIN_RECORD: no special location is listed for this record

### Numerical Locations

* PLAIN_RECORD: no special location for this record
* OUTSIDE_THREE_STD_DEV: the record is outside three standard deviations
* OUTSIDE_FOUR_STD_DEV: the record is outside four standard deviations

### Date Location

* PLAIN_RECORD: as above

## Output from Veritas

In addition to the final LLMD file with the data quality scores (described below), four additional files are generated:

* `output/veritas/quality_files/error.csv` - For each rule applied to the raw data, an error can be produced. Depending on the rule, there might be multiple errors for a single column of data, or just one. The columns are:
    * rule_ID: the ID of the rule being violated (for lookup in rules.csv)
    * error_ID: the ID of the error
    * group_ID: the assigned group ID
    <br/><br/>

* `output/veritas/quality_files/rules.csv` - Rules can be generated based on a variety of factors (column predisposition to normality, presence of listed unit constraints, etc). This file contains a list of all the rules for every table/column of data pair. The columns are:
    * rule_ID: the ID of the listed rule
    * table_name: the name of the table the rule is applied to
    * attribute_name: the name of the column (attribute) the rule is being applied to
    * rule_description: a preset description of the general rule being applied
    <br/><br/>

* `output/veritas/quality_files/erroneous_records.csv` -  An error can affect multiple records. And each record can be affected by multiple errors. This file contains a list of all the error affected records from all the tables. We say error affected because a record might be affected by an error but depending on its location/group pair we might decide that system is being 'too strict' in its application of the rules, or another record (such as a key-identifier pair) might be responsible for the error. **It is important to note that the same record can be listed multiple times as erroneous in this file due to being affected by multiple errors.** The columns are:
    * `<empty>`: the index of the erroneous record (NOTE: DUE TO HOW PANDAS INDEXES ITS DATAFRAMES WHEN THE DATA FILES ARE VIEWED IN EXCEL YOU MUST ADD +2 TO ALL LOOKUP INDICES TO FIND THE RIGHT RECORD)
    * table_name: the name of the table the erroneous record is from
    * attribute_name: the name of the column (attribute) the erroneous record is from
    * error_ID: the ID of the error the erroneous record is associated with
    * location_ID: the location ID of the erroneous record
    * error_probability: the probability the record is erroneous based on the group/location pair
    <br/><br/>

* `output/veritas/quality_files/missing_records.csv` -  This file contains all the same information as erroneous_records.csv, except, each missing record is precisely that, missing. Missing records are grouped based on table/attribute/value combinations so that the same missing record isn't listed multiple times in the file.

## Data Quality Scores

Veritas produces 6 different data quality scores, 5 of which are also produced at the table level:

* Error Affected Records: This is the percentage of records that were affected by an error in any form (not including missing) and before probabilities were considered
* Erroneous Records: This is the percentage of records that were determined to be erroneous after probabilities were considered
* Missing Records: This is the percentage of records that were found to be missing from the data
* Completeness Metric: This metric is an indication of how many missing records there are
* Accuracy Metric: This metric is a function of how many records were considered erroneous
* Overall Quality Metric: This is a combination of the Accuracy and Completeness metrics and is the only metric not reflected on a table level

For more information on how these metrics are calculated please address the white paper for this software <mark>(RS?: reference/link once published)</mark>

# Pipeline - Schema Validation

Once the final version of the LLMD is generated it is compared to the JSON schema that comes prepackaged with the git repository. It highly recommended to not alter this file but to pull for periodic updates with the code. 

# Pipeline - PDF Generation

Once the LLMD has been verified it is submitted to a process that generates HTML that is then converted to a PDF. There are two files generated by this process:

* `output/pdf_generation/html/dictionary-<dataset_identifier>.html` - This is the HTML used to generate the PDF and can be analyzed for correctness
* `output/pdf_generation/pdf/dictionary-<dataset_identifier>.pdf` - This is the final PDF product and is what is provided to the LDP to be shown to the user.

# Pipeline - Final Metadata

After the final PDF is generated the final metadata is generated. The two different files are: 

* `output/final/metadata/<dataset_identifier>.json` - The final full metadata that is provided to dataset users on the LDP repository
* `output/final/metadata/<dataset_identifier>.quality-summary.json` - A data quality summary extract that is used by the LDP to show the users the data quality on the LDP repository

# Acknowledgements

The data quality work present in this repository orginate from *Data Quality Assessment* by Arkady Maydanchik
