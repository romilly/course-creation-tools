import pytest
from pathlib import Path
import yaml
import json
from knowledge_graph_visualizer import create_knowledge_graph, create_inline_html
import tempfile
import os

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def sample_yaml_file(temp_dir):
    yaml_content = {
        "entities": [
            {
                "id": "test1",
                "name": "Test Entity 1",
                "description": "Description 1"
            },
            {
                "id": "test2",
                "name": "Test Entity 2",
                "description": "Description 2"
            }
        ],
        "relationships": [
            {
                "source": "test1",
                "target": "test2",
                "name": "test relationship"
            }
        ]
    }
    
    yaml_path = Path(temp_dir) / "test_graph.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(yaml_content, f)
    return yaml_path

def test_create_knowledge_graph(sample_yaml_file, temp_dir):
    # Generate the SVG file
    svg_file = create_knowledge_graph(sample_yaml_file, output_dir=temp_dir)
    
    # Check that the SVG file was created
    assert svg_file.exists()
    
    # Check that the SVG file contains expected content
    with open(svg_file) as f:
        svg_content = f.read()
        assert 'Test Entity 1' in svg_content
        assert 'Test Entity 2' in svg_content
        assert 'test relationship' in svg_content

def test_create_inline_html(sample_yaml_file, temp_dir):
    # Generate the SVG and HTML files
    svg_file = create_knowledge_graph(sample_yaml_file, output_dir=temp_dir)
    html_file = create_inline_html(svg_file, output_dir=temp_dir)
    
    # Check that the HTML file was created
    assert html_file.exists()
    
    # Check HTML content
    with open(html_file) as f:
        html_content = f.read()
        # Check for required HTML structure
        assert '<!DOCTYPE html>' in html_content
        assert '<html' in html_content
        assert '<svg' in html_content
        # Check for graph content
        assert 'Test Entity 1' in html_content
        assert 'Test Entity 2' in html_content
        assert 'test relationship' in html_content

def test_invalid_yaml_structure():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create invalid YAML file (missing required fields)
        invalid_yaml = {
            "entities": [
                {
                    "id": "test1",
                    # Missing name and description
                }
            ],
            "relationships": []
        }
        
        yaml_path = Path(temp_dir) / "invalid.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(invalid_yaml, f)
        
        # Test should raise an exception
        with pytest.raises(KeyError):
            create_knowledge_graph(yaml_path, output_dir=temp_dir)

def test_invalid_relationship():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create YAML with invalid relationship (nonexistent entity)
        invalid_yaml = {
            "entities": [
                {
                    "id": "test1",
                    "name": "Test 1",
                    "description": "Description 1"
                }
            ],
            "relationships": [
                {
                    "source": "test1",
                    "target": "nonexistent",
                    "name": "invalid relationship"
                }
            ]
        }
        
        yaml_path = Path(temp_dir) / "invalid_rel.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(invalid_yaml, f)
        
        # Test should create the graph but we should verify the error is handled gracefully
        svg_file = create_knowledge_graph(yaml_path, output_dir=temp_dir)
        assert svg_file.exists()
