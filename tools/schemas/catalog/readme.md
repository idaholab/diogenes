# Livewire Data Platform - Schemas: Catalog

This schema defines the structure of one of catalogs of datasets available through the
Livewire Data Platform (LDP). In its current implementation, it is an expansion of the
DCAT-US Schema v1.1 (Project Open Data Metadata Schema) described at
https://resources.data.gov/resources/dcat-us/.

In expanding the POD metadata schema, we have incorporated additional elements or expanded
existing elements as described below. Within LDP, we also designate some optional
elements from the original POD schema as required based on how they are used. There are also
several elements required by POD which LDP does not consider required. For all other
elements, we refer the user to the documentation
at https://resources.data.gov/resources/podm-field-mapping/.

In addition to the primary schema `catalog.json`, we have a secondary version which can be
useful for validation: `catalog-strict.json` will generate validation errors for any additional
attributes (useful for catching incorrectly spelled/named attributes) and for any keywords
which are not in the current curated set.

## LDP Catalog Structure

### Key

+ Inherited from POD
+ **Inherited from POD (required)**
+ _Specific to LDP_
+ _**Specific to LDP (required)**_

### Structure
+ Catalog
  + @context
  + @id
  + @type
  + _**accessLevel**_
  + _**accessRestriction**_
  + _citation_
  + **conformsTo**
  + _contactPoint [ ]_
    + _@type_
    + **fn**
    + **hasEmail**
    + _hasOrg_
    + _hasRole_
  + describedBy
  + _description_
  + _**identifier**_
  + _identifierSchema_
  + _participatingOrganizations [ ]_
    + @type
    + **name**
    + subOrganizationOf
  + _references [ ]_
    + _@type_
    + _**referenceTitle**_
		+ _referenceCategory_
    + _referenceURL_
  + _**shortName**_
  + _**title**_
  + **dataset [ ]**
    + @type
    + **accessLevel**
    + _**accessRestriction**_
    + accrualPeriodicity
    + **bureauCode**
    + conformsTo
    + **contactPoint [ ]**
      + _@type_
      + **fn**
      + **hasEmail**
      + _hasOrg_
      + _hasRole_
    + dataQuality
    + describedBy
    + describedByType
    + **description**<sup>1</sup>
    + distribution [ ]
      + @type
      + accessURL
      + _accessRole [ ]_
      + conformsTo
      + describedBy
      + describedByType
      + **description**
      + _**distributionType**_
      + downloadURL
      + format
      + **identifier**
      + _identifierSchema_
      + mediaType (**required if downloadURL is specified**)
      + _**shortName**_
      + **title**
    + _doiName_
    + **identifier**
    + _identifierSchema_
    + isPartOf
    + issued
    + **keyword [ ]**
    + landingPage
    + language
    + license
    + **modified**
    + primaryITInvestmentUII
    + **programCode**
    + **publisher [ ]**
      + @type
      + **name**
      + subOrganizationOf
    + references [ ]
      + _@type_
      + _**referenceTitle**_
			+ _referenceCategory_
      + _referenceURL_
    + rights
    + _**shortName**_
    + spatial [ ]
    + systemOfRecords
    + temporal
    + theme
    + **title**<sup>1</sup>

## LDP-specific Catalog Fields

Within the LDP, each project sharing one or more datasets is described by a `catalog` object. LDP expands on POD's `catalog` object with the following fields:

Field | Label | Definition | Required<sup>2</sup>
----- | ----- | ---------- | --------------------
`accessLevel` | Project/Catalog Access Level | The extent to which information about this project/catalog can be made publicly-available. Choices: public (information is or could be made publicly available to all without restrictions), restricted public (information is available under certain use restrictions), or non-public (information is not available to members of the public). | Always
`accessRestriction` | Project/Catalog Access Restriction | Access restriction, if any, applied in conjunction with accessLevel to determine whether information about this project/catalog can be accessed by a given platform user. | If-Applicable
`citation` | Catalog Citation | Citation to be used in publications for which the catalog/project's data was used. | No
`contactPoint` | Catalog Point(s) of Contact | Contact person(s)'s name and contact information for the project catalog. | No
`description` | Catalog Description | Human-readable description (e.g., an abstract) with sufficient detail to enable a user to quickly understand whether the asset is of interest. | No
`identifier` | Unique Catalog Identifier | A unique identifier for the the project catalog. _May be subject to structural contraints imposed by `identifierSchema`._ | Always
`identifierSchema` | Identifier Schema | Object defining structure, content, and semantics of `identifier`; primarily applicable to datasets and distributions hosted within LDP. | If applicable
`participatingOrganizations` | Participating Organization(s) | Organization(s) who participated in the project producing the dataset(s) within this catalog. | No
`references` | Catalog References | References, if any, for the project producing the datasets within this catalog. | No
`shortName` | Short Catalog Name | Concise name for this object; should be human-readable; may be munged for use in UI. | Always
`title` | Catalog Title | Human-readable name of the catalog. Should be in plain English and include sufficient detail to facilitate search and discovery. | Always

## LDP-specific Dataset Fields

Each dataset shared by a project is described by a `dataset` object.  LDP epands on or modifies POD's `dataset` object with the following fields:

Field | Label | Definition | Required<sup>2</sup>
----- | ----- | ---------- | --------------------
`accessRestriction` | Dataset Access Restriction | Access restriction, if any, applied in conjunction with accessLevel to determine whether this dataset can be accessed by a given platform user. | If-Applicable
`contactPoint` | Dataset Point(s) of Contact | Contact person(s)'s name and email for the asset. _LDP expands POD to support mulitple POC's for a dataset._ | Always
`doiName` | Dataset DOI Name | The digital object identifier (DOI) name for the dataset. | No
`identifier` | Unique Dataset Identifier | A unique identifier for the the dataset as maintained within a project catalog. _May be subject to structural contraints imposed by `identifierSchema`._ | Always
`identifierSchema` | Identifier Schema | Object defining structure, content, and semantics of `identifier`; primarily applicable to datasets and distributions hosted within LDP. | If applicable
`references` | Related Documents | References, if any, for the asset; specified as a required title and optional URL. _Change to existing POD element for consistency with catalog references._ | No
`shortName` | Short Dataset Name | Concise name for this object; should be human-readable; may be munged for use in UI. | Always
`spatial` | Spatial |  The range of spatial applicability of a dataset. Could include a spatial region like a bounding box or a named place. For LDP, if specified, this should be an array of latitude/longitude pairs. _Modification of existing POD element._ | No

## LDP-specifc Distribution Fields

Each method for sharing a given dataset is described by a `distribution` object. Each `distribution` object can describe an API, a downloadable resource (e.g., a CSV, Excel, or compressed archive file), or an asset available by request. LDP expands on POD's `dataset` object with the following fields:

Field | Label | Definition | Required<sup>2</sup>
----- | ----- | ---------- | --------------------
`accessRole` | Access Role | Access role(s), if applicable, which users must hold in order to access this distribution. _Primarily used for managing access to API distributions._ | If applicable
`distributionType` | Distribution Type | The type of this distribution; must be one of the following: "api", "by-request", "download-external", "download-livewire". | Always
`identifier` | Unique Distribution Identifier | A unique identifier for the distribution as maintained within a project catalog. _May be subject to structural contraints imposed by `identifierSchema`._ | Always
`identifierSchema` | Identifier Schema | Object defining structure, content, and semantics of `identifier`; primarily applicable to datasets and distributions hosted within LDP. | If applicable
`shortName` | Short Distribution Name | Concise name for this object; should be human-readable; may be munged for use in UI. | No

***

## Conventions and Guidelines

### Project and Dataset Point(s) of Contact (POC)

As described in the schema above, both `catalog.contactPoint` and `dataset.contactPoint` are
arrays of one or more POC's for the relevant object. Each POC is
required to have attributes `fn` (name) and `hasEmail` (email address). In addition, each POC
_may_ include `hasOrg` (identifying the contact's organization) and/or `hasRole` (identifying
the contact's role with the catalog or dataset).

For LDP, the following conventions apply to using these additional attributes:

+ If the POC's parent organization matters and can't be easily inferred from the catalog/project or dataset description, the contact's organization should be specified with attribute `hasOrg`. This could include the following situations (intended to be illustrative rather than exhaustive):
  + Multiple POC's are listed and those POC's are from more than one organization
  + A project or dataset is affiliated with multiple organizations, and having the POC's organization listed clarifies the contact's organizational affiliation
  + A contact is not affiliated with any of the organizations listed or described for the project or dataset
+ For projects or datasets associated with a single organization, if a single contact is listed and that contact is affiliated with the project's/dataset's organization, attribute `hasOrg` should typically be omitted.
+ In situations where catalog/project or dataset owners wish to list more than one POC, each contact should include attribute `hasRole`. Roles should be chosen in a manner which assists LDP users in deciding which listed POC should be contacted based on the nature of their inquiry. Roles should be concisely stated. The LDP project team will assist in curating contact roles for consistency and clarity.
+ Project/catalog and dataset owners may opt to specify a POC's role even when only one POC is listed.

***

## Notes

1. Specific attributes within the catalog require review and approval by the DOE communications team/processes and **must not be changed** once a given project's datasets have been published within the LDP. These attributes currently include `dataset.title` and `dataset.description`.
2. The required vs. optional aspect of many schema elements, both sourced from the original POD schema and which we have added for LDP, is subject to change.
