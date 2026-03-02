#!/usr/bin/env python3
"""
LangGraph Workflow Diagram Generator

This script generates comprehensive workflow diagrams for the LangGraph data preprocessing system
using Graphviz library. It creates both basic and enhanced workflow visualizations.
"""

import graphviz
from pathlib import Path
from typing import Dict, List, Tuple
import sys


class LangGraphWorkflowDiagram:
    """
    Generates Graphviz diagrams for LangGraph workflows.
    Supports both basic and enhanced preprocessing workflows.
    """
    
    def __init__(self):
        self.colors = {
            'start': '#4CAF50',      # Green
            'end': '#F44336',        # Red
            'data': '#2196F3',       # Blue
            'validation': '#FF9800',  # Orange
            'processing': '#9C27B0', # Purple
            'quality': '#795548',    # Brown
            'feedback': '#607D8B',   # Blue Grey
            'parallel': '#00BCD4',   # Cyan
            'error': '#E91E63'        # Pink
        }
        
        self.shapes = {
            'start': 'ellipse',
            'end': 'ellipse',
            'process': 'box',
            'decision': 'diamond',
            'parallel': 'hexagon'
        }
    
    def create_basic_workflow_diagram(self) -> graphviz.Digraph:
        """
        Create diagram for basic LangGraph workflow.
        """
        dot = graphviz.Digraph(
            'LangGraph_Basic_Workflow',
            comment='LangGraph Basic Data Preprocessing Workflow',
            format='png',
            engine='dot'
        )
        
        dot.attr(
            rankdir='TB',
            size='12,8',
            bgcolor='white',
            fontname='Arial',
            fontsize='12'
        )
        
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
        dot.attr('edge', fontname='Arial', fontsize='10')
        
        # Start node
        dot.node('START', 'START', shape='ellipse', fillcolor=self.colors['start'])
        
        # Processing nodes
        dot.node('load_data', 'Data Loader\n• Load CSV/Excel/JSON/Parquet\n• Initialize metadata', 
                fillcolor=self.colors['data'])
        dot.node('detect_anomalies', 'Anomaly Detector\n• IQR method\n• Z-score detection\n• Rare categories', 
                fillcolor=self.colors['processing'])
        dot.node('handle_anomalies', 'Anomaly Handler\n• Cap outliers\n• Remove/transform/flag', 
                fillcolor=self.colors['processing'])
        dot.node('detect_nulls', 'Null Detector\n• Count null values\n• Calculate percentages', 
                fillcolor=self.colors['processing'])
        dot.node('handle_nulls', 'Null Handler\n• Smart imputation\n• Mean/median/mode', 
                fillcolor=self.colors['processing'])
        dot.node('process_features', 'Feature Processor\n• Encoding\n• Scaling\n• Remove duplicates', 
                fillcolor=self.colors['data'])
        dot.node('validate', 'Validator\n• ML-readiness checks\n• Validation rules', 
                fillcolor=self.colors['validation'])
        dot.node('retry_decision', 'Retry Decision\n• Strategy adjustment\n• Iteration limit', 
                fillcolor=self.colors['feedback'])
        dot.node('END', 'END', shape='ellipse', fillcolor=self.colors['end'])
        
        # Edges
        dot.edge('START', 'load_data')
        dot.edge('load_data', 'detect_anomalies')
        dot.edge('detect_anomalies', 'handle_anomalies', label='anomalies found')
        dot.edge('detect_anomalies', 'detect_nulls', label='no anomalies')
        dot.edge('handle_anomalies', 'detect_nulls')
        dot.edge('detect_nulls', 'handle_nulls', label='nulls found')
        dot.edge('detect_nulls', 'process_features', label='no nulls')
        dot.edge('handle_nulls', 'process_features')
        dot.edge('process_features', 'validate')
        dot.edge('validate', 'retry_decision', label='validation failed')
        dot.edge('validate', 'END', label='validation passed')
        dot.edge('retry_decision', 'detect_anomalies', label='retry', style='dashed', color=self.colors['feedback'])
        dot.edge('retry_decision', 'END', label='max iterations', style='dashed', color=self.colors['error'])
        
        return dot
    
    def create_enhanced_workflow_diagram(self) -> graphviz.Digraph:
        """
        Create diagram for enhanced LangGraph workflow with all data quality features.
        """
        dot = graphviz.Digraph(
            'LangGraph_Enhanced_Workflow',
            comment='LangGraph Enhanced Data Preprocessing Workflow',
            format='png',
            engine='dot'
        )
        
        dot.attr(
            rankdir='TB',
            size='16,12',
            bgcolor='white',
            fontname='Arial',
            fontsize='12',
            splines='ortho',
            nodesep='0.6',
            ranksep='0.8'
        )
        
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', width='2', height='0.8')
        dot.attr('edge', fontname='Arial', fontsize='9')
        
        # Start and End
        dot.node('START', 'START', shape='ellipse', fillcolor=self.colors['start'])
        dot.node('END', 'END', shape='ellipse', fillcolor=self.colors['end'])
        
        # Data Loading
        dot.node('load_data', 'Data Loader\n• Load multiple formats\n• File validation', 
                fillcolor=self.colors['data'])
        
        # Schema Validation
        dot.node('validate_schema', 'Schema Validator\n• Pydantic validation\n• Type constraints', 
                fillcolor=self.colors['validation'])
        dot.node('enforce_schema', 'Schema Enforcer\n• Type casting\n• Schema compliance', 
                fillcolor=self.colors['processing'])
        
        # Data Type & Format
        dot.node('cast_types', 'Data Type Caster\n• Auto type detection\n• Intelligent casting', 
                fillcolor=self.colors['data'])
        dot.node('normalize_formats', 'Format Normalizer\n• Date standardization\n• Email/phone formatting', 
                fillcolor=self.colors['processing'])
        dot.node('standardize_encoding', 'Encoding Standardizer\n• UTF-8 enforcement\n• Character detection', 
                fillcolor=self.colors['processing'])
        
        # Data Quality
        dot.node('check_integrity', 'Referential Integrity\n• PK/FK validation\n• Duplicate detection', 
                fillcolor=self.colors['quality'])
        
        # Anomaly Detection & Handling
        dot.node('detect_anomalies', 'Anomaly Detector\n• IQR/Z-score methods\n• Rare categories', 
                fillcolor=self.colors['processing'])
        dot.node('handle_anomalies', 'Anomaly Handler\n• Multiple strategies\n• Cap/remove/transform', 
                fillcolor=self.colors['processing'])
        
        # Null Value Handling
        dot.node('detect_nulls', 'Null Detector\n• Comprehensive analysis\n• Percentage calculation', 
                fillcolor=self.colors['processing'])
        dot.node('handle_nulls', 'Null Handler\n• Smart imputation\n• Multiple strategies', 
                fillcolor=self.colors['processing'])
        
        # Quality Rules
        dot.node('apply_quality_rules', 'Quality Rules Engine\n• Range checks\n• Pattern matching\n• Actions: REJECT/FLAG/QUARANTINE/FIX', 
                fillcolor=self.colors['quality'])
        
        # Deduplication
        dot.node('deduplicate', 'Deduplication\n• PK-based\n• Hash-based', 
                fillcolor=self.colors['data'])
        
        # Feature Processing
        dot.node('process_features', 'Feature Processor\n• Encoding\n• Scaling\n• Feature engineering', 
                fillcolor=self.colors['data'])
        
        # Validation & Retry
        dot.node('validate', 'Final Validator\n• ML-readiness\n• Comprehensive checks', 
                fillcolor=self.colors['validation'])
        dot.node('retry_decision', 'Retry Decision\n• Strategy adjustment\n• Feedback loop', 
                fillcolor=self.colors['feedback'])
        
        # Main workflow edges
        dot.edge('START', 'load_data')
        dot.edge('load_data', 'validate_schema')
        
        # Schema validation conditional
        dot.edge('validate_schema', 'enforce_schema', label='validation failed')
        dot.edge('validate_schema', 'cast_types', label='validation passed')
        dot.edge('enforce_schema', 'cast_types')
        
        # Type and format processing
        dot.edge('cast_types', 'normalize_formats')
        dot.edge('normalize_formats', 'standardize_encoding')
        dot.edge('standardize_encoding', 'check_integrity')
        
        # Anomaly detection
        dot.edge('check_integrity', 'detect_anomalies')
        dot.edge('detect_anomalies', 'handle_anomalies', label='anomalies found')
        dot.edge('detect_anomalies', 'detect_nulls', label='no anomalies')
        dot.edge('handle_anomalies', 'detect_nulls')
        
        # Null handling
        dot.edge('detect_nulls', 'handle_nulls', label='nulls found')
        dot.edge('detect_nulls', 'apply_quality_rules', label='no nulls')
        dot.edge('handle_nulls', 'apply_quality_rules')
        
        # Quality rules and beyond
        dot.edge('apply_quality_rules', 'deduplicate')
        dot.edge('deduplicate', 'process_features')
        dot.edge('process_features', 'validate')
        
        # Validation and retry
        dot.edge('validate', 'retry_decision', label='validation failed')
        dot.edge('validate', 'END', label='validation passed')
        dot.edge('retry_decision', 'detect_anomalies', label='retry', style='dashed', color=self.colors['feedback'])
        dot.edge('retry_decision', 'END', label='max iterations', style='dashed', color=self.colors['error'])
        
        return dot
    
    def create_parallel_processing_diagram(self) -> graphviz.Digraph:
        """
        Create diagram showing parallel processing capabilities.
        """
        dot = graphviz.Digraph(
            'LangGraph_Parallel_Processing',
            comment='LangGraph Parallel Processing Architecture',
            format='png',
            engine='dot'
        )
        
        dot.attr(
            rankdir='LR',
            size='14,8',
            bgcolor='white',
            fontname='Arial',
            fontsize='12'
        )
        
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
        dot.attr('edge', fontname='Arial', fontsize='10')
        
        # Main components
        dot.node('input', 'Input Data\nLarge Dataset', fillcolor=self.colors['data'])
        dot.node('partitioner', 'Data Partitioner\n• Row partitioning\n• Column grouping\n• Key-based\n• Date-based', 
                fillcolor=self.colors['parallel'])
        dot.node('executor', 'Parallel Executor\n• Thread pool\n• Process pool\n• Async support', 
                fillcolor=self.colors['parallel'])
        dot.node('workers', 'Worker Processes\n• Independent agents\n• Parallel execution\n• Error handling', 
                fillcolor=self.colors['processing'])
        dot.node('aggregator', 'Result Aggregator\n• Combine results\n• Error collection\n• Performance metrics', 
                fillcolor=self.colors['data'])
        dot.node('output', 'Processed Data\nClean & Validated', fillcolor=self.colors['data'])
        
        # Edges
        dot.edge('input', 'partitioner')
        dot.edge('partitioner', 'executor')
        dot.edge('executor', 'workers', label='distribute tasks')
        dot.edge('workers', 'aggregator', label='collect results')
        dot.edge('aggregator', 'output')
        
        # Add subgraph for workers
        with dot.subgraph(name='cluster_workers') as c:
            c.attr(label='Parallel Workers', style='dashed', color=self.colors['parallel'])
            c.attr('node', shape='box', style='filled', fontname='Arial')
            
            c.node('w1', 'Worker 1\nSchema Validation', fillcolor=self.colors['validation'])
            c.node('w2', 'Worker 2\nType Casting', fillcolor=self.colors['data'])
            c.node('w3', 'Worker 3\nQuality Rules', fillcolor=self.colors['quality'])
            c.node('w4', 'Worker 4\nAnomaly Detection', fillcolor=self.colors['processing'])
            
            c.edge('w1', 'w2', style='dotted')
            c.edge('w2', 'w3', style='dotted')
            c.edge('w3', 'w4', style='dotted')
        
        return dot
    
    def create_agent_communication_diagram(self) -> graphviz.Digraph:
        """
        Create diagram showing agent communication flow.
        """
        dot = graphviz.Digraph(
            'LangGraph_Agent_Communication',
            comment='LangGraph Agent Communication Flow',
            format='png',
            engine='dot'
        )
        
        dot.attr(
            rankdir='TB',
            size='12,10',
            bgcolor='white',
            fontname='Arial',
            fontsize='12'
        )
        
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', width='2.5', height='0.6')
        dot.attr('edge', fontname='Arial', fontsize='9')
        
        # Agents
        agents = [
            ('data_loader', 'Data Loader', self.colors['data']),
            ('schema_validator', 'Schema Validator', self.colors['validation']),
            ('type_caster', 'Type Caster', self.colors['data']),
            ('format_normalizer', 'Format Normalizer', self.colors['processing']),
            ('encoding_std', 'Encoding Standardizer', self.colors['processing']),
            ('integrity_checker', 'Integrity Checker', self.colors['quality']),
            ('anomaly_detector', 'Anomaly Detector', self.colors['processing']),
            ('anomaly_handler', 'Anomaly Handler', self.colors['processing']),
            ('null_detector', 'Null Detector', self.colors['processing']),
            ('null_handler', 'Null Handler', self.colors['processing']),
            ('quality_rules', 'Quality Rules', self.colors['quality']),
            ('deduplicator', 'Deduplicator', self.colors['data']),
            ('feature_processor', 'Feature Processor', self.colors['data']),
            ('validator', 'Validator', self.colors['validation']),
            ('retry_decision', 'Retry Decision', self.colors['feedback'])
        ]
        
        for agent_id, agent_name, color in agents:
            dot.node(agent_id, agent_name, fillcolor=color)
        
        # Communication edges with message types
        communications = [
            ('data_loader', 'schema_validator', 'Data loaded'),
            ('schema_validator', 'type_caster', 'Schema validated'),
            ('type_caster', 'format_normalizer', 'Types casted'),
            ('format_normalizer', 'encoding_std', 'Formats normalized'),
            ('encoding_std', 'integrity_checker', 'Encoding standardized'),
            ('integrity_checker', 'anomaly_detector', 'Integrity checked'),
            ('anomaly_detector', 'anomaly_handler', 'Anomalies detected'),
            ('anomaly_handler', 'null_detector', 'Anomalies handled'),
            ('null_detector', 'null_handler', 'Nulls detected'),
            ('null_handler', 'quality_rules', 'Nulls handled'),
            ('quality_rules', 'deduplicator', 'Quality rules applied'),
            ('deduplicator', 'feature_processor', 'Deduplicated'),
            ('feature_processor', 'validator', 'Features processed'),
            ('validator', 'retry_decision', 'Validation result'),
            ('retry_decision', 'anomaly_detector', 'Retry signal')
        ]
        
        for from_agent, to_agent, message in communications:
            if to_agent == 'anomaly_detector' and from_agent == 'retry_decision':
                dot.edge(from_agent, to_agent, label=message, style='dashed', color=self.colors['feedback'])
            else:
                dot.edge(from_agent, to_agent, label=message)
        
        return dot
    
    def save_diagrams(self, output_dir: str = './diagrams'):
        """
        Generate and save all workflow diagrams.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        diagrams = [
            ('basic_workflow', self.create_basic_workflow_diagram()),
            ('enhanced_workflow', self.create_enhanced_workflow_diagram()),
            ('parallel_processing', self.create_parallel_processing_diagram()),
            ('agent_communication', self.create_agent_communication_diagram())
        ]
        
        saved_files = []
        
        for name, diagram in diagrams:
            try:
                # Render as PNG
                output_file = diagram.render(filename=name, directory=output_path, cleanup=True, format='png')
                saved_files.append(f"{name}.png")
                print(f"✓ Saved: {name}.png")
                
                # Also render as SVG for better quality
                svg_file = diagram.render(filename=name, directory=output_path, cleanup=True, format='svg')
                saved_files.append(f"{name}.svg")
                print(f"✓ Saved: {name}.svg")
                
            except Exception as e:
                print(f"✗ Error saving {name}: {str(e)}")
        
        return saved_files


def main():
    """
    Main function to generate all workflow diagrams.
    """
    print("🎨 Generating LangGraph Workflow Diagrams...")
    print("=" * 50)
    
    try:
        # Check if graphviz is available
        import graphviz
        print("✓ Graphviz library found")
        
        # Create diagram generator
        generator = LangGraphWorkflowDiagram()
        
        # Generate and save all diagrams
        saved_files = generator.save_diagrams()
        
        print("\n" + "=" * 50)
        print("📊 Diagram Generation Complete!")
        print(f"📁 Files saved: {len(saved_files)}")
        print("\nGenerated diagrams:")
        for file in saved_files:
            print(f"  • {file}")
        
        print(f"\n📂 Output directory: {Path('./diagrams').absolute()}")
        print("\n💡 To view diagrams:")
        print("  1. Open PNG files in any image viewer")
        print("  2. Open SVG files in web browser for better quality")
        
    except ImportError:
        print("❌ Graphviz library not found!")
        print("Please install it with:")
        print("  pip install graphviz")
        print("\nAlso ensure Graphviz system package is installed:")
        print("  • Windows: Download from https://graphviz.org/download/")
        print("  • macOS: brew install graphviz")
        print("  • Linux: sudo apt-get install graphviz")
        return 1
    
    except Exception as e:
        print(f"❌ Error generating diagrams: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
