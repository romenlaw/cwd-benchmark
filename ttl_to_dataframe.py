import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS
import re

def read_ttl_to_dataframe(file_path):
    """
    Read a TTL (Turtle) file and convert its content into a pandas DataFrame.
    
    Args:
        file_path (str): Path to the TTL file
    
    Returns:
        pd.DataFrame: DataFrame containing the RDF triples and structured data
    """
    
    # Create an RDF graph and parse the TTL file
    g = Graph()
    g.parse(file_path, format='turtle')
    
    # Define namespaces used in the file
    QandA = Namespace("http://models.data.world/benchmarks/QandA#")
    dwt = Namespace("https://templates.data.world/")
    dct = Namespace("http://purl.org/dc/terms/")
    
    # Lists to store extracted data
    data_records = []
    
    # Extract all triples and organize them
    for subject, predicate, obj in g:
        # Convert URIs and literals to strings for easier handling
        subj_str = str(subject)
        pred_str = str(predicate)
        obj_str = str(obj)
        
        # Extract the local name from URIs for better readability
        subj_local = subj_str.split('/')[-1].split('#')[-1] if '/' in subj_str or '#' in subj_str else subj_str
        pred_local = pred_str.split('/')[-1].split('#')[-1] if '/' in pred_str or '#' in pred_str else pred_str
        
        data_records.append({
            'subject': subj_str,
            'subject_local': subj_local,
            'predicate': pred_str,
            'predicate_local': pred_local,
            'object': obj_str,
            'object_type': 'URI' if isinstance(obj, URIRef) else 'Literal'
        })
    
    # Create DataFrame from the extracted triples
    df_triples = pd.DataFrame(data_records)
    
    # Create a more structured DataFrame focusing on key entities
    structured_data = []
    
    # Extract queries and their properties
    for subject in g.subjects(RDF.type, dwt.SqlQuery):
        query_data = {'entity_type': 'SqlQuery', 'id': str(subject)}
        
        # Extract common properties
        for prop in [QandA.inLanguage, QandA.queryText, dct.description, dct.title, dwt.agentId, dwt.content, dwt.projectId]:
            values = list(g.objects(subject, prop))
            if values:
                prop_name = str(prop).split('/')[-1].split('#')[-1]
                query_data[prop_name] = str(values[0])
        
        structured_data.append(query_data)
    
    # Extract SPARQL queries
    for subject in g.subjects(RDF.type, dwt.SparqlQuery):
        query_data = {'entity_type': 'SparqlQuery', 'id': str(subject)}
        
        # Extract common properties
        for prop in [QandA.inLanguage, QandA.queryText, dct.description, dct.title, dwt.agentId, dwt.content, dwt.projectId]:
            values = list(g.objects(subject, prop))
            if values:
                prop_name = str(prop).split('/')[-1].split('#')[-1]
                query_data[prop_name] = str(values[0])
        
        structured_data.append(query_data)
    
    # Extract Inquiries
    for subject in g.subjects(RDF.type, QandA.Inquiry):
        inquiry_data = {'entity_type': 'Inquiry', 'id': str(subject)}
        
        # Extract prompt
        prompts = list(g.objects(subject, QandA.prompt))
        if prompts:
            inquiry_data['prompt'] = str(prompts[0])
        
        # Extract expected queries
        expected_queries = list(g.objects(subject, QandA.expects))
        if expected_queries:
            inquiry_data['expected_queries'] = [str(q) for q in expected_queries]
            inquiry_data['expected_queries_count'] = len(expected_queries)
        
        structured_data.append(inquiry_data)
    
    # Extract Investigation
    for subject in g.subjects(RDF.type, QandA.Investigation):
        investigation_data = {'entity_type': 'Investigation', 'id': str(subject)}
        
        # Extract properties
        for prop in [QandA.modelSpecification, QandA.sampleData, QandA.schemaSpecification]:
            values = list(g.objects(subject, prop))
            if values:
                prop_name = str(prop).split('/')[-1].split('#')[-1]
                investigation_data[prop_name] = str(values[0])
        
        # Extract pursued inquiries
        pursued_inquiries = list(g.objects(subject, QandA.pursues))
        if pursued_inquiries:
            investigation_data['pursued_inquiries'] = [str(q) for q in pursued_inquiries]
            investigation_data['pursued_inquiries_count'] = len(pursued_inquiries)
        
        structured_data.append(investigation_data)
    
    # Create structured DataFrame
    df_structured = pd.DataFrame(structured_data)
    
    return df_triples, df_structured

def analyze_ttl_content(df_triples, df_structured):
    """
    Analyze the content of the TTL file and provide summary statistics.
    
    Args:
        df_triples (pd.DataFrame): DataFrame containing RDF triples
        df_structured (pd.DataFrame): DataFrame containing structured entities
    
    Returns:
        dict: Summary statistics
    """
    
    analysis = {
        'total_triples': len(df_triples),
        'unique_subjects': df_triples['subject'].nunique(),
        'unique_predicates': df_triples['predicate'].nunique(),
        'entity_types': df_structured['entity_type'].value_counts().to_dict() if not df_structured.empty else {},
        'predicate_frequency': df_triples['predicate_local'].value_counts().head(10).to_dict(),
        'object_types': df_triples['object_type'].value_counts().to_dict()
    }
    
    return analysis

# Example usage
if __name__ == "__main__":
    # Read the TTL file
    file_path = "data/ACME_Insurance/investigation/acme-benchmark.ttl"
    
    try:
        # Convert TTL to DataFrames
        df_triples, df_structured = read_ttl_to_dataframe(file_path)
        
        print("=== TTL File Analysis ===")
        print(f"Successfully loaded TTL file: {file_path}")
        
        # Analyze content
        analysis = analyze_ttl_content(df_triples, df_structured)
        
        print(f"\n=== Summary Statistics ===")
        print(f"Total RDF triples: {analysis['total_triples']}")
        print(f"Unique subjects: {analysis['unique_subjects']}")
        print(f"Unique predicates: {analysis['unique_predicates']}")
        
        print(f"\n=== Entity Types ===")
        for entity_type, count in analysis['entity_types'].items():
            print(f"{entity_type}: {count}")
        
        print(f"\n=== Top 10 Most Common Predicates ===")
        for predicate, count in analysis['predicate_frequency'].items():
            print(f"{predicate}: {count}")
        
        print(f"\n=== Object Types ===")
        for obj_type, count in analysis['object_types'].items():
            print(f"{obj_type}: {count}")
        
        print(f"\n=== DataFrame Shapes ===")
        print(f"Triples DataFrame: {df_triples.shape}")
        print(f"Structured DataFrame: {df_structured.shape}")
        
        print(f"\n=== Sample of Triples DataFrame ===")
        print(df_triples.head())
        
        print(f"\n=== Sample of Structured DataFrame ===")
        print(df_structured.head())
        
        # Save DataFrames to CSV for further analysis
        df_triples.to_csv("acme_benchmark_triples.csv", index=False)
        df_structured.to_csv("acme_benchmark_structured.csv", index=False)
        
        print(f"\n=== Files Saved ===")
        print("- acme_benchmark_triples.csv: Contains all RDF triples")
        print("- acme_benchmark_structured.csv: Contains structured entities (queries, inquiries, etc.)")
        
        # Display specific query examples
        print(f"\n=== Sample SQL Queries ===")
        sql_queries = df_structured[df_structured['entity_type'] == 'SqlQuery']
        if not sql_queries.empty:
            for idx, row in sql_queries.head(3).iterrows():
                print(f"\nQuery ID: {row['id']}")
                print(f"Description: {row.get('description', 'N/A')}")
                print(f"Title: {row.get('title', 'N/A')}")
                if 'queryText' in row and pd.notna(row['queryText']):
                    query_text = row['queryText'][:200] + "..." if len(row['queryText']) > 200 else row['queryText']
                    print(f"Query: {query_text}")
        
        print(f"\n=== Sample SPARQL Queries ===")
        sparql_queries = df_structured[df_structured['entity_type'] == 'SparqlQuery']
        if not sparql_queries.empty:
            for idx, row in sparql_queries.head(2).iterrows():
                print(f"\nQuery ID: {row['id']}")
                print(f"Description: {row.get('description', 'N/A')}")
                print(f"Title: {row.get('title', 'N/A')}")
                if 'queryText' in row and pd.notna(row['queryText']):
                    query_text = row['queryText'][:200] + "..." if len(row['queryText']) > 200 else row['queryText']
                    print(f"Query: {query_text}")
        
        print(f"\n=== Sample Inquiries ===")
        inquiries = df_structured[df_structured['entity_type'] == 'Inquiry']
        if not inquiries.empty:
            for idx, row in inquiries.head(3).iterrows():
                print(f"\nInquiry ID: {row['id']}")
                print(f"Prompt: {row.get('prompt', 'N/A')}")
                print(f"Expected Queries Count: {row.get('expected_queries_count', 'N/A')}")
                
    except Exception as e:
        print(f"Error processing TTL file: {e}")
