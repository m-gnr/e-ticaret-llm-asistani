from pathlib import Path
from typing import Any
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.app.answer_generator import generate_answer
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
                flex: 0 0 312px !important;
                flex-basis: 312px !important;
                flex-grow: 0 !important;
                flex-shrink: 0 !important;
                width: 312px !important;
                min-width: 310px !important;
                max-width: 330px !important;
                background: #7ca7e8;
                border-right: 2px solid #9eaac0;
                padding: 0 14px 18px 14px;
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

            .xp-menubar {
                background: #ece9d8;
                border-bottom: 1px solid #b8b4a8;
                padding: 6px 12px;
                font-size: 15px;
                color: #222;
                word-spacing: 20px;
            }

            .xp-toolbar {
                background: #f4f1e6;
                border-bottom: 1px solid #c8c2b4;
                padding: 9px 12px;
                display: flex;
                gap: 22px;
                align-items: center;
                font-size: 15px;
            }

            .xp-toolbar-item {
                padding: 6px 10px;
                border: 1px solid transparent;
            }

            .xp-toolbar-item.active {
                border: 1px solid #9aa7c2;
                background: #eef3ff;
                box-shadow: inset 1px 1px white;
            }

            .xp-addressbar {
                background: #ece9d8;
                border-bottom: 1px solid #c8c2b4;
                padding: 7px 12px;
                display: flex;
                gap: 8px;
                align-items: center;
                font-size: 14px;
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
                background: #d7e4ff;
                border-bottom: 1px solid #9db5e9;
                padding: 9px 10px;
                margin: 0 -14px 18px -14px;
                box-shadow: inset 1px 1px white;
            }

            .speech-bubble {
                background: #f7f7f7;
                color: #222;
                border-radius: 12px;
                border: 1px solid #c7c7c7;
                padding: 18px;
                box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.15);
                position: relative;
                margin-bottom: 18px;
            }

            .speech-bubble:after {
                content: "";
                position: absolute;
                bottom: -26px;
                left: 42px;
                border-width: 26px 12px 0 0;
                border-style: solid;
                border-color: #f7f7f7 transparent transparent transparent;
            }

            .bubble-title {
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 10px;
            }

            .bubble-text {
                font-size: 14px;
                margin-bottom: 4px;
                color: #333;
                line-height: 1.45;
            }

            .example-box {
                background: #eaf2ff;
                border: 1px solid #9db5e9;
                padding: 9px 10px;
                margin-top: 12px;
                font-size: 13px;
                line-height: 1.6;
                color: #1a2f55;
                box-shadow: inset 1px 1px white;
            }

            .example-title {
                font-weight: bold;
                margin-bottom: 8px;
                color: #1f3763;
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
                background: #f7faff;
                padding: 13px 15px;
                margin-bottom: 12px;
                box-shadow: 2px 2px 0 rgba(0,0,0,0.08);
            }

            .result-card-title {
                font-weight: bold;
                color: #003c9e;
                font-size: 16px;
                margin-bottom: 6px;
            }

            .result-meta {
                color: #333;
                font-size: 13px;
                margin-bottom: 8px;
            }

            .result-content {
                color: #444;
                font-size: 13px;
                line-height: 1.4;
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
                margin-top: 4px;
            }

            .stExpander {
                border: 1px solid #b8c7e6 !important;
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
        "query": "",
        "results": [],
        "parsed_query": None,
        "answer": "",
        "rover_state": "idle",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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
            <div class="xp-menubar">
                File Edit View Favorites Tools Help
            </div>
            <div class="xp-toolbar">
                <span class="xp-toolbar-item">← Back</span>
                <span class="xp-toolbar-item">→ Forward</span>
                <span class="xp-toolbar-item active">🔍 Search</span>
                <span class="xp-toolbar-item">📁 Folders</span>
            </div>
            <div class="xp-addressbar">
                <span>Address</span>
                <div class="xp-address-input">Search Results</div>
                <div class="xp-go-button">Go</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_left_panel() -> tuple[str, int, bool, bool]:
    rover_state = st.session_state.rover_state
    parsed_query = st.session_state.parsed_query
    intent = parsed_query.intent if parsed_query else None

    rover_message = get_rover_message(rover_state, intent)
    rover_image = get_rover_image(rover_state)

    st.markdown('<div class="xp-left-title">Search Companion</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="speech-bubble">
            <div class="bubble-title">Ne aramamı istersin?</div>
            <div class="bubble-text">{rover_message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Sorgu",
        value=st.session_state.query,
        placeholder="Örn: stokta kulaklık öner",
        label_visibility="collapsed",
    )

    result_limit = st.selectbox("Sonuç sayısı", options=[3, 5, 10], index=1)
    show_debug = st.checkbox("Teknik detayları göster", value=True)
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

    html_answer = answer.replace("\n", "<br>")
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

        with col2:
            st.write("**Max fiyat:**", parsed_query.max_price)
            st.write("**Min fiyat:**", parsed_query.min_price)
            st.write("**Min puan:**", parsed_query.min_rating)

        with col3:
            st.write("**Stokta:**", parsed_query.in_stock_only)
            st.write("**Stokta olmayan:**", parsed_query.out_of_stock_only)
            st.write("**Durum:**", parsed_query.status)

        st.write("**Arama metni:**", parsed_query.search_text)
        st.write("**Kaynak tablolar:**", parsed_query.source_tables)


def shorten_text(text: str, max_length: int = 360) -> str:
    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."


def render_result_cards(results: list[dict[str, Any]]) -> None:
    if not results:
        return

    st.markdown("### Kaynak Sonuçlar")

    for index, result in enumerate(results, start=1):
        title = result.get("baslik", "Başlıksız")
        source_table = result.get("kaynak_tablo", "-")
        score = result.get("similarity_score", 0)
        content = shorten_text(result.get("icerik", ""))

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-card-title">{index}. {title}</div>
                <div class="result-meta">
                    Kaynak tablo: <b>{source_table}</b> |
                    Benzerlik skoru: <b>{score:.4f}</b>
                </div>
                <div class="result-content">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metadata(results: list[dict[str, Any]]) -> None:
    if not results:
        return

    with st.expander("Metadata Detayları", expanded=False):
        for index, result in enumerate(results, start=1):
            st.write(f"**{index}. {result.get('baslik')}**")
            st.json(result.get("metadata", {}))


def render_right_panel(show_debug: bool) -> None:
    render_answer(st.session_state.answer)

    if show_debug:
        render_parsed_query(st.session_state.parsed_query)
        render_result_cards(st.session_state.results)
        render_metadata(st.session_state.results)


def run_search(query: str, limit: int) -> None:
    st.session_state.query = query
    st.session_state.rover_state = "searching"

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


def main() -> None:
    st.set_page_config(
        page_title="E-Ticaret Rover Asistanı",
        page_icon="🔎",
        layout="wide",
    )

    inject_css()
    init_session_state()

    render_xp_header()

    left_col, right_col = st.columns([0.88, 2.35], gap="small")

    with left_col:
        query, result_limit, should_search, show_debug = render_left_panel()

    if should_search:
        run_search(query=query.strip(), limit=result_limit)

    with right_col:
        render_right_panel(show_debug)


if __name__ == "__main__":
    main()
