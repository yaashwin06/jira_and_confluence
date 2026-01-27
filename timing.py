import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import csv
import pytz

# ---------- USER INPUT ----------
JIRA_BASE_URL = input("Enter Jira Base URL (e.g. https://your-domain.atlassian.net): ").rstrip("/")
EMAIL = input("Enter Jira Email: ")
API_TOKEN = input("Enter Jira API Token: ")
PROJECT_KEY = input("Enter Jira Project Key (e.g. T1): ")

MAX_RESULTS = 150
EXPORT_CSV = True
CSV_FILENAME = "latest_assignee.csv"
# --------------------------------

auth = HTTPBasicAuth(EMAIL, API_TOKEN)
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# ---------- FUNCTION: FETCH ALL ISSUES ----------
def fetch_all_issues(project_key):
    print(f"\nFetching all issues from project: {project_key}")
    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    all_issues = []
    start_at = 0

    while True:
        params = {
            "jql": f"project = {project_key}",
            "startAt": start_at,
            "maxResults": MAX_RESULTS,
            "fields": "key",
            "expand": "changelog"
        }

        response = requests.get(url, headers=headers, auth=auth, params=params)

        if response.status_code != 200:
            print(f"❌ Error fetching issues: {response.status_code}")
            print(response.text)
            break

        data = response.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)

        print(f"Fetched {len(issues)} issues (startAt={start_at})")

        if start_at + len(issues) >= data.get("total", 0):
            break

        start_at += len(issues)

    print(f"\n✅ Total issues fetched: {len(all_issues)}\n")
    return all_issues

# ---------- FUNCTION: GET LATEST ASSIGNEE CHANGE ----------
def get_latest_assignee_from_data(issue_data):
    latest_change = None

    for history in issue_data.get("changelog", {}).get("histories", []):
        changed_at = history.get("created")
        for item in history.get("items", []):
            if item.get("field") == "assignee":
                if latest_change is None or changed_at > latest_change["changed_at"]:
                    latest_change = {
                        "changed_at": changed_at,
                        "from": item.get("fromString", "Unassigned"),
                        "to": item.get("toString", "Unassigned")
                    }
    return latest_change

# ---------- FUNCTION: CONVERT TO IST ----------
def convert_to_ist(timestamp_str):
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        ist = pytz.timezone("Asia/Kolkata")
        dt_ist = dt.astimezone(ist)
        return dt_ist.strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception as e:
        print(f"⚠️ Timestamp conversion error: {e}")
        return timestamp_str

# ---------- MAIN ----------
if __name__ == "__main__":
    issues = fetch_all_issues(PROJECT_KEY)
    results = []

    for issue in issues:
        key = issue.get("key")
        latest = get_latest_assignee_from_data(issue)

        if latest:
            ist_time = convert_to_ist(latest["changed_at"])
            print(f"{key} | {ist_time}")
            results.append([key, ist_time])
        else:
            print(f"{key} | No assignee changes found")
            results.append([key, ""])

    # ---------- CSV EXPORT ----------
    if EXPORT_CSV:
        with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Issue Key", "Last Assignee Change Date (IST)"])
            writer.writerows(results)

        print(f"\n📁 Results exported to {CSV_FILENAME}")
