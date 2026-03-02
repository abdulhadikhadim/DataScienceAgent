#!/usr/bin/env python3
"""
LangGraph Native Workflow PNG Generator

This script uses LangGraph's built-in graph drawing capabilities to generate
actual workflow PNGs from the compiled workflows.
"""

import os
from pathlib import Path
from langgraph.graph import StateGraph, END
from langgraph_agents.enhanced_state import EnhancedPreprocessingState
from langgraph_agents.state import PreprocessingState
from langgraph_agents.workflow import create_preprocessing_workflow
from langgraph_agents.enhanced_workflow import create_enhanced_preprocessing_workflow
from langgraph_agents.nodes.data_loader_node import load_data_node
from langgraph_agents.nodes.anomaly_detector_node import detect_anomalies_node
from langgraph_agents.nodes.anomaly_handler_node import handle_anomalies_node
from langgraph_agents.nodes.null_handler_node import detect_null_values_node, handle_null_values_node
from langgraph_agents.nodes.feature_processor_node import process_features_node
from langgraph_agents.nodes.validator_node import validate_data_node, should_retry_node


def generate_basic_workflow_png():
    """Generate PNG for basic LangGraph workflow"""
    print("🎨 Generating Basic Workflow PNG...")
    
    try:
        # Create basic workflow
        workflow = StateGraph(PreprocessingState)
        
        # Add nodes
        workflow.add_node("load_data", load_data_node)
        workflow.add_node("detect_anomalies", detect_anomalies_node)
        workflow.add_node("handle_anomalies", handle_anomalies_node)
        workflow.add_node("detect_nulls", detect_null_values_node)
        workflow.add_node("handle_nulls", handle_null_values_node)
        workflow.add_node("process_features", process_features_node)
        workflow.add_node("validate", validate_data_node)
        workflow.add_node("retry_decision", should_retry_node)
        
        # Set entry point
        workflow.set_entry_point("load_data")
        
        # Add edges
        workflow.add_edge("load_data", "detect_anomalies")
        
        # Conditional edges
        def route_after_anomaly_detection(state: PreprocessingState):
            anomalies = state.get("anomalies_detected", [])
            return "handle_anomalies" if len(anomalies) > 0 else "detect_nulls"
        
        def route_after_null_detection(state: PreprocessingState):
            null_info = state.get("null_values_info", {})
            return "handle_nulls" if len(null_info) > 0 else "process_features"
        
        def route_after_validation(state: PreprocessingState):
            validation_passed = state.get("validation_passed", False)
            iteration_count = state.get("iteration_count", 0)
            max_iterations = state.get("max_iterations", 3)
            
            if validation_passed:
                return "end"
            elif iteration_count < max_iterations:
                return "retry"
            else:
                return "end"
        
        workflow.add_conditional_edges(
            "detect_anomalies",
            route_after_anomaly_detection,
            {
                "handle_anomalies": "handle_anomalies",
                "detect_nulls": "detect_nulls"
            }
        )
        
        workflow.add_edge("handle_anomalies", "detect_nulls")
        
        workflow.add_conditional_edges(
            "detect_nulls",
            route_after_null_detection,
            {
                "handle_nulls": "handle_nulls",
                "process_features": "process_features"
            }
        )
        
        workflow.add_edge("handle_nulls", "process_features")
        workflow.add_edge("process_features", "validate")
        
        workflow.add_conditional_edges(
            "validate",
            route_after_validation,
            {
                "retry": "retry_decision",
                "end": END
            }
        )
        
        workflow.add_edge("retry_decision", "detect_anomalies")
        
        # Compile and draw
        app = workflow.compile()
        
        # Create output directory
        output_dir = Path("./diagrams")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PNG
        app.get_graph().draw_png(str(output_dir / "basic_workflow_langgraph.png"))
        print("✅ Basic workflow PNG saved: diagrams/basic_workflow_langgraph.png")
        
        # Also generate mermaid for web display
        try:
            app.get_graph().draw_mermaid(str(output_dir / "basic_workflow.mmd"))
            print("✅ Basic workflow Mermaid saved: diagrams/basic_workflow.mmd")
        except:
            print("⚠️ Mermaid generation not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating basic workflow PNG: {str(e)}")
        return False


def generate_enhanced_workflow_png():
    """Generate PNG for enhanced LangGraph workflow"""
    print("\n🎨 Generating Enhanced Workflow PNG...")
    
    try:
        # Create enhanced workflow using existing function
        app = create_enhanced_preprocessing_workflow()
        
        # Create output directory
        output_dir = Path("./diagrams")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PNG
        app.get_graph().draw_png(str(output_dir / "enhanced_workflow_langgraph.png"))
        print("✅ Enhanced workflow PNG saved: diagrams/enhanced_workflow_langgraph.png")
        
        # Also generate mermaid
        try:
            app.get_graph().draw_mermaid(str(output_dir / "enhanced_workflow.mmd"))
            print("✅ Enhanced workflow Mermaid saved: diagrams/enhanced_workflow.mmd")
        except:
            print("⚠️ Mermaid generation not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating enhanced workflow PNG: {str(e)}")
        return False


def create_custom_workflow_demo():
    """Create a simple custom workflow for demonstration"""
    print("\n🎨 Generating Custom Demo Workflow PNG...")
    
    try:
        # Create a simple demo workflow
        workflow = StateGraph(dict)
        
        # Add some demo nodes
        def node1(state):
            return {"step": "node1"}
        
        def node2(state):
            return {"step": "node2"}
        
        def node3(state):
            return {"step": "node3"}
        
        def route_decision(state):
            return "node2" if state.get("continue", True) else "node3"
        
        workflow.add_node("start_node", node1)
        workflow.add_node("middle_node", node2)
        workflow.add_node("end_node", node3)
        
        workflow.set_entry_point("start_node")
        
        workflow.add_conditional_edges(
            "start_node",
            route_decision,
            {
                "node2": "middle_node",
                "node3": "end_node"
            }
        )
        
        workflow.add_edge("middle_node", "end_node")
        workflow.add_edge("end_node", "__end__")
        
        # Compile and draw
        app = workflow.compile()
        
        # Create output directory
        output_dir = Path("./diagrams")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PNG
        app.get_graph().draw_png(str(output_dir / "demo_workflow_langgraph.png"))
        print("✅ Demo workflow PNG saved: diagrams/demo_workflow_langgraph.png")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating demo workflow PNG: {str(e)}")
        return False


def print_workflow_info():
    """Print information about the generated workflows"""
    print("\n" + "=" * 60)
    print("📊 LangGraph Workflow PNG Generation Complete!")
    print("=" * 60)
    
    print("\n🎯 Generated Files:")
    output_dir = Path("./diagrams")
    
    if output_dir.exists():
        png_files = list(output_dir.glob("*.png"))
        mmd_files = list(output_dir.glob("*.mmd"))
        
        print(f"\n📸 PNG Files ({len(png_files)}):")
        for png in png_files:
            print(f"  • {png.name}")
        
        print(f"\n📝 Mermaid Files ({len(mmd_files)}):")
        for mmd in mmd_files:
            print(f"  • {mmd.name}")
    
    print(f"\n📂 Output Directory: {output_dir.absolute()}")
    
    print("\n💡 Usage:")
    print("  • View PNG files in any image viewer")
    print("  • Use Mermaid files in GitHub/GitLab markdown")
    print("  • Include in documentation and presentations")
    
    print("\n🔧 Workflow Features:")
    print("  • Native LangGraph graph rendering")
    print("  • Actual node connections and conditional edges")
    print("  • Real workflow structure")
    print("  • Professional quality diagrams")


def main():
    """Main function to generate all workflow PNGs"""
    print("🚀 LangGraph Native Workflow PNG Generator")
    print("=" * 50)
    
    success_count = 0
    
    # Generate workflows
    if generate_basic_workflow_png():
        success_count += 1
    
    if generate_enhanced_workflow_png():
        success_count += 1
    
    if create_custom_workflow_demo():
        success_count += 1
    
    # Print summary
    print_workflow_info()
    
    print(f"\n✅ Successfully generated {success_count}/3 workflow diagrams")
    
    if success_count == 3:
        print("🎉 All workflows generated successfully!")
    else:
        print("⚠️ Some workflows failed to generate")
    
    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    exit(main())
