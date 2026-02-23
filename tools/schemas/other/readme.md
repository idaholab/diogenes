# tools / schemas / other

## Stuff Related to Dealing With Schemas

LDP's primary schemas for high-level and low-level metadata (a "catalog" and a "dictionary", respectively) are maintained as part of a [private Github repository](https://github.com/livewire-data-platform/meta) managed by PNNL. We also have a couple of different version of the catalog schema that we use locally, primarily for validating metadata files:

- `../catalog/catalog.json`
- `../catalog/catalog-strict.json`

## Notes on Validating LDP JSON Files

Until we build our own shiny validator tool, we are using [Justify](https://github.com/leadpony/justify) and pointing it to these standalone schemas. We also use these schemas and this same type of validation with Justify to sanity check any changes to the project's schema (since Justify does that, too).

### Using `justify` to validate a JSON file

```bash
# Validate the schema:
$ justify -s ../catalog/catalog.json

# Validate a JSON file based on the schema:
$ justify -s ../catalog/catalog.json -i path-to-json/file.json
```
