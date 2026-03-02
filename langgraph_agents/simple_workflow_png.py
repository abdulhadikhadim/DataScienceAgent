#!/usr/bin/env python3
"""
Simple LangGraph Workflow PNG Generator

Uses LangGraph's native graph drawing capabilities to generate workflow PNGs.
"""

import sys
import os
from pathlib import Path
from typing import Literal
from langgraph.graph import StateGraph, END


def create_basic_workflow():
    """Create basic LangGraph workflow"""
    
    def load_data(state: dict) -> dict:
        """Load data node"""
        state["step"] = "data_loaded"
        return state
    
    def detect_anomalies(state: dict) -> dict:
        """Detect anomalies node"""
        state["step"] = "anomalies_detected"
        state["anomalies_found"] = True  # Simulate finding anomalies
        return state
    
    def handle_anomalies(state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle anomalies node"""
        state["step"] = "anomalies_handled"
        return state
    
    def detect_nulls(state: Dict[str, Any]) -> Dict[str, Any]:
        """Detect null values node"""
        state["step"] = "nulls_detected"
        state["nulls_found"] = True  # Simulate finding nulls
        return state
    
    def handle_nulls(state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle null values node"""
        state["step"] = "nulls_handled"
        return state
    
    def process_features(state: Dict[str, Any]) -> Dict[str, Any]:
        """Process features node"""
        state["step"] = "features_processed"
        return state
    
    def validate(state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data node"""
        state["step"] = "validation_completed"
        state["validation_passed"] = True  # Simulate passing validation
        return state
    
    def retry_decision(state: Dict[str, Any]) -> Dict[str, Any]:
        """Retry decision node"""
        state["step"] = "retry_decision"
        return state
    
    # Create workflow
    workflow = StateGraph(Dict[str, Any])
    
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
    
    # Conditional routing functions
    def route_after_anomaly_detection(state: Dict[str, Any]) -> Literal["handle_anomalies", "detect_nulls"]:
        return "handle_anomalies" if state.get("anomalies_found", False) else "detect_nulls"
    
    def route_after_null_detection(state: Dict[str, Any]) -> Literal["handle_nulls", "process_features"]:
        return "handle_nulls" if state.get("nulls_found", False) else "process_features"
    
    def route_after_validation(state: Dict[str, Any]) -> Literal["retry_decision", "__end__"]:
        return "retry_decision" if not state.get("validation_passed", True) else "__end__"
    
    def route_after_retry(state: Dict[str, Any]) -> Literal["detect_anomalies", "__end__"]:
        # Simulate max iterations reached
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
    """Create enhanced LangGraph workflow with more nodes"""
    
    def load_data(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "data_loaded"
        return state
    
    def validate_schema(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "schema_validated"
        state["schema_valid"] = True
        return state
    
    def enforce_schema(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "schema_enforced"
        return state
    
    def cast_types(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "types_casted"
        return state
    
    def normalize_formats(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "formats_normalized"
        return state
    
    def standardize_encoding(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "encoding_standardized"
        return state
    
    def check_integrity(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "integrity_checked"
        return state
    
    def detect_anomalies(state: dict) -> dict:
        state["step"] = "anomalies_detected"
        state["anomalies_found"] = True
        return state
    
    def handle_anomalies(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "anomalies_handled"
        return state
    
    def detect_nulls(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "nulls_detected"
        state["nulls_found"] = True
        return state
    
    def handle_nulls(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "nulls_handled"
        return state
    
    def apply_quality_rules(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "quality_rules_applied"
        return state
    
    def deduplicate(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "deduplicated"
        return state
    
    def process_features(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "features_processed"
        return state
    
    def validate(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "validation_completed"
        state["validation_passed"] = True
        return state
    
    def retry_decision(state: Dict[str, Any]) -> Dict[str, Any]:
        state["step"] = "retry_decision"
        return state
    
    # Create enhanced workflow
    workflow = StateGraph(Dict[str, Any])
    
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
    def route_after_schema(state: Dict[str, Any]) -> Literal["enforce_schema", "cast_types"]:
        return "enforce_schema" if not state.get("schema_valid", True) else "cast_types"
    
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
    def route_after_anomaly_detection(state: Dict[str, Any]) -> Literal["handle_anomalies", "detect_nulls"]:
        return "handle_anomalies" if state.get("anomalies_found", False) else "detect_nulls"
    
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
    def route_after_null_detection(state: Dict[str, Any]) -> Literal["handle_nulls", "apply_quality_rules"]:
        return "handle_nulls" if state.get("nulls_found", False) else "apply_quality_rules"
    
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
    def route_after_validation(state: Dict[str, Any]) -> Literal["retry_decision", "__end__"]:
        return "retry_decision" if not state.get("validation_passed", True) else "__end__"
    
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "retry_decision": "retry_decision",
            "__end__": END
        }
    )
    
    # Retry decision conditional
    def route_after_retry(state: Dict[str, Any]) -> Literal["detect_anomalies", "__end__"]:
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


def main():
    """Main function to generate workflow PNGs"""
    print("🎨 LangGraph Native Workflow PNG Generator")
    print("=" * 50)
    
    try:
        # Create output directory
        output_dir = Path("./diagrams")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate basic workflow
        print("\n📊 Generating Basic Workflow...")
        basic_app = create_basic_workflow()
        basic_app.get_graph().draw_png(str(output_dir / "basic_workflow_langgraph.png"))
        print("✅ Basic workflow PNG saved!")
        
        # Generate enhanced workflow
        print("\n📊 Generating Enhanced Workflow...")
        enhanced_app = create_enhanced_workflow()
        enhanced_app.get_graph().draw_png(str(output_dir / "enhanced_workflow_langgraph.png"))
        print("✅ Enhanced workflow PNG saved!")
        
        # Try to generate mermaid files
        try:
            basic_app.get_graph().draw_mermaid(str(output_dir / "basic_workflow.mmd"))
            enhanced_app.get_graph().draw_mermaid(str(output_dir / "enhanced_workflow.mmd"))
            print("✅ Mermaid files saved!")
        except Exception as e:
            print(f"⚠️ Mermaid generation failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Workflow PNG Generation Complete!")
        print(f"📂 Output directory: {output_dir.absolute()}")
        print("\n📁 Generated files:")
        
        for file in output_dir.glob("*.png"):
            print(f"  📸 {file.name}")
        
        for file in output_dir.glob("*.mmd"):
            print(f"  📝 {file.name}")
        
        print("\n💡 These are the actual LangGraph workflow diagrams!")
        print("   • Real node connections")
        print("   • Conditional edges")
        print("   • Feedback loops")
        print("   • Professional quality")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
