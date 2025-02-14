#!/usr/bin/env python3
import yaml
from graphviz import Digraph
import sys
from pathlib import Path

def create_knowledge_graph(yaml_file, output_dir='output'):
    # Read YAML file
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    # Create Digraph object
    dot = Digraph(comment='Knowledge Graph')
    dot.attr(rankdir='LR')  # Left to right layout
    
    # Set graph attributes for better visualization
    dot.attr('node', shape='circle', style='filled', fillcolor='lightblue')
    dot.attr('edge', fontsize='10')

    # Add nodes (entities)
    for entity in data['entities']:
        # Use title attribute for hover text (description)
        dot.node(entity['id'], entity['name'], tooltip=entity['description'])

    # Add edges (relationships)
    for rel in data['relationships']:
        dot.edge(rel['source'], rel['target'], rel['name'])

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Save the graph
    output_path = Path(output_dir) / 'knowledge_graph'
    dot.render(output_path, format='svg', cleanup=True)
    return output_path.with_suffix('.svg')

def create_inline_html(svg_file, output_dir='output'):
    # Read the SVG content
    with open(svg_file, 'r') as f:
        svg_content = f.read()
    
    # Create HTML with inline SVG
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Graph Visualization</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        #graph-container {{
            width: 100%;
            overflow: auto;
        }}
        svg {{
            width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Knowledge Graph Visualization</h1>
        <div id="graph-container">
            {svg_content}
        </div>
    </div>
</body>
</html>'''
    
    # Write the HTML file
    output_path = Path(output_dir) / 'knowledge_graph_inline.html'
    with open(output_path, 'w') as f:
        f.write(html_content)
    return output_path

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python knowledge_graph_visualizer.py <yaml_file>")
        sys.exit(1)
    
    svg_file = create_knowledge_graph(sys.argv[1])
    inline_html = create_inline_html(svg_file)
    print(f"Generated SVG file: {svg_file}")
    print(f"Generated inline HTML file: {inline_html}")
