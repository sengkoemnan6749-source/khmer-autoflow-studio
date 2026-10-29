import streamlit as st
import io
import re
import zipfile
import json
import os
from google import genai

# Check for gTTS (Khmer Audio Engine)
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

@st.cache_data(show_spinner=False)
def get_khmer_audio_cached(text: str) -> bytes:
    if not HAS_GTTS or not text:
        return b""
    try:
        tts = gTTS(text=text, lang='km')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except Exception:
        return b""


# ----------------- 💾 CONFIG PROFILE PERSISTENCE HELPERS -----------------

API_KEY_FILE = ".api_key.txt"

def get_saved_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if os.path.exists(API_KEY_FILE):
        try:
            with open(API_KEY_FILE, "r", encoding="utf-8") as f:
                k = f.read().strip()
                if k:
                    return k
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY", "")

def save_api_key(key_str):
    if key_str and len(key_str.strip()) > 5:
        try:
            with open(API_KEY_FILE, "w", encoding="utf-8") as f:
                f.write(key_str.strip())
        except Exception:
            pass
    elif key_str == "":
        try:
            if os.path.exists(API_KEY_FILE):
                os.remove(API_KEY_FILE)
        except Exception:
            pass

CONFIG_FILE = "saved_configs.json"

def get_default_configs():
    return {
        "🌟 Default Duo (Sima & Rex)": {
            "num_characters": 2,
            "characters": [
                {"tag": "@sima", "gender": "👩 មនុស្សស្រី (Female)", "dna": "young Southeast Asian woman, neat high hair bun, white crop top", "voice": "Aoede (ស្រីស្រទន់)"},
                {"tag": "@rex", "gender": "👩 មនុស្សស្រី (Female)", "dna": "young beautiful woman, long straight natural black hair, center-parted, light blue buttoned collared dress shirt", "voice": "Kore (ស្រីរស់រវើក)"}
            ]
        },
        "✨ 4 Characters Squad (Bioaqua Teasing)": {
            "num_characters": 4,
            "characters": [
                {"tag": "@sima", "gender": "👩 មនុស្សស្រី (Female)", "dna": "young Southeast Asian woman, neat high hair bun, white crop top", "voice": "Aoede (ស្រីស្រទន់)"},
                {"tag": "@rex", "gender": "👩 មនុស្សស្រី (Female)", "dna": "young beautiful woman, long straight natural black hair, center-parted, light blue buttoned collared dress shirt", "voice": "Kore (ស្រីរស់រវើក)"},
                {"tag": "@bopha", "gender": "👩 មនុស្សស្រី (Female)", "dna": "cheerful young Cambodian woman with twin braids, wearing a pastel yellow t-shirt and light blue jeans", "voice": "Leda (ស្រីចាស់ទុំ)"},
                {"tag": "@dara", "gender": "👨 មនុស្សប្រុស (Male)", "dna": "handsome young Cambodian man with trendy short wavy black hair, wearing an open denim jacket over a white tee", "voice": "Alnilam (ប្រុសស្វាហាប់)"}
            ]
        }
    }

def load_saved_configs():
    configs = get_default_configs()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                configs.update(saved)
        except Exception:
            pass
    return configs

def save_config_profile(name, data):
    configs = load_saved_configs()
    configs[name] = data
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Khmer AI Studio Pro | Custom Characters & Gender Lock",
    page_icon="e:/Ai/app_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- MODERN STREAMLINED STYLING (AUTOFLOW CUTE CRIMSON THEME) -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', 'Kantumruy Pro', sans-serif; }
    
    /* Background & App */
    .stApp { 
        background: radial-gradient(circle at 50% 0%, #1e0711 0%, #0d0307 100%) !important;
        color: #fce7f3 !important; 
    }
    
    /* AutoFlow Header Banner */
    .autoflow-card {
        background: linear-gradient(180deg, #1d0912 0%, #14050c 100%);
        border: 1px solid rgba(225, 29, 72, 0.28);
        border-radius: 18px;
        padding: 16px 20px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45);
        margin-bottom: 12px;
    }
    
    /* Status Bar Pill */
    .status-bar-pill {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #14050c;
        border: 1px solid rgba(225, 29, 72, 0.22);
        border-radius: 20px;
        padding: 7px 16px;
        font-size: 13px;
        font-weight: 600;
        color: #fecdd3;
        margin-bottom: 14px;
    }
    .status-dot {
        width: 9px;
        height: 9px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 10px #22c55e, 0 0 4px #22c55e;
    }
    
    /* Pill Tabs (like Control / Settings / Logs in AutoFlow) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #14050c !important;
        border: 1px solid rgba(225, 29, 72, 0.25) !important;
        border-radius: 35px !important;
        padding: 5px !important;
        gap: 6px !important;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.5) !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 26px !important;
        padding: 8px 22px !important;
        color: #fda4af !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.22s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(225, 29, 72, 0.5) !important;
    }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }
    
    /* Cute Cards & Panels */
    .panel-card {
        background: #17070f;
        border: 1px solid rgba(225, 29, 72, 0.22);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
    .panel-header {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #fb7185;
        margin-bottom: 10px;
    }
    
    .char-card {
        background: #190812;
        border: 1px solid rgba(225, 29, 72, 0.24);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }
    
    .scene-box {
        background: #17070f;
        border: 1px solid rgba(225, 29, 72, 0.22);
        border-left: 4px solid #e11d48;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    /* Cute Main Action Button (Glow Crimson Pill) */
    .stButton>button {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
        color: white !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        border-radius: 26px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 18px rgba(225, 29, 72, 0.45) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(244, 63, 94, 0.6) !important;
    }
    .stButton>button:active {
        transform: translateY(1px) !important;
    }
    
    /* Preset Buttons - Cute Dark Wine Pill */
    div[data-testid="column"] .stButton>button {
        background: #230b15 !important;
        color: #fecdd3 !important;
        border: 1px solid #4a1524 !important;
        border-radius: 22px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        padding: 8px 14px !important;
    }
    div[data-testid="column"] .stButton>button:hover {
        background: #340f1f !important;
        border-color: #e11d48 !important;
        color: #ffffff !important;
        box-shadow: 0 0 14px rgba(225, 29, 72, 0.4) !important;
    }
    
    /* Inputs, Selectboxes & Textareas (Dark sleek crimson) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background-color: #120409 !important;
        border: 1px solid #3d1220 !important;
        border-radius: 12px !important;
        color: #fce7f3 !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #e11d48 !important;
        box-shadow: 0 0 12px rgba(225, 29, 72, 0.45) !important;
    }
    
    /* Cute Download Button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #200814 0%, #2e0c1d 100%) !important;
        border: 1px solid #e11d48 !important;
        color: #fecdd3 !important;
        border-radius: 24px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.3) !important;
    }
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 6px 20px rgba(225, 29, 72, 0.5) !important;
    }

    /* Clean Container Border Wrapper */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background: #17070f !important;
        border: 1px solid rgba(225, 29, 72, 0.22) !important;
        border-radius: 16px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
    }

</style>
""", unsafe_allow_html=True)

# ----------------- TOP AUTOFLOW HEADER BAR -----------------
st.markdown("""
<div class="autoflow-card">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div style="display:flex; align-items:center; gap:16px;">
            <img src="data:image/png;base64,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" alt="Khmer Auto-Flow Studio Logo" style="height:62px; filter: drop-shadow(0 4px 14px rgba(225,29,72,0.45));" />
            <div style="border-left:1px solid rgba(225,29,72,0.3); padding-left:14px; display:flex; flex-direction:column; justify-content:center;">
                <div style="color:#fff; font-size:13px; font-weight:700; display:flex; align-items:center; gap:6px;">
                    AI Drama & Storyboard Engine <span style="background:#be123c; color:#fff; font-size:10px; padding:2px 7px; border-radius:10px; font-weight:800;">PRO</span>
                </div>
                <div style="color:#fda4af; font-size:12px; margin-top:2px;">Auto batch videos, 100% character locked on Google Flow & Veo.</div>
            </div>
        </div>
        <div style="display:flex; gap:8px;">
            <a href="https://flow.google.com" target="_blank" style="text-decoration:none;">
                <div style="background:#200814; border:1px solid #4a1524; color:#fecdd3; padding:7px 16px; border-radius:20px; font-size:12px; font-weight:600; display:flex; align-items:center; gap:6px;">
                    🌐 Open Google Flow
                </div>
            </a>
            <a href="https://t.me/tha_nann" target="_blank" style="text-decoration:none;">
                <div style="background:linear-gradient(135deg, #0088cc, #005f8f); color:white; padding:7px 16px; border-radius:20px; font-size:12px; font-weight:700; display:flex; align-items:center; gap:6px; box-shadow:0 2px 12px rgba(0,136,204,0.45); border:1px solid rgba(255,255,255,0.2);">
                    ✈️ Telegram @tha_nann
                </div>
            </a>
        </div>
    </div>
</div>

<div class="status-bar-pill">
    <div class="status-dot"></div>
    <span>Connected to Google Flow & AWS AutoFlow Extension Ready</span>
</div>
""", unsafe_allow_html=True)

# Load & persist Gemini API Key
saved_key_init = get_saved_api_key()
if "user_api_key" not in st.session_state:
    st.session_state["user_api_key"] = saved_key_init

col_api_dummy, col_api = st.columns([1.5, 1.5])
with col_api_dummy:
    if st.session_state.get("user_api_key"):
        st.markdown("""
        <div style="display:flex; align-items:center; gap:8px; font-size:12.5px; color:#22c55e; padding-top:7px; font-weight:600;">
            <span style="display:inline-block; width:8px; height:8px; background:#22c55e; border-radius:50%; box-shadow:0 0 8px #22c55e;"></span>
            <span>🔒 Gemini API Key Saved (Auto-restores on Refresh)</span>
        </div>
        """, unsafe_allow_html=True)

with col_api:
    api_key_input = st.text_input(
        "🔑 Gemini API Key:", 
        value=st.session_state.get("user_api_key", ""), 
        type="password", 
        placeholder="Paste Gemini API Key (Auto-saved)...", 
        label_visibility="collapsed",
        key="input_gemini_api_key"
    )
    if api_key_input != st.session_state.get("user_api_key", ""):
        st.session_state["user_api_key"] = api_key_input
        save_api_key(api_key_input)
        st.rerun()

api_key = st.session_state.get("user_api_key", "")

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ----------------- STUDIO WORKSPACE TABS (CUTE PILL CONTROLS) -----------------
tab_create, tab_doctor, tab_reroll, tab_srt = st.tabs([
    "🚀 Story Creator", 
    "🩺 Prompt Doctor", 
    "🔄 Scene Fixer",
    "📥 CapCut SRT"
])


# ----------------- 🗣️ ROBUST DIALOGUE / SCRIPT EXTRACTOR -----------------
def extract_dialogue(scene_content, story_input, scene_idx):
    if not scene_content:
        scene_content = ""
    # 1. Match standard speech patterns: says, dialogue, voiceover
    m1 = re.search(r'(?:says|dialogue|voiceover|audio|track)[^"«“]*["“«]([^"”»]+)["”»]', scene_content, re.IGNORECASE)
    if m1 and any('ក' <= c <= '៿' for c in m1.group(1)):
        return m1.group(1).strip()

    # 2. Match any Khmer text in quotes inside the scene prompt
    m2 = re.search(r'["“«]([ក-៿\s\d\.,!?៖\(\)]+)["”»]', scene_content)
    if m2 and len(m2.group(1).strip()) > 3:
        return m2.group(1).strip()

    # 3. Fallback: Extract directly from the user pasted story for scene_idx
    if story_input:
        chunks = re.split(r'ឈុតទី\s*\d+[\s៖:]*', story_input)
        scene_chunks = [c.strip() for c in chunks if c.strip()]
        if scene_chunks and scene_idx <= len(scene_chunks):
            chunk = scene_chunks[scene_idx - 1]
            q_m = re.search(r'["“«]([^"”»]+)["”»]', chunk)
            if q_m:
                return q_m.group(1).strip()
            lines = [l.strip() for l in chunk.splitlines() if l.strip()]
            if lines:
                return lines[0][:120]

    return None

# ----------------- 🎯 INTELLIGENT STORY ATTRIBUTE DETECTOR -----------------
def detect_story_attributes(story_text):
    text_lower = story_text.lower()
    km_digits = {'០':'0', '១':'1', '២':'2', '៣':'3', '៤':'4', '៥':'5', '៦':'6', '៧':'7', '៨':'8', '៩':'9'}

    # 1. Detect scenes count (support 6, 12, 18 scenes / 1, 2, 3 min)
    is_18_scenes = bool(re.search(r"(?:18|១៨)\s*(?:ឈុត|scene|scenes|sence|sences|clip|clips|វគ្គ)", story_text, re.IGNORECASE))
    is_3_min = bool(re.search(r"(?:3|៣)\s*(?:នាទី|min|minute|minutes)", story_text, re.IGNORECASE))
    is_12_scenes = bool(re.search(r"(?:12|១២)\s*(?:ឈុត|scene|scenes|sence|sences|clip|clips|វគ្គ)", story_text, re.IGNORECASE))
    is_2_min = bool(re.search(r"(?:2|២)\s*(?:នាទី|min|minute|minutes)", story_text, re.IGNORECASE))

    # Match all scene markers: ឈុតទី 1-18, ឈុត 1-18, ឈុត1-18, ឈុតទី១-១៨, ឈុត១-១៨, scene 1-18, sence 1-18, #scene 1-18
    pattern = r"(?:ឈុតទី|ឈុត|#scene|scene|sence|clip)\s*([0-9\u17e0-\u17e9]+)"
    raw_matches = re.findall(pattern, story_text, re.IGNORECASE)

    scene_nums = []
    for rm in raw_matches:
        norm = "".join(km_digits.get(ch, ch) for ch in rm)
        try:
            val = int(norm)
            if 1 <= val <= 100:
                scene_nums.append(val)
        except ValueError:
            pass

    max_scene = max(scene_nums) if scene_nums else 0
    unique_scenes_count = len(set(scene_nums)) if scene_nums else 0
    fallback_scene_count = len(re.findall(r"(?:ឈុតទី|ឈុត|#scene|scene|sence)", story_text, re.IGNORECASE))

    if is_3_min or is_18_scenes or max_scene >= 13 or unique_scenes_count >= 13 or fallback_scene_count >= 13:
        dur_val = 3      # 3 minutes = 18 clips
        dur_idx = 2
        detected_scenes = 18
    elif is_12_scenes or is_2_min or max_scene >= 7 or unique_scenes_count >= 7 or fallback_scene_count >= 7:
        dur_val = 2      # 2 minutes = 12 clips
        dur_idx = 1
        detected_scenes = 12
    elif max_scene >= 1 or unique_scenes_count >= 1 or fallback_scene_count >= 1:
        dur_val = 1      # 1 minute = 6 clips
        dur_idx = 0
        detected_scenes = 6
    else:
        dur_val = 1
        dur_idx = 0
        detected_scenes = 6

    # 2. Detect character count (2, 3, 4, or 5)
    num_chars = None
    if re.search(r"(?:តួអង្គទាំង\s*[៥5]|ទាំង\s*[៥5]|ប្រាំនាក់|[៥5]\s*នាក់)", story_text):
        num_chars = 5
    elif re.search(r"(?:តួអង្គទាំង\s*[៤4]|ទាំង\s*[៤4]|បួននាក់|[៤4]\s*នាក់)", story_text):
        num_chars = 4
    elif re.search(r"(?:តួអង្គទាំង\s*[៣3]|ទាំង\s*[៣3]|បីនាក់|[៣3]\s*នាក់)", story_text):
        num_chars = 3
    elif re.search(r"(?:តួអង្គទាំង\s*(?:ពីរ|[២2])|ទាំង\s*(?:ពីរ|[២2])|ពីរនាក់|[២2]\s*នាក់)", story_text):
        num_chars = 2

    if num_chars is None:
        known_names = ["សីម៉ា", "រ៉ិច", "អាណា", "លីសា", "តុលា", "សុផា", "បុប្ផា", "ដារ៉ា", "វីរៈ", "សុខា"]
        found_names = [n for n in known_names if n in story_text]
        if len(found_names) >= 2:
            num_chars = min(5, max(2, len(found_names)))
        else:
            num_chars = 2 # default duo when 2 or fewer names

    # 3. Detect location preset index
    loc_idx = 0
    if any(k in story_text for k in ["កញ្ចក់", "ឆ្លុះ", "បន្ទប់គេង", "mirror"]):
        loc_idx = 0 # Bedroom & vanity mirror
    elif any(k in story_text for k in ["តង់", "បោះតង់", "ព្រៃស្រល់", "campsite", "ព្រៃ"]):
        loc_idx = 1 # Campsite
    elif any(k in story_text for k in ["កំពត", "បូកគោ", "មាត់ព្រែក"]):
        loc_idx = 2 # Kampot
    elif any(k in story_text for k in ["ហ្គេម", "rank", "កុំព្យូទ័រ"]):
        loc_idx = 3 # Gaming room
    elif any(k in story_text for k in ["ផ្ទះឈើ", "បុរាណ", "ខ្មោច"]):
        loc_idx = 4 # Wooden house
    elif any(k in story_text for k in ["អង្គរ", "ប្រាសាទ"]):
        loc_idx = 5 # Angkor
    elif any(k in story_text for k in ["កាហ្វេ", "cafe", "ហាង"]):
        loc_idx = 6 # Cafe
    elif any(k in story_text for k in ["សមុទ្រ", "ឆ្នេរ", "beach"]):
        loc_idx = 7 # Beach

    # 4. Detect prop preset index
    prop_idx = 0
    if any(k in text_lower for k in ["bioaqua", "ម៉ាស់", "mask"]):
        prop_idx = 5 # Bioaqua mask
    elif any(k in story_text for k in ["ស្កូតឺ", "អាសង់", "scooter"]):
        prop_idx = 1 # Scooter
    elif any(k in text_lower for k in ["sport", "superbike", "ម៉ូតូធំ"]):
        prop_idx = 2 # Superbike
    elif any(k in story_text for k in ["កង់", "bicycle"]):
        prop_idx = 3 # Bicycle
    elif any(k in text_lower for k in ["ឡាន", "suv"]):
        prop_idx = 4 # SUV
    elif any(k in story_text for k in ["តង់", "ពិល"]):
        prop_idx = 0 # Tent & flashlight

    return {
        "num_chars": num_chars,
        "detected_scenes": detected_scenes,
        "dur_val": dur_val,
        "dur_idx": dur_idx,
        "loc_idx": loc_idx,
        "prop_idx": prop_idx
    }

# ================= TAB 1: STORY CREATOR =================
with tab_create:
    st.markdown("### ✍️ ជំហានទី ១៖ ជ្រើសរើសប្រធានបទរឿង (Quick Presets)")
    
    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    preset_choice = None
    with c_p1:
        if st.button("🎮 អូស Rank ធ្លាក់ផ្កាយ & ម៉ាស់", key="p1"):
            preset_choice = "តួអង្គទាំងពីរអូស Rank យប់ជ្រៅធ្លាក់ផ្កាយ ត្រូវគេព្រូតវៃទក់សាច់ មុខបាក់ រួចនាំគ្នាទៅបិទម៉ាស់ Bioaqua ឱ្យស្អាតវិញ"
    with c_p2:
        if st.button("🏕️ ជិះម៉ូតូទៅបោះតង់ក្នុងព្រៃ", key="p2"):
            preset_choice = "តួអង្គសុំម៉ែដើរលេង ម៉ែស្តីឱ្យតែអង្វរទាល់តែបានទៅ រៀបចំកាតាបជិះទៅយកមិត្តភក្តិ ជិះកាត់ផ្លូវជួបរឿងកំប្លែង ឈប់ញ៉ាំអី និងទៅដល់គោលដៅបញ្ចប់ទៅមានន័យ"
    with c_p3:
        if st.button("👻 ខ្មោចលងក្នុងផ្ទះបុរាណ", key="p3"):
            preset_choice = "តួអង្គទាំងពីរជិះកង់ទៅលេងផ្ទះឈើបុរាណមួយ ស្រាប់តែមានរឿងចម្លែកៗកើតឡើងយ៉ាងកំប្លែង"
    with c_p4:
        if st.button("🏛️ ដំណើរផ្សងព្រេងមហានគរ", key="p4"):
            preset_choice = "ក្រុមអ្នកក្លាហានបានរកឃើញខ្លោងទ្វារអាថ៌កំបាំងដែលនាំទៅកាន់សម័យមហានគរដ៏រុងរឿង"

    default_story = preset_choice if preset_choice else "តួអង្គទាំងពីរបោះតង់ក្នុងព្រៃពេលយប់..."
    story_input = st.text_area("សរសេរគំនិតសាច់រឿងរបស់អ្នក (ឬចុចប៊ូតុងខាងលើ):", value=default_story, height=80)

    # ----------------- 🎯 SMART STORY AUTO-SYNC -----------------
    detected = detect_story_attributes(story_input)
    last_story = st.session_state.get('last_analyzed_story_text', None)
    if last_story != story_input:
        st.session_state['last_analyzed_story_text'] = story_input
        st.session_state['sel_duration_min'] = detected['dur_val']
        st.session_state['num_c_select'] = detected['num_chars']
        st.session_state['num_characters_val'] = detected['num_chars']
        st.session_state['detected_dur_idx'] = detected['dur_idx']
        st.session_state['detected_dur_val'] = detected['dur_val']
        st.session_state['detected_loc_idx'] = detected['loc_idx']
        st.session_state['detected_prop_idx'] = detected['prop_idx']
        st.rerun()

    dur_disp = f"{detected['dur_val']} នាទី ({detected['detected_scenes']} ឈុត)" 
    st.markdown(f"""
    <div style="background:linear-gradient(90deg, rgba(225,29,72,0.18) 0%, rgba(20,5,12,0.4) 100%); border:1px solid rgba(225,29,72,0.35); border-radius:12px; padding:9px 16px; margin-top:6px; margin-bottom:12px; font-size:13px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">
        <span style="color:#fecdd3; display:flex; align-items:center; gap:8px;">
            🎯 <b>Smart Story Detection:</b> រកឃើញ <b>{detected['num_chars']} តួអង្គ</b> | <b>{dur_disp}</b>
        </span>
        <span style="background:#22c55e; color:#fff; font-size:11px; padding:2px 10px; border-radius:12px; font-weight:700; box-shadow:0 0 8px rgba(34,197,94,0.4);">
            ✅ AUTO-APPLIED SETTINGS
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ----------------- ⚙️ CONFIG & PROFILE MANAGER (SAVE & LOAD) -----------------
    with st.expander("💾 រក្សាទុក & គ្រប់គ្រងការកំណត់ Preset Profiles (Save & Load Config)", expanded=False):
        all_configs = load_saved_configs()
        c_cfg_load, c_cfg_save = st.columns(2)
        with c_cfg_load:
            st.markdown("##### ⚡ ទាញយកការកំណត់មកប្រើ (Load Profile)")
            selected_prof_name = st.selectbox("ជ្រើសរើស Profile ដែលបានរក្សាទុក:", list(all_configs.keys()), key="sel_prof_name")
            c_btn_l1, c_btn_l2 = st.columns([1, 1.2])
            with c_btn_l1:
                if st.button("⚡ Apply Profile", key="btn_apply_prof"):
                    target_p = all_configs[selected_prof_name]
                    target_chars = target_p.get("characters", [])
                    st.session_state["num_characters_val"] = target_p.get("num_characters", len(target_chars))
                    for ci, tc in enumerate(target_chars):
                        st.session_state[f"sq_tag_{ci}"] = tc.get("tag", f"@char{ci+1}")
                        st.session_state[f"sq_gen_{ci}"] = tc.get("gender", "👩 មនុស្សស្រី (Female)")
                        st.session_state[f"sq_dna_{ci}"] = tc.get("dna", "")
                        st.session_state[f"sq_voc_{ci}"] = tc.get("voice", "Aoede").split(" ")[0]
                    st.success(f"✅ បានទាញយក Profile '{selected_prof_name}' រួចរាល់!")
                    st.rerun()
            with c_btn_l2:
                uploaded_cfg = st.file_uploader("📤 Import .json:", type=["json"], key="up_cfg", label_visibility="collapsed")
                if uploaded_cfg is not None:
                    try:
                        imported_data = json.loads(uploaded_cfg.read().decode("utf-8"))
                        for k, v in imported_data.items():
                            save_config_profile(k, v)
                        st.success("✅ បាន Import ជោគជ័យ!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        with c_cfg_save:
            st.markdown("##### 💾 រក្សាទុកការកំណត់បច្ចុប្បន្ន (Save Profile)")
            new_p_name = st.text_input("ឈ្មោះ Profile ថ្មី (ឧ. My 4 Girls Drama):", key="new_prof_input", placeholder="វាយឈ្មោះ Profile...")
            c_btn_s1, c_btn_s2 = st.columns([1, 1.2])
            with c_btn_s1:
                if st.button("💾 Save Profile", key="btn_save_prof"):
                    if new_p_name.strip():
                        curr_num_c = st.session_state.get("num_characters_val", 4)
                        saved_chars = []
                        for ci in range(curr_num_c):
                            saved_chars.append({
                                "tag": st.session_state.get(f"sq_tag_{ci}", DEFAULT_CHARS[ci]["tag"] if ci < len(DEFAULT_CHARS) else f"@char{ci+1}"),
                                "gender": st.session_state.get(f"sq_gen_{ci}", DEFAULT_CHARS[ci]["gender"] if ci < len(DEFAULT_CHARS) else "👩 មនុស្សស្រី (Female)"),
                                "dna": st.session_state.get(f"sq_dna_{ci}", DEFAULT_CHARS[ci]["dna"] if ci < len(DEFAULT_CHARS) else ""),
                                "voice": st.session_state.get(f"sq_voc_{ci}", DEFAULT_CHARS[ci]["voice"] if ci < len(DEFAULT_CHARS) else "Aoede")
                            })
                        save_config_profile(new_p_name.strip(), {
                            "num_characters": curr_num_c,
                            "characters": saved_chars
                        })
                        st.success(f"✅ បានរក្សាទុក '{new_p_name.strip()}' ជោគជ័យ!")
                        st.rerun()
                    else:
                        st.warning("⚠️ សូមវាយឈ្មោះ Profile ជាមុនសិន!")
            with c_btn_s2:
                st.download_button(
                    label="📥 Export Configs (.json)",
                    data=json.dumps(all_configs, ensure_ascii=False, indent=2),
                    file_name="autoflow_saved_configs.json",
                    mime="application/json",
                    key="dl_configs"
                )

    # ----------------- 👥 CUSTOM CHARACTER & GENDER SETUP (UP TO 4+ CHARACTERS) -----------------
    col_hdr, col_num_c = st.columns([2, 1])
    with col_hdr:
        st.markdown("#### 👥 កំណត់ក្រុមតួអង្គ ឈ្មោះ ភេទ និងសំឡេង (Character Squad Studio)")
    with col_num_c:
        current_num_c = st.session_state.get("num_characters_val", detected["num_chars"])
        c_opts = [2, 3, 4, 5]
        def_c_idx = c_opts.index(current_num_c) if current_num_c in c_opts else 0
        num_characters = st.selectbox("👥 ចំនួនតួអង្គក្នុងរឿង (Squad Size):", c_opts, index=def_c_idx, format_func=lambda x: f"{x} តួអង្គ ({x} Characters)", key="num_c_select")
        st.session_state["num_characters_val"] = num_characters

    DEFAULT_CHARS = [
        {"tag": "@sima", "gender": "👩 មនុស្សស្រី (Female)", "dna": "young Southeast Asian woman, neat high hair bun, white crop top", "voice": "Aoede (ស្រីស្រទន់)"},
        {"tag": "@rex", "gender": "👩 មនុស្សស្រី (Female)", "dna": "young beautiful woman, long straight natural black hair, center-parted, light blue buttoned collared dress shirt", "voice": "Kore (ស្រីរស់រវើក)"},
        {"tag": "@bopha", "gender": "👩 មនុស្សស្រី (Female)", "dna": "cheerful young Cambodian woman with twin braids, wearing a pastel yellow t-shirt and light blue jeans", "voice": "Leda (ស្រីចាស់ទុំ)"},
        {"tag": "@dara", "gender": "👨 មនុស្សប្រុស (Male)", "dna": "handsome young Cambodian man with trendy short wavy black hair, wearing an open denim jacket over a white tee", "voice": "Alnilam (ប្រុសស្វាហាប់)"},
        {"tag": "@mom", "gender": "👩 មនុស្សស្រី (Female)", "dna": "caring Cambodian middle-aged mother wearing a traditional floral Khmer blouse", "voice": "Leda (ស្រីចាស់ទុំ)"}
    ]

    chars_data = []
    for row_start in range(0, num_characters, 2):
        row_cols = st.columns(2)
        for i in range(2):
            c_idx = row_start + i
            if c_idx < num_characters:
                with row_cols[i]:
                    preset = DEFAULT_CHARS[c_idx] if c_idx < len(DEFAULT_CHARS) else {"tag": f"@char{c_idx+1}", "gender": "👩 មនុស្សស្រី (Female)", "dna": "young Asian character", "voice": "Aoede (ស្រីស្រទន់)"}
                    with st.container(border=True):
                        st.markdown(f"**👤 តួអង្គទី {c_idx+1} (Character {c_idx+1})**")
                        sub1, sub2 = st.columns(2)
                        with sub1:
                            c_tag = st.text_input(f"Tag ឈ្មោះ (ឧ. {preset['tag']}):", value=preset['tag'], key=f"sq_tag_{c_idx}")
                        with sub2:
                            c_gender = st.selectbox(f"ភេទ (Gender) {c_idx+1}:", ["👩 មនុស្សស្រី (Female)", "👨 មនុស្សប្រុស (Male)"], index=0 if "ស្រី" in preset['gender'] else 1, key=f"sq_gen_{c_idx}")
                        c_dna = st.text_input(f"ពិពណ៌នារូបរាង (DNA) {c_idx+1}:", value=preset['dna'], key=f"sq_dna_{c_idx}")
                        v_options = ["Aoede (ស្រីស្រទន់)", "Kore (ស្រីរស់រវើក)", "Leda (ស្រីចាស់ទុំ)"] if "ស្រី" in c_gender else ["Alnilam (ប្រុសស្វាហាប់)", "Fenrir (ប្រុសរឹងមាំ)", "Orpheus (ប្រុសសំឡេងធំ)"]
                        def_v_idx = 0
                        for vi, vname in enumerate(v_options):
                            if preset['voice'].split(" ")[0] in vname:
                                def_v_idx = vi
                                break
                        c_voice = st.selectbox(f"សំឡេងនិយាយ Flow {c_idx+1}:", v_options, index=def_v_idx, key=f"sq_voc_{c_idx}").split(" ")[0]
                    chars_data.append({
                        "tag": c_tag,
                        "gender": c_gender,
                        "is_female": "ស្រី" in c_gender,
                        "gender_desc": "young woman, female, feminine features" if "ស្រី" in c_gender else "young man, male, masculine features",
                        "dna": c_dna,
                        "voice": c_voice
                    })

    # Compatibility shortcuts for primary characters
    c1_tag = chars_data[0]["tag"]
    c1_gender = chars_data[0]["gender"]
    c1_dna = chars_data[0]["dna"]
    c1_voice = chars_data[0]["voice"]
    c1_is_female = chars_data[0]["is_female"]
    c1_gender_desc = chars_data[0]["gender_desc"]

    c2_tag = chars_data[1]["tag"] if len(chars_data) > 1 else "@companion"
    c2_gender = chars_data[1]["gender"] if len(chars_data) > 1 else "👩 មនុស្សស្រី (Female)"
    c2_dna = chars_data[1]["dna"] if len(chars_data) > 1 else "young woman"
    c2_voice = chars_data[1]["voice"] if len(chars_data) > 1 else "Kore"
    c2_is_female = chars_data[1]["is_female"] if len(chars_data) > 1 else True
    c2_gender_desc = chars_data[1]["gender_desc"] if len(chars_data) > 1 else "young woman, female, feminine features"

    # ----------------- ➕ SUPPORTING CHARACTER & PRODUCT PLACEMENT -----------------
    col_feat1, col_feat2 = st.columns(2)
    with col_feat1:
        with st.container(border=True):
            enable_c3 = st.toggle("➕ បន្ថែមតួអង្គបន្ទាប់បន្សំ (Supporting Character ម៉ាក់/អ្នកលក់/មិត្តទី៣)", value=False)
            c3_tag, c3_voice, c3_dna, c3_desc = None, None, None, ""
            if enable_c3:
                c3_sub1, c3_sub2 = st.columns(2)
                with c3_sub1:
                    c3_role = st.selectbox("តួនាទីតួអង្គ:", ["👩‍🦰 ម៉ាក់ (Mother)", "🛒 អ្នកលក់ (Local Vendor)", "🧑‍🤝‍🧑 មិត្តភក្តិទី ៣ (Friend 3)", "✍️ ផ្ទាល់ខ្លួន"], key="c3_role")
                    c3_tag = "@mom" if "ម៉ាក់" in c3_role else ("@vendor" if "អ្នកលក់" in c3_role else ("@friend3" if "មិត្ត" in c3_role else "@extra"))
                with c3_sub2:
                    c3_voice = st.selectbox("សំឡេង:", ["Leda (ស្រីចាស់ទុំ)", "Aoede (ស្រីស្រទន់)", "Fenrir (ប្រុសរឹងមាំ)", "Alnilam (ប្រុសស្វាហាប់)"], key="c3_voc").split(" ")[0]
                default_c3_dna = "caring Cambodian middle-aged mother wearing a traditional floral Khmer blouse" if "ម៉ាក់" in c3_role else "cheerful Cambodian local market vendor wearing an apron and sun visor"
                c3_dna = st.text_input("DNA រូបរាងតួអង្គទី ៣:", value=default_c3_dna, key="c3_dna")
                c3_desc = f"- Supporting character: {c3_tag} ({c3_dna}). Voice: {c3_voice}."

    with col_feat2:
        with st.container(border=True):
            enable_product = st.toggle("🛍️ បញ្ចូលផលិតផលផ្សព្វផ្សាយក្នុងរឿង (Product Placement / Sponsor)", value=False)
            product_dna, product_rules = "", ""
            if enable_product:
                pr_sub1, pr_sub2 = st.columns([1, 1.5])
                with pr_sub1:
                    pr_type = st.selectbox("ជ្រើសរើសប្រភេទផលិតផល:", [
                        "🧴 ម៉ាស់បិទមុខ Bioaqua (Bioaqua Face Mask)",
                        "☀️ ឡេការពារកម្ដៅថ្ងៃ (Sunscreen Lotion)",
                        "🥤 ភេសជ្ជៈប៉ូវកម្លាំង/តែបៃតង (Energy Drink)",
                        "💄 ក្រែមលាបមាត់ (Lipstick)",
                        "✍️ វាយបញ្ចូលផលិតផលផ្ទាល់ខ្លួន"
                    ], key="pr_type")
                with pr_sub2:
                    default_pr_dna = "Bioaqua green hydrating sheet mask package, soothing tired sunburnt face with instant glowing skin" if "Bioaqua" in pr_type else "premium skincare lotion bottle, giving instant UV protection and radiant skin"
                    product_dna = st.text_input("អត្ថប្រយោជន៍ និងរូបរាងផលិតផល:", value=default_pr_dna, key="pr_dna")
                product_rules = f"""
            PRODUCT PLACEMENT INTEGRATION (NATURAL & MEMORABLE):
            - Featured sponsor product: {product_dna}.
            - Seamlessly weave this product into the story (e.g. during Scene 4 Pit-Stop or when exhausted/sunburnt). One character uses or introduces it humorously, resulting in instant comedic relief and radiant glowing results. Do NOT make it feel like a forced commercial; make it a natural funny part of the adventure!
            """

    # ----------------- 🔒 KHMER DROPDOWN ASSET & LOCATION PRESETS -----------------
    st.markdown("#### 🔒 ចាក់សោររបស់របរ យានយន្ត និងទីតាំង (Dropdown ភាសាខ្មែរ)")


    # Smart Auto-Detection from story_input
    is_bioaqua_story = "bioaqua" in story_input.lower() or "ម៉ាស់" in story_input
    is_mirror_story = "កញ្ចក់" in story_input or "ឆ្លុះ" in story_input
    num_detected_scenes = len(re.findall(r'ឈុតទី\s*\d+', story_input))

    default_loc_idx = 0
    if is_mirror_story:
        default_loc_idx = 0 # Bedroom is now first!
    elif "កំពត" in story_input:
        default_loc_idx = 2

    default_prop_idx = 5 if is_bioaqua_story else 0
    default_dur_idx = 0 if num_detected_scenes == 6 else (1 if num_detected_scenes == 12 else 0)
    LOCATION_MAP = {
        "🪞 បន្ទប់គេងទំនើប & កញ្ចក់ឆ្លុះមុខ (Bedroom & Vanity Mirror)": "cozy modern stylish bedroom with warm vanity mirror lights, wooden dressing table, and soft indoor aesthetic",
        "🏕️ ទីធ្លាបោះតង់ក្នុងព្រៃស្រល់ (Campsite)": "cozy night campsite in a pine forest, glowing orange campfire, orange camping tent, and starry night sky",
        "🏞️ ខេត្តកំពត មាត់ព្រែក & ភ្នំបូកគោ (Kampot & Bokor)": "picturesque Kampot province, scenic riverside promenade, distant misty Bokor mountain range, tropical sunset over the water, fruit market stalls, and French colonial heritage streets",
        "🎮 បន្ទប់លេងហ្គេមទំនើប (Gaming Room)": "cozy modern gamer bedroom with purple LED light strips, white bookshelf, gaming PC desk, and grey window curtains",
        "🏡 ផ្ទះឈើបុរាណបែបខ្មែរ (Khmer Wooden House)": "traditional elevated Khmer wooden countryside house with wooden stairs, open veranda, and tropical palm garden",
        "🏛️ ប្រាសាទថ្មបុរាណសម័យអង្គរ (Angkor Temple)": "ancient Angkor stone temple courtyard with mossy carved stone towers, dramatic morning mist, and stone pillars",
        "☕ ហាងកាហ្វេទំនើបបែប Minimalist (Cafe)": "stylish modern aesthetic coffee shop with floor-to-ceiling glass windows, warm wooden tables, and green indoor plants",
        "🏖️ មាត់ឆ្នេរសមុទ្រពេលថ្ងៃលិច (Beach Sunset)": "tropical white sand beach at vibrant golden sunset, swaying coconut palm trees, and gentle sparkling ocean waves",
        "✍️ វាយបញ្ចូលទីតាំងផ្ទាល់ខ្លួន (Custom Location)": "CUSTOM"
    }

    PROP_MAP = {
        "🏕️ តង់បោះតង់ពណ៌ទឹកក្រូច & ពិល (Camping Tent & Flashlight)": "cozy modern orange camping tent with durable poles and heavy-duty flashlight",
        "🏍️ ម៉ូតូអាសង់ក្រហមស្កូតឺ (Cherry Red Scooter)": "vintage cherry-red scooter with chrome round mirrors and black leather seat",
        "🛵 ម៉ូតូធំទំនើបបែប Sport (Cyberpunk Superbike)": "sleek aerodynamic black sport motorcycle with glowing cyan neon accents and modern carbon fiber frame",
        "🚲 កង់បុរាណបែប Classic (Vintage Bicycle)": "classic light-green vintage bicycle with a front woven basket, silver bell, and brown leather saddle",
        "🚗 ឡានទំនើបបែប SUV ផ្សងព្រេង (Off-road SUV)": "rugged pearl-white adventure off-road SUV with roof luggage rack and black wheels",
        "🎁 កញ្ចប់ម៉ាស់ Bioaqua ពណ៌បៃតងភ្លឺ (Bioaqua Mask)": "shiny premium Bioaqua facial sheet mask packaging radiating glowing green sparkles",
        "✍️ វាយបញ្ចូលរបស់របរផ្ទាល់ខ្លួន (Custom Vehicle/Prop)": "CUSTOM"
    }

    c_env1, c_env2 = st.columns(2)
    with c_env1:
        loc_choice = st.selectbox("🏠 ជ្រើសរើសទីតាំង/ផ្ទះ/បន្ទប់:", list(LOCATION_MAP.keys()), index=st.session_state.get("detected_loc_idx", detected["loc_idx"]))
        location_dna = LOCATION_MAP[loc_choice] if LOCATION_MAP[loc_choice] != "CUSTOM" else st.text_input("វាយទីតាំង:", value="pine forest campsite at night")
    with c_env2:
        prop_choice = st.selectbox("🏍️ ជ្រើសរើសយានយន្ត ឬរបស់របរ:", list(PROP_MAP.keys()), index=st.session_state.get("detected_prop_idx", detected["prop_idx"]))
        prop_dna = PROP_MAP[prop_choice] if PROP_MAP[prop_choice] != "CUSTOM" else st.text_input("វាយរបស់របរ:", value="camping tent")

    # PRO SETTINGS (ROW 1)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        target_ai = st.selectbox("🤖 គោលដៅ AI Video Model:", [
            "Google Flow / Veo (Extension)",
            "Hailuo AI / MiniMax (ចលនារលូនបំផុត មិនឆ្គង)",
            "Kling AI / PixVerse (Cinematic Physics)"
        ])
    with col2:
        dur_options = [1, 2, 3, 5]
        if "sel_duration_min" not in st.session_state or st.session_state["sel_duration_min"] not in dur_options:
            st.session_state["sel_duration_min"] = detected["dur_val"]
        duration_min = st.selectbox(
            "⏱️ ប្រវែងវីដេអូ:", 
            dur_options, 
            format_func=lambda x: f"{x} នាទី ({x*6} ឈុត)",
            key="sel_duration_min"
        )
    with col3:
        workflow_type = st.selectbox("🛠️ ទម្រង់ Workflow:", [
            "🎯 2-in-1 Universal (Text to Image + Image to Video 16:9)",
            "Text to Video (Full Story 10s - AutoFlow)",
            "Text to Image (Scene Keyframes / Storyboard 16:9)",
            "Character Sheet (8-Angle Turnaround Model Sheet)",
            "Image to Video (Keyframe Animation 10s)"
        ])
    with col4:
        smooth_shield = st.toggle("🛡️ Smooth Motion Shield", value=True, help="បំបាត់ភាពឆ្គង ការពារកុំឱ្យខូចដៃមាត់ និងប្រើតែចលនាស្រទន់ធម្មជាតិ!")

    col_a1, col_a2, col_a3 = st.columns([1.2, 1, 1])
    with col_a1:
        art_style = st.selectbox("🎨 រចនាប័ទ្មរូបភាព (Visual Art Style):", [
            "📸 មនុស្សពិតជាក់ស្តែង (100% Photorealistic Live-Action)",
            "🎨 គំនូរជីវចល 3D (3D Pixar / Disney Style)",
            "🎌 គំនូរជីវចល Anime (Japanese Anime Cinematic)"
        ], index=0)
    with col_a2:
        audio_choice = st.selectbox("🎵 Soundtrack:", ["Clean Voice Only (គ្មានភ្លេង ទុកដាក់ភ្លេងខ្លួនឯង)", "With Music (មានភ្លេងអម)"])
    with col_a3:
        enable_tts = st.checkbox("🔊 បង្កើតសំឡេងខ្មែរ (Audio Preview)", value=False, help="បើកមុខងារនេះទើបវាទាញយកសំឡេង MP3។ បើបិទ វានឹងដំណើរការលឿនខ្លាំង!")
    num_clips = duration_min * 6

    clothing_directives = "\n".join([
        f"- {c['tag']}: {c['gender_desc']}. MANDATORY OUTFIT LOCK: strictly wearing {c['dna']}. ABSOLUTELY FORBIDDEN: NO dark hoodies, NO navy jackets, NO black t-shirts, NO unrequested sweaters, NO denim jackets. In EVERY single scene, {c['tag']} MUST wear this exact outfit with zero clothing drift."
        for c in chars_data
    ])
    chars_prompt_lock = " and ".join([
        f"{c['tag']} ({c['gender_desc']}, wearing {c['dna']}, strictly NO hoodie, NO dark jacket)"
        for c in chars_data
    ])
    ref_asset_lock_str = " | ".join([
        f"Reference Asset Lock {c['tag']}: 100% visual match to uploaded {c['tag']} reference image, identical facial likeness and strictly wearing {c['dna']} with zero outfit change, strictly no hoodie, no dark jacket, no black t-shirt"
        for c in chars_data
    ])
    tags_str = ", ".join([c["tag"] for c in chars_data])
    squad_summary = "\n".join([f"- {c['tag']}: {c['gender_desc']}, {c['dna']}. Assigned voice: {c['voice']}." for c in chars_data])
    voice_rules = "; ".join([f"{c['tag']} uses {c['voice']}" for c in chars_data])

    btn_label = f"🚀 បង្កើតរឿងភាគ {duration_min} នាទី ({num_clips} ឈុត) ក្រុម {len(chars_data)} តួអង្គ ({tags_str})!"
    if st.button(btn_label, key="btn_gen"):
        if not api_key:
            st.error("⚠️ សូមបញ្ចូល Gemini API Key នៅខាងលើជាមុនសិន!")
        elif not story_input:
            st.warning("⚠️ សូមបញ្ចូលគំនិតសាច់រឿង!")
        else:
            with st.spinner(f"⚡ កំពុងរៀបចំសាច់រឿង {num_clips} ឈុត ចាក់សោរឈ្មោះ និងភេទតាមការកំណត់..."):
                try:
                    client = genai.Client(api_key=api_key)
                    music_rule = "no background music, no soundtrack, clear spoken voices only" if "Clean" in audio_choice else "rich background soundtrack, sound effects, and clear spoken dialogue"

                    motion_rules = """
                    CRITICAL SMOOTH-MOTION RULES (ZERO AWKWARDNESS):
                    - Avoid exaggerated, violent, rapid limb movements.
                    - Use cinema-grade MICRO-MOVEMENTS: subtle expressive blinking, natural slow breathing, gentle head turns, soft smiling eyes, stable limb physics, zero warping, coherent hand placement.
                    """ if smooth_shield else ""

                    continuity_master_rule = """
                    CRITICAL SEAMLESS SCENE CONTINUITY:
                    1. Positional Handover: Scene [N] MUST start from the exact physical position, body orientation, and emotional state where Scene [N-1] ended.
                    2. Cause and Effect: Scene [N]'s opening action directly reacts to Scene [N-1].
                    3. Lighting & Palette Continuity: Environmental lighting, time of day, and background details in Scene [N] match Scene [N-1].
                    """

                    asset_lock_rules = f"""
                    STRICT ASSET, VEHICLE & ENVIRONMENT CONSISTENCY:
                    1. Location: {location_dna}. Strictly preserve architectural design, lighting atmosphere, and environment with zero drift.
                    2. Vehicle & Prop: {prop_dna}. Preserve exact model, color, and textures across all scenes.
                    """

                    gender_lock_rules = f"""
                    ABSOLUTE CHARACTER GENDER & VOICE LOCK:
                    - {c1_tag}: {c1_gender_desc}, {c1_dna}. Assigned voice: {c1_voice} ({'Female' if c1_is_female else 'Male'} voice). Strictly maintain this gender and voice across all scenes.
                    - {c2_tag}: {c2_gender_desc}, {c2_dna}. Assigned voice: {c2_voice} ({'Female' if c2_is_female else 'Male'} voice). Strictly maintain this gender and voice across all scenes.
                    - Two distinct individuals, zero gender swapping, zero character cloning.
                    """

                    if "មនុស្សពិត" in art_style:
                        art_prompt = "VISUAL ART STYLE: 100% authentic live-action cinematic photography, real human skin texture and pores, raw natural photograph, shot on 35mm lens. ABSOLUTE FORBIDDEN: zero 3D render, zero CGI, zero Pixar cartoon, zero anime styling."
                    elif "3D" in art_style:
                        art_prompt = "VISUAL ART STYLE: High-end 3D animated film aesthetic, Pixar/Disney 3D animation style, expressive stylized character design, rich vibrant lighting."
                    else:
                        art_prompt = "VISUAL ART STYLE: Makoto Shinkai anime aesthetic, highly detailed 2D anime animation, vibrant sky and cinematic anime lighting."

                    dynamic_progression_rules = """
                    CRITICAL DYNAMIC CINEMATIC PROGRESSION (ZERO REPETITIVE SCENES):
                    - Every single scene MUST be a unique, fresh visual framing and progressive story moment!
                    - Do NOT repeat the exact same static camera angle, sitting posture, or sub-location across multiple scenes.
                    - Dynamically vary the cinematography across scenes:
                      * Scene 1: Wide establishing shot (Arrival, travel kickoff, vehicle and environment).
                      * Scene 2: Medium action shot (Active interaction with local environment or items).
                      * Scene 3: Emotional comedy close-up (Surprised/funny reaction, vivid facial expression, hilarious moment).
                      * Scene 4: Cinematic traveling/tracking shot (Movement, cruising on vehicle along scenic route).
                      * Scene 5: Comedy climax or unexpected twist.
                      * Scene 6: Scenic golden hour or sunset resolution.
                    """

                    if "2-in-1" in workflow_type:
                        system_prompt = f"""
                        You are an elite Hollywood Director and AI Cinematographer.
                        Generate exactly {num_clips} sequential 16:9 cinematic 2-IN-1 UNIVERSAL DUAL-COMPATIBLE prompts for a complete {duration_min}-minute drama ({num_clips} scenes).
                        
                        PURPOSE OF 2-IN-1 PROMPTS:
                        Each prompt is uniquely crafted to work seamlessly for BOTH:
                        1. Generating the initial 16:9 photographic Keyframe image (Text-to-Image).
                        2. Directly animating that exact Keyframe image into a 10-second cinematic video (Image-to-Video) using the SAME prompt!

                        CRITICAL MASTER DIRECTIVES:
                        1. DUAL COMPATIBILITY: Include rich static composition details (setting, lighting, framing) AND fluid micro-actions (natural slow breathing, expressive eyes, subtle head turn, gentle hand gestures, stable cinematic physics, slow camera push-in).
                        2. DYNAMIC SCENE DIVERSITY: Every scene must have a different sub-location and camera angle within {location_dna}.
                        3. STRICT CHARACTER & OUTFIT LOCK (ZERO CLOTHING DRIFT):
{clothing_directives}
                           - In EVERY single scene prompt, you MUST explicitly specify each character's outfit: {chars_prompt_lock}.
                           - STRICT NEGATIVE CLOTHING: ABSOLUTELY NO HOODIES, NO NAVY JACKETS, NO BLACK T-SHIRTS, NO SWEATERS.

                        4. ABSOLUTE ZERO SPEECH BUBBLES & ZERO ON-SCREEN TEXT (STRICT PHOTOREALISM):
                           - This is a photorealistic live-action film frame, NOT a comic book.
                           - ABSOLUTELY FORBIDDEN: ZERO speech bubbles, ZERO comic dialogue balloons, ZERO speech callouts, ZERO floating text, ZERO subtitles, ZERO typography rendered on image.
                           - Clean frame, no text, no watermark.

                        Format for each scene:
                        #scene[N] A cinematic 16:9 4K scene. Setting: [specific distinct sub-spot in {location_dna}]. Action: {chars_prompt_lock} [describe expressive action with cinema-grade micro-movements: natural breathing, subtle head turn, expressive blinking, natural gestures]. [Camera movement: subtle slow push-in / gentle pan]. [{ref_asset_lock_str}]. {art_prompt}. Masterwork 8k resolution, shot on 35mm lens, natural cinematic lighting, identical facial likeness and outfit to character reference sheet with zero drift. Clean frame, absolute zero speech bubbles, zero comic text balloons, no subtitles, no floating text, no watermark. Audio dialogue script: [Speaker] says, "[Short natural funny dialogue in Khmer language matching this scene]"

                        Rules:
                        - Start with #scene1, #scene2... up to #scene{num_clips}.
                        - Leave exactly ONE empty line between prompts.
                        """
                    elif "Text to Image" in workflow_type:
                        system_prompt = f"""
                        You are an elite Hollywood AI Cinematographer.
                        Generate exactly {num_clips} sequential 16:9 cinematic PHOTOGRAPHY KEYFRAME IMAGE prompts for a complete {duration_min}-minute drama ({num_clips} scenes).

                        CRITICAL MASTER DIRECTIVES:
                        1. PUNCHY AND FOCUSED: Under 70 words per prompt.
                        2. DYNAMIC SCENE DIVERSITY: Every scene must have a different sub-location and camera angle within {location_dna}.
                        3. STRICT CHARACTER & OUTFIT LOCK (ZERO CLOTHING DRIFT):
{clothing_directives}
                           - In EVERY single scene prompt, you MUST explicitly specify each character's outfit: {chars_prompt_lock}.
                           - STRICT NEGATIVE CLOTHING: ABSOLUTELY NO HOODIES, NO NAVY JACKETS, NO BLACK T-SHIRTS, NO SWEATERS.

                        4. ABSOLUTE ZERO SPEECH BUBBLES & ZERO ON-SCREEN TEXT (STRICT PHOTOREALISM):
                           - This is a photorealistic live-action film still photograph, NOT a comic book.
                           - ABSOLUTELY FORBIDDEN: ZERO speech bubbles, ZERO comic dialogue balloons, ZERO speech callouts, ZERO floating text, ZERO subtitles, ZERO typography rendered on image.
                           - Clean frame, no text, no watermark.

                        Format for each scene:
                        #scene[N] A cinematic 16:9 4K photography keyframe still image. Setting: [specific distinct sub-spot in {location_dna}]. Action: {chars_prompt_lock} [describe dynamic physical action, natural body posture, and vivid facial expressions matching the story beat]. [{ref_asset_lock_str}]. {art_prompt}. Masterwork 8k resolution, shot on 35mm lens, natural cinematic lighting, identical facial likeness and outfit to character reference sheet with zero drift. Clean live-action photo, absolute zero speech bubbles, zero comic text balloons, no subtitles, no floating text, no watermark. Audio dialogue script: [Speaker] says, "[Short natural funny dialogue in Khmer language matching this scene]"

                        Rules:
                        - Start with #scene1, #scene2... up to #scene{num_clips}.
                        - Leave exactly ONE empty line between prompts.
                        """
                    elif "Character Sheet" in workflow_type:
                        system_prompt = f"""
                        You are an elite Hollywood Character Concept Designer.
                        Generate ultra-detailed Character Turnaround Model Sheet prompts for both characters.
                        
                        {art_prompt}

                        Format:
                        #character1 Ultra-detailed character turnaround reference sheet of {c1_tag} ({c1_gender_desc}, {c1_dna}). Clean solid white studio background, 8 distinct perspectives in a neat 2x4 grid: top row shows full-body front view, three-quarter turn, side profile view, and back view; bottom row shows high-detail close-up facial portraits front view, 3/4 turn smiling, side profile, and 45-degree angle. {art_prompt}, uniform natural soft lighting, razor-sharp focus, consistent facial geometry and identical clothing across all angles, zero morphing, zero blur, professional model sheet.

                        #character2 Ultra-detailed character turnaround reference sheet of {c2_tag} ({c2_gender_desc}, {c2_dna}). Clean solid white studio background, 8 distinct perspectives in a neat 2x4 grid: top row shows full-body front view, three-quarter turn, side profile view, and back view; bottom row shows high-detail close-up facial portraits front view, 3/4 turn smiling, side profile, and 45-degree angle. {art_prompt}, uniform natural soft lighting, razor-sharp focus, consistent facial geometry and identical clothing across all angles, zero morphing, zero blur, professional model sheet.
                        """
                    elif "Image to Video" in workflow_type:
                        system_prompt = f"""
                        You are an elite Hollywood AI Filmmaker.
                        Generate exactly {num_clips} sequential continuous Image-to-Video prompts for a {duration_min}-minute drama starting from reference keyframe images.
                        
                        {art_prompt}
                        {gender_lock_rules}
                        {continuity_master_rule}
                        {motion_rules}
                        
                        Format for each scene:
                        #scene[N] Animate directly from the reference keyframe into a single continuous 10-second cinematic clip in 16:9 widescreen, 4K HDR. Beginning from the exact static keyframe pose, {chars_prompt_lock} [describe physical micro-actions picking up smoothly from the image]. [{ref_asset_lock_str}]. Strictly preserve exact facial likeness, clothing, and environment from input keyframe with zero drift. {art_prompt}. Voice assignment: {c1_tag} uses voice {c1_voice}; {c2_tag} uses voice {c2_voice}. Dialogue line (spoken audio only, never render text): [Speaker] says, "[Natural funny dialogue in Khmer language]" Clean frame, no subtitles, no text on screen, no watermark.
                        
                        Rules:
                        - Start with #scene1, #scene2... up to #scene{num_clips}.
                        - Leave exactly ONE empty line between prompts.
                        """
                    else: # Text to Video
                        system_prompt = f"""
                        You are an elite Hollywood Director for Google Flow (Veo) and AI video generators.
                        Generate exactly {num_clips} continuous 10-second cinematic video prompts for a {duration_min}-minute drama ({num_clips} scenes).

                        STRICT MASTER DIRECTIVES (FAITHFUL STORY & SMART CHARACTER MAPPING):
                        1. STORY FIDELITY & EXACT SCENE PROGRESSION:
                           - If the user provides a custom script or scene-by-scene story (such as gaming bedroom, mirror reflection, Bioaqua mask, teasing, selfie, debt joke), YOU MUST 100% FAITHFULLY FOLLOW THE USER'S EXACT SCENES, PLOT, JOKES, AND DIALOGUE! Do NOT replace it with travel/asking-mom stories!
                           - Generate all {num_clips} scenes sequentially from #scene1 up to #scene{num_clips}.
                           - SMART CHARACTER CONSOLIDATION: Map all dialogues and comedic teasing into the active squad ({tags_str}).

                        2. STRICT CLOTHING & APPEARANCE LOCK (ZERO CLOTHING DRIFT):
{clothing_directives}
                           - In EVERY scene prompt, you MUST explicitly specify each character's outfit: {chars_prompt_lock}.
                           - ABSOLUTELY NO HOODIES, NO DARK JACKETS, NO BLACK T-SHIRTS, NO SWEATERS, NO UNREQUESTED DENIM JACKETS.

                        3. ABSOLUTE ZERO SPEECH BUBBLES & ZERO ON-SCREEN TEXT:
                           - Clean cinematic live-action video frame.
                           - Absolutely NO speech bubbles, NO comic text balloons, NO floating text, NO subtitles, NO typography rendered on screen.
                           - Spoken dialogue is for audio track only, NEVER render as a visual bubble or text.

                        4. PUNCHY & CONCISE: Every scene prompt must be around 65-75 words.

                        5. CHARACTER SQUAD LOCK ({len(chars_data)} CHARACTERS):
{squad_summary}
{c3_desc}
                           - All characters have identical facial likeness to character reference sheet with zero drift. Distinct individuals.

                        Format for each prompt:
                        #scene[N] A cinematic 10-second 4K clip in 16:9 widescreen. Setting: [specific distinct sub-location in {location_dna}]. Action: {chars_prompt_lock} [describe dynamic squad action, natural micro-movements, and expressions matching the user's story beat]. [{ref_asset_lock_str}]. [Camera movement]. Photorealistic live-action, natural lighting. Identical facial features and exact clothing matching character reference image with zero outfit change, strictly no hoodies, no dark jackets, zero clothing drift. Clean cinematic live-action frame, absolute zero speech bubbles, zero comic text balloons, no subtitles, zero on-screen typography, no watermark. Voice assignment: {voice_rules}. Audio dialogue track only (spoken audio only, strictly forbidden to render visual speech bubbles): [Speaker] says, "[Short natural funny dialogue in Khmer language matching the story]"

                        Rules:
                        - Start with #scene1, #scene2... up to #scene{num_clips}.
                        - Leave exactly ONE empty line between prompts.
                        """

                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=f"Story Concept: {story_input}",
                        config={'system_instruction': system_prompt}
                    )

                    st.session_state['full_prompts'] = response.text
                    st.session_state['num_scenes'] = num_clips
                    st.success("🎉 បង្កើតរឿងភាគដោយជោគជ័យ! ចាក់សោរឈ្មោះ ភេទ និងមុខមាត់ ១០០%!")
                except Exception as e:
                    st.error(f"មានបញ្ហា៖ {e}")

    # Display results
    if 'full_prompts' in st.session_state:
        prompts_text = st.session_state['full_prompts']
        st.markdown("---")
        
        if "2-in-1" in workflow_type:
            st.markdown("""
            <div style="background:linear-gradient(90deg, rgba(16,185,129,0.15) 0%, rgba(6,78,59,0.25) 100%); border:1px solid rgba(16,185,129,0.4); border-radius:12px; padding:12px 18px; margin-top:14px; margin-bottom:12px; font-size:13.5px; color:#a7f3d0;">
                🎯 <b>របៀបប្រើ 2-in-1 Workflow:</b><br>
                1. ចុចចម្លង <b>Prompt 2-in-1</b> ខាងក្រោម ➔ យកទៅ Gen រូបភាព 16:9 (Text-to-Image) ក្នុង Google Flow / Midjourney ឱ្យចេញរូបស្អាតសិន។<br>
                2. ពេលបានរូបភាពហើយ ➔ យករូបនោះបញ្ចូលទៅ Image-to-Video រួច <b>Paste Prompt ដដែលនេះចូលម្តងទៀត</b> ដើម្បីបង្កើតវីដេអូចលនារលូន 10s ដោយមិនបាច់ប្តូរ Prompt ឡើយ!
            </div>
            """, unsafe_allow_html=True)

        # ACTION BAR
        st.markdown("### 📥 ទាញយកឯកសារសម្រាប់ផលិតវីដេអូ")
        c_dl1, c_dl2, c_dl3 = st.columns([1, 1, 1.2])
        with c_dl1:
            st.download_button(
                label="💾 Download Prompts (.txt)",
                data=prompts_text,
                file_name=f"drama_autoflow_{duration_min}min.txt",
                mime="text/plain",
                help="សម្រាប់ Import ចូល Extension"
            )
        
        # Batch Voice ZIP generator
        scenes = [s.strip() for s in prompts_text.split("#scene") if s.strip()]
        khmer_dialogues = []
        for idx, sc in enumerate(scenes, start=1):
            dia_line = extract_dialogue(sc, story_input, idx)
            if dia_line:
                khmer_dialogues.append((idx, dia_line))

        with c_dl2:
            if enable_tts and HAS_GTTS and khmer_dialogues:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for s_idx, d_text in khmer_dialogues:
                        audio_data = get_khmer_audio_cached(d_text)
                        if audio_data:
                            zf.writestr(f"scene_{s_idx}.mp3", audio_data)
                zip_buffer.seek(0)
                st.download_button(
                    label="📦 Download All Voiceover (.zip)",
                    data=zip_buffer,
                    file_name="khmer_all_voices.zip",
                    mime="application/zip",
                    help="ទាញយកសំឡេងខ្មែរគ្រប់ Scene ក្នុង Folder តែមួយ!"
                )
            elif not enable_tts:
                st.caption("⚡ សំឡេងបិទ (Fast Mode) - ដើម្បីបើក សូម Tick លើ '🔊 បង្កើតសំឡេងខ្មែរ'")
            elif not HAS_GTTS:
                st.caption("💡 `pip install gTTS` ដើម្បី Download ZIP")
        
        with c_dl3:
            st.info("💡 **Extension:** ចុច **Import .txt** ➔ ជ្រើសរើស File នេះ ➔ រួចចុច **Start**!")

        # ----------------- 📋 ASSET & REFERENCE REQUIREMENTS CHECKLIST -----------------
        st.markdown("""
        <div style="background:#190812; border:1px solid #e11d48; border-radius:16px; padding:18px; margin-top:16px; margin-bottom:16px; box-shadow:0 4px 20px rgba(225,29,72,0.35);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="font-size:17px; font-weight:800; color:#fff; display:flex; align-items:center; gap:8px;">
                    📋 តារាងតម្រូវការរូបភាព Reference & Assets សម្រាប់ Google Flow
                </div>
                <span style="background:#be123c; color:#fff; font-size:11px; padding:3px 12px; border-radius:14px; font-weight:700;">REQUIRED ASSETS</span>
            </div>
            <div style="color:#fecdd3; font-size:13px;">
                💡 ដើម្បីឱ្យវីដេអូចេញមកត្រូវមុខ និងខោអាវ ១០០% បងត្រូវ Upload រូបភាព Reference ទាំងនេះចូលក្នុង Google Flow "Assets" មុនពេលចុច Start:
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔍 មើលតម្រូវការរូបភាព Reference & Prompt បង្កើតរូបតួអង្គ (Asset Checklist)", expanded=True):
            num_c_cols = min(len(chars_data), 4)
            chk_cols = st.columns(num_c_cols)
            for ci, c in enumerate(chars_data):
                col_target = chk_cols[ci % num_c_cols]
                with col_target:
                    st.markdown(f"**👤 Reference: `{c['tag']}`**")
                    st.caption(f"📌 {c['gender_desc']}\n\n👗 ខោអាវ: {c['dna']}")
                    turnaround_prompt = f"Ultra-detailed character turnaround reference sheet of {c['tag']} ({c['gender_desc']}). Strictly wearing {c['dna']}. ABSOLUTELY FORBIDDEN: NO dark hoodies, NO navy jackets, NO black t-shirts, NO sweaters, NO clothing drift. Solid clean white background, 8 distinct angles in a 2x4 grid: top row displays full-body front view, three-quarter turn, side profile view, and back view; bottom row displays high-detail close-up facial portraits front view, 3/4 turn smiling, side profile, and 45-degree angle. Masterpiece studio photography, uniform natural soft lighting, razor-sharp focus, consistent facial geometry and 100% identical clothing across all angles, zero morphing, zero blur, professional model sheet."
                    st.text_area(f"Turnaround Prompt ({c['tag']}):", value=turnaround_prompt, height=90, key=f"tp_{ci}")

            st.markdown("---")
            c_p_req1, c_p_req2 = st.columns(2)
            with c_p_req1:
                st.markdown(f"**🏠 Location Reference Asset (ទីតាំងទេសភាព)**")
                st.caption(f"📍 បរិយាកាស: `{location_dna}`")
                loc_ref_prompt = (
                    f"Ultra-detailed cinematic 16:9 environment photography of {location_dna}. "
                    f"Architectural wide angle establishing shot, authentic atmosphere, natural ambient and soft volumetric lighting, "
                    f"shot on 35mm lens, f/2.8, photorealistic 8k resolution masterwork, rich spatial textures and depth, "
                    f"clean empty scene with zero people, zero characters, absolute zero text, no watermark, no logo."
                )
                st.text_area("📋 Location Image Prompt (ចុច Copy យកទៅ Gen រូបទីតាំង):", value=loc_ref_prompt, height=105, key="loc_ref_prompt")
                st.caption("💡 រូបភាពទីតាំងបន្ទប់ ឬមាត់ព្រៃ សម្រាប់ Upload ចូល Assets ក្នុង Google Flow")

            with c_p_req2:
                st.markdown(f"**🎁 Prop/Product Reference Asset (សម្ភារ/ផលិតផល)**")
                st.caption(f"📦 របស់របរ/ផលិតផល: `{prop_dna}`")
                prop_ref_prompt = (
                    f"Ultra-detailed commercial studio product photography of {prop_dna}. "
                    f"Centered composition on clean minimalist studio pedestal table, professional three-point softbox studio lighting, "
                    f"crisp reflections, razor-sharp focus on packaging texture and branding details, "
                    f"shot on 85mm macro lens, 8k resolution, photorealistic commercial advertising still, "
                    f"zero people, no hands, clean neutral studio background, zero text overlay, no watermark."
                )
                st.text_area("📋 Prop/Product Image Prompt (ចុច Copy យកទៅ Gen រូបសម្ភារ):", value=prop_ref_prompt, height=105, key="prop_ref_prompt")
                st.caption("💡 រូបភាពកញ្ចប់ផលិតផល ឬរបស់របរ សម្រាប់ Upload ចូល Assets ក្នុង Google Flow")

            if enable_c3 and c3_tag:
                st.markdown("---")
                st.markdown(f"**👵 Supporting Character Reference: `{c3_tag}` (តួអង្គបន្ទាប់បន្សំ)**")
                st.caption(f"🎭 តួនាទី: `{c3_role}` | 🧬 DNA: {c3_dna}")
                c3_turnaround = (
                    f"Ultra-detailed character turnaround reference sheet of {c3_tag} ({c3_dna}). "
                    f"Solid clean white background, 8 distinct perspectives in a neat 2x4 grid: top row displays full-body front view, "
                    f"three-quarter turn, side profile view, and back view; bottom row displays high-detail close-up facial portraits "
                    f"front view, 3/4 turn smiling, side profile, and 45-degree angle. Masterpiece studio photography, uniform natural "
                    f"soft lighting, razor-sharp focus, consistent facial geometry and identical clothing across all angles, "
                    f"zero morphing, zero blur, professional model sheet."
                )
                st.text_area(f"Turnaround Prompt ({c3_tag}):", value=c3_turnaround, height=95, key="tp_c3")

                # Scene Timeline
        st.markdown("#### 🎬 ពិនិត្យមើលតាមឈុតនីមួយៗ (Timeline & Prompts)")
        for idx, scene_content in enumerate(scenes, start=1):
            full_scene_str = f"#scene{scene_content}"
            khmer_speech = extract_dialogue(scene_content, story_input, idx)

            clean_visual = re.sub(r'Audio dialogue (?:track|script)[^:]*:.*$', '', full_scene_str, flags=re.IGNORECASE).strip()
            clean_visual = re.sub(r'Voice assignment:.*$', '', clean_visual, flags=re.IGNORECASE).strip()
            if not clean_visual.endswith('.'):
                clean_visual += '.'
            
            with st.container():
                st.markdown(f'<div class="scene-box"><span style="font-weight:700; color:#fb7185;">🎬 ឈុតទី {idx} (10 វិនាទី)</span> | <span style="font-size:12px; color:#22c55e;">🔒 Locked Continuity & Zero Speech Bubbles</span></div>', unsafe_allow_html=True)
                
                c_left, c_right = st.columns([2, 1])
                with c_left:
                    st.code(full_scene_str, language="text")
                    with st.expander("🛡️ ចម្លង Prompt 2-in-1 សុទ្ធ (ប្រើបានទាំង Gen រូបភាព & Gen វីដេអូ គ្មាន Speech Bubble ១០០%):", expanded=False):
                        st.code(clean_visual, language="text")
                with c_right:
                    if khmer_speech:
                        st.markdown(f"🗣️ **Script និយាយ (Audio Voiceover):** *\"{khmer_speech}\"*")
                        if enable_tts and HAS_GTTS:
                            audio_bytes = get_khmer_audio_cached(khmer_speech)
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3")

# ================= TAB 2: AI PROMPT DOCTOR =================
with tab_doctor:
    st.markdown("""
    <div style="background:#17070f; border:1px solid rgba(225, 29, 72, 0.28); border-radius:16px; padding:18px; margin-bottom:16px; box-shadow:0 4px 20px rgba(0,0,0,0.35);">
        <div style="color:#fb7185; font-size:18px; font-weight:800; display:flex; align-items:center; gap:8px;">
            🩺 AI Prompt Doctor <span style="background:#be123c; color:#fff; font-size:11px; padding:2px 8px; border-radius:12px; font-weight:700;">POLICY & GENDER FIX</span>
        </div>
        <div style="color:#fecdd3; font-size:13px; margin-top:4px;">
            Paste Prompt ដែលចេញសារ <b>"Policy Violation"</b> ឬ <b>"Failed"</b> ឬចេញមនុស្សប្រុសខុសភេទ ចូលទីនេះ AI នឹងកែឱ្យត្រូវច្បាប់ និងត្រូវមុខ ១០០%!
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_doc_in, c_doc_opt = st.columns([2, 1])
    with c_doc_in:
        broken_prompt = st.text_area("Paste Prompt ដែលមានបញ្ហា ឬជាប់ Policy:", height=130)
    with c_doc_opt:
        issue_type = st.radio("🔍 ប្រភេទបញ្ហាដែលចង់កែ:", [
            "👩 តួអង្គស្រី បែរជាចេញមនុស្សប្រុស (Fix Female Turned Into Man)",
            "🚨 ជាប់ Content Policy (ហាមឃាត់អំពើហិង្សា/ពាក្យរសើប)",
            "👥 តួអង្គខូចមុខ ឬចេញមនុស្សដូចគ្នា ២ នាក់ (Clones)",
            "🏍️ ម៉ូតូ កង់ ឬផ្ទះ ប្តូររូបរាង (Fix Vehicle/House Drift)",
            "🎭 វីដេអូចេញមនុស្សពិត (Realistic) ចង់កែមក 3D Pixar វិញ"
        ])

    if st.button("🩺 ចាប់ផ្តើមព្យាបាល និងកែ Prompt ឥឡូវនេះ (Fix Prompt)"):
        if not api_key:
            st.error("⚠️ សូមបញ្ចូល Gemini API Key នៅខាងលើជាមុនសិន!")
        elif not broken_prompt:
            st.warning("⚠️ សូមបញ្ចូល Prompt ដែលមានបញ្ហា!")
        else:
            with st.spinner("AI Doctor កំពុងពិនិត្យ និងកែតម្រូវភេទ និងមុខមាត់..."):
                try:
                    client = genai.Client(api_key=api_key)
                    doctor_instruction = f"""
                    You are an expert AI Video Prompt Sanitizer and Character Gender Enforcer for Google Flow (Veo), Hailuo, and Kling.
                    Fix the prompt to completely resolve: '{issue_type}'.
                    Crucial rule: If a female character is turned into a man, forcefully lock her as a beautiful young woman, female, feminine facial features, female hands, and assigned female voice. Never allow male pronouns or male voices for female characters.
                    Output ONLY the fixed, cleaned prompt ready to use.
                    """
                    fix_res = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=f"Problematic Prompt:\n{broken_prompt}",
                        config={'system_instruction': doctor_instruction}
                    )
                    st.success("✅ បានកែសម្រួលរួចរាល់! Prompt នេះចាក់សោរភេទ និងរលូន ១០០%:")
                    st.code(fix_res.text.strip(), language="text")
                except Exception as e:
                    st.error(f"Error: {e}")

# ================= TAB 3: SINGLE SCENE FIXER =================
with tab_reroll:
    st.subheader("🔄 កែតម្រូវតែ ១ ឈុតជាក់លាក់ (Single Scene Fixer)")
    col_r1, col_r2 = st.columns([1, 2])
    with col_r1:
        scene_num = st.number_input("ឈុតដែលចង់កែ (Scene #):", min_value=1, max_value=30, value=3)
        desired_change = st.text_area("តើអ្នកចង់ប្តូរអ្វីក្នុងឈុតនេះ?", value="កុំឱ្យចេញជាប្រុស ឱ្យ Rex ចេញជាស្រីស្អាតសក់វែងអាវខៀវវិញ")
    with col_r2:
        old_scene_text = st.text_area("Prompt ចាស់នៃឈុតនោះ:", height=130, placeholder="Paste prompt ចាស់ចូល...")

    if st.button("✨ កែសម្រួលឈុតនេះឡើងវិញ"):
        if not api_key:
            st.error("⚠️ សូមបញ្ចូល Gemini API Key!")
        else:
            with st.spinner("កំពុងកែសម្រួល..."):
                try:
                    client = genai.Client(api_key=api_key)
                    re_prompt = f"""
                    Rewrite #scene{scene_num} to apply: {desired_change}.
                    Original: {old_scene_text}
                    Enforce strict character consistency and matching gender.
                    Output ONLY the updated #scene{scene_num} prompt.
                    """
                    r_res = client.models.generate_content(model='gemini-3.8-flash', contents=re_prompt)
                    st.success(f"✅ ឈុតទី {scene_num} ថ្មី:")
                    st.code(r_res.text.strip(), language="text")
                except Exception as e:
                    st.error(f"Error: {e}")

# ================= TAB 4: CAPCUT SUBTITLES =================
with tab_srt:
    st.subheader("📥 Export Subtitles (.srt) សម្រាប់ CapCut")
    if 'full_prompts' in st.session_state:
        scenes_data = [s.strip() for s in st.session_state['full_prompts'].split("#scene") if s.strip()]
        srt_content = ""
        for i, sc in enumerate(scenes_data, start=1):
            start_sec = (i - 1) * 10
            end_sec = i * 10
            def fmt_time(seconds):
                h = seconds // 3600
                m = (seconds % 3600) // 60
                s = seconds % 60
                return f"{h:02d}:{m:02d}:{s:02d},000"
            kh_text = extract_dialogue(sc, story_input, i) or f"ឈុតទី {i}"
            srt_content += f"{i}\n{fmt_time(start_sec)} --> {fmt_time(end_sec)}\n{kh_text}\n\n"
            
        st.text_area("Preview Subtitle (.srt):", value=srt_content, height=200)
        st.download_button(
            label="💾 Download CapCut Subtitles (.srt)",
            data=srt_content,
            file_name="drama_subtitles_khmer.srt",
            mime="text/plain"
        )
    else:
        st.info("💡 សូមបង្កើតរឿងក្នុង Tab ទី ១ សិន នោះ File Subtitles (.srt) នឹងបង្ហាញនៅទីនេះដោយស្វ័យប្រវត្តិតែម្តង!")

# ==============================================================================
# ✅ FULLY UPDATED: SMART STORY FIDELITY, CLOTHING LOCK & SQUAD CONSOLIDATION
# 1. 100% User Story Fidelity: Faithfully follows custom scripts (Bioaqua, mirror, selfie...)
# 2. Smart Consolidation: If custom script has 5 names but tool has 2, smartly maps them to @sima & @rex!
# 3. Strict Clothing Lock: @sima in white crop top, @rex in blue shirt (ZERO jackets/sweaters)
# 4. Zero Speech Bubbles: Clean video frame, no comic bubbles, no text balloons, no subtitles
# ==============================================================================
