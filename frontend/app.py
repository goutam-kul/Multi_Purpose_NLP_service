import streamlit as st
import requests
import json
import pandas as pd

# API Base URL
API_BASE = "http://localhost:8000/api/v1"

# Page config
st.set_page_config(
    page_title="NLP Services Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Removed container boxes and improved styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    
    /* Remove default containers and padding */
    div.block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    .service-card {
        background: rgba(17, 25, 40, 0.75);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.125);
        margin-bottom: 1.5rem;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }
    
    .service-title {
        color: #1E88E5;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Style text areas */
    .stTextArea textarea {
        background-color: rgba(17, 25, 40, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.125);
        color: white;
        border-radius: 8px;
    }
    
    /* Style buttons */
    .stButton button {
        width: 100%;
        background-color: #1E88E5;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #1976D2;
        transform: translateY(-2px);
    }
    
    /* Style checkboxes and radio buttons */
    .stCheckbox label, .stRadio label {
        color: rgba(255, 255, 255, 0.85);
    }
    
    /* Style sliders */
    .stSlider {
        padding: 1rem 0;
    }
    
    /* Add dividers between options */
    .options-section {
        padding: 0.5rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.125);
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 1.5rem 0 2.5rem 0;'>
    <h1 style='
        color: #64B5F6;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #64B5F6, #1E88E5);
        -webkit-background-clip: text;
    '>
        🤖 Multi-Purpose NLP Services
    </h1>
    <div style='
        max-width: 800px;
        margin: 0 auto;
        color: #B0BEC5;
        font-size: 1.2rem;
        line-height: 1.6;
    '>
        <p style='margin-bottom: 0.5rem;'>
            Advanced Natural Language Processing solutions powered by state-of-the-art Ollama models.
        </p>
        <p style='font-size: 1.1rem; color: #90A4AE;'>
            Sentiment Analysis • Named Entity Recognition • Text Classification • Summarization
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# API Health Check Section
st.markdown("""
<style>
.status-container {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin: 10px 0;
}
.api-status {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    border-radius: 5px;
    background: rgba(17, 25, 40, 0.75);
}
.status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}
.status-text {
    font-size: 14px;
    font-weight: 500;
}
.healthy {
    background: #4CAF50;
    box-shadow: 0 0 10px #4CAF50;
}
.unhealthy {
    background: #f44336;
    box-shadow: 0 0 10px #f44336;
}
</style>
""", unsafe_allow_html=True)

# Check API and Ollama Health
api_healthy = False
ollama_healthy = False

try:
    health_response = requests.get(f"{API_BASE}/health", timeout=5)
    api_healthy = health_response.status_code == 200
except Exception:
    api_healthy = False

try:
    ollama_response = requests.get("http://localhost:11434/", timeout=10)
    ollama_healthy = ollama_response.status_code == 200
except Exception:
    ollama_healthy = False

# Create status indicators
st.markdown(f"""
    <div class="status-container">
        <div class="api-status">
            <span class="status-dot {'healthy' if api_healthy else 'unhealthy'}"></span>
            <span class="status-text" style="color: {'#4CAF50' if api_healthy else '#f44336'}">
                API Status: {'HEALTHY' if api_healthy else 'NOT CONNECTED'}
            </span>
        </div>
        <div class="api-status">
            <span class="status-dot {'healthy' if ollama_healthy else 'unhealthy'}"></span>
            <span class="status-text" style="color: {'#4CAF50' if ollama_healthy else '#f44336'}">
                Ollama Status: {'HEALTHY' if ollama_healthy else 'NOT CONNECTED'}
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Add this after the API status checks
def get_available_models():
    try:
        response = requests.get(f"{API_BASE}/available-models")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Add model selector in the sidebar
with st.sidebar:
    st.markdown("""
        <div style='padding: 1rem 0;'>
            <h3 style='color: #1E88E5; font-size: 1.2rem; margin-bottom: 1rem;'>
                🤖 Model Selection
            </h3>
        </div>
    """, unsafe_allow_html=True)

    models_info = get_available_models()
    if models_info:
        current_model = models_info.get('current_model')
        available_models = models_info.get('models', {})
        
        selected_model = st.radio(
            "Select Model",
            options=list(available_models.keys()),
            index=list(available_models.values()).index(current_model) if current_model else 0,
            format_func=lambda x: f"{x} ({available_models[x]})"
        )

        if st.button("Apply Model", type="primary", use_container_width=True):
            try:
                response = requests.post(
                    f"{API_BASE}/set-model",
                    json={"model_name": selected_model}
                )
                if response.status_code == 200:
                    st.success(f"Successfully switched to {selected_model}")
                else:
                    st.error("Failed to switch model")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.error("Unable to fetch available models")

# Documentation Section - after your service cards but before footer
st.markdown("---")  # Add a divider

# Documentation Header
st.markdown("""
<div style='padding: 1.0rem 0'>
    <h2 style='color: #1E88E5; font-size: 1.8rem; margin-bottom: 1rem;'>
        📚 API Documentation
    </h2>
    <p style='color: #E0E0E0; font-size: 1.1rem;'>
        Explore our comprehensive API documentation to integrate these NLP services into your applications.
    </p>
</div>
""", unsafe_allow_html=True)

# Create columns for documentation cards
doc_col1, doc_col2, doc_col3 = st.columns(3)

with doc_col1:
    st.markdown("""
        <div style='background: rgba(17, 25, 40, 0.75); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125); height: 100%;'>
            <h3 style='color: #1E88E5; font-size: 1.2rem; margin-bottom: 0.5rem;'>🔍 Swagger UI</h3>
            <p style='color: #B0BEC5; margin-bottom: 1rem;'>Interactive API documentation</p>
            <a href='http://localhost:8000/docs' target='_blank' style='background: #1E88E5; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; display: inline-block;'>View Docs</a>
        </div>
    """, unsafe_allow_html=True)

with doc_col2:
    st.markdown("""
        <div style='background: rgba(17, 25, 40, 0.75); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125); height: 100%;'>
            <h3 style='color: #1E88E5; font-size: 1.2rem; margin-bottom: 0.5rem;'>📘 ReDoc</h3>
            <p style='color: #B0BEC5; margin-bottom: 1rem;'>Beautiful and responsive API documentation</p>
            <a href='http://localhost:8000/redoc' target='_blank' style='background: #1E88E5; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; display: inline-block;'>View Docs</a>
        </div>
    """, unsafe_allow_html=True)

with doc_col3:
    st.markdown("""
        <div style='background: rgba(17, 25, 40, 0.75); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125); height: 100%;'>
            <h3 style='color: #1E88E5; font-size: 1.2rem; margin-bottom: 0.5rem;'>⚙️ OpenAPI Spec</h3>
            <p style='color: #B0BEC5; margin-bottom: 1rem;'>Raw OpenAPI/Swagger specification</p>
            <a href='http://localhost:8000/api/v1/openapi.json' target='_blank' style='background: #1E88E5; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; display: inline-block;'>View Spec</a>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='padding: 1.0rem 0'>
    <h2 style='color: #1E88E5; font-size: 1.8rem; margin-bottom: 1rem;'>
        👨‍🔧 Services
    </h2>
    <p style='color: #E0E0E0; font-size: 1.1rem;'>
        Powerful natural language processing tools for text analysis. Select a service below to get started.
    </p>
</div>
""", unsafe_allow_html=True)

# Create two columns for the service cards
col1, col2 = st.columns(2)

# Sentiment Analysis Card
with col1:
    st.markdown('<div class="service-title">🎭 Sentiment Analysis</div>', unsafe_allow_html=True)
    
    text_input = st.text_area(
        "Enter text to analyze sentiment:",
        placeholder="e.g., I really enjoyed this product! The service was excellent.",
        height=100,
        key="sentiment_input"
    )
    
    # Sentiment Analysis Options
    with st.expander("Advanced Options"):
        include_metadata = st.checkbox("Include detailed metadata", value=False)
    
    if st.button("Analyze Sentiment", key="sentiment_button"):
        if text_input:
            with st.spinner("Analyzing sentiment..."):
                try:
                    cleaned_text = text_input.strip().strip('"')
                    response = requests.post(
                        f"{API_BASE}/sentiment",
                        json={
                            "text": text_input,
                            "options": {
                                "include_metadata": include_metadata
                            }
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display sentiment with emoji
                        emoji = {"POSITIVE": "😊", "NEGATIVE": "😔", "NEUTRAL": "😐"}
                        color = {"POSITIVE": "green", "NEGATIVE": "red", "NEUTRAL": "grey"}
                        
                        # Main sentiment result with model info
                        st.markdown(f"""
                            <div style='background: rgba(17, 25, 40, 0.75); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125);'>
                                <h2 style='color: {color[result["sentiment"]]}; display: flex; align-items: center; gap: 0.5rem; margin: 0;'>
                                    {emoji[result["sentiment"]]} {result["sentiment"]} ({result["confidence"]:.2%})
                                </h2>
                                <p style='color: #E0E0E0; margin-top: 1rem;'>{result["explanation"]}</p>
                                <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.125);'>
                                    <span style='background: #1E88E5; color: white; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.9em;'>
                                        Model: {result["model"]}
                                    </span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Display metadata if available
                        if "metadata" in result and result["metadata"] is not None:
                            st.markdown("""
                                <div style='margin-top: 1.5rem;'>
                                    <h3 style='color: #1E88E5; margin-bottom: 1rem;'>Detailed Analysis</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if "sentiment_breakdown" in result["metadata"]:
                                breakdown = result["metadata"]["sentiment_breakdown"]
                                
                                for key, value in breakdown.items():
                                    if value:
                                        formatted_key = key.replace('_', ' ').title()
                                        formatted_value = ', '.join(value)
                                        st.markdown(f"**{formatted_key}:** {formatted_value}")
                                        
                                # Processing Information
                                st.markdown("""
                                    <p style='color: #90CAF9; font-weight: bold; margin-bottom: 0.5rem;'>
                                        Processing Stats
                                    </p>
                                """, unsafe_allow_html=True)
                            if "processing_time_seconds" in result["metadata"]: 
                                processing_time = result["metadata"]["processing_time_seconds"]
                                
                                # Display processing metrics
                                st.markdown(f"""Processing Time: {processing_time} Seconds
                                """, unsafe_allow_html=True)
                    else: 
                        error_detail = response.json()
                        if response.status_code == 422:
                            error_msg = error_detail.get('detail', [{}])[0].get('msg', 'Validation Error')
                            st.error(f"Input Error: {error_msg}")
                        
                        elif response.status_code == 500:
                            st.error("Internal Server Error: The server encountered an error. Please try again later.")
                            
                        else:
                            st.error(f"⚠️ Error: {response.status_code} - {response.text}")
                except requests.exceptions.Timeout:
                    st.error("⚠️ Request timed out. Please check if the server is responding.")
                except Exception as e:
                    st.error(f"⚠️ An unexpected error occurred: {str(e)}")
        else: 
            st.warning("Please enter some text to analyze")
st.markdown("---")

# NER Card
with col2:
    st.markdown('<div class="service-title">🎯 Named Entity Recognition</div>', unsafe_allow_html=True)
    
    ner_text = st.text_area(
        "Enter text to identify entities:",
        placeholder="e.g., Elon Musk announced that Tesla will open a new factory in Berlin.",
        height=100,
        key="ner_input"
    )
    
    # NER Options
    with st.expander("Additional Entity Types"):
        extract_time = st.checkbox("Time expressions", value=True)
        extract_numerical = st.checkbox("Numerical values", value=True)
        extract_email = st.checkbox("Email addresses", value=True)
        
        st.markdown("""
            <div style='font-size: 0.8em; color: #666;'>
            Default entities (always extracted): Person, Organization, Location
            </div>
        """, unsafe_allow_html=True)

    if st.button("Analyze Entities", key="ner_button"):
        if ner_text:
            with st.spinner("Identifying entities..."):
                try:
                    # Prepare options
                    options = {}
                    if extract_time:
                        options["extract_time"] = True
                    if extract_numerical:
                        options["extract_numerical"] = True
                    if extract_email:
                        options["extract_email"] = True

                    payload = {"text": ner_text}
                    if options:
                        payload["options"] = options

                    response = requests.post(
                        f"{API_BASE}/ner",
                        json=payload
                    )

                    if response.status_code == 200:
                        result = response.json()
                        entities = result["entities"]

                        if entities:
                            # Create a structured display of entities
                            st.markdown("""
                                <div style='background: rgba(17, 25, 40, 0.75); padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
                                    <h3 style='color: #64B5F6; margin-bottom: 10px;'>Identified Entities</h3>
                                </div>
                            """, unsafe_allow_html=True)

                            # Display entities in a clean table format
                            data = []
                            type_icons = {
                                'PERSON': '👤', 'ORG': '🏢', 'LOC': '📍',
                                'TIME': '⏰', 'NUMBER': '🔢', 'EMAIL': '📧'
                            }
                            
                            for entity in entities:
                                icon = type_icons.get(entity['type'], '🔍')
                                confidence = f"{entity['confidence']*100:.1f}%"
                                data.append([
                                    f"{icon} {entity['type']}", 
                                    entity['text'],
                                    f"{entity['start']}-{entity['end']}",
                                    confidence
                                ])
                            
                            df = pd.DataFrame(data, columns=['Type', 'Text', 'Position', 'Confidence'])
                            st.dataframe(df, hide_index=True, width=1000)
                        else:
                            st.info("No entities found in the text.")
                                            # Display model info in a simple banner
                        st.markdown(f"""
                            <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.125);'>
                                <span style='background: #1E88E5; color: white; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.9em;'>
                                    Model: {result["model"]}
                                </span>
                            </div>
                        """, unsafe_allow_html=True)

                    else:
                        error_detail = response.json()
                        if response.status_code == 422:
                            error_msg = error_detail.get('detail', [{}])[0].get('msg', 'Validation Error')
                            st.error(f"Input Error: {error_msg}")
                        elif response.status_code == 500:
                            st.error("Internal Server Error: The server encountered an error. Please try again later.")
                        else:
                            st.error(f"⚠️ Error: {response.status_code} - {response.text}")

                except requests.exceptions.Timeout:
                    st.error("⚠️ Request timed out. Please check if the server is responding.")
                except Exception as e:
                    st.error(f"⚠️ An unexpected error occurred: {str(e)}")
        else:
            st.warning("Please enter some text to perform NER analysis.")
# Create two more columns
col3, col4 = st.columns(2)

# Text Classification Card
with col3:
    # st.markdown('<div class="service-card">', unsafe_allow_html=True)
    st.markdown('<div class="service-title">📑 Text Classification</div>', unsafe_allow_html=True)
    
    classify_text = st.text_area(
        "Enter text to classify:",
        placeholder="e.g., Tesla announces new electric vehicle battery technology",
        height=100,
        key="classify_input"
    )
    
    # Classification Options
    with st.expander("Classification Options"):
        multi_label = st.checkbox("Enable multi-label classification")
        custom_categories = st.multiselect(
            "Select categories",
            ["Business", "Technology", "Politics", "Sports", "Entertainment", "Science", "Health"],
            default=["Business", "Technology", "Science"]
        )
    
    if st.button("Classify Text", key="classify_button"):
        if classify_text:
            with st.spinner("Classifying text..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/classify",
                        json={
                            "text": classify_text,
                            "options": {
                                "multi_label": multi_label,
                                "categories": custom_categories
                            }
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display primary category
                        st.markdown(f"""
                            **Primary Category:** 
                            `{result['primary_category']}` ({result['confidence']:.2%})
                        """)
                        
                        # Display all categories in a more visual way
                        st.markdown("**All Categories:**")
                        for category in result['all_categories']:
                            confidence = category['confidence']
                            bar_length = int(confidence * 20)
                            bar = "█" * bar_length + "░" * (20 - bar_length)
                            st.markdown(f"""
                                {category['category']}:\n
                                `{bar}` {confidence:.2%}
                            """)
                        
                        st.markdown("**Analysis:**")
                        st.write(result['explanation'])
                        
                        st.markdown(f"""
                            <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.125);'>
                                <span style='background: #1E88E5; color: white; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.9em;'>
                                    Model: {result["model"]}
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                    else: 
                        error_detail = response.json()

                        if response.status_code == 422:
                            error_msg = error_detail.get('detail', [{}])[0].get('msg', 'Validation Error')
                            st.error(f"Input Error: {error_msg}")

                        elif response.status_code == 500:
                            st.error(f"Internal Server Error: The server encountered an error. Please try again later.")

                        else: 
                            st.error(f"⚠️Error: {response.status_code} - {response.text}")

                except requests.exceptions.Timeout:
                    st.error("⚠️ Request timed out. Please check if the server is responding.")
                except Exception as e:
                    st.error(f"⚠️ An unexpected error occurred: {str(e)}")
        else:
            st.warning("Please enter some text to classify")
# Text Summarization Card
with col4:
    # st.markdown('<div class="service-card">', unsafe_allow_html=True)
    st.markdown('<div class="service-title">📚 Text Summarization</div>', unsafe_allow_html=True)
    
    summarize_text = st.text_area(
        "Enter text to summarize:",
        placeholder="Enter a long text (minimum 10 words) to generate a summary...",
        height=100,
        key="summarize_input"
    )
    
    # Summarization Options
    with st.expander("Summarization Options"):
        col_length, col_type = st.columns(2)
        with col_length:
            max_length = st.slider("Max length (words)", 10, 200, 100)
        with col_type:
            sum_type = st.radio("Type", ["abstractive", "extractive"])
    
    if st.button("Summarize Text", key="summarize_button"):
        if summarize_text:
            if len(summarize_text.split()) < 10:
                st.warning("Please enter at least 10 words for summarization")
            else:
                with st.spinner("Generating summary..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/summarize",
                            json={
                                "text": summarize_text,
                                "options": {
                                    "max_length": max_length,
                                    "type": sum_type
                                }
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.markdown("**Summary:**")
                            st.write(result['summary'])
                            
                            # Display key points in a more visual way
                            st.markdown("**Key Points:**")
                            for i, point in enumerate(result['key_points'], 1):
                                st.markdown(f"{i}. {point}")
                            
                            # Display metrics in columns
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Original Length", f"{result['metadata']['original_length']} words")
                            with col2:
                                st.metric("Summary Length", f"{result['metadata']['summary_length']} words")
                            with col3:
                                st.metric("Compression", f"{result['metadata']['compression_ratio']:.1%}")
                            # Display model
                            st.markdown(f"""
                                <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.125);'>
                                    <span style='background: #1E88E5; color: white; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.9em;'>
                                        Model: {result["model"]}
                                    </span>
                                </div>
                            """, unsafe_allow_html=True)
                        else: 
                            error_detail = response.json()

                            if response.status_code == 422:
                                error_msg = error_detail.get('detail', [{}])[0].get('msg', 'Validation Error')
                                st.error(f"Input Error: {error_msg}")

                            elif response.status_code == 500:
                                st.error(f"Internal Server Error: The server encountered an error. Please try again later.")

                            else: 
                                st.error(f"⚠️Error: {response.status_code} - {response.text}")

                    except requests.exceptions.Timeout:
                        st.error("⚠️ Request timed out. Please check if the server is responding.")
                    except Exception as e:
                        st.error(f"⚠️ An unexpected error occurred: {str(e)}")
        else:
            st.warning("Please enter some text to classify")

# About Section
st.markdown("---")
st.markdown("""
<div style='padding: 1.0rem 0'>
    <h2 style='color: #1E88E5; font-size: 1.8rem; margin-bottom: 1rem;'>
        ℹ️ About
    </h2>
</div>
""", unsafe_allow_html=True)


# Create three columns for different aspects
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div style='background: rgba(17, 25, 40, 0.75); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125); height: 100%;'>
            <h3 style='color: #1E88E5; font-size: 1.2rem; margin-bottom: 0.5rem;'>🚀 Features</h3>
            <ul style='color: #B0BEC5; margin: 0; padding-left: 1.2rem;'>
                <li>Real-time NLP Analysis</li>
                <li>Four Powerful Services</li>
                <li>Redis Caching System</li>
                <li>Response Model: Llama3.2:3b </li>
                <li>FastAPI Backend</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style='background: rgba(17, 25, 40, 0.75); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125); height: 100%;'>
            <h3 style='color: #1E88E5; font-size: 1.2rem; margin-bottom: 0.5rem;'>🛠️ Technology Stack</h3>
            <ul style='color: #B0BEC5; margin: 0; padding-left: 1.2rem;'>
                <li>Python FastAPI</li>
                <li>Streamlit UI</li>
                <li>Redis Cache</li>
                <li>Ollama Models</li>
                <li>Docker Support</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style='background: rgba(17, 25, 40, 0.75); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125); height: 100%;'>
            <h3 style='color: #1E88E5; font-size: 1.2rem; margin-bottom: 0.5rem;'>👨‍💻 Developer</h3>
            <p style='color: #B0BEC5; margin-bottom: 1rem;'>Created by Goutam</p>
            <div style='display: flex; gap: 0.5rem;'>
                <a href='https://github.com/goutam-kul' target='_blank' style='background: #1E88E5; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; display: inline-block;'>GitHub</a>
                <a href='mailto:goutammunda3134@gmail.com' style='background: #1E88E5; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; display: inline-block;'>Email</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Footer with version and license
st.markdown("""
<div style='margin-top: 2rem; text-align: center; color: #B0BEC5; font-size: 0.9rem;'>
    <p>Version 1.0.0 | Licensed under MIT</p>
    <p style='margin-top: 0.5rem;'>© 2024 Multi-Purpose NLP Service. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)