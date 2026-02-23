# Livewire Data Platform - Schemas: Dictionary

This schema defines the structure of a data dictionary for a dataset available
through the Livewire Data Platform (LDP). Each dictionary describes the objects (i.e.,
tables or classes) comprising the dataset and the attributes (i.e., columns of
a table or attributes of a class) of each object. The schema also provides a
means of capturing aspects of the quality of the information in the dataset at
the dataset, object, and attribute level.

## Structure
+ Dictionary
  + $schema
  + name
  + description
  + modified
  + version
  + dataQualitySummary
    + measures [ ]
      + name
      + value
      + _description_
      + _units_
      + _notes_
      + _showAsSummary_
      + ... _(additional properties)_
    + _referenceURL_
    + ... _(additional properties)_
  + objects [ ]
    + name
    + type
    + description
    + count
    + _relationships_
      + _refersToPrimaryKeyTables_
      + _primaryKeys_
    + dataQualitySummary
      + measures [ ]
        + name
        + value
        + _description_
        + _units_
        + _notes_
        + _showAsSummary_
        + ... _(additional properties)_
      + ... _(additional properties)_
    + attributes [ ]
      + name
      + description
      + type
      + units
      + dataQuality [ ]
        + name
        + _description_
        + value
        + units
        + ... _(additional properties)_
      + _dataQualityClass_
      + ... _(additional properties)_
    + ... _(additional properties)_
  + ... _(additional properties)_

## Dictionary Fields
Field | Type | Description | Required
------|------|-------------|---------
`$schema` | string | Schema for this JSON document; if specified, should match this schema's identifier (`https://livewire.energy.gov/schemas/dictionary.json`) | No
`name` | string | Dictionary name or title | Always
`description` | string | Dictionary description | No
`modified` | string | Date in YYYY-MM-DD format when the dictionary was last modified | No
`version` | string | Complete version identifier for the process used to produce the dictionary; specified in 0.0.0 format | Always
`dataQualitySummary` | object | Data quality summary for the dataset, including an array of measures describing data quality and other relevant attributes | No
`objects` | array | Array of objects comprising the dataset | Always

Note: The current version of the schema allows for the presence of additional
fields at the dictionary level but restricts any additional parameters to be
of type `string`. These additional parameters might be used to include
additional information specific to a given dataset or its dictionary. These
additional parameters may not be visible within the LDP UI.

## Object Fields

Within a dictionary, the set of objects (classes or tables) are each described
as follows:

Field | Type | Description | Required
------|------|-------------|---------
`name` | string | Object (table or class) name | Always
`type` | string | Object type. Choices: `table`, `class`| No
`description` | string | Object (table or class) description | No
`count` | integer | Count of items in object (e.g., rows in a table) | No
`relationships` | object | Summarizes the key relationships between the various tables. These keys can be either standalone or composite. | No
`dataQualitySummary` | object | Data quality summary for the object (table or class) | No
`attributes` | array | Array of attributes for this object | Always

Note: The current version of the schema allows for the presence of additional
fields at the object level but restricts any additional fields to be
of type `string`. These additional parameters might be used to include
additional information specific to a given dataset or its dictionary. These
additional parameters may not be visible within the LDP UI.

## Attribute Fields

The attributes of each object in the dataset (e.g, the columns of a table or the
attributes of a class) are described as follows:

Field | Type | Description | Required
------|------|-------------|---------
`name` | string | Attribute/column name | Always
`type` | string | Attribute/column type. Choices: `string`, `integer`, `float`, `boolean`, `date`, `time`, `date-time`, `sequence, `json`, `xml`, `blob` | Always
`description` | string | Attribute/column description | No
`units` | string | Attribute/column units, if applicable | No
`dataQuality` | array | Array of data quality metrics available at the object level | No
`dataQualityClass` | enumeration | Class of attribute, from a data quality perspective | No

Notes:
- The current version of the schema allows for the presence of additional fields at the attribute level but restricts any additional fields to be of type `string`. These additional parameters might be used to include additional information specific to a given dataset or its dictionary. These additional parameters may not be visible within the LDP UI.
- Type `sequence` represents a numeric value which is expected to be monitonically increasing across a group of records and confers information about how those records should be ordered without necessarily specifying the time or date/time of each record.

## Relationships Fields

Field | Type | Description | Required
------|------|-------------|---------
`refersToPrimarykeyTables` | object | A dictionary of tables that specify the foreign key relationships between this table and its corresponding primary key tables. Each table has an array of keys specifying the mapping from foreign key (`foreignKey`) to primary key (`foreignKeyRefersTo`) | No
`primaryKeys` | array | An array of primary key name(s) that comprise the primary key in this table | No

## Data Quality Summary Fields

An aggregate representation of all the data in the dataset. 

Field | Type | Description | Required
------|------|-------------|---------
`measures` | string | A list of different aspects of quality throughout the dataset that include the same values as the data quality across each table but also include an overall aggregate score
`reference_url` | string | The file path to the pdf representation of the metadata 

## Data Quality Metric Fields

Characterization of data quality at the attribute level is specified as an array of
metrics, each described as follows:

Field | Type | Description | Required
------|------|-------------|---------
`name` | string | Name/title for this data quality metric | Always
`description` | string | Description of this data quality metric | No
`value` | string, integer, number | Value for this data quality metric | Always
`units` | string | Units, if applicable, for this data quality metric; if not applicable, should be specified as `n/a` | Always
`frequencies` | array | Frequency distribution, if applicable | No

Note: The current version of the schema allows for the presence of additional
fields at the data quality metric level but restricts any additional fields to be
of type `string`. These additional parameters might be used to include
additional information specific to a given dataset or its dictionary. These
additional parameters may not be visible within the LDP UI.

## Frequency Distributions

For categorical data, the schema supports inclusion of frequency distribution
information as part of a data quality metric. The distribution is provided as an
array of objects, with each object describing one category and how frequently it
appears.

Field | Type | Description | Required
------|------|-------------|---------
`name` | string, integer, number | Name or value (for categorical data which is provided exclusively as a set of integer codes) of this category or group in the frequency distribution | Always
`frequencyN` | integer | Count of entries in this group in the frequency distribution | No
`frequencyPercent` | number | Percent of entries in this group in the frequency distribution | No

Notes:
1. Either `frequencyN` or `frequencyPercent` (or both) should be provided for the
distribution to be meaningful.
2. The current version of the schema allows for the presence of additional fields
within each of objects comprising the distribution but restricts those additional fields to
be of type `string`.
3. By convention, the array of objects comprising the distribution is
sorted in descending order by frequency for ease of consumption/display.
4. The schema allows for the presence of additional fields as part of the frequency
distribution, but does restrict any additional fields to be of type `string`.

***

## Notes
