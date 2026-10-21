import re
import time

import pandas as pd
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
}


GLOBAL_LOCATION_TERMS = {"worldwide", "global", "anywhere"}

# Extra names a remote job board may use for a candidate's country or region.
LOCATION_ALIASES = {
    "united kingdom": {"uk", "england", "scotland", "wales", "northern ireland", "britain", "europe", "emea"},
    "uk": {"united kingdom", "england", "scotland", "wales", "northern ireland", "britain", "europe", "emea"},
    "ireland": {"europe", "emea", "eu"},
    "germany": {"europe", "emea", "eu"},
    "france": {"europe", "emea", "eu"},
    "netherlands": {"europe", "emea", "eu"},
    "spain": {"europe", "emea", "eu"},
    "united states": {"usa", "us", "north america", "americas"},
    "usa": {"united states", "us", "north america", "americas"},
    "canada": {"north america", "americas"},
}


def _location_terms(candidate_location: str) -> set[str]:
    """Lower-cased place names that match a candidate location such as 'Dublin, Ireland'."""
    parts = {p.strip().lower() for p in candidate_location.split(",") if p.strip()}
    terms = set(parts)
    for part in parts:
        terms |= LOCATION_ALIASES.get(part, set())
    return terms


def _location_ok(location_str: str, candidate_location: str = "") -> bool:
    """Return True if a role's required location is compatible with the candidate's location."""
    if not location_str or not candidate_location.strip():
        return True
    loc = location_str.lower()
    if any(term in loc for term in GLOBAL_LOCATION_TERMS) or loc.strip() == "remote":
        return True
    words = set(re.findall(r"[a-z]+", loc))
    for term in _location_terms(candidate_location):
        # Short codes like "uk"/"us"/"eu" must match a whole word, not part of "russia".
        if (term in words) if len(term) <= 3 else (term in loc):
            return True
    return False


def _remotive(term: str, results_wanted: int, candidate_location: str = "") -> list[dict]:
    """Remotive public API — free, no auth, remote jobs only."""
    try:
        resp = requests.get(
            "https://remotive.com/api/remote-jobs",
            params={"search": term, "limit": results_wanted * 2},  # fetch extra to allow filtering
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
        results = []
        for j in jobs:
            loc = j.get("candidate_required_location") or "Worldwide"
            if not _location_ok(loc, candidate_location):
                continue
            results.append({
                "site": "remotive",
                "title": j.get("title", ""),
                "company": j.get("company_name", ""),
                "location": loc,
                "job_url": j.get("url", ""),
                "date_posted": (j.get("publication_date") or "")[:10],
                "description": j.get("description", "")[:3000],
                "job_type": j.get("job_type", ""),
            })
        return results[:results_wanted]
    except Exception as e:
        print(f"  [remotive] failed for '{term}': {e}")
        return []


def _jobicy(term: str, results_wanted: int, candidate_location: str = "") -> list[dict]:
    """Jobicy public API — free, no auth, remote jobs only."""
    try:
        resp = requests.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"count": min(results_wanted, 50), "tag": term},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
        results = []
        for j in jobs:
            loc = j.get("jobGeo") or "Remote"
            if not _location_ok(loc, candidate_location):
                continue
            results.append({
                "site": "jobicy",
                "title": j.get("jobTitle", ""),
                "company": j.get("companyName", ""),
                "location": loc,
                "job_url": j.get("url", ""),
                "date_posted": (j.get("pubDate") or "")[:10],
                "description": j.get("jobDescription", "")[:3000],
                "job_type": j.get("jobType", ""),
            })
        return results
    except Exception as e:
        print(f"  [jobicy] failed for '{term}': {e}")
        return []


def _jobspy_linkedin(term: str, location: str, results_wanted: int, remote_only: bool) -> list[dict]:
    """LinkedIn via jobspy — best-effort, may 403."""
    try:
        from jobspy import scrape_jobs
        df = scrape_jobs(
            site_name=["linkedin"],
            search_term=term,
            location=location,
            results_wanted=results_wanted,
            is_remote=remote_only,
        )
        if df is None or df.empty:
            return []
        keep = ["site", "job_url", "title", "company", "location", "date_posted",
                "description", "job_type", "min_amount", "max_amount"]
        available = [c for c in keep if c in df.columns]
        return df[available].to_dict("records")
    except Exception as e:
        if "403" in str(e):
            print(f"  [linkedin] blocked (403) for '{term}' — skipping")
        else:
            print(f"  [linkedin] failed for '{term}': {e}")
        return []


def fetch_jobs(
    search_terms: list[str],
    location: str = "Remote",
    results_per_term: int = 25,
    remote_only: bool = True,
    candidate_location: str = "",
) -> tuple[pd.DataFrame, dict]:
    """Search all sources. candidate_location (e.g. "Dublin, Ireland") filters remote
    roles that are restricted to other countries; empty means no filtering."""
    all_jobs = []
    source_counts: dict[str, int] = {"remotive": 0, "jobicy": 0, "linkedin": 0}

    for term in search_terms:
        print(f"Searching: {term}")

        jobs = _remotive(term, results_per_term, candidate_location)
        source_counts["remotive"] += len(jobs)
        all_jobs.extend(jobs)
        time.sleep(0.5)

        jobs = _jobicy(term, results_per_term, candidate_location)
        source_counts["jobicy"] += len(jobs)
        all_jobs.extend(jobs)
        time.sleep(0.5)

        jobs = _jobspy_linkedin(term, location, results_per_term, remote_only)
        source_counts["linkedin"] += len(jobs)
        all_jobs.extend(jobs)
        time.sleep(1)

    if not all_jobs:
        return pd.DataFrame(), source_counts

    df = pd.DataFrame(all_jobs)
    df = df.drop_duplicates(subset=["title", "company"], keep="first")
    return df.reset_index(drop=True), source_counts


SENIORITY_PREFIXES = ("junior", "graduate", "senior", "sr", "lead", "staff", "principal")

# Title prefix for the candidate's level, and for the next step up.
SENIORITY_LADDER = {
    "junior": ("Junior", ""),
    "mid": ("", "Senior"),
    "senior": ("Senior", "Lead"),
    "staff": ("Staff", "Principal"),
    "principal": ("Principal", "Head of"),
}


def _core_role(title: str) -> str:
    """'Senior Technical Product Manager' -> 'Technical Product Manager'."""
    words = title.replace(".", "").split()
    while words and words[0].lower() in SENIORITY_PREFIXES:
        words = words[1:]
    return " ".join(words)


def build_search_terms(profile: dict, max_terms: int = 8) -> list[str]:
    """Derive job-board search terms from the parsed CV: the current title, a
    seniority-adjusted and a next-step version of it, then recent past titles."""
    current = (profile.get("current_title") or "").strip()
    past = [t.strip() for t in (profile.get("past_titles") or []) if t and t.strip()]
    seniority = (profile.get("seniority") or "").strip().lower()

    terms = []
    if current:
        terms.append(current)
        core = _core_role(current)
        level, next_level = SENIORITY_LADDER.get(seniority, ("", ""))
        if core:
            for prefix in (level, next_level):
                terms.append(f"{prefix} {core}".strip())
            if not level:
                terms.append(core)
    terms += past[:4]

    seen = []
    for t in terms:
        if t and t.lower() not in {s.lower() for s in seen}:
            seen.append(t)
    return seen[:max_terms]
