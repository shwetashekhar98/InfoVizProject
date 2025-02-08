import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import plotly.express as px
import subprocess
import os
import time
from threading import Thread

st.set_page_config(layout="wide")

# Start all Dash apps in the background
def run_dash_app():
    subprocess.Popen(["python", "dash_app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dash_sparklines_app():
    subprocess.Popen(["python", "dash_sparklines.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dash_parallel_coordinates_app():
    subprocess.Popen(["python", "dash_parallel_coordinates.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dash_risk_return_matrix_app():
    subprocess.Popen(["python", "dash_risk_return_matrix.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dash_bar_chart_race_app():
    subprocess.Popen(["python", "dash_bar_chart_race.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dash_bubble_chart_animation_app():
    subprocess.Popen(["python", "dash_bubble_chart_animation.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

run_dash_app()
run_dash_sparklines_app()
run_dash_parallel_coordinates_app()
run_dash_risk_return_matrix_app()
run_dash_bar_chart_race_app()
run_dash_bubble_chart_animation_app()

# Initialize chatbot state
if "chat_visible" not in st.session_state:
    st.session_state.chat_visible = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# JavaScript and CSS for Floating Chatbot Icon
st.markdown("""
    <style>
        .chat-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #0078FF;
            color: white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 24px;
            border: none;
            cursor: pointer;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
        }

        .chat-button:hover {
            background-color: #0056b3;
        }

        .chat-window {
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 300px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
            padding: 10px;
            display: none;
        }

        .chat-visible {
            display: block !important;
        }
    </style>

    <button class="chat-button" onclick="toggleChat()">💬</button>

    <div id="chat-window" class="chat-window">
        <h4>Chat with AI</h4>
        <div id="chat-messages" style="height: 200px; overflow-y: auto;"></div>
        <input type="text" id="user-input" placeholder="Type a message..." style="width: 100%;">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        function toggleChat() {
            var chatWindow = document.getElementById('chat-window');
            if (chatWindow.style.display === 'none' || chatWindow.style.display === '') {
                chatWindow.style.display = 'block';
            } else {
                chatWindow.style.display = 'none';
            }
        }
    </script>
""", unsafe_allow_html=True)

# Streamlit Chatbot Logic
with st.sidebar.expander("💬 Chat with AI"):
    for msg in st.session_state.chat_history:
        st.markdown(msg)
    
    user_input = st.text_input("Ask me anything:")
    if st.button("Send"):
        if user_input:
            st.session_state.chat_history.append(f"**You:** {user_input}")
            response = "🤖 AI: I'm here to assist! How can I help?"
        
            st.session_state.chat_history.append(response)
            st.rerun()

# Main Content (Your existing dashboard logic here)
st.markdown('<div class="title">Stock Market Visualization Dashboard</div>', unsafe_allow_html=True)
