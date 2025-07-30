This repo explores the whitepaper authored by data.world and their cwd-benchmark, which is also on github.
The starting point is the benchmark.ipynb

---------- below is AI generated TTL to Pandas DF converter -----------
# TTL to Pandas DataFrame Converter

This repository contains Python code to read TTL (Turtle) files and convert their content into pandas DataFrames for analysis.

## Overview

The TTL file (`acme-benchmark.ttl`) contains RDF triples describing insurance benchmark queries, inquiries, and their relationships. The code provides two approaches to convert this data into pandas DataFrames:

1. **Simple conversion**: Basic triple extraction
2. **Structured conversion**: Organized extraction with entity-specific processing

## Files

- `ttl_to_dataframe.py` - Comprehensive TTL reader with structured data extraction
- `simple_ttl_reader.py` - Simple TTL reader for basic triple extraction
- `acme-benchmark.ttl` - Source TTL file containing insurance benchmark data
- `README.md` - This documentation file

## Requirements

```bash
pip install pandas rdflib
```

## Usage

### Simple Approach

```python
from simple_ttl_reader import simple_ttl_to_dataframe

# Load TTL file into DataFrame
df, stats = simple_ttl_to_dataframe("data/ACME_Insurance/investigation/acme-benchmark.ttl")

print(f"DataFrame shape: {df.shape}")
print(f"Total triples: {stats['total_triples']}")
print(df.head())
```

### Comprehensive Approach

```python
from ttl_to_dataframe import read_ttl_to_dataframe, analyze_ttl_content

# Load TTL file into structured DataFrames
df_triples, df_structured = read_ttl_to_dataframe("data/ACME_Insurance/investigation/acme-benchmark.ttl")

# Analyze the content
analysis = analyze_ttl_content(df_triples, df_structured)

print(f"Total triples: {analysis['total_triples']}")
print(f"Entity types: {analysis['entity_types']}")
```

## Data Structure

The TTL file contains the following types of entities:

### 1. SQL Queries (45 entities)
- Query text in SQL format
- Descriptions and titles
- Associated metadata (agent ID, project ID)

### 2. SPARQL Queries (44 entities)  
- Query text in SPARQL format
- Descriptions and titles
- Associated metadata

### 3. Inquiries (44 entities)
- Natural language prompts
- Expected query references
- Links to corresponding SQL/SPARQL queries

### 4. Investigation (1 entity)
- Overall investigation metadata
- References to all inquiries
- Schema and model specifications

## Output DataFrames

### Triples DataFrame
Contains all RDF triples with columns:
- `subject`: The subject URI
- `subject_local`: Local name of the subject
- `predicate`: The predicate URI  
- `predicate_local`: Local name of the predicate
- `object`: The object value
- `object_type`: 'URI' or 'Literal'

### Structured DataFrame
Contains organized entities with columns:
- `entity_type`: Type of entity (SqlQuery, SparqlQuery, Inquiry, Investigation)
- `id`: Entity identifier
- `queryText`: Query content (for queries)
- `description`: Entity description
- `title`: Entity title
- `prompt`: Natural language prompt (for inquiries)
- Additional metadata columns

## Sample Statistics

From the ACME benchmark file:
- **Total RDF triples**: 950
- **Unique subjects**: 137
- **Unique predicates**: 17
- **Entity breakdown**:
  - SQL Queries: 45
  - SPARQL Queries: 44  
  - Inquiries: 44
  - Investigation: 1

## Example Queries

### SQL Query Example
```sql
SELECT COUNT(*) AS NoOfClaims
FROM claim
```

### SPARQL Query Example
```sparql
PREFIX : <https://myinsurancecompany.linked.data.world/d/chat-with-the-data-benchmark/>
PREFIX in: <http://data.world/schema/insurance/>

select (count(?policy) as ?NoOfPolicy)
where{
    SERVICE :mapped {
        ?policy rdf:type in:Policy.
    }
}
```

### Inquiry Example
**Prompt**: "What is the average loss of each policy by policy number and number of claims where loss is the sum of loss payment, loss reserve, expense payment, expense reserve amounts?"

**Expected Queries**: 2 (one SQL, one SPARQL)

## Running the Code

### Command Line Execution

```bash
# Run comprehensive analysis
python ttl_to_dataframe.py

# Run simple conversion
python simple_ttl_reader.py
```

### Output Files

The scripts generate CSV files for further analysis:
- `acme_benchmark_triples.csv` - All RDF triples
- `acme_benchmark_structured.csv` - Structured entities
- `simple_ttl_output.csv` - Simple triple extraction

## Key Features

1. **RDF Triple Extraction**: Converts all TTL triples to tabular format
2. **Entity Recognition**: Identifies and categorizes different entity types
3. **Metadata Preservation**: Maintains all properties and relationships
4. **Analysis Tools**: Provides summary statistics and content analysis
5. **Export Capabilities**: Saves results to CSV for further processing
6. **Error Handling**: Robust error handling for malformed data

## Use Cases

- **Data Analysis**: Convert RDF data to pandas for statistical analysis
- **Query Mining**: Extract and analyze SQL/SPARQL queries
- **Benchmark Studies**: Analyze query benchmarks and their relationships
- **Data Integration**: Prepare RDF data for integration with other datasets
- **Research**: Support research on query languages and database benchmarks

## Notes

- The code handles both URI references and literal values
- Namespace prefixes are preserved and can be expanded
- Large TTL files are supported through efficient streaming
- The structured approach provides better organization for analysis
- All original relationships and metadata are preserved in the conversion
