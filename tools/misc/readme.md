# livewire / tools / misc

Parquet to CSV & CSV to Parquet conversion tools

Schema Files:

A schema file is required to coerce datatypes when converting from a CSV file to a parquet file. 
There are four fields that must be specified in the schema. The first is the column name
The schema file must list the different columns in the order they are found in the CSV file. 
The name of the column in the schema must also be identical to the name in the CSV file. The second field
in the schema is the datatype. This does not have to be quoted unless the type includes a special character
(like a comma). The next field specified whether the column can have null values. You specify this via a 
boolean (True or False). The final field is the metadata associated with the columns (DO NOT ALTER not yet implemented).

Example Schema File:

Field Name, Field Type, Nullable, Metadata
ReservationMode, "string", True, {}
ReservationStartTime, "string", True, {}
BookingStartTime, "string", True, {}
BookingEndedAt, "string", True, {}
CancelledAt, "string", True, {}
CancellationReason, "string", True, {}
DriveTime, "string", True, {}

Coercible Type Values:
"data"
"null"
"string"
"binary"
"bool"
"data"
"timestamp"
"double"
"float"
"byte"
"int"
"long"
"short"
"decimal(x, y)" where x is the precision (max # of total digits) and y is the scale (max # of total digits behind decimal point)

CSV to Parquet reader:
When coercing the datatypes from a parquet to a csv 

(content)