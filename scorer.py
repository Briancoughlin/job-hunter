import json
import os
import anthropic
from dotenv import load_dotenv
load_dotenv()


SCORE_PROMPT = """You are an expert recruiter. Score how well this candidate profile matches this job posting.
The candidate is based in the UK. Roles that are US-only or exclude UK candidates should be scored lower on location fit.

CANDIDATE PROFILE:
{profile}

JOB POSTING:
Title: {title}
Company: {company}
Location: {location}
Description:
{description}

Score the match and return ONLY valid JSON:
{{
  "overall_score": <0-100 integer>,
  "interview_probability": "low|medium|high|very high",
  "skills_match": <0-100>,
  "seniority_match": <0-100>,
  "domain_match": <0-100>,
  "strengths": ["strength1", "strength2", "strength3"],
  "gaps": ["gap1", "gap2"],
  "fit_summary": "2-3 sentence explanation of why this is or isn't a good fit",
  "recommended": <true|false>
}}

Be honest and calibrated. A score above 75 means genuinely strong match likely to get an interview callback."""


def score_job(job: dict, profile: dict, client: anthropic.Anthropic) -> dict:
    description = (job.get("description") or "")[:3000]  # truncate to save tokens

    prompt = SCORE_PROMPT.format(
        profile=json.dumps(profile, indent=2),
        title=job.get("title", ""),
        company=job.get("company", ""),
        location=job.get("location", ""),
        description=description,
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text.strip()
        print(f"[scorer] raw response: {content[:200]}", flush=True)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())
    except Exception as e:
        print(f"[scorer] ERROR: {e}", flush=True)
        import traceback; traceback.print_exc()
        return {
            "overall_score": 0,
            "interview_probability": "unknown",
            "skills_match": 0,
            "seniority_match": 0,
            "domain_match": 0,
            "strengths": [],
            "gaps": [f"Scoring error: {e}"],
            "fit_summary": "Could not score this role.",
            "recommended": False,
        }


def score_all_jobs(jobs_df, profile: dict, client: anthropic.Anthropic, progress_callback=None):
    results = []
    total = len(jobs_df)

    for i, (_, row) in enumerate(jobs_df.iterrows()):
        if progress_callback:
            progress_callback(i, total, row.get("title", ""), row.get("company", ""))

        score = score_job(row.to_dict(), profile, client)
        result = row.to_dict()
        result.update(score)
        results.append(result)

    return sorted(results, key=lambda x: x.get("overall_score", 0), reverse=True)
