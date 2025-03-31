import re
from graphviz import Digraph

def parse_schema_file(file_path):
    """Parse the schema.sql file to extract table definitions and relationships."""
    with open(file_path, 'r') as f:
        schema = f.read()

    # Extract CREATE TABLE statements
    create_table_pattern = r'CREATE TABLE (\w+) \((.*?)\);'
    tables = {}
    
    for match in re.finditer(create_table_pattern, schema, re.DOTALL):
        table_name = match.group(1)
        columns_text = match.group(2)
        
        # Extract columns
        columns = []
        for line in columns_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('CONSTRAINT'):
                # Remove trailing comma if exists
                if line.endswith(','):
                    line = line[:-1]
                columns.append(line)
        
        tables[table_name] = columns

    # Extract foreign key relationships
    relationships = []
    fk_pattern = r'FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)'
    
    for table_name, columns in tables.items():
        for column in columns:
            fk_match = re.search(fk_pattern, column)
            if fk_match:
                from_col = fk_match.group(1)
                to_table = fk_match.group(2)
                relationships.append((table_name, to_table, from_col))

    return tables, relationships

def create_er_diagram():
    """Create ER diagram using GraphViz."""
    # Parse schema.sql
    tables, relationships = parse_schema_file('schema.sql')
    
    # Create a new directed graph
    dot = Digraph(comment='University Course Management System ER Diagram')
    dot.attr(rankdir='LR')  # Left to right layout
    
    # Add table nodes
    for table_name, columns in tables.items():
        # Format columns for display
        formatted_columns = []
        for col in columns:
            # Remove FOREIGN KEY clauses for display
            if 'FOREIGN KEY' not in col:
                # Extract just the column name and type
                col_parts = col.split(' ')
                col_name = col_parts[0]
                # Add (PK) if it's a primary key
                if 'PRIMARY KEY' in col.upper():
                    col_name += ' (PK)'
                formatted_columns.append(col_name)
        
        # Create node label
        label = f'''{table_name}\\n''' + '\\n'.join(formatted_columns)
        dot.node(table_name, label)
    
    # Add relationships
    for from_table, to_table, fk_col in relationships:
        dot.edge(from_table, to_table, f'has ({fk_col})')
    
    # Save the diagram
    try:
        dot.render('er_diagram', format='png', cleanup=True)
        print("ER diagram generated successfully as 'er_diagram.png'")
    except Exception as e:
        print(f"Error generating ER diagram: {e}")

if __name__ == '__main__':
    create_er_diagram() 