from pathlib import Path
from typing import Any
import csv
import html
import json
import re
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.app.answer_generator import generate_answer
from src.config_loader import get_project_root
from src.embedding.tokenizer_demo import analyze_tokenization
from src.search.query_parser import parse_query
from src.search.semantic_search import semantic_search


ROVER_IDLE = PROJECT_ROOT / "ui" / "assets" / "rover" / "rover_idle.gif"
ROVER_SEARCHING = PROJECT_ROOT / "ui" / "assets" / "rover" / "rover_searching.gif"
ROVER_RESULT = PROJECT_ROOT / "ui" / "assets" / "rover" / "rover_result.gif"
ROVER_NOT_FOUND = PROJECT_ROOT / "ui" / "assets" / "rover" / "rover_not_found.gif"


EXAMPLE_QUERIES = [
    "1000 TL altı stokta olan kablosuz kulaklık öner",
    "teslim edilen kargoları listele",
    "yüksek puanlı ayakkabı yorumları",
    "Samsung marka telefonları göster",
    "hasarlı gelen ürün iadelerini göster",
    "oyuncu mouse öner",
    "stokta olmayan ürünleri listele",
]


def inject_css() -> None:
    st.markdown(
        """
        <style>
            header[data-testid="stHeader"] {
                display: none;
            }

            .stApp {
                background: #3a6ea5;
                font-family: Tahoma, Verdana, Arial, sans-serif;
            }

            .block-container {
                max-width: 1180px;
                padding-top: 1.1rem;
                padding-bottom: 2rem;
            }

            div[data-testid="stVerticalBlock"] {
                gap: 0;
            }

            .xp-shell {
                border: 3px solid #0055e5;
                background: #ece9d8;
                box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.35);
                margin-bottom: 0;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-left-title) {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                background: white;
                border-left: 3px solid #0055e5;
                border-right: 3px solid #0055e5;
                border-bottom: 3px solid #0055e5;
                box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.35);
                gap: 0 !important;
                align-items: stretch;
                min-height: 650px;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-left-title) > div[data-testid="stColumn"]:first-child {
                flex: 0 0 328px !important;
                flex-basis: 328px !important;
                flex-grow: 0 !important;
                flex-shrink: 0 !important;
                width: 328px !important;
                min-width: 320px !important;
                max-width: 350px !important;
                background: #7ca7e8;
                border-right: 2px solid #9eaac0;
                padding: 0 14px 20px 14px;
                min-height: 650px;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-left-title) > div[data-testid="stColumn"]:last-child {
                flex: 1 1 auto !important;
                flex-basis: auto !important;
                flex-grow: 1 !important;
                flex-shrink: 1 !important;
                width: auto !important;
                min-width: 420px !important;
                max-width: none !important;
                background: white;
                padding: 18px 24px 24px 24px;
                min-height: 650px;
            }

            .xp-titlebar {
                background: linear-gradient(90deg, #0055e5, #3c8dff);
                color: white;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 18px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .xp-window-buttons {
                display: flex;
                gap: 5px;
            }

            .xp-window-button {
                background: #dfe8ff;
                color: #003c9e;
                border: 1px solid white;
                width: 24px;
                height: 22px;
                text-align: center;
                line-height: 20px;
                font-weight: bold;
                box-shadow: inset -1px -1px #4b6db3;
            }

            .xp-window-button.close {
                background: #e85b3f;
                color: white;
            }

            .xp-menu-row {
                height: 34px;
                display: flex;
                align-items: center;
                padding: 0 18px;
                background: #ece9d8;
                border-bottom: 1px solid #aca899;
                box-sizing: border-box;
                font-size: 14px;
                color: #222;
                word-spacing: 18px;
            }

            .xp-toolbar {
                height: 32px;
                display: flex;
                align-items: center;
                gap: 0;
                padding: 3px 0 3px 24px;
                background: #ece9d8;
                border-left: 3px solid #0055e5;
                border-right: 3px solid #0055e5;
                border-top: 1px solid #ffffff;
                border-bottom: 1px solid #aca899;
                box-sizing: border-box;
            }

            .xp-toolbar-item {
                height: 26px;
                padding: 2px 14px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                border: 1px solid #9aa7c2;
                background: #ece9d8;
                color: #222;
                box-shadow: inset 1px 1px white, inset -1px -1px #777;
                font-size: 13px;
                line-height: 18px;
                font-weight: normal;
                min-width: 100px;
                text-align: center;
                white-space: nowrap;
                box-sizing: border-box;
                margin: 0;
                position: relative;
                top: 0;
            }

            .xp-toolbar-item.active {
                border: 1px solid #9aa7c2;
                background: #eef3ff;
                color: #003c9e;
                box-shadow: inset 1px 1px white, inset -1px -1px #7b8ebc;
            }

            .xp-addressbar {
                background: #ece9d8;
                border-left: 3px solid #0055e5;
                border-right: 3px solid #0055e5;
                border-bottom: 1px solid #c8c2b4;
                padding: 7px 12px;
                display: flex;
                gap: 8px;
                align-items: center;
                font-size: 14px;
                box-shadow: 4px 0 0 rgba(0, 0, 0, 0.35);
            }

            .xp-address-input {
                background: white;
                border: 1px solid #7f9db9;
                padding: 5px 8px;
                flex: 1;
                color: #333;
            }

            .xp-go-button {
                background: linear-gradient(#4ec85d, #168729);
                color: white;
                border: 1px solid #0d651b;
                padding: 5px 13px;
                font-weight: bold;
            }

            .xp-left-title {
                font-weight: bold;
                color: #1f3763;
                font-size: 15px;
                background: #dbe8ff;
                border-bottom: 1px solid #9db5e9;
                padding: 12px 14px;
                margin: 0 -14px 36px -14px;
                line-height: 1.2;
                position: relative;
                top: 18px;
            }

            .example-box {
                background: #eaf2ff;
                border: 1px solid #9db5e9;
                padding: 14px;
                margin-top: 22px;
                font-size: 13px;
                line-height: 1.7;
                color: #1a2f55;
                box-shadow: inset 1px 1px white;
            }

            .example-title {
                font-weight: bold;
                margin-bottom: 8px;
                color: #1f3763;
            }

            .xp-form-heading {
                color: #1f3763;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 8px;
            }

            .xp-form-description {
                color: #333;
                font-size: 13px;
                line-height: 1.5;
                margin-bottom: 16px;
            }

            .xp-form-section-label {
                color: #1f3763;
                font-size: 13px;
                font-weight: bold;
                margin: 14px 0 7px 0;
            }

            div[data-testid="stVerticalBlock"]:has(.xp-form-card-marker):not(:has(.xp-left-title)) {
                background: #f7f7f7;
                border: 1px solid #9db5e9;
                border-radius: 0;
                box-shadow: inset 1px 1px white, 2px 2px 0 rgba(0, 0, 0, 0.12);
                padding: 18px;
                margin-top: 14px;
                margin-bottom: 0;
                gap: 0.55rem;
            }

            div[data-testid="stVerticalBlockBorderWrapper"]:has(.xp-form-card-marker) {
                background: #f7f7f7;
                border: 1px solid #9db5e9;
                border-radius: 0;
                box-shadow: inset 1px 1px white, 2px 2px 0 rgba(0, 0, 0, 0.12);
                margin-top: 14px;
                margin-bottom: 0;
            }

            div[data-testid="stVerticalBlockBorderWrapper"]:has(.xp-form-card-marker) > div {
                padding: 18px;
            }

            .result-header {
                font-size: 22px;
                color: #1b376d;
                font-weight: bold;
                margin-bottom: 12px;
                background: white;
                border: 1px solid #b8c7e6;
                padding: 12px 15px;
                box-shadow: inset 1px 1px white;
            }

            .right-hint {
                color: #666;
                font-size: 16px;
                margin-bottom: 20px;
                background: #fbfbfb;
                border: 1px solid #d8deea;
                padding: 14px 15px;
            }

            .empty-results {
                position: relative;
                min-height: 470px;
            }

            .search-watermark {
                position: absolute;
                right: 52px;
                bottom: 36px;
                color: rgba(0, 80, 180, 0.055);
                font-size: 148px;
                line-height: 1;
                pointer-events: none;
                user-select: none;
            }

            .answer-box {
                background: #fffbe8;
                border: 1px solid #e2d28a;
                padding: 15px;
                margin-bottom: 18px;
                color: #222;
                line-height: 1.55;
                font-size: 14px;
            }

            .result-card {
                border: 1px solid #b8c7e6;
                border-bottom-color: #9db5e9;
                background: #f7faff;
                padding: 10px 12px;
                margin-bottom: 8px;
                box-shadow: inset 1px 1px white;
            }

            .result-card-topline {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
                margin-bottom: 4px;
            }

            .result-title-wrap {
                display: flex;
                align-items: center;
                gap: 7px;
                min-width: 0;
            }

            .result-icon {
                font-size: 14px;
                line-height: 1;
            }

            .result-card-title {
                font-weight: bold;
                color: #003c9e;
                font-size: 15px;
                line-height: 1.25;
            }

            .score-badge {
                background: #fff8cf;
                border: 1px solid #d6c77a;
                color: #4a4218;
                font-size: 12px;
                white-space: nowrap;
                padding: 2px 6px;
            }

            .result-source {
                color: #333;
                font-size: 12px;
                margin-bottom: 7px;
            }

            .metadata-chips {
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
                margin: 5px 0 7px 0;
            }

            .metadata-chip {
                background: #ece9d8;
                border: 1px solid #aaa;
                color: #1f3763;
                font-size: 12px;
                padding: 2px 6px;
                box-shadow: inset 1px 1px white;
            }

            .result-content {
                color: #444;
                font-size: 13px;
                line-height: 1.5;
            }

            .price-lines {
                color: #222;
                font-size: 13px;
                line-height: 1.55;
                margin: 6px 0;
            }

            .feature-line {
                color: #555;
                font-size: 12px;
                line-height: 1.5;
                margin: 5px 0;
            }

            .product-description {
                color: #333;
                font-size: 14px;
                line-height: 1.45;
                margin-top: 10px;
            }

            div[data-testid="stTextInput"] input {
                border: 1px solid #7f9db9;
                border-radius: 0;
                font-family: Tahoma, Verdana, Arial, sans-serif;
                font-size: 14px;
                height: 32px;
                min-height: 32px;
                padding: 4px 8px;
                background: white;
                box-shadow: inset 1px 1px #d5d5d5;
            }

            div[data-testid="stButton"] button {
                background: #ece9d8;
                color: #222;
                border: 1px solid #888;
                border-radius: 0;
                box-shadow: inset 1px 1px white, inset -1px -1px #777;
                font-family: Tahoma, Verdana, Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                min-height: 36px;
                height: 36px;
                padding: 4px 12px;
            }

            div[data-testid="stButton"] button:hover {
                border: 1px solid #0055e5;
                color: #003c9e;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-toolbar-marker) {
                height: 32px !important;
                display: flex !important;
                align-items: center !important;
                gap: 6px !important;
                padding: 3px 0 3px 24px !important;
                background: #ece9d8;
                border-left: 3px solid #0055e5;
                border-right: 3px solid #0055e5;
                border-top: 1px solid #ffffff;
                border-bottom: 1px solid #aca899;
                box-sizing: border-box !important;
                box-shadow: 4px 0 0 rgba(0, 0, 0, 0.35);
                overflow: hidden !important;
                white-space: nowrap !important;
                margin-top: 0 !important;
                transform: none !important;
                position: relative !important;
                top: 0 !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-toolbar-marker) > div[data-testid="stColumn"] {
                display: flex !important;
                align-items: center !important;
                width: auto !important;
                flex: 0 0 auto !important;
                padding: 0 !important;
                margin: 0 8px 0 0 !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-toolbar-marker) div[data-testid="stButton"] button {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 5px !important;
                white-space: nowrap !important;
                width: auto !important;
                min-width: 105px !important;
                min-height: 26px !important;
                height: 26px !important;
                line-height: 18px !important;
                font-size: 13px !important;
                font-weight: normal !important;
                letter-spacing: normal !important;
                padding: 2px 14px !important;
                border: 1px solid #8d8d8d !important;
                background: #ece9d8 !important;
                color: #222 !important;
                box-shadow: inset 1px 1px white, inset -1px -1px #777 !important;
                outline: none !important;
                box-sizing: border-box !important;
                margin: 0 !important;
                position: relative !important;
                top: 0 !important;
                transform: none !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-toolbar-marker) > div[data-testid="stColumn"]:nth-child(3) div[data-testid="stButton"] button {
                min-width: 125px !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-toolbar-marker) > div[data-testid="stColumn"]:nth-child(4) div[data-testid="stButton"] button {
                min-width: 160px !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-toolbar-marker) div[data-testid="stButton"] button:focus,
            div[data-testid="stHorizontalBlock"]:has(.xp-toolbar-marker) div[data-testid="stButton"] button:active {
                border: 1px solid #7f9db9 !important;
                background: #dbe8f9 !important;
                color: #003c9e !important;
                box-shadow: inset 1px 1px 0 #ffffff !important;
                outline: none !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.xp-toolbar-marker) div[data-testid="stButton"] button[kind="secondary"]:focus:not(:active) {
                box-shadow: inset 1px 1px white, inset -1px -1px #777 !important;
            }

            div[data-testid="stSelectbox"] label {
                color: #1f3763;
                font-size: 13px;
            }

            div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
                min-height: 32px;
                height: 32px;
                border-radius: 0;
                border-color: #7f9db9;
                background: white;
                font-family: Tahoma, Verdana, Arial, sans-serif;
                font-size: 14px;
            }

            div[data-testid="stCheckbox"] label {
                color: #1f3763;
                font-size: 13px;
                min-height: 22px;
            }

            div[data-testid="stCheckbox"] {
                margin-top: 3px;
                margin-bottom: 12px;
            }

            div[data-testid="stCheckbox"] label span {
                font-size: 13px;
            }

            div[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] {
                min-height: 22px;
            }

            div[data-testid="stImage"] {
                text-align: center;
                background: transparent;
                border: 0;
                padding: 0;
                margin-top: 24px;
            }

            .stExpander {
                border: 1px solid #b8c7e6 !important;
            }

            .tokenizer-demo-box {
                background: #ece9d8;
                border: 1px solid #8c8c8c;
                padding: 10px 12px 12px 12px;
                color: #222;
                font-family: Tahoma, Verdana, Arial, sans-serif;
                box-shadow: inset 1px 1px white;
            }

            .tokenizer-fieldset {
                border: 1px solid #9a9a9a;
                background: #f4f1e6;
                margin: 8px 0 12px 0;
                padding: 12px;
            }

            .tokenizer-legend {
                display: inline-block;
                background: #ece9d8;
                color: #003c9e;
                font-weight: bold;
                font-size: 13px;
                padding: 0 6px;
                position: relative;
                top: -20px;
                margin-bottom: -12px;
            }

            .tokenizer-note {
                background: #fffef2;
                border: 1px solid #c8c2a4;
                padding: 8px 9px;
                font-size: 13px;
                line-height: 1.45;
                margin-bottom: 10px;
            }

            .tokenizer-summary-table,
            .tokenizer-token-table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                font-family: Tahoma, Verdana, Arial, sans-serif;
                font-size: 12px;
                color: #222;
            }

            .tokenizer-summary-table th,
            .tokenizer-summary-table td,
            .tokenizer-token-table th,
            .tokenizer-token-table td {
                border: 1px solid #b8b8b8;
                padding: 5px 7px;
                text-align: left;
                vertical-align: top;
            }

            .tokenizer-summary-table th,
            .tokenizer-token-table th {
                background: #dbe8ff;
                color: #1f3763;
                font-weight: bold;
            }

            .tokenizer-warning {
                background: #fff2bf;
                border: 1px solid #b99b32;
                color: #3d3200;
                padding: 9px 10px;
                font-size: 13px;
                box-shadow: inset 1px 1px white;
            }

            .xp-info-panel {
                background: #ece9d8;
                border: 1px solid #8c8c8c;
                padding: 12px;
                color: #222;
                font-family: Tahoma, Verdana, Arial, sans-serif;
                font-size: 13px;
                line-height: 1.5;
                box-shadow: inset 1px 1px white;
                margin-bottom: 12px;
            }

            .xp-page-title {
                font-size: 22px;
                color: #1b376d;
                font-weight: bold;
                margin-bottom: 12px;
                background: white;
                border: 1px solid #b8c7e6;
                padding: 12px 15px;
                box-shadow: inset 1px 1px white;
            }

            .xp-report-section {
                border: 1px solid #9a9a9a;
                background: #f4f1e6;
                margin: 12px 0;
                padding: 12px;
                box-shadow: inset 1px 1px white;
            }

            .xp-table {
                width: 100%;
                max-width: 100%;
                border-collapse: collapse;
                background: white;
                font-family: Tahoma, Verdana, Arial, sans-serif;
                font-size: 11px;
                color: #222;
                margin-top: 8px;
            }

            .xp-table th,
            .xp-table td {
                border: 1px solid #b8b8b8;
                padding: 5px 7px;
                text-align: left;
                vertical-align: top;
            }

            .xp-table th {
                background: #dbe8ff;
                color: #1f3763;
                font-weight: bold;
            }

            .xp-table-scroll {
                max-width: 100%;
                overflow-x: auto;
                border: 1px solid #b8b8b8;
                background: white;
                margin-top: 8px;
            }

            textarea {
                border: 1px solid #7f9db9 !important;
                border-radius: 0 !important;
                font-family: Tahoma, Verdana, Arial, sans-serif !important;
                font-size: 14px !important;
                background: white !important;
                box-shadow: inset 1px 1px #d5d5d5 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_rover_message(state: str, intent: str | None = None) -> str:
    if state == "searching":
        return "Bir saniye... veritabanındaki ürünleri, siparişleri ve yorumları araştırıyorum."

    if state == "not_found":
        return "Hmm... bu sorguya uygun bir kayıt bulamadım. Biraz daha farklı yazmayı deneyebilirsin."

    if state == "result":
        if intent == "product":
            return "Buldum! Ürün kayıtlarını kontrol ettim ve en uygun sonuçları sağ tarafa listeledim."
        if intent == "cargo":
            return "Kargo kayıtlarını inceledim. Teslimat bilgilerini sağ tarafta görebilirsin."
        if intent == "review":
            return "Müşteri yorumlarını taradım. En uygun yorumları sağ tarafta listeledim."
        if intent == "return":
            return "İade kayıtlarını kontrol ettim. İlgili talepleri sağ tarafta gösteriyorum."
        return "Buldum! Sorguna en uygun kayıtları sağ tarafta listeledim."

    return "Merhaba! E-ticaret veritabanında ne aramamı istersin?"


def get_rover_image(state: str) -> Path:
    if state == "searching":
        return ROVER_SEARCHING
    if state == "result":
        return ROVER_RESULT
    if state == "not_found":
        return ROVER_NOT_FOUND
    return ROVER_IDLE


def init_session_state() -> None:
    defaults = {
        "active_page": "search",
        "query": "",
        "query_input": "",
        "tokenizer_input": "1000 TL altı stokta olan kablosuz kulaklık öner",
        "tokenizer_analysis": None,
        "pending_query": "",
        "pending_limit": 5,
        "search_in_progress": False,
        "results": [],
        "parsed_query": None,
        "answer": "",
        "rover_state": "idle",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.active_page not in {"search", "tokenizer", "model_report"}:
        st.session_state.active_page = "search"


def set_active_page(page: str) -> None:
    st.session_state.active_page = page


def clear_search_state() -> None:
    st.session_state.query = ""
    st.session_state.query_input = ""
    st.session_state.pending_query = ""
    st.session_state.pending_limit = 5
    st.session_state.search_in_progress = False
    st.session_state.results = []
    st.session_state.parsed_query = None
    st.session_state.answer = ""
    st.session_state.rover_state = "idle"


def queue_search(query: str, limit: int) -> None:
    st.session_state.query = query
    st.session_state.pending_query = query
    st.session_state.pending_limit = limit
    st.session_state.search_in_progress = True
    st.session_state.rover_state = "searching"
    st.rerun()


def render_xp_header() -> None:
    st.markdown(
        """
        <div class="xp-shell">
            <div class="xp-titlebar">
                <div>🔎 E-Ticaret Rover Asistanı</div>
                <div class="xp-window-buttons">
                    <div class="xp-window-button">_</div>
                    <div class="xp-window-button">□</div>
                    <div class="xp-window-button close">×</div>
                </div>
            </div>
            <div class="xp-menu-row">
                File Edit View Favorites Tools Help
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_toolbar() -> None:
    active_page = st.session_state.active_page
    labels = [
        ("search", "Search"),
        ("tokenizer", "Tokenizer"),
        ("model_report", "Model Report"),
    ]
    cols = st.columns([0.01, 0.72, 0.86, 1.08, 5.0], gap="small")

    with cols[0]:
        st.markdown('<span class="xp-toolbar-marker"></span>', unsafe_allow_html=True)

    for column, (page, label) in zip(cols[1:4], labels):
        with column:
            st.button(
                label,
                key=f"toolbar_{page}",
                use_container_width=False,
                on_click=set_active_page,
                args=(page,),
            )


def get_address_label() -> str:
    labels = {
        "search": "Search Results",
        "tokenizer": "Tokenizer Demo",
        "model_report": "Model Evaluation Report",
    }
    return labels.get(st.session_state.active_page, "Search Results")


def render_addressbar() -> None:
    st.markdown(
        f"""
        <div class="xp-addressbar">
            <span>Address</span>
            <div class="xp-address-input">{html.escape(get_address_label())}</div>
            <div class="xp-go-button">Go</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_left_panel() -> tuple[str, int, bool, bool]:
    rover_state = st.session_state.rover_state
    rover_image = get_rover_image(rover_state)

    st.markdown('<div class="xp-left-title">Search Companion</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<span class="xp-form-card-marker"></span>', unsafe_allow_html=True)
        st.markdown('<div class="xp-form-heading">Doğal dil ile ara</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="xp-form-description">
                E-ticaret veritabanında ürün, kargo, iade, yorum ve sipariş kayıtlarını arayabilirsin.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="xp-form-section-label">Ne aramak istiyorsun?</div>', unsafe_allow_html=True)
        query = st.text_input(
            "Ne aramak istiyorsun?",
            placeholder="Orn: stokta kulaklik oner",
            label_visibility="collapsed",
            key="query_input",
        )

        st.markdown('<div class="xp-form-section-label">Sonuç sayısı</div>', unsafe_allow_html=True)
        result_limit = st.selectbox("Sonuç sayısı", options=[3, 5, 10], index=1, label_visibility="collapsed")

        st.markdown('<div class="xp-form-section-label">Seçenekler</div>', unsafe_allow_html=True)
        show_debug = st.checkbox("Teknik detayları göster", value=True)

        clear_col, search_col = st.columns([1, 1], gap="small")
        with clear_col:
            st.button("Temizle", use_container_width=True, on_click=clear_search_state)
        with search_col:
            search_clicked = st.button("Ara", use_container_width=True)

    st.markdown(
        """
        <div class="example-box">
            <div class="example-title">Örnek sorgular</div>
            <div>→ 1000 TL altı stokta olan kablosuz kulaklık öner</div>
            <div>→ teslim edilen kargoları listele</div>
            <div>→ yüksek puanlı ayakkabı yorumları</div>
            <div>→ hasarlı gelen ürün iadelerini göster</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.image(str(rover_image), width=135)

    return query, result_limit, search_clicked and bool(query.strip()), show_debug


def format_answer_html(answer: str) -> str:
    escaped_answer = html.escape(answer)
    formatted_answer = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped_answer)
    return formatted_answer.replace("\n", "<br>")


def render_answer(answer: str) -> None:
    st.markdown('<div class="result-header">Search Results</div>', unsafe_allow_html=True)

    if not answer:
        st.markdown(
            """
            <div class="empty-results">
                <div class="right-hint">
                    Aramaya başlamak için sol paneldeki Rover’a ne aradığını yaz.
                </div>
                <div class="search-watermark">🔍</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    html_answer = format_answer_html(answer)
    st.markdown(
        f"""
        <div class="answer-box">
            {html_answer}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_parsed_query(parsed_query: Any) -> None:
    if parsed_query is None:
        return

    with st.expander("Sorgu Analizi", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Intent:**", parsed_query.intent)
            st.write("**Kategori:**", parsed_query.category)
            st.write("**Marka:**", parsed_query.brand)
            st.write("**Model filtre:**", parsed_query.model_filter or "Yok")

        with col2:
            st.write("**Max fiyat:**", parsed_query.max_price)
            st.write("**Min fiyat:**", parsed_query.min_price)
            st.write("**Min puan:**", parsed_query.min_rating)
            st.write("**Max puan:**", parsed_query.max_rating)
            st.write("**Eşit puan:**", parsed_query.rating_equals or "Yok")

        with col3:
            st.write("**Stokta:**", parsed_query.in_stock_only)
            st.write("**Stokta olmayan:**", parsed_query.out_of_stock_only)
            st.write("**Durum:**", parsed_query.status)
            st.write("**Sıralama alanı:**", parsed_query.sort_by or "Yok")
            st.write("**Sıralama yönü:**", parsed_query.sort_direction or "Yok")

        st.write("**Arama metni:**", parsed_query.search_text)
        st.write("**Kaynak tablolar:**", parsed_query.source_tables)
        st.write(
            "**Özellik filtreleri:**",
            parsed_query.attribute_filters or "Yok",
        )


def get_token_explanation(
    token: str,
    attention: int,
    special_value: int | None,
    analysis: dict[str, Any],
) -> str:
    if token == analysis.get("unk_token"):
        return "Bilinmeyen token"

    if token == analysis.get("pad_token") or attention == 0:
        return "Padding"

    if special_value == 1:
        if token == analysis.get("cls_token"):
            return "Başlangıç özel token"
        if token == analysis.get("sep_token"):
            return "Bitiş özel token"
        return "Özel token"

    return "Gerçek token"


def render_xp_warning(message: str) -> None:
    st.markdown(
        f"""
        <div class="tokenizer-warning">
            {html.escape(message)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_xp_table(headers: list[str], rows: list[list[Any]], class_name: str = "xp-table") -> None:
    header_html = "".join(f"<th>{html.escape(str(header))}</th>" for header in headers)
    row_html = ""

    for row in rows:
        row_html += "<tr>"
        row_html += "".join(f"<td>{html.escape(str(value))}</td>" for value in row)
        row_html += "</tr>"

    st.markdown(
        f"""
        <div class="xp-table-scroll">
            <table class="{class_name}">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{row_html}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tokenizer_analysis(analysis: dict[str, Any], show_padding_tokens: bool) -> None:
    token_rows = []
    special_tokens_mask = analysis.get("special_tokens_mask") or []

    for index, (token, token_id, attention) in enumerate(
        zip(
            analysis["tokens"],
            analysis["token_ids"],
            analysis["attention_mask"],
        )
    ):
        if int(attention) == 0 and not show_padding_tokens:
            continue

        special_value = special_tokens_mask[index] if index < len(special_tokens_mask) else None
        explanation = get_token_explanation(
            token=token,
            attention=int(attention),
            special_value=special_value,
            analysis=analysis,
        )
        token_rows.append([index, token, token_id, attention, explanation])

    st.markdown(
        """
        <div class="tokenizer-demo-box">
            <div class="tokenizer-note">
                Bu ekran, girilen metnin model tarafından nasıl sayısal girdiye çevrildiğini gösterir.
                Metin önce tokenlara ayrılır, her token model sözlüğündeki token id’ye çevrilir ve
                attention mask ile gerçek token/padding ayrımı yapılır.<br><br>
                <b>Tokenization:</b> Metni modelin işleyebileceği küçük parçalara ayırma işlemidir.<br>
                <b>Vocabulary/Sözlük:</b> Modelin bildiği token → id eşleşmeleridir.<br>
                <b>Token ID:</b> Her token’ın sözlükteki sayısal karşılığıdır.<br>
                <b>Attention Mask:</b> 1 gerçek token, 0 padding token demektir.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="xp-report-section"><b>Tokenizer Özeti</b>', unsafe_allow_html=True)
    render_xp_table(
        ["Alan", "Değer"],
        [
            ["Tokenizer source / model path", analysis["tokenizer_source"]],
            ["Vocabulary size", analysis["vocab_size"]],
            ["Max length", analysis["max_length"]],
            ["Padding", analysis["padding"]],
            ["Truncation", analysis["truncation"]],
            ["Real token count", analysis["real_token_count"]],
            ["Padding token count", analysis["padding_token_count"]],
            ["Unknown token count", analysis["unk_token_count"]],
            ["CLS token", analysis.get("cls_token")],
            ["SEP token", analysis.get("sep_token")],
            ["PAD token", analysis.get("pad_token")],
            ["UNK token", analysis.get("unk_token")],
        ],
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="xp-report-section"><b>Token Tablosu</b>', unsafe_allow_html=True)
    if show_padding_tokens:
        st.markdown(
            '<div class="tokenizer-note">Gösterilen satırlar: gerçek tokenlar ve padding tokenları.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="tokenizer-note">Gösterilen satırlar: gerçek tokenlar. Padding tokenlarını görmek için checkbox’ı açın.</div>',
            unsafe_allow_html=True,
        )
    render_xp_table(
        ["Index", "Token", "Token ID", "Attention", "Açıklama"],
        token_rows,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_tokenizer_left_panel() -> None:
    st.markdown('<div class="xp-left-title">Tokenizer Companion</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<span class="xp-form-card-marker"></span>', unsafe_allow_html=True)
        st.markdown('<div class="xp-form-heading">Tokenization incele</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="xp-form-description">
                Bir metin girerek modelin tokenization, token id ve attention mask adımlarını inceleyebilirsiniz.
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        """
        <div class="example-box">
            <div class="example-title">Gösterilen kavramlar</div>
            <div>→ Token: Metnin küçük parçası</div>
            <div>→ Token ID: Token’ın sözlükteki sayısal karşılığı</div>
            <div>→ Vocabulary: Token → ID sözlüğü</div>
            <div>→ Attention Mask: 1 gerçek token, 0 padding</div>
            <div>→ Padding: Maksimum uzunluğu dolduran boş token</div>
            <div>→ Truncation: Çok uzun metnin kesilmesi</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def set_tokenizer_example(text: str) -> None:
    st.session_state.tokenizer_input = text
    try:
        st.session_state.tokenizer_analysis = analyze_tokenization(text)
    except Exception:
        st.session_state.tokenizer_analysis = None


def render_tokenizer_page() -> None:
    left_col, right_col = st.columns([0.88, 2.35], gap="small")

    with left_col:
        render_tokenizer_left_panel()

    with right_col:
        st.markdown('<div class="xp-page-title">Tokenizer Demo</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="xp-info-panel">
                Bu ekran, girilen metnin model tarafından nasıl sayısal girdiye çevrildiğini gösterir.
                Metin önce tokenlara ayrılır, her token model sözlüğündeki token id’ye çevrilir ve
                attention mask ile gerçek token/padding ayrımı yapılır.
            </div>
            """,
            unsafe_allow_html=True,
        )
        text = st.text_area(
            "Tokenizer metni",
            key="tokenizer_input",
            label_visibility="collapsed",
            height=72,
        )
        example_col1, example_col2, example_col3 = st.columns(3, gap="small")
        with example_col1:
            st.button(
                "Örnek: Kulaklık sorgusu",
                key="tokenizer_example_product",
                use_container_width=True,
                on_click=set_tokenizer_example,
                args=("1000 TL altı stokta olan kablosuz kulaklık öner",),
            )
        with example_col2:
            st.button(
                "Örnek: Sipariş sorgusu",
                key="tokenizer_example_order",
                use_container_width=True,
                on_click=set_tokenizer_example,
                args=("SIP-2026-0007 numaralı sipariş",),
            )
        with example_col3:
            st.button(
                "Örnek: Kupon sorgusu",
                key="tokenizer_example_coupon",
                use_container_width=True,
                on_click=set_tokenizer_example,
                args=("KARGO0 kuponu geçerli mi",),
            )

        show_padding_tokens = st.checkbox(
            "Padding tokenlarını göster",
            value=False,
            key="show_padding_tokens",
        )

        if st.button("Tokenize Et", key="tokenize_button"):
            try:
                st.session_state.tokenizer_analysis = analyze_tokenization(text)
            except Exception:
                st.session_state.tokenizer_analysis = None
                render_xp_warning("Tokenizer yüklenemedi. Model dosyalarını kontrol edin.")
                return

        if st.session_state.tokenizer_analysis is None:
            try:
                st.session_state.tokenizer_analysis = analyze_tokenization(text)
            except Exception:
                render_xp_warning("Tokenizer yüklenemedi. Model dosyalarını kontrol edin.")
                return

        render_tokenizer_analysis(st.session_state.tokenizer_analysis, show_padding_tokens)


def shorten_text(text: str, max_length: int = 240) -> str:
    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."


def format_price(value: Any, currency: str | None = None) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""

    formatted = f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formatted} {currency or 'TRY'}"


def format_feature_key(key: str) -> str:
    known_keys = {
        "renk": "Renk",
        "baglanti": "Bağlantı",
        "pil_suresi": "Pil süresi",
        "gurultu_azaltma": "Gürültü azaltma",
    }

    if key in known_keys:
        return known_keys[key]

    return key.replace("_", " ").capitalize()


def format_feature_value(value: Any) -> str:
    if isinstance(value, bool):
        return "Var" if value else "Yok"

    return str(value)


def format_features(features: Any) -> str:
    if not isinstance(features, dict) or not features:
        return ""

    formatted_features = [
        f"{format_feature_key(str(key))}: {format_feature_value(value)}"
        for key, value in features.items()
    ]
    return " · ".join(formatted_features)


def format_metadata_chips(metadata: dict[str, Any]) -> str:
    chip_values = []

    for key in ("marka", "kategori", "varyant"):
        value = metadata.get(key)
        if value:
            chip_values.append(str(value))

    stock = metadata.get("stok")
    if stock is not None:
        chip_values.append(f"Stok: {stock}")

    if not chip_values:
        return ""

    chips = "".join(f'<span class="metadata-chip">{value}</span>' for value in chip_values)
    return f'<div class="metadata-chips">{chips}</div>'


def get_product_description(metadata: dict[str, Any]) -> str:
    for key in ("aciklama", "urun_aciklama", "urun_aciklamasi", "description"):
        value = metadata.get(key)
        if value:
            return shorten_text(str(value), max_length=200)

    return ""


def render_product_result_card(result: dict[str, Any], index: int) -> None:
    metadata = result.get("metadata") or {}
    title = result.get("baslik", "Başlıksız")
    source_table = result.get("kaynak_tablo", "-")
    score = result.get("similarity_score", 0)
    currency = metadata.get("para_birimi", "TRY")
    sku = metadata.get("sku")
    sale_price = format_price(metadata.get("satis_fiyati"), currency)
    list_price = format_price(metadata.get("liste_fiyati"), currency)
    features = format_features(metadata.get("ozellikler"))
    description = get_product_description(metadata)
    metadata_chips = format_metadata_chips(metadata)

    body_parts = []
    price_lines = []

    if sale_price:
        price_lines.append(f"<div><b>Satış fiyatı:</b> {sale_price}</div>")
    if list_price:
        price_lines.append(f"<div><b>Liste fiyatı:</b> {list_price}</div>")
    if price_lines:
        body_parts.append(f'<div class="price-lines">{"".join(price_lines)}</div>')
    if features:
        body_parts.append(f'<div class="feature-line"><b>Özellikler:</b> {features}</div>')
    if description:
        body_parts.append(f'<div class="product-description"><b>Açıklama:</b> {description}</div>')

    source_text = f"Kaynak: <b>{source_table}</b>"
    if sku:
        source_text = f"{source_text} | SKU: <b>{sku}</b>"

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-card-topline">
                <div class="result-title-wrap">
                    <span class="result-icon">📄</span>
                    <span class="result-card-title">{index}. {title}</span>
                </div>
                <span class="score-badge">Skor: {score:.4f}</span>
            </div>
            <div class="result-source">{source_text}</div>
            {metadata_chips}
            {"".join(body_parts)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_generic_result_card(result: dict[str, Any], index: int) -> None:
    title = result.get("baslik", "Başlıksız")
    source_table = result.get("kaynak_tablo", "-")
    score = result.get("similarity_score", 0)
    content = shorten_text(result.get("icerik", ""), max_length=220)

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-card-topline">
                <div class="result-title-wrap">
                    <span class="result-icon">📄</span>
                    <span class="result-card-title">{index}. {title}</span>
                </div>
                <span class="score-badge">Skor: {score:.4f}</span>
            </div>
            <div class="result-source">Kaynak: <b>{source_table}</b></div>
            <div class="result-content">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_cards(results: list[dict[str, Any]]) -> None:
    if not results:
        return

    st.markdown("### Kaynak Sonuçlar")

    for index, result in enumerate(results, start=1):
        if result.get("kaynak_tablo") == "urun_varyantlari":
            render_product_result_card(result, index)
        else:
            render_generic_result_card(result, index)


def render_metadata(results: list[dict[str, Any]]) -> None:
    if not results:
        return

    with st.expander("Metadata Detayları", expanded=False):
        for index, result in enumerate(results, start=1):
            st.write(f"**{index}. {result.get('baslik')}**")
            st.json(result.get("metadata", {}))


def render_search_page() -> None:
    left_col, right_col = st.columns([0.88, 2.35], gap="small")

    with left_col:
        query, result_limit, should_search, show_debug = render_left_panel()

    if should_search:
        queue_search(query=query.strip(), limit=result_limit)

    with right_col:
        render_right_panel(show_debug)

    run_pending_search_if_needed()


def load_json_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data if isinstance(data, dict) else None


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def format_accuracy(value: Any) -> str:
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return "Yok"


def get_top_k_accuracy(summary: dict[str, Any]) -> Any:
    if "top_k_accuracy" in summary:
        return summary["top_k_accuracy"]

    for key, value in summary.items():
        if key.startswith("top_") and key.endswith("_accuracy") and key != "top_1_accuracy":
            return value

    return None


def build_metric_rows(validation: dict[str, Any] | None, test: dict[str, Any] | None) -> list[list[Any]]:
    validation = validation or {}
    test = test or {}

    return [
        ["Top-1 Accuracy", format_accuracy(validation.get("top_1_accuracy")), format_accuracy(test.get("top_1_accuracy"))],
        ["Top-5 Accuracy", format_accuracy(get_top_k_accuracy(validation)), format_accuracy(get_top_k_accuracy(test))],
        ["MRR", format_accuracy(validation.get("mrr")), format_accuracy(test.get("mrr"))],
        ["Evaluated Records", validation.get("evaluated_records", "Yok"), test.get("evaluated_records", "Yok")],
        ["Skipped Records", validation.get("skipped_records", "Yok"), test.get("skipped_records", "Yok")],
    ]


def build_source_table_rows(summaries: list[tuple[str, str, dict[str, Any] | None]]) -> list[list[Any]]:
    rows: list[list[Any]] = []

    for split, mode, summary in summaries:
        if not summary:
            continue

        source_summary = summary.get("source_table_summary") or {}
        if not isinstance(source_summary, dict):
            continue

        for source_table, metrics in source_summary.items():
            if not isinstance(metrics, dict):
                continue

            rows.append(
                [
                    split,
                    mode,
                    source_table,
                    metrics.get("total", "Yok"),
                    format_accuracy(metrics.get("top_1_accuracy")),
                    format_accuracy(get_top_k_accuracy(metrics)),
                    format_accuracy(metrics.get("mrr")),
                ]
            )

    return rows


def render_model_report_page() -> None:
    report_dir = get_project_root() / "reports" / "evaluation"
    validation_exact = load_json_file(report_dir / "validation_exact_id_summary.json")
    test_exact = load_json_file(report_dir / "test_exact_id_summary.json")
    validation_metadata = load_json_file(report_dir / "validation_metadata_summary.json")
    test_metadata = load_json_file(report_dir / "test_metadata_summary.json")
    csv_rows = load_csv_rows(report_dir / "evaluation_summary.csv")

    left_col, right_col = st.columns([0.88, 2.35], gap="small")

    with left_col:
        st.markdown('<div class="xp-left-title">Report Companion</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="example-box">
                <div class="example-title">Rapor içeriği</div>
                <div>→ Exact-id evaluation</div>
                <div>→ Metadata evaluation</div>
                <div>→ Source table başarıları</div>
                <div>→ CSV summary</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown('<div class="xp-page-title">Model Evaluation Report</div>', unsafe_allow_html=True)

        if not any([validation_exact, test_exact, validation_metadata, test_metadata, csv_rows]):
            render_xp_warning("Evaluation rapor dosyaları bulunamadı. Önce evaluation komutlarını çalıştırın.")
            return

        st.markdown(
            """
            <div class="xp-info-panel">
                <b>Exact-id evaluation:</b> Belirli kayıt hedefleyen sorgularda source_table + source_id doğru geldi mi ölçer.<br>
                <b>Metadata evaluation:</b> Fiyat, stok, kategori, marka, renk, beden ve puan gibi koşulların sağlanıp sağlanmadığını ölçer.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="xp-report-section"><b>Exact-id Evaluation</b>', unsafe_allow_html=True)
        render_xp_table(["Metric", "Validation", "Test"], build_metric_rows(validation_exact, test_exact))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="xp-report-section"><b>Metadata Evaluation</b>', unsafe_allow_html=True)
        render_xp_table(["Metric", "Validation", "Test"], build_metric_rows(validation_metadata, test_metadata))
        st.markdown("</div>", unsafe_allow_html=True)

        source_rows = build_source_table_rows(
            [
                ("validation", "exact_id", validation_exact),
                ("test", "exact_id", test_exact),
                ("validation", "metadata", validation_metadata),
                ("test", "metadata", test_metadata),
            ]
        )
        if source_rows:
            st.markdown('<div class="xp-report-section"><b>Source table bazlı başarı</b>', unsafe_allow_html=True)
            render_xp_table(
                ["Split", "Mode", "Source Table", "Total", "Top-1 Acc", "Top-5 Acc", "MRR"],
                source_rows,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        if csv_rows:
            show_csv_summary = st.checkbox(
                "Ham CSV özetini göster",
                value=False,
                key="show_raw_csv_summary",
            )
            if show_csv_summary:
                st.markdown('<div class="xp-report-section"><b>Raw CSV Summary</b>', unsafe_allow_html=True)
                headers = [
                    "split",
                    "evaluation_mode",
                    "evaluated_records",
                    "top_1_accuracy",
                    "top_k_accuracy",
                    "mrr",
                ]
                render_xp_table(
                    headers,
                    [[row.get(header, "") for header in headers] for row in csv_rows],
                )
                st.markdown("</div>", unsafe_allow_html=True)


def render_right_panel(show_debug: bool) -> None:
    render_answer(st.session_state.answer)

    if show_debug:
        render_parsed_query(st.session_state.parsed_query)
        render_result_cards(st.session_state.results)
        render_metadata(st.session_state.results)


def run_search(query: str, limit: int) -> None:
    st.session_state.query = query

    parsed_query = parse_query(query)

    with st.spinner("Rover veritabanını araştırıyor..."):
        results = semantic_search(query, limit=limit)

    answer = generate_answer(
        query=query,
        results=results,
        parsed_query=parsed_query,
    )

    st.session_state.parsed_query = parsed_query
    st.session_state.results = results
    st.session_state.answer = answer
    st.session_state.rover_state = "result" if results else "not_found"
    st.session_state.search_in_progress = False
    st.session_state.pending_query = ""
    st.session_state.pending_limit = 5


def run_pending_search_if_needed() -> None:
    if not st.session_state.search_in_progress:
        return

    query = st.session_state.pending_query
    limit = st.session_state.pending_limit

    if not query:
        st.session_state.search_in_progress = False
        st.session_state.rover_state = "idle"
        return

    run_search(query=query, limit=limit)
    st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="E-Ticaret Rover Asistanı",
        page_icon="🔎",
        layout="wide",
    )

    inject_css()
    init_session_state()

    render_xp_header()
    render_toolbar()
    render_addressbar()

    active_page = st.session_state.active_page
    if active_page == "tokenizer":
        render_tokenizer_page()
    elif active_page == "model_report":
        render_model_report_page()
    else:
        render_search_page()


if __name__ == "__main__":
    main()
