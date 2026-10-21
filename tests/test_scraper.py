import pytest

from scraper import _location_ok, build_search_terms

PM_PROFILE = {
    "current_title": "Senior Technical Product Manager",
    "seniority": "senior",
    "past_titles": ["Senior Technical Product Manager", "Product Manager", "Business Analyst"],
}

DEV_PROFILE = {
    "current_title": "Senior PL/SQL Developer",
    "seniority": "senior",
    "past_titles": ["Oracle PL/SQL Developer", "Java Developer"],
}


def test_pm_profile_gets_pm_terms():
    terms = build_search_terms(PM_PROFILE)
    assert terms[0] == "Senior Technical Product Manager"
    assert "Lead Technical Product Manager" in terms
    assert "Product Manager" in terms
    assert terms.count("Senior Technical Product Manager") == 1


def test_developer_profile_gets_no_pm_terms():
    terms = build_search_terms(DEV_PROFILE)
    assert terms[0] == "Senior PL/SQL Developer"
    assert "Java Developer" in terms
    assert not any("Product Manager" in t for t in terms)


def test_mid_level_adds_next_step_and_plain_title():
    terms = build_search_terms({"current_title": "Data Engineer", "seniority": "mid"})
    assert terms == ["Data Engineer", "Senior Data Engineer"]


def test_empty_profile_gives_no_terms():
    assert build_search_terms({}) == []


def test_terms_are_capped():
    profile = {"current_title": "Engineer", "seniority": "senior", "past_titles": [f"Role {i}" for i in range(20)]}
    assert len(build_search_terms(profile, max_terms=5)) == 5


@pytest.mark.parametrize(
    "role_location, candidate, expected",
    [
        ("UK", "United Kingdom", True),
        ("Europe", "United Kingdom", True),
        ("USA only", "United Kingdom", False),
        ("Worldwide", "United Kingdom", True),
        ("Remote", "United Kingdom", True),
        ("Ireland", "Dublin, Ireland", True),
        ("EMEA", "Dublin, Ireland", True),
        ("UK only", "Dublin, Ireland", False),
        ("Dublin", "Dublin, Ireland", True),
        ("Russia", "United States", False),  # "us" must not match inside "russia"
        ("US", "United States", True),
        ("Canada", "", True),  # blank location means no filtering
        ("", "United Kingdom", True),
    ],
)
def test_location_filter(role_location, candidate, expected):
    assert _location_ok(role_location, candidate) is expected
