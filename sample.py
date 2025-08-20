# app.py - Simple Topic Bar Chart with Click Interaction
from faicons import icon_svg
import plotly.graph_objects as go
import pandas as pd

from shiny import reactive
from shiny.express import input, render, ui
from bertopic_model import PerformanceTechnicalAnalyzer

# Page configuration
ui.page_opts(title="Code Connection Topic Analysis", fillable=True)

# Initialize reactive values
analyzer = reactive.Value(None)
is_fitted = reactive.Value(False)
selected_topic = reactive.Value(None)

# Sidebar
with ui.sidebar(title="RescuShell"):
    ui.input_select("code_pair_dropdown",
                    "Code Pair",
                    ["Performance.Parameters_Technical.Constraints"],
                    multiple=False)

# Main content
with ui.layout_columns():
    # Topic Distribution Bar Chart
    with ui.card(full_screen=True):
        ui.card_header("Topic Distribution - Click bars to see documents")
        
        @render.plot
        def topic_bar_chart():
            if not is_fitted():
                return None
            
            try:
                # Get topic info
                topic_info = analyzer().model.get_topic_info()
                
                # Create bar chart data
                df_plot = topic_info.copy()
                
                # Color coding: highlight selected topic
                colors = ['darkblue' if topic == selected_topic() else 'lightblue' 
                         for topic in df_plot['Topic']]
                
                # Create plotly bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=df_plot['Topic'], 
                        y=df_plot['Count'],
                        text=df_plot['Count'],
                        textposition='auto',
                        marker_color=colors,
                        hovertemplate='<b>Topic %{x}</b><br>' +
                                      'Documents: %{y}<br>' +
                                      'Keywords: %{customdata}<br>' +
                                      '<extra></extra>',
                        customdata=df_plot['Name']
                    )
                ])
                
                fig.update_layout(
                    title="Click on any bar to see its documents",
                    xaxis_title="Topic ID",
                    yaxis_title="Number of Documents",
                    height=500,
                    showlegend=False
                )
                
                return fig
                
            except Exception as e:
                print(f"Error creating bar chart: {e}")
                return None

# Documents section - only shows when a topic is selected
with ui.card(full_screen=True):
    ui.card_header("Documents in Selected Topic")
    
    @render.text
    def topic_documents():
        if not is_fitted():
            return "Loading analysis..."
        
        if selected_topic() is None:
            return "Click on a bar in the chart above to see documents for that topic"
        
        try:
            topic_id = selected_topic()
            doc_indices = [i for i, t in enumerate(analyzer().topics) if t == topic_id]
            
            if not doc_indices:
                return f"No documents found in Topic {topic_id}"
            
            # Get topic name/keywords
            topic_info = analyzer().model.get_topic_info()
            topic_row = topic_info[topic_info['Topic'] == topic_id]
            topic_name = topic_row.iloc[0]['Name'] if not topic_row.empty else f"Topic {topic_id}"
            
            documents_text = [f"📋 Topic {topic_id}: {topic_name}\n📄 {len(doc_indices)} documents:\n"]
            
            for i, doc_idx in enumerate(doc_indices[:15]):  # Show first 15 documents
                doc_text = analyzer().docs[doc_idx]
                # Truncate long documents
                if len(doc_text) > 250:
                    doc_text = doc_text[:250] + "..."
                documents_text.append(f"Document {doc_idx}: {doc_text}")
            
            if len(doc_indices) > 15:
                documents_text.append(f"\n... and {len(doc_indices) - 15} more documents")
            
            return "\n\n".join(documents_text)
            
        except Exception as e:
            return f"Error loading documents: {e}"

# Auto-run analysis effect
@reactive.Effect
def auto_run_analysis():
    """Auto-run analysis when app starts"""
    try:
        print("Starting BERTopic analysis...")
        
        # Create analyzer and fit model automatically
        topic_analyzer = PerformanceTechnicalAnalyzer()
        topics, probs = topic_analyzer.fit_transform()
        
        # Store analyzer
        analyzer.set(topic_analyzer)
        is_fitted.set(True)
        
        print(f"Analysis complete: {len(topic_analyzer.docs)} documents, {len(set(topics))} topics")
        
    except Exception as e:
        print(f"Error in auto-analysis: {e}")
        is_fitted.set(False)

# Handle bar chart clicks (simplified approach using plotly events)
# Note: For true click events, you'd need to use plotly's click callbacks
# For now, we'll simulate with a simple topic selector that updates the chart

# Simple way to handle "clicks" - you can manually set topic in console for testing
@reactive.Effect
def handle_topic_selection():
    """Handle topic selection changes"""
    if selected_topic() is not None:
        print(f"Selected topic: {selected_topic()}")

# For testing - you can add this temporarily to simulate clicks
# You can remove this once you implement proper plotly click handling
def select_topic(topic_id):
    """Helper function to select a topic (for testing)"""
    selected_topic.set(topic_id)