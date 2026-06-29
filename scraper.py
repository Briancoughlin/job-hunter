import time
import requests
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
}


UK_LOCATION_TERMS = {"uk", "united kingdom", "england", "worldwide", "global", "anywhere", "remote"}


def _location_ok(location_str: str) -> bool:
    """Return True if the role's location is compatible with a UK-based candidate."""
    if not location_str:
        return True
    return any(term in location_str.lower() for term in UK_LOCATION_TERMS)


def _remotive(term: str, results_wanted: int) -> list[dict]:
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
            if not _location_ok(loc):
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


def _weworkremotely(term: str) -> list[dict]:
    """We Work Remotely RSS — free, no auth."""
    import xml.etree.ElementTree as ET
    import urllib.parse

    url = f"https://weworkremotely.com/remote-jobs/search.rss?term={urllib.parse.quote(term)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        jobs = []
        for item in root.findall(".//item"):
            def tag(name):
                el = item.find(name)
                return el.text.strip() if el is not None and el.text else ""

            title_raw = tag("title")
            # WWR title format: "Company: Job Title"
            if ": " in title_raw:
                company, title = title_raw.split(": ", 1)
            else:
                company, title = "", title_raw

            jobs.append({
                "site": "weworkremotely",
                "title": title,
                "company": company,
                "location": "Remote",
                "job_url": tag("link"),
                "date_posted": tag("pubDate")[:10],
                "description": tag("description")[:3000],
                "job_type": "",
            })
        return jobs
    except Exception as e:
        print(f"  [weworkremotely] failed for '{term}': {e}")
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
) -> pd.DataFrame:
    all_jobs = []

    for term in search_terms:
        print(f"Searching: {term}")

        jobs = _remotive(term, results_per_term)
        if jobs:
            print(f"  [remotive] {len(jobs)} roles")
            all_jobs.extend(jobs)
        time.sleep(0.5)

        jobs = _weworkremotely(term)
        if jobs:
            print(f"  [weworkremotely] {len(jobs)} roles")
            all_jobs.extend(jobs)
        time.sleep(0.5)

        jobs = _jobspy_linkedin(term, location, results_per_term, remote_only)
        if jobs:
            print(f"  [linkedin] {len(jobs)} roles")
            all_jobs.extend(jobs)
        time.sleep(1)

    if not all_jobs:
        return pd.DataFrame()

    df = pd.DataFrame(all_jobs)
    df = df.drop_duplicates(subset=["title", "company"], keep="first")
    return df.reset_index(drop=True)


def build_search_terms(profile: dict) -> list[str]:
    seniority = profile.get("seniority", "senior").title()
    domains = profile.get("domains") or []
    industries = profile.get("industries") or []

    terms = [
        "Senior Technical Product Manager",
        "Senior Product Manager",
    ]

    domain_map = {
        "Community Platforms": "Senior Product Manager Community",
        "Developer Tools": "Senior Product Manager Developer Tools",
        "Gaming & Interactive Media": "Senior Product Manager Gaming",
        "Search & Discovery": "Senior Product Manager Search",
        "Trust & Safety": "Senior Product Manager Trust Safety",
        "Data & Analytics": "Senior Product Manager Data Analytics",
        "Platform Strategy": "Head of Product Platform",
        "Go-to-Market Enablement": "Senior Product Manager GTM",
    }

    for domain in domains + industries:
        mapped = domain_map.get(domain)
        if mapped and mapped not in terms:
            terms.append(mapped)

    terms += [
        "Director of Product Management",
        "Group Product Manager",
        "Principal Product Manager",
    ]

    seen = []
    for t in terms:
        if t not in seen:
            seen.append(t)
    return seen[:8]
