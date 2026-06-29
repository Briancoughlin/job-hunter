import os
import json
import tempfile
import anthropic
import streamlit as st
import pandas as pd
from dotenv import load_dotenv, set_key

from resume_parser import parse_resume
from scraper import fetch_jobs, build_search_terms
from scorer import score_all_jobs

load_dotenv()

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "saved_profile.json")
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")


def load_profile() -> dict | None:
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH) as f:
            return json.load(f)
    return None


def save_profile(profile: dict):
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)


def save_env_key(key: str, value: str):
    if not os.path.exists(ENV_PATH):
        open(ENV_PATH, "w").close()
    set_key(ENV_PATH, key, value)


st.set_page_config(page_title="Job Hunter", page_icon="🎯", layout="wide")

st.markdown("""
<link rel="manifest" href="/app/static/manifest.json">
<meta name="theme-color" content="#ff4b4b">
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/app/static/sw.js');
  }
</script>
""", unsafe_allow_html=True)

st.title("🎯 Job Hunter")
st.caption("Upload your LinkedIn profile, find roles most likely to get you an interview.")

# --- Sidebar: config ---
with st.sidebar:
    st.header("Configuration")

    api_key = st.text_input(
        "API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Your Anthropic API key (or internal LLM gateway key)",
    )
    if api_key and api_key != os.getenv("ANTHROPIC_API_KEY", ""):
        save_env_key("ANTHROPIC_API_KEY", api_key)
        os.environ["ANTHROPIC_API_KEY"] = api_key

    base_url = st.text_input(
        "API Base URL (optional)",
        value=os.getenv("ANTHROPIC_BASE_URL", ""),
        help="Leave blank for standard Anthropic. Set this if your organisation has an internal LLM gateway.",
    )
    if base_url and base_url != os.getenv("ANTHROPIC_BASE_URL", ""):
        save_env_key("ANTHROPIC_BASE_URL", base_url)
        os.environ["ANTHROPIC_BASE_URL"] = base_url

    st.divider()
    st.subheader("Search settings")

    remote_only = st.checkbox("Remote roles only", value=True)
    location = st.text_input("Location (for non-remote)", value="United Kingdom")
    results_per_term = st.slider("Results per search term", 10, 50, 25)
    min_score = st.slider("Minimum match score to show", 0, 100, 50)

    st.divider()
    st.subheader("Custom search terms")
    custom_terms = st.text_area(
        "Extra job titles to search (one per line)",
        placeholder="Senior Product Manager\nDirector of Engineering",
    )

# --- Session state ---
if "profile" not in st.session_state:
    st.session_state.profile = load_profile()
if "results" not in st.session_state:
    st.session_state.results = []
if "applied" not in st.session_state:
    st.session_state.applied = set()
if "saved" not in st.session_state:
    st.session_state.saved = set()

# --- Step 1: Upload resume ---
st.header("Step 1: Upload your LinkedIn PDF")
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Export your LinkedIn profile as PDF (Me → Resources → Save to PDF)",
        type=["pdf"],
    )

with col2:
    if st.session_state.profile:
        p = st.session_state.profile
        st.success("Profile loaded")
        st.write(f"**{p.get('name', 'Unknown')}**")
        st.write(f"{p.get('current_title', '')} · {p.get('seniority', '').title()}")
        st.write(f"{p.get('years_experience', '?')} years experience")
        if os.path.exists(PROFILE_PATH):
            st.caption("Saved — will reload automatically next time")
        if st.button("Clear profile", use_container_width=True):
            st.session_state.profile = None
            st.session_state.results = []
            if os.path.exists(PROFILE_PATH):
                os.remove(PROFILE_PATH)
            st.rerun()

if uploaded_file and not st.session_state.profile:
    if not api_key:
        st.error("Add your API key in the sidebar first.")
    else:
        with st.spinner("Parsing your resume with Claude..."):
            try:
                client = anthropic.Anthropic(api_key=api_key, base_url=base_url or None)
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                profile = parse_resume(tmp_path, client)
                save_profile(profile)
                st.session_state.profile = profile
                st.success(f"Profile loaded and saved for **{profile.get('name', 'you')}**")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to parse resume: {e}")

# Show parsed profile in expander
if st.session_state.profile:
    with st.expander("View parsed profile", expanded=False):
        p = st.session_state.profile
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Skills**")
            for s in (p.get("skills") or [])[:15]:
                st.write(f"• {s}")
        with col2:
            st.write("**Domains**")
            for d in (p.get("domains") or []):
                st.write(f"• {d}")
            st.write("**Industries**")
            for i in (p.get("industries") or []):
                st.write(f"• {i}")
        with col3:
            st.write("**Past titles**")
            for t in (p.get("past_titles") or [])[:5]:
                st.write(f"• {t}")
        st.write("**Summary**")
        st.write(p.get("summary", ""))

# --- Step 2: Search ---
st.header("Step 2: Find matching roles")

if st.session_state.profile:
    profile = st.session_state.profile
    auto_terms = build_search_terms(profile)
    extra_terms = [t.strip() for t in custom_terms.strip().splitlines() if t.strip()]
    all_terms = list(dict.fromkeys(auto_terms + extra_terms))

    st.write(f"Will search for: {', '.join(f'`{t}`' for t in all_terms)}")

    if st.button("🔍 Search & Score Jobs", type="primary", use_container_width=True):
        if not api_key:
            st.error("Add your API key in the sidebar first.")
        else:
            print(f"[app] using base_url={base_url!r} key={api_key[:10]}...", flush=True)
            client = anthropic.Anthropic(api_key=api_key, base_url=base_url or None)

            with st.spinner("Scraping job boards..."):
                try:
                    jobs_df, source_counts = fetch_jobs(
                        search_terms=all_terms,
                        location=location if not remote_only else "Remote",
                        results_per_term=results_per_term,
                        remote_only=remote_only,
                    )
                except Exception as e:
                    st.error(f"Scraping failed: {e}")
                    jobs_df = pd.DataFrame()
                    source_counts = {}

            if source_counts:
                cols = st.columns(len(source_counts))
                for col, (src, count) in zip(cols, source_counts.items()):
                    col.metric(src.title(), count, help=f"Roles found from {src}")

            if jobs_df.empty:
                st.warning("No jobs found — all sources returned 0 results. Job boards may be rate-limiting. Try again in a few minutes or add custom search terms.")
            else:
                st.info(f"Found {len(jobs_df)} unique roles. Scoring with Claude...")
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(i, total, title, company):
                    progress_bar.progress((i + 1) / total)
                    status_text.text(f"Scoring {i+1}/{total}: {title} at {company}")

                results = score_all_jobs(jobs_df, profile, client, update_progress)
                st.session_state.results = results
                progress_bar.empty()
                status_text.empty()

                # Surface scoring errors if everything came back 0
                all_zero = all(r.get("overall_score", 0) == 0 for r in results)
                if all_zero and results:
                    first_gaps = results[0].get("gaps", [])
                    error_msg = next((g for g in first_gaps if "Scoring error" in g), None)
                    if error_msg:
                        st.error(f"Scoring failed for all roles — {error_msg}")
                    else:
                        st.warning("All roles scored 0. Check your API key and Base URL in the sidebar.")
                else:
                    st.success(f"Done! Scored {len(results)} roles.")
                st.rerun()
else:
    st.info("Upload your LinkedIn PDF above to get started.")

# --- Step 3: Results dashboard ---
if st.session_state.results:
    st.header("Step 3: Your matches")

    results = st.session_state.results
    filtered = [r for r in results if r.get("overall_score", 0) >= min_score]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total roles found", len(results))
    col2.metric(f"Above {min_score} score", len(filtered))
    col3.metric("Recommended", sum(1 for r in results if r.get("recommended")))
    col4.metric("Applied", len(st.session_state.applied))

    tab_all, tab_recommended, tab_saved, tab_applied = st.tabs(
        ["All matches", "Recommended", "Saved", "Applied"]
    )

    def render_job_card(job, idx, tab):
        score = job.get("overall_score", 0)
        prob = job.get("interview_probability", "unknown")
        recommended = job.get("recommended", False)

        if score >= 75:
            score_color = "🟢"
        elif score >= 55:
            score_color = "🟡"
        else:
            score_color = "🔴"

        job_id = job.get("job_url", str(idx))
        is_saved = job_id in st.session_state.saved
        is_applied = job_id in st.session_state.applied
        key_prefix = f"{tab}_{idx}_{job_id}"

        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                title = job.get("title", "Unknown role")
                company = job.get("company", "Unknown company")
                url = job.get("job_url", "")
                if url:
                    st.markdown(f"### [{title}]({url})")
                else:
                    st.markdown(f"### {title}")
                st.write(f"**{company}** · {job.get('location', 'Remote')} · {job.get('site', '').title()}")
                posted = job.get("date_posted", "")
                if posted:
                    st.caption(f"Posted: {posted}")
            with col2:
                st.metric("Match score", f"{score_color} {score}/100")
                st.write(f"Interview: **{prob}**")
                if recommended:
                    st.success("✓ Recommended")
            with col3:
                if st.button("💾 Save" if not is_saved else "✓ Saved", key=f"save_{key_prefix}"):
                    if is_saved:
                        st.session_state.saved.discard(job_id)
                    else:
                        st.session_state.saved.add(job_id)
                    st.rerun()
                if st.button("✅ Mark applied" if not is_applied else "Applied", key=f"apply_{key_prefix}"):
                    if is_applied:
                        st.session_state.applied.discard(job_id)
                    else:
                        st.session_state.applied.add(job_id)
                    st.rerun()

            with st.expander("Fit analysis"):
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Skills match", f"{job.get('skills_match', 0)}%")
                col_b.metric("Seniority match", f"{job.get('seniority_match', 0)}%")
                col_c.metric("Domain match", f"{job.get('domain_match', 0)}%")

                if job.get("strengths"):
                    st.write("**Strengths:**")
                    for s in job["strengths"]:
                        st.write(f"✓ {s}")
                if job.get("gaps"):
                    st.write("**Gaps:**")
                    for g in job["gaps"]:
                        st.write(f"✗ {g}")
                st.write("**Summary:**")
                st.write(job.get("fit_summary", ""))

    def render_list(jobs_list, tab, empty_msg="No roles here yet."):
        if not jobs_list:
            st.info(empty_msg)
            return
        for idx, job in enumerate(jobs_list):
            render_job_card(job, idx, tab)

    with tab_all:
        render_list(filtered, "all", "No roles above your minimum score threshold.")

    with tab_recommended:
        render_list(
            [r for r in filtered if r.get("recommended")],
            "recommended",
            "No recommended roles above your score threshold.",
        )

    with tab_saved:
        render_list(
            [r for r in results if r.get("job_url", "") in st.session_state.saved],
            "saved",
            "You haven't saved any roles yet.",
        )

    with tab_applied:
        render_list(
            [r for r in results if r.get("job_url", "") in st.session_state.applied],
            "applied",
            "No applications tracked yet.",
        )

    st.divider()
    if st.button("📥 Export results to CSV"):
        df = pd.DataFrame(filtered)
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "job_matches.csv", "text/csv")
