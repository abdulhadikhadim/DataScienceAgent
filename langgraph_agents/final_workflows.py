#!/usr/bin/env python3
"""
Final LangGraph Workflow PNG Generator with proper state handling
"""

from pathlib import Path
from typing import Annotated
from operator import add
from langgraph.graph import StateGraph, END


def create_basic_workflow():
    """Create basic LangGraph workflow with proper state"""
    
    # Define state structure
    def load_data(state):
        return {"step": "data_loaded"}
    
    def detect_anomalies(state):
        return {"step": "anomalies_detected", "anomalies_found": True}
    
    def handle_anomalies(state):
        return {"step": "anomalies_handled"}
    
    def detect_nulls(state):
        return {"step": "nulls_detected", "nulls_found": True}
    
    def handle_nulls(state):
        return {"step": "nulls_handled"}
    
    def process_features(state):
        return {"step": "features_processed"}
    
    def validate(state):
        return {"step": "validation_completed", "validation_passed": True}
    
    def retry_decision(state):
        return {"step": "retry_decision"}
    
    # Create workflow
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("load_data", load_data)
    workflow.add_node("detect_anomalies", detect_anomalies)
    workflow.add_node("handle_anomalies", handle_anomalies)
    workflow.add_node("detect_nulls", detect_nulls)
    workflow.add_node("handle_nulls", handle_nulls)
    workflow.add_node("process_features", process_features)
    workflow.add_node("validate", validate)
    workflow.add_node("retry_decision", retry_decision)
    
    # Set entry point
    workflow.set_entry_point("load_data")
    
    # Add edges
    workflow.add_edge("load_data", "detect_anomalies")
    
    # Conditional routing
    def route_after_anomaly_detection(state):
        return "handle_anomalies" if state.get("anomalies_found") else "detect_nulls"
    
    def route_after_null_detection(state):
        return "handle_nulls" if state.get("nulls_found") else "process_features"
    
    def route_after_validation(state):
        return "retry_decision" if not state.get("validation_passed") else "__end__"
    
    def route_after_retry(state):
        return "__end__" if state.get("iteration_count", 0) >= 3 else "detect_anomalies"
    
    # Add conditional edges
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
            "retry_decision": "retry_decision",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "retry_decision",
        route_after_retry,
        {
            "detect_anomalies": "detect_anomalies",
            "__end__": END
        }
    )
    
    return workflow.compile()


def create_enhanced_workflow():
    """Create enhanced LangGraph workflow"""
    
    def load_data(state):
        return {"step": "data_loaded"}
    
    def validate_schema(state):
        return {"step": "schema_validated", "schema_valid": True}
    
    def enforce_schema(state):
        return {"step": "schema_enforced"}
    
    def cast_types(state):
        return {"step": "types_casted"}
    
    def normalize_formats(state):
        return {"step": "formats_normalized"}
    
    def standardize_encoding(state):
        return {"step": "encoding_standardized"}
    
    def check_integrity(state):
        return {"step": "integrity_checked"}
    
    def detect_anomalies(state):
        return {"step": "anomalies_detected", "anomalies_found": True}
    
    def handle_anomalies(state):
        return {"step": "anomalies_handled"}
    
    def detect_nulls(state):
        return {"step": "nulls_detected", "nulls_found": True}
    
    def handle_nulls(state):
        return {"step": "nulls_handled"}
    
    def apply_quality_rules(state):
        return {"step": "quality_rules_applied"}
    
    def deduplicate(state):
        return {"step": "deduplicated"}
    
    def process_features(state):
        return {"step": "features_processed"}
    
    def validate(state):
        return {"step": "validation_completed", "validation_passed": True}
    
    def retry_decision(state):
        return {"step": "retry_decision"}
    
    # Create enhanced workflow
    workflow = StateGraph(dict)
    
    # Add all nodes
    nodes = [
        ("load_data", load_data),
        ("validate_schema", validate_schema),
        ("enforce_schema", enforce_schema),
        ("cast_types", cast_types),
        ("normalize_formats", normalize_formats),
        ("standardize_encoding", standardize_encoding),
        ("check_integrity", check_integrity),
        ("detect_anomalies", detect_anomalies),
        ("handle_anomalies", handle_anomalies),
        ("detect_nulls", detect_nulls),
        ("handle_nulls", handle_nulls),
        ("apply_quality_rules", apply_quality_rules),
        ("deduplicate", deduplicate),
        ("process_features", process_features),
        ("validate", validate),
        ("retry_decision", retry_decision)
    ]
    
    for name, func in nodes:
        workflow.add_node(name, func)
    
    # Set entry point
    workflow.set_entry_point("load_data")
    
    # Add edges
    workflow.add_edge("load_data", "validate_schema")
    
    # Schema validation conditional
    def route_after_schema(state):
        return "enforce_schema" if not state.get("schema_valid") else "cast_types"
    
    workflow.add_conditional_edges(
        "validate_schema",
        route_after_schema,
        {
            "enforce_schema": "enforce_schema",
            "cast_types": "cast_types"
        }
    )
    
    workflow.add_edge("enforce_schema", "cast_types")
    workflow.add_edge("cast_types", "normalize_formats")
    workflow.add_edge("normalize_formats", "standardize_encoding")
    workflow.add_edge("standardize_encoding", "check_integrity")
    workflow.add_edge("check_integrity", "detect_anomalies")
    
    # Anomaly detection conditional
    def route_after_anomaly_detection(state):
        return "handle_anomalies" if state.get("anomalies_found") else "detect_nulls"
    
    workflow.add_conditional_edges(
        "detect_anomalies",
        route_after_anomaly_detection,
        {
            "handle_anomalies": "handle_anomalies",
            "detect_nulls": "detect_nulls"
        }
    )
    
    workflow.add_edge("handle_anomalies", "detect_nulls")
    
    # Null detection conditional
    def route_after_null_detection(state):
        return "handle_nulls" if state.get("nulls_found") else "apply_quality_rules"
    
    workflow.add_conditional_edges(
        "detect_nulls",
        route_after_null_detection,
        {
            "handle_nulls": "handle_nulls",
            "apply_quality_rules": "apply_quality_rules"
        }
    )
    
    workflow.add_edge("handle_nulls", "apply_quality_rules")
    workflow.add_edge("apply_quality_rules", "deduplicate")
    workflow.add_edge("deduplicate", "process_features")
    workflow.add_edge("process_features", "validate")
    
    # Validation conditional
    def route_after_validation(state):
        return "retry_decision" if not state.get("validation_passed") else "__end__"
    
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "retry_decision": "retry_decision",
            "__end__": END
        }
    )
    
    # Retry decision conditional
    def route_after_retry(state):
        return "__end__" if state.get("iteration_count", 0) >= 3 else "detect_anomalies"
    
    workflow.add_conditional_edges(
        "retry_decision",
        route_after_retry,
        {
            "detect_anomalies": "detect_anomalies",
            "__end__": END
        }
    )
    
    return workflow.compile()


def create_simple_demo():
    """Create a simple demo workflow"""
    
    def start_node(state):
        return {"status": "started"}
    
    def process_node(state):
        return {"status": "processed"}
    
    def end_node(state):
        return {"status": "completed"}
    
    workflow = StateGraph(dict)
    
    workflow.add_node("start", start_node)
    workflow.add_node("process", process_node)
    workflow.add_node("end", end_node)
    
    workflow.set_entry_point("start")
    workflow.add_edge("start", "process")
    workflow.add_edge("process", "end")
    
    return workflow.compile()


def main():
    """Main function to generate workflow PNGs"""
    print("🎨 Final LangGraph Workflow PNG Generator")
    print("=" * 50)
    
    try:
        # Create output directory
        output_dir = Path("./diagrams")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate simple demo first
        print("\n📊 Creating Simple Demo Workflow...")
        demo_app = create_simple_demo()
        demo_app.get_graph().draw_png(str(output_dir / "demo_workflow_langgraph.png"))
        print("✅ Demo workflow PNG saved!")
        
        # Generate basic workflow
        print("\n📊 Creating Basic Workflow...")
        basic_app = create_basic_workflow()
        basic_app.get_graph().draw_png(str(output_dir / "basic_workflow_langgraph.png"))
        print("✅ Basic workflow PNG saved!")
        
        # Generate enhanced workflow
        print("\n📊 Creating Enhanced Workflow...")
        enhanced_app = create_enhanced_workflow()
        enhanced_app.get_graph().draw_png(str(output_dir / "enhanced_workflow_langgraph.png"))
        print("✅ Enhanced workflow PNG saved!")
        
        # Try to generate mermaid files
        try:
            demo_app.get_graph().draw_mermaid(str(output_dir / "demo_workflow.mmd"))
            basic_app.get_graph().draw_mermaid(str(output_dir / "basic_workflow.mmd"))
            enhanced_app.get_graph().draw_mermaid(str(output_dir / "enhanced_workflow.mmd"))
            print("✅ Mermaid files saved!")
        except Exception as e:
            print(f"⚠️ Mermaid generation failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 LangGraph Workflow PNG Generation Complete!")
        print(f"📂 Output directory: {output_dir.absolute()}")
        print("\n📁 Generated files:")
        
        png_files = sorted(output_dir.glob("*.png"))
        mmd_files = sorted(output_dir.glob("*.mmd"))
        
        print(f"\n📸 PNG Files ({len(png_files)}):")
        for file in png_files:
            print(f"  • {file.name}")
        
        print(f"\n📝 Mermaid Files ({len(mmd_files)}):")
        for file in mmd_files:
            print(f"  • {file.name}")
        
        print("\n🌟 SUCCESS! These are the ACTUAL LangGraph workflow diagrams!")
        print("   • Generated using LangGraph's native .get_graph().draw_png()")
        print("   • Real node connections and conditional edges")
        print("   • Feedback loops and retry logic")
        print("   • Professional quality for documentation")
        print("   • Ready for presentations and technical docs")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    main()
