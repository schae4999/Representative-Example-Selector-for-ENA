import plotly.graph_objects as go

from shiny import reactive, render, ui, App, Inputs, Outputs, Session
from bertopic_model import PerformanceTechnicalAnalyzer

analyzer = reactive.Value(None)
is_fitted = reactive.Value(False)
selected_topic = reactive.Value(None)

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            "code_pair_dropdown",
            "Code Pair",
            ["Performance.Parameters_Technical.Constraints"],
            multiple=False
        ),
        ui.br(),
        ui.input_select(
            "topic_dropdown",
            "Select Topic",
            choices=[],
            selected=None
        ),
        ui.markdown("Select a topic from the dropdown above to see its documents.")
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Top 10 Topic Distribution"),
            ui.output_ui("topic_bar_chart"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Documents in Selected Topic"),
            ui.output_ui("topic_documents"),
            full_screen=True
        )
    ),
    title="Code Connection Topic Analysis",
    fillable=True,
)

def server(input: Inputs, output: Outputs, session: Session):

    @output
    @render.ui
    def topic_bar_chart():
        if not is_fitted():
            return ui.div("Loading analysis...")
            
        try:
            # Get topic info
            topic_info = analyzer().model.get_topic_info()

            # Create bar chart data
            df_plot = topic_info.sort_values(by='Count', ascending=False).head(10)
            df_plot['Topic Label'] = df_plot['Name'].str.replace(r'^-?\d+_', '', regex=True)

            # Color coding: highlight selected topic
            colors = ['darkblue' if topic == selected_topic() else 'lightblue' for topic in df_plot['Topic']]

            print(df_plot[['Topic Label', 'Count']])
            print(df_plot.index)

            fig = go.Figure(data=[
                go.Bar(
                    x=df_plot['Topic Label'], # topic keywords
                    y=df_plot['Count'], # number of documents in that topic
                    text=df_plot['Count'],
                    textposition='auto', # where to place the text
                    marker_color=colors,
                    hovertemplate='<b>%{x}</b><br>' +
                                    'Documents: %{y}<br>' +
                                    '<extra></extra>',
                    customdata=df_plot['Topic']
                )
            ])

            # Styles and configures the overall appearance of the chart
            fig.update_layout(
                xaxis_title="Topic",
                yaxis_title="Number of Documents",
                height=600,
                showlegend=False,
                xaxis_tickangle=-45
            )

            # Convert to JSON and create HTML
            fig_json = fig.to_json()
            
            plot_html = f"""
            <div id="topic_chart" style="width:100%;height:500px;"></div>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script>
                var figData = {fig_json};
                Plotly.newPlot('topic_chart', figData.data, figData.layout);
            </script>
            """
            
            return ui.HTML(plot_html)
        
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return ui.div(f"Error creating chart: {e}")
            
    @output 
    @render.ui
    def topic_documents():
        if not is_fitted():
            return ui.p("Loading analysis...")
        
        if selected_topic() is None:
            return ui.p("Select a topic from the dropdown in the sidebar to see its documents.")
        
        try:
            topic_id = selected_topic() # Gets the currently selected topic ID
            topic_info = analyzer().model.get_topic_info()
            topic_row = topic_info[topic_info['Topic'] == topic_id]

            if topic_row.empty:
                return ui.p(f"No information found for Topic {topic_id}")

            import ast

            topic_data = topic_row.iloc[0]
            topic_name = str(topic_data['Name'])
            topic_count = str(topic_data['Count'])
            representative_docs = topic_data['Representative_Docs']

            cleaned_docs = []

            # representative_docs is a list of strings that look like "['text']"
            for doc in representative_docs:
                if isinstance(doc, str):
                    try:
                        parsed_doc = ast.literal_eval(doc) # ['text']

                        if isinstance(parsed_doc, list):
                            cleaned_docs.append(" ".join(str(item) for item in parsed_doc))
                        else:
                            cleaned_docs.append(str(parsed_doc))

                    except Exception:
                        cleaned_docs.append(str(doc))
                else:
                    cleaned_docs.append(str(doc))

            numbered_docs = [f"{i}. {doc}" for i, doc in enumerate(cleaned_docs, 1)]

            content = [
                ui.h4(f"📋 Topic: {topic_name}"),
                ui.p(f"📄 Total documents: {topic_count}"),
                ui.h5("🎯 Representative documents:"),
                ui.br(),
            ]

            for doc in numbered_docs:
                content.append(ui.p(doc))

            return ui.div(*content)

        except Exception as e:
            return ui.p(f"Error loading documents: {e}")

    # Auto-run analysis effect
    @reactive.Effect
    def auto_run_analysis():
        """Auto-run analysis when app starts."""
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

    @reactive.Effect
    def update_topic_dropdown():
        if is_fitted():
            try:
                topic_info = analyzer().model.get_topic_info()
                topic_info = topic_info.sort_values(by='Count', ascending=False).head(10)
                
                # Create choices dictionary: {topic_id: "Topic ID: topic_name"}
                choices = {}
                for _, row in topic_info.iterrows():
                    topic_id = row['Topic']
                    topic_name = row['Name']
                    choices[topic_id] = f"Topic: {topic_name}"
                
                # Update the dropdown
                ui.update_select(
                    "topic_dropdown",
                    choices=choices,
                    selected=None
                )
                print(f"Updated dropdown with {len(choices)} topics")
                
            except Exception as e:
                print(f"Error updating dropdown: {e}")

    @reactive.Effect
    def handle_topic_selection():
        """Handle topic selection from dropdown."""
        if input.topic_dropdown() is not None:
            topic_id = int(input.topic_dropdown())
            selected_topic.set(topic_id)
            print(f"Selected topic from dropdown: {topic_id}")

app = App(app_ui, server)