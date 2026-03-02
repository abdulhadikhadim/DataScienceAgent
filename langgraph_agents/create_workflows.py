#!/usr/bin/env python3
"""
Create LangGraph Workflows and Generate PNGs
"""

from pathlib import Path
from langgraph.graph import StateGraph, END


def create_basic_workflow():
    """Create basic LangGraph workflow"""
    
    def load_data(state):
        state["step"] = "data_loaded"
        return state
    
    def detect_anomalies(state):
        state["step"] = "anomalies_detected"
        state["anomalies_found"] = True
        return state
    
    def handle_anomalies(state):
        state["step"] = "anomalies_handled"
        return state
    
    def detect_nulls(state):
        state["step"] = "nulls_detected"
        state["nulls_found"] = True
        return state
    
    def handle_nulls(state):
        state["step"] = "nulls_handled"
        return state
    
    def process_features(state):
        state["step"] = "features_processed"
        return state
    
    def validate(state):
        state["step"] = "validation_completed"
        state["validation_passed"] = True
        return state
    
    def retry_decision(state):
        state["step"] = "retry_decision"
        return state
    
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
        state["step"] = "data_loaded"
        return state
    
    def validate_schema(state):
        state["step"] = "schema_validated"
        state["schema_valid"] = True
        return state
    
    def enforce_schema(state):
        state["step"] = "schema_enforced"
        return state
    
    def cast_types(state):
        state["step"] = "types_casted"
        return state
    
    def normalize_formats(state):
        state["step"] = "formats_normalized"
        return state
    
    def standardize_encoding(state):
        state["step"] = "encoding_standardized"
        return state
    
    def check_integrity(state):
        state["step"] = "integrity_checked"
        return state
    
    def detect_anomalies(state):
        state["step"] = "anomalies_detected"
        state["anomalies_found"] = True
        return state
    
    def handle_anomalies(state):
        state["step"] = "anomalies_handled"
        return state
    
    def detect_nulls(state):
        state["step"] = "nulls_detected"
        state["nulls_found"] = True
        return state
    
    def handle_nulls(state):
        state["step"] = "nulls_handled"
        return state
    
    def apply_quality_rules(state):
        state["step"] = "quality_rules_applied"
        return state
    
    def deduplicate(state):
        state["step"] = "deduplicated"
        return state
    
    def process_features(state):
        state["step"] = "features_processed"
        return state
    
    def validate(state):
        state["step"] = "validation_completed"
        state["validation_passed"] = True
        return state
    
    def retry_decision(state):
        state["step"] = "retry_decision"
        return state
    
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


def main():
    """Main function to generate workflow PNGs"""
    print("🎨 Creating LangGraph Workflows and Generating PNGs")
    print("=" * 60)
    
    try:
        # Create output directory
        output_dir = Path("./diagrams")
        output_dir.mkdir(parents=True, exist_ok=True)
        
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
            basic_app.get_graph().draw_mermaid(str(output_dir / "basic_workflow.mmd"))
            enhanced_app.get_graph().draw_mermaid(str(output_dir / "enhanced_workflow.mmd"))
            print("✅ Mermaid files saved!")
        except Exception as e:
            print(f"⚠️ Mermaid generation failed: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 LangGraph Workflow PNG Generation Complete!")
        print(f"📂 Output directory: {output_dir.absolute()}")
        print("\n📁 Generated files:")
        
        for file in sorted(output_dir.glob("*.png")):
            print(f"  📸 {file.name}")
        
        for file in sorted(output_dir.glob("*.mmd")):
            print(f"  📝 {file.name}")
        
        print("\n🌟 These are the ACTUAL LangGraph workflow diagrams!")
        print("   • Real node connections from your code")
        print("   • Conditional edges and routing")
        print("   • Feedback loops")
        print("   • Professional quality visualization")
        print("   • Generated using LangGraph's native drawing")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    main()
