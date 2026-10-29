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
    page_icon="🎬",
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
        <div style="display:flex; align-items:center; gap:14px;">
            <div style="width:50px; height:50px; border-radius:50%; background:linear-gradient(135deg, #e11d48, #be123c); display:flex; align-items:center; justify-content:center; font-size:24px; box-shadow:0 0 16px rgba(225,29,72,0.6); border:2px solid #fda4af;">
                🎬
            </div>
            <div>
                <div style="font-size:20px; font-weight:800; color:#fff; display:flex; align-items:center; gap:8px;">
                    Khmer AutoFlow Studio <span style="background:#be123c; color:#fff; font-size:11px; padding:2px 8px; border-radius:12px; font-weight:700;">PRO</span>
                </div>
                <div style="color:#fda4af; font-size:12.5px;">Batch videos, storyboards & audio on Google Flow, 100% character locked.</div>
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

col_api_dummy, col_api = st.columns([2, 1])
with col_api:
    api_key = st.text_input("🔑 Gemini API Key:", type="password", placeholder="Paste Gemini API Key...", label_visibility="collapsed")

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ----------------- STUDIO WORKSPACE TABS (CUTE PILL CONTROLS) -----------------
tab_create, tab_doctor, tab_reroll, tab_srt = st.tabs([
    "🚀 Story Creator", 
    "🩺 Prompt Doctor", 
    "🔄 Scene Fixer",
    "📥 CapCut SRT"
])

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
        current_num_c = st.session_state.get("num_characters_val", 4)
        c_opts = [2, 3, 4, 5]
        def_c_idx = c_opts.index(current_num_c) if current_num_c in c_opts else 2
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
        loc_choice = st.selectbox("🏠 ជ្រើសរើសទីតាំង/ផ្ទះ/បន្ទប់:", list(LOCATION_MAP.keys()), index=default_loc_idx)
        location_dna = LOCATION_MAP[loc_choice] if LOCATION_MAP[loc_choice] != "CUSTOM" else st.text_input("វាយទីតាំង:", value="pine forest campsite at night")
    with c_env2:
        prop_choice = st.selectbox("🏍️ ជ្រើសរើសយានយន្ត ឬរបស់របរ:", list(PROP_MAP.keys()), index=default_prop_idx)
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
        duration_min = st.selectbox("⏱️ ប្រវែងវីដេអូ:", [1, 2, 3, 5], index=default_dur_idx, format_func=lambda x: f"{x} នាទី ({x*6} ឈុត)")
    with col3:
        workflow_type = st.selectbox("🛠️ ទម្រង់ Workflow:", [
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

    clothing_directives = "\n".join([f"- {c['tag']}: 100% IDENTICAL to reference image ({c['dna']}). Must wear the EXACT same outfit from the reference image in all scenes with zero outfit modification, zero added jackets, zero sweaters, zero clothing drift." for c in chars_data])
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

                    if "Text to Image" in workflow_type:
                        system_prompt = f"""
                        You are an elite Hollywood AI Cinematographer.
                        Generate exactly {num_clips} sequential 16:9 cinematic PHOTOGRAPHY KEYFRAME IMAGE prompts for a complete {duration_min}-minute drama.

                        CORE DIRECTIVES:
                        1. PUNCHY AND FOCUSED: Under 65 words per prompt.
                        2. DYNAMIC SCENE DIVERSITY: Every scene must have a different sub-location and camera angle (Scene 1: arrival on road, Scene 2: walking through market, Scene 3: close-up reaction, Scene 4: scenic riverside sunset, Scene 5: comedy mishap, Scene 6: night dinner). Do NOT repeat the vehicle in every shot.
                        3. STRICT CHARACTER LOCK: {c1_tag} ({c1_gender_desc}, {c1_dna}) and {c2_tag} ({c2_gender_desc}, {c2_dna}). {art_prompt}.
                        4. CLEAN FRAME: Single standalone image, zero split screen, zero duplicate panels, zero text, zero subtitles, no watermark.

                        Format for each scene:
                        #scene[N] A cinematic 16:9 4K photography keyframe still image. Setting: [specific distinct sub-spot in {location_dna}]. Characters: {c1_tag} ({c1_gender_desc}) and {c2_tag} ({c2_gender_desc}) [describe distinct physical action and expressive face]. {art_prompt}. Masterwork 8k resolution, shot on 35mm lens, cinematic lighting, identical facial likeness to character reference sheet with zero drift, clean frame, no text, no watermark.

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
                        #scene[N] Animate directly from the reference keyframe into a single continuous 10-second cinematic clip in 16:9 widescreen, 4K HDR. Beginning from the exact static keyframe pose, {c1_tag} ({c1_gender_desc}) and {c2_tag} ({c2_gender_desc}) [describe physical micro-actions picking up smoothly from the image]. Strictly preserve exact facial likeness, clothing, and environment from input keyframe with zero drift. {art_prompt}. Voice assignment: {c1_tag} uses voice {c1_voice}; {c2_tag} uses voice {c2_voice}. Dialogue line (spoken audio only, never render text): [Speaker] says, "[Natural funny dialogue in Khmer language]" Clean frame, no subtitles, no text on screen, no watermark.
                        
                        Rules:
                        - Start with #scene1, #scene2... up to #scene{num_clips}.
                        - Leave exactly ONE empty line between prompts.
                        """
                    else: # Text to Video
                        system_prompt = f"""
                        You are an elite Hollywood Director for Google Flow (Veo) and AI video generators.
                        Generate exactly {num_clips} continuous 10-second cinematic video prompts.

                        STRICT MASTER DIRECTIVES (FAITHFUL STORY & SMART CHARACTER MAPPING):
                        1. STORY FIDELITY & SMART CHARACTER SQUAD CONSOLIDATION:
                           - If the user provides a custom script or scene-by-scene story (such as mirror reflection, Bioaqua mask, teasing, selfie), YOU MUST 100% FAITHFULLY FOLLOW THE USER'S EXACT SCENES, PLOT, JOKES, AND DIALOGUE! Do NOT replace it with travel/asking-mom stories!
                           - SMART CHARACTER CONSOLIDATION: If the user's custom story mentions many characters (e.g. សីម៉ា, អាណា, លីសា, តុលា, សុផា), but only {len(chars_data)} characters are configured in this tool ({tags_str}), SMARTLY CONSOLIDATE AND MAP all the roles, dialogues, and funny teasing into the active characters ({tags_str})! Keep all the humor, the Bioaqua masking, the uneven mask jokes, and the final selfie punchline 100% intact!
                           - (Only if the user gave a very generic prompt like 'តួអង្គទាំងពីរទៅដើរលេង', follow the 3-act travel arc: Scene 1 Asking Mom / Call, Scene 2 Packing & Pickup, Scene 3 On the road, Scene 4 Pit stop, Scene 5 Destination, Scene 6 Meaningful ending).

                        2. STRICT CLOTHING & APPEARANCE LOCK (ZERO CLOTHING DRIFT):
{clothing_directives}
                           - Characters MUST strictly wear their configured outfit in every scene. ABSOLUTELY NO DENIM JACKETS, NO SWEATERS, NO OUTFIT CHANGES unless the script explicitly specifies changing into something (like applying a Bioaqua face mask).

                        3. ABSOLUTE ZERO SPEECH BUBBLES & ZERO ON-SCREEN TEXT:
                           - Clean cinematic video frame. Absolutely NO speech bubbles, NO comic text balloons, NO floating text, NO subtitles, NO typography rendered on screen.

                        4. PUNCHY & CONCISE: Every scene prompt must be around 65-75 words. Never write long bloated essays.

                        5. CHARACTER SQUAD LOCK ({len(chars_data)} CHARACTERS):
{squad_summary}
{c3_desc}
                           - All characters have identical facial likeness to character reference sheet with zero drift. Distinct individuals.

                        Format for each prompt (follow this exact structure):
                        #scene[N] A cinematic 10-second 4K clip in 16:9 widescreen. Setting: [specific distinct sub-location for this scene]. Action: {tags_str} [describe dynamic squad action, group interactions, and expressions matching the user's story beat]. [Camera movement]. Photorealistic live-action, natural lighting. Identical facial features and exact clothing matching character reference image with zero outfit change, no added jackets, zero clothing drift. Clean cinematic live-action frame, absolute zero speech bubbles, zero comic text balloons, no subtitles, zero on-screen typography, no watermark. Voice assignment: {voice_rules}. Audio dialogue track only (do NOT render visual speech balloon or text): [Speaker] says, "[Short natural funny dialogue in Khmer language matching the story]"

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
            dm = re.search(r'says,\s*"([^"]+)"', sc)
            if dm:
                khmer_dialogues.append((idx, dm.group(1)))

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
                    turnaround_prompt = f"Ultra-detailed character turnaround reference sheet of {c['tag']} ({c['gender_desc']}, {c['dna']}). Solid clean white background, 8 distinct angles in a 2x4 grid: top row displays full-body front view, three-quarter turn, side profile view, and back view; bottom row displays high-detail close-up facial portraits front view, 3/4 turn smiling, side profile, and 45-degree angle. Masterpiece studio photography, uniform natural soft lighting, razor-sharp focus, consistent facial geometry and identical clothing across all angles, zero morphing, zero blur, professional model sheet."
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
            dialogue_match = re.search(r'says,\s*"([^"]+)"', scene_content)
            khmer_speech = dialogue_match.group(1) if dialogue_match else None
            
            with st.container():
                st.markdown(f'<div class="scene-box"><span style="font-weight:700; color:#fb7185;">🎬 ឈុតទី {idx} (10 វិនាទី)</span> | <span style="font-size:12px; color:#22c55e;">🔒 Custom Locked Continuity</span></div>', unsafe_allow_html=True)
                
                c_left, c_right = st.columns([2, 1])
                with c_left:
                    st.code(full_scene_str, language="text")
                with c_right:
                    if khmer_speech:
                        st.markdown(f"🗣️ **Script និយាយ:** *\"{khmer_speech}\"*")
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
            dm = re.search(r'says,\s*"([^"]+)"', sc)
            kh_text = dm.group(1) if dm else f"ឈុតទី {i}"
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
