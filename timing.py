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
# # # Jira Project Generator - Company-Managed Projects
# # # Automatically creates Company-managed Jira projects with Epics and Stories
# # # Custom fields are added to project-specific screens
# # # Uses .env file for credentials

# # # FIXED VERSION - Proper screen discovery and field context handling
# # # """

# # # import requests
# # # import base64
# # # import json
# # # import re
# # # import sys
# # # import os
# # # import time
# # # from datetime import datetime, timedelta
# # # from typing import Dict, List, Optional, Tuple
# # # from pathlib import Path
# # # import getpass

# # # # try:
# # # #     from dotenv import load_dotenv
# # # # except ImportError:
# # # #     print("\n❌ Error: python-dotenv package not found!")
# # # #     print("Install it with: pip install python-dotenv")
# # # #     print()
# # # #     sys.exit(1)

# # # # load_dotenv()

# # # # ---------- CREDENTIALS (from .env file) ----------
# # # # JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
# # # # JIRA_EMAIL = os.getenv("JIRA_EMAIL")
# # # # JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# # # # Company-managed project templates
# # # VALID_TEMPLATES = {
# # #     "1": ("Kanban", "com.pyxis.greenhopper.jira:gh-kanban-template"),
# # #     "2": ("Scrum", "com.pyxis.greenhopper.jira:gh-scrum-template"),
# # #     "3": ("Bug Tracking", "com.atlassian.jira-core-project-templates:jira-core-project-management"),
# # # }

# # # # Project structure to create
# # # EPICS = {
# # #     "ASSESSMENT & PLANNING (2 - 12 weeks, depending on project scope, sizing, access, onboarding)": [
# # #         "Onboarding and Access - See Access Tab for Details",
# # #         "Introductory Call",
# # #         "Discuss NON-PRODUCTION environments",
# # #         "Set up Weekly Touchpoint w/Atlassian (if above 1000 users)",
# # #         "Discuss Atlassian Cloud Status",
# # #         "Start Atlassian CLOUD Trial (if needed)",
# # #         "Set up Weekly Touchpoint w/Project Team",
# # #         "Set up Atlassian Guard (if needed/in scope)",
# # #         "Open Ticket w/Atlassian for MOVE",
# # #         "Refresh lower instance of Jira to current version",
# # #         "Licensing Tier Jira",
# # #         "Licensing Tier Confluence",
# # #         "Discussion/Discovery Migration Scope for Confluence",
# # #         "Discussion/Discovery Migration Scope for Jira",
# # #         "Discussion/Discovery Integrations",
# # #         "Discussion/Discovery User Management",
# # #         "Start Atlassian Guard Trial (if needed/in scope)",
# # #         "User Clean Up Tasks",
# # #         "Jira - Add-on Assessment",
# # #         "Confluence - Add-on Assessment",
# # #         "Environment Assessment & Pre-Migration Checklist",
# # #         "Develop Migration Approach & Draft Runbook",
# # #         "Develop Testing Plan",
# # #         "Develop Communications Plan",
# # #         "Develop Training Plan (if needed)",
# # #         "Review & Acceptance - Environment Assessment",
# # #         "Review & Acceptance - Jira Projects Assessment",
# # #         "Review & Acceptance - Confluence Spaces",
# # #         "Review & Acceptance - Jira Add-ons",
# # #         "Review & Acceptance - Atlassian Guard Setup",
# # #         "Review & Acceptance - Confluence Addons",
# # #         "Review & Acceptance - Confluence Macros",
# # #         "Review & Acceptance - Integrations",
# # #         "Review & Acceptance - Pre Migration Checklists (Jira & Confluence)",
# # #         "Budget Review Meeting (T&M)",
# # #         "Refresh Staging Environments (Jira and Confluence)",
# # #         "<other tasks as identified>"
# # #     ],
# # #     "TEST MIGRATION (4 - 16 weeks, depending on scope, sizing, & capacity of Client)": [
# # #         "Execute User Migration using JCMA",
# # #         "Execute Complete test migration using JCMA",
# # #         "Transformation Tasks - Scriptrunner",
# # #         "Basic Application Integrity Tests",
# # #         "Workflow Review & Migration Assistant Errors",
# # #         "Working Session to review Migration Assistant Findings (if needed)",
# # #         "Execute Add-on Remediation Plan",
# # #         "Execute Confluence Migration using CCMA",
# # #         "Post migration checks Jira & Confluence"
# # #     ],
# # #     "USER ACCEPTANCE TESTING (1 - 2 weeks, depending on scope, sizing, & capacity of Client)": [
# # #         "Capula Project Team Testing",
# # #         "Hold UAT Training (if needed)",
# # #         "User Acceptance Testing",
# # #         "Issue Resolution",
# # #         "Go/No Go Decision (UAT Acceptance)"
# # #     ],
# # #     "PRODUCTION MIGRATION (TBD)": ["Finalize Migration Runbook", "See Migration Timeline Tab "],
# # #     "POST MIGRATION SUPPORT (4 weeks)": ["<items as identified>"],
# # # }

# # # # Expected custom fields with their types
# # # EXPECTED_FIELDS = {
# # #     "percent_complete": {
# # #         "name": "% Complete",
# # #         "field_id": None,
# # #         "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
# # #         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
# # #         "description": "Percentage of task completion"
# # #     },
# # #     "target_start": {
# # #         "name": "Target Start Date",
# # #         "field_id": None,
# # #         "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
# # #         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
# # #         "description": "Target start date for the task"
# # #     },
# # #     "target_end": {
# # #         "name": "Target End Date",
# # #         "field_id": None,
# # #         "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
# # #         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
# # #         "description": "Target end date for the task"
# # #     },
# # #     "owning": {
# # #         "name": "Owning",
# # #         "field_id": None,
# # #         "type": "com.atlassian.jira.plugin.system.customfieldtypes:userpicker",
# # #         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:userpickergroupsearcher",
# # #         "description": "Owner of the task"
# # #     }
# # # }


# # # class JiraProjectGenerator:
# # #     def __init__(self, base_url: str, email: str, api_token: str):
# # #         self.base_url = base_url.rstrip('/')
# # #         self.email = email
# # #         self.api_token = api_token
# # #         self.headers = self._get_auth_header() #Combines them as email:api_token and Encodes that string in Base64
# # #         self.debug_mode = False  # Set to True for verbose output shows logs

# # #     def _get_auth_header(self) -> dict:
# # #         """Generate Basic Auth header for Jira API"""
# # #         token = f"{self.email}:{self.api_token}"
# # #         b64 = base64.b64encode(token.encode()).decode()
# # #         return {
# # #             "Authorization": f"Basic {b64}",
# # #             "Content-Type": "application/json",
# # #             "Accept": "application/json"
# # #         }

# # #     def _log(self, message: str, level: str = "INFO"):
# # #         """Pretty logging with emoji indicators"""
# # #         icons = {
# # #             "INFO": "🔵",
# # #             "SUCCESS": "✅",
# # #             "ERROR": "❌",
# # #             "WARN": "⚠️",
# # #             "QUESTION": "❓",
# # #             "DEBUG": "🔍"
# # #         }
# # #         # Only show DEBUG messages if debug_mode is True
# # #         if level == "DEBUG" and not self.debug_mode:
# # #             return
# # #         print(f"{icons.get(level, '•')} {message}")

# # #     def suggest_project_key(self, name: str) -> str:
# # #         """Generate a suggested project key from project name"""
# # #         name_clean = re.sub(r'[^A-Za-z0-9 ]+', '', name).strip()
# # #         parts = name_clean.split()

# # #         if len(parts) == 1:
# # #             key = parts[0][:4].upper()
# # #         else:
# # #             key = ''.join(p[0] for p in parts if p)[:4].upper()

# # #         if len(key) < 2:
# # #             key = (key + "PR")[:2]

# # #         return key[:10]

# # #     def check_project_exists(self, project_key: str) -> bool:
# # #         """Check if a project with this key already exists"""
# # #         try:
# # #             url = f"{self.base_url}/rest/api/3/project/{project_key}"
# # #             r = requests.get(url, headers=self.headers, timeout=10)
# # #             return r.status_code == 200
# # #         except Exception:
# # #             return False

# # #     def test_connection(self) -> Tuple[bool, dict]:
# # #         """Test API connection and get current user info"""
# # #         try:
# # #             url = f"{self.base_url}/rest/api/3/myself"
# # #             r = requests.get(url, headers=self.headers, timeout=10)
# # #             r.raise_for_status()
# # #             return True, r.json()
# # #         except requests.exceptions.RequestException as e:
# # #             return False, {"error": str(e)}

# # #     def fetch_all_fields(self) -> List[dict]:
# # #         """Fetch all Jira fields to discover custom field IDs"""
# # #         url = f"{self.base_url}/rest/api/3/field"
# # #         r = requests.get(url, headers=self.headers, timeout=30)
# # #         r.raise_for_status()
# # #         return r.json()

# # #     def find_field_id(self, fields: List[dict], display_name: str) -> Optional[str]:
# # #         """Find field ID by display name (case-insensitive)"""
# # #         for f in fields:
# # #             if f.get("name", "").strip().lower() == display_name.strip().lower():
# # #                 return f.get("id")
# # #         return None

# # #     # ==================== SCREEN DISCOVERY - FIXED ====================

# # #     def get_project_screens_by_name(self, project_key: str) -> List[dict]:
# # #         """
# # #         Find screens that belong to this project by searching for project key in screen name.
# # #         This is the most reliable method for company-managed projects.
# # #         """
# # #         screens = []
# # #         start_at = 0
# # #         max_results = 100
        
# # #         self._log(f"  Searching for screens containing '{project_key}'...", "DEBUG")
        
# # #         while True:
# # #             url = f"{self.base_url}/rest/api/3/screens"
# # #             params = {"startAt": start_at, "maxResults": max_results}
            
# # #             try:
# # #                 r = requests.get(url, headers=self.headers, params=params, timeout=30)
# # #                 if r.status_code != 200:
# # #                     break
                    
# # #                 data = r.json()
# # #                 values = data.get("values", [])
                
# # #                 for screen in values:
# # #                     screen_name = screen.get("name", "")
# # #                     # Match screens that start with project key or contain ": Project Key"
# # #                     if (screen_name.startswith(f"{project_key}:") or 
# # #                         screen_name.startswith(f"{project_key} ") or
# # #                         f": {project_key}" in screen_name):
# # #                         screens.append({
# # #                             "id": screen.get("id"),
# # #                             "name": screen_name,
# # #                             "description": screen.get("description", "")
# # #                         })
# # #                         self._log(f"    Found: {screen_name} (ID: {screen.get('id')})", "DEBUG")
                
# # #                 if len(values) < max_results:
# # #                     break
# # #                 start_at += max_results
                
# # #             except Exception as e:
# # #                 self._log(f"Error searching screens: {e}", "WARN")
# # #                 break
        
# # #         return screens

# # #     def get_screen_scheme_for_project(self, project_key: str) -> Optional[dict]:
# # #         """Get screen scheme info by searching for project-named scheme"""
# # #         try:
# # #             url = f"{self.base_url}/rest/api/3/screenscheme"
# # #             params = {"startAt": 0, "maxResults": 100}
# # #             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
# # #             if r.status_code == 200:
# # #                 schemes = r.json().get("values", [])
# # #                 for scheme in schemes:
# # #                     scheme_name = scheme.get("name", "")
# # #                     if project_key in scheme_name:
# # #                         self._log(f"  Found Screen Scheme: {scheme_name}", "DEBUG")
# # #                         return scheme
# # #             return None
# # #         except Exception as e:
# # #             self._log(f"Error getting screen schemes: {e}", "WARN")
# # #             return None

# # #     def get_screens_from_screen_scheme(self, screen_scheme_id: str) -> List[dict]:
# # #         """Get all screens from a screen scheme"""
# # #         screens = []
# # #         try:
# # #             url = f"{self.base_url}/rest/api/3/screenscheme/{screen_scheme_id}"
# # #             r = requests.get(url, headers=self.headers, timeout=30)
            
# # #             if r.status_code == 200:
# # #                 data = r.json()
# # #                 screen_mappings = data.get("screens", {})
                
# # #                 for operation, screen_id in screen_mappings.items():
# # #                     if screen_id:
# # #                         screens.append({
# # #                             "id": screen_id,
# # #                             "operation": operation,
# # #                             "name": f"Screen {screen_id}"
# # #                         })
# # #             return screens
# # #         except Exception as e:
# # #             self._log(f"Error getting screens from scheme: {e}", "WARN")
# # #             return screens

# # #     def get_all_project_screens(self, project_key: str, project_id: str) -> List[dict]:
# # #         """
# # #         Get all screens for a project using multiple methods:
# # #         1. Search by project key in screen name (most reliable)
# # #         2. Get from screen scheme if found
# # #         3. Use issue type screen scheme mappings
# # #         """
# # #         all_screens = []
# # #         seen_ids = set()
        
# # #         # Method 1: Search by project key in screen name
# # #         self._log("  Method 1: Searching screens by project key...", "DEBUG")
# # #         named_screens = self.get_project_screens_by_name(project_key)
# # #         for screen in named_screens:
# # #             if screen["id"] not in seen_ids:
# # #                 seen_ids.add(screen["id"])
# # #                 all_screens.append(screen)
        
# # #         if named_screens:
# # #             self._log(f"  Found {len(named_screens)} screen(s) by name", "INFO")
        
# # #         # Method 2: Get from screen scheme
# # #         self._log("  Method 2: Checking screen schemes...", "DEBUG")
# # #         screen_scheme = self.get_screen_scheme_for_project(project_key)
# # #         if screen_scheme:
# # #             scheme_screens = self.get_screens_from_screen_scheme(screen_scheme.get("id"))
# # #             for screen in scheme_screens:
# # #                 if screen["id"] not in seen_ids:
# # #                     seen_ids.add(screen["id"])
# # #                     all_screens.append(screen)
# # #             self._log(f"  Found {len(scheme_screens)} screen(s) from screen scheme", "DEBUG")
        
# # #         # Method 3: Try issue type screen scheme
# # #         self._log("  Method 3: Checking issue type screen scheme...", "DEBUG")
# # #         itss_screens = self.get_screens_from_itss(project_id)
# # #         for screen in itss_screens:
# # #             if screen["id"] not in seen_ids:
# # #                 seen_ids.add(screen["id"])
# # #                 all_screens.append(screen)
        
# # #         if itss_screens:
# # #             self._log(f"  Found {len(itss_screens)} screen(s) from ITSS", "DEBUG")
        
# # #         return all_screens

# # #     def get_screens_from_itss(self, project_id: str) -> List[dict]:
# # #         """Get screens through Issue Type Screen Scheme chain"""
# # #         screens = []
        
# # #         try:
# # #             # Step 1: Get Issue Type Screen Scheme for project
# # #             url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/project"
# # #             params = {"projectId": project_id}
# # #             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
# # #             if r.status_code != 200:
# # #                 return screens
            
# # #             data = r.json()
# # #             values = data.get("values", [])
# # #             if not values:
# # #                 return screens
            
# # #             itss = values[0].get("issueTypeScreenScheme", {})
# # #             itss_id = itss.get("id")
            
# # #             if not itss_id:
# # #                 return screens
            
# # #             # Step 2: Get screen scheme mappings
# # #             url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/{itss_id}/mapping"
# # #             params = {"startAt": 0, "maxResults": 50}
# # #             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
# # #             if r.status_code != 200:
# # #                 return screens
            
# # #             mappings = r.json().get("values", [])
# # #             screen_scheme_ids = set()
            
# # #             for mapping in mappings:
# # #                 ss_id = mapping.get("screenSchemeId")
# # #                 if ss_id:
# # #                     screen_scheme_ids.add(str(ss_id))
            
# # #             # Step 3: Get screens from each screen scheme
# # #             for ss_id in screen_scheme_ids:
# # #                 ss_screens = self.get_screens_from_screen_scheme(ss_id)
# # #                 screens.extend(ss_screens)
            
# # #         except Exception as e:
# # #             self._log(f"Error in ITSS lookup: {e}", "DEBUG")
        
# # #         return screens

# # #     # ==================== SCREEN TAB AND FIELD MANAGEMENT ====================

# # #     def get_screen_tabs(self, screen_id: int) -> List[dict]:
# # #         """Get all tabs for a screen"""
# # #         try:
# # #             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs"
# # #             r = requests.get(url, headers=self.headers, timeout=30)
# # #             if r.status_code == 200:
# # #                 return r.json()
# # #         except Exception as e:
# # #             self._log(f"Error getting screen tabs: {e}", "WARN")
# # #         return []

# # #     def get_tab_fields(self, screen_id: int, tab_id: int) -> List[str]:
# # #         """Get all field IDs already on a screen tab"""
# # #         try:
# # #             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
# # #             r = requests.get(url, headers=self.headers, timeout=30)
# # #             if r.status_code == 200:
# # #                 fields = r.json()
# # #                 return [f.get("id") for f in fields if f.get("id")]
# # #         except Exception as e:
# # #             self._log(f"Error getting tab fields: {e}", "WARN")
# # #         return []

# # #     def add_field_to_screen_tab(self, screen_id: int, tab_id: int, field_id: str) -> bool:
# # #         """Add a field to a specific screen tab"""
# # #         try:
# # #             # Check if field already exists
# # #             existing = self.get_tab_fields(screen_id, tab_id)
# # #             if field_id in existing:
# # #                 return True
            
# # #             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
# # #             payload = {"fieldId": field_id}
# # #             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
# # #             if r.status_code in (200, 201, 204):
# # #                 return True
# # #             elif r.status_code == 400 and "already" in r.text.lower():
# # #                 return True
# # #             else:
# # #                 self._log(f"    Could not add {field_id} to screen {screen_id}: {r.text[:100]}", "DEBUG")
# # #                 return False
                
# # #         except Exception as e:
# # #             self._log(f"Error adding field: {e}", "WARN")
# # #             return False

# # #     def add_fields_to_project_screens(self, project_key: str, project_id: str, 
# # #                                        field_ids: List[str]) -> Tuple[int, int]:
# # #         """
# # #         Add custom fields to project-specific screens only.
# # #         Returns (screens_updated, total_fields_added)
# # #         """
# # #         screens_updated = 0
# # #         total_added = 0
        
# # #         # Get project-specific screens
# # #         project_screens = self.get_all_project_screens(project_key, project_id)
        
# # #         if not project_screens:
# # #             self._log("  No project-specific screens found!", "WARN")
# # #             self._log("  Fields will need to be added manually to screens.", "WARN")
# # #             return 0, 0
        
# # #         self._log(f"  Found {len(project_screens)} project screen(s) to update", "INFO")
        
# # #         for screen in project_screens:
# # #             screen_id = screen.get("id")
# # #             screen_name = screen.get("name", f"Screen {screen_id}")
            
# # #             tabs = self.get_screen_tabs(screen_id)
# # #             if not tabs:
# # #                 self._log(f"    {screen_name}: No tabs found", "WARN")
# # #                 continue
            
# # #             # Add to first tab
# # #             tab_id = tabs[0].get("id")
# # #             tab_name = tabs[0].get("name", "Field Tab")
            
# # #             fields_added = 0
# # #             for field_id in field_ids:
# # #                 if self.add_field_to_screen_tab(screen_id, tab_id, field_id):
# # #                     fields_added += 1
# # #                 time.sleep(0.1)  # Rate limiting
            
# # #             if fields_added > 0:
# # #                 self._log(f"    ✓ {screen_name}: Added {fields_added} fields to '{tab_name}'", "SUCCESS")
# # #                 screens_updated += 1
# # #                 total_added += fields_added
# # #             else:
# # #                 self._log(f"    • {screen_name}: Fields already present", "INFO")
        
# # #         return screens_updated, total_added

# # #     # ==================== FIELD CONTEXT MANAGEMENT - FIXED ====================

# # #     def get_field_contexts(self, field_id: str) -> List[dict]:
# # #         """Get all contexts for a custom field"""
# # #         try:
# # #             url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
# # #             params = {"maxResults": 100}
# # #             r = requests.get(url, headers=self.headers, params=params, timeout=30)
# # #             if r.status_code == 200:
# # #                 return r.json().get("values", [])
# # #         except Exception as e:
# # #             self._log(f"Error getting contexts: {e}", "DEBUG")
# # #         return []

# # #     def add_project_to_field_context(self, field_id: str, project_id: str, 
# # #                                       project_key: str) -> bool:
# # #         """
# # #         Add project to an existing field context or create a new one.
# # #         Uses the correct Jira Cloud API format.
# # #         """
# # #         contexts = self.get_field_contexts(field_id)
        
# # #         # Check if there's already a global context (field available everywhere)
# # #         for ctx in contexts:
# # #             if ctx.get("isGlobalContext", False):
# # #                 self._log(f"    Field has global context - available in all projects", "DEBUG")
# # #                 return True
        
# # #         # Check if project already in a context
# # #         for ctx in contexts:
# # #             project_ids = [str(p) for p in ctx.get("projectIds", [])]
# # #             if str(project_id) in project_ids:
# # #                 self._log(f"    Project already in context", "DEBUG")
# # #                 return True
        
# # #         # Try to add project to an existing non-global context
# # #         if contexts:
# # #             first_context = contexts[0]
# # #             ctx_id = first_context.get("id")
            
# # #             try:
# # #                 url = f"{self.base_url}/rest/api/3/field/{field_id}/context/{ctx_id}/project"
# # #                 payload = {"projectIds": [str(project_id)]}
# # #                 r = requests.put(url, headers=self.headers, json=payload, timeout=30)
                
# # #                 if r.status_code in (200, 204):
# # #                     self._log(f"    Added project to existing context", "DEBUG")
# # #                     return True
# # #                 else:
# # #                     self._log(f"    Could not add to context: {r.status_code}", "DEBUG")
# # #             except Exception as e:
# # #                 self._log(f"    Context update error: {e}", "DEBUG")
        
# # #         # If no contexts exist, try to create one
# # #         if not contexts:
# # #             try:
# # #                 url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
# # #                 # Note: For Jira Cloud, we might need issue type IDs as well
# # #                 payload = {
# # #                     "name": f"Context for {project_key}",
# # #                     "projectIds": [str(project_id)]
# # #                 }
# # #                 r = requests.post(url, headers=self.headers, json=payload, timeout=30)
                
# # #                 if r.status_code in (200, 201):
# # #                     self._log(f"    Created new context for project", "DEBUG")
# # #                     return True
# # #                 else:
# # #                     self._log(f"    Could not create context: {r.text[:100]}", "DEBUG")
# # #             except Exception as e:
# # #                 self._log(f"    Context creation error: {e}", "DEBUG")
        
# # #         # Fields with global context or standard fields should work without explicit context
# # #         return True

# # #     # ==================== FIELD CREATION ====================

# # #     def create_custom_field(self, field_name: str, field_type: str,
# # #                             searcher_key: str, description: str) -> Optional[str]:
# # #         """Create a new custom field"""
# # #         url = f"{self.base_url}/rest/api/3/field"
        
# # #         payload = {
# # #             "name": field_name,
# # #             "description": description,
# # #             "type": field_type,
# # #             "searcherKey": searcher_key
# # #         }
        
# # #         try:
# # #             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
# # #             if r.status_code in (200, 201):
# # #                 result = r.json()
# # #                 field_id = result.get("id")
# # #                 self._log(f"  Created field '{field_name}' → {field_id}", "SUCCESS")
# # #                 return field_id
# # #             else:
# # #                 self._log(f"  Failed to create '{field_name}': {r.text[:150]}", "ERROR")
# # #                 return None
                
# # #         except Exception as e:
# # #             self._log(f"Error creating field: {e}", "ERROR")
# # #             return None

# # #     def find_or_create_field(self, field_config: dict, project_id: str, 
# # #                               project_key: str, all_fields: List[dict]) -> Optional[str]:
# # #         """Find existing field or create new one"""
# # #         field_name = field_config["name"]
        
# # #         # Check if exists
# # #         existing_id = self.find_field_id(all_fields, field_name)
        
# # #         if existing_id:
# # #             self._log(f"  Found existing: '{field_name}' → {existing_id}", "SUCCESS")
# # #             # Ensure project has access
# # #             self.add_project_to_field_context(existing_id, project_id, project_key)
# # #             return existing_id
        
# # #         # Create new
# # #         self._log(f"  Creating: '{field_name}'...", "INFO")
# # #         field_id = self.create_custom_field(
# # #             field_name,
# # #             field_config["type"],
# # #             field_config["searcherKey"],
# # #             field_config["description"]
# # #         )
        
# # #         if field_id:
# # #             # Add to fields list
# # #             all_fields.append({
# # #                 "id": field_id,
# # #                 "name": field_name,
# # #                 "custom": True
# # #             })
# # #             time.sleep(0.5)
# # #             self.add_project_to_field_context(field_id, project_id, project_key)
# # #             return field_id
        
# # #         return None

# # #     # ==================== MAIN SETUP METHOD ====================

# # #     def setup_project_fields(self, all_fields: List[dict], 
# # #                               project_key: str, project_id: str) -> Tuple[dict, Optional[str]]:
# # #         """
# # #         Main method to set up custom fields:
# # #         1. Find or create each field
# # #         2. Ensure project can access fields  
# # #         3. Add fields to project screens
# # #         """
# # #         discovered = {} #will store field keys and their corresponding Jira field IDs that are either found or created.
# # #         field_ids = [] #a list of all Jira field IDs to be added to the project screens later.
        
# # #         print()
# # #         self._log("=" * 50, "INFO")
# # #         self._log("PHASE 1: Setting up custom fields", "INFO")
# # #         self._log("=" * 50, "INFO")
# # #         print()
        
# # #         for key, config in EXPECTED_FIELDS.items():
# # #             field_id = self.find_or_create_field(config, project_id, project_key, all_fields) #the function that actually creates the field if it doesn’t exist.
# # #             if field_id:
# # #                 discovered[key] = field_id
# # #                 field_ids.append(field_id)
        
# # #         # Find Epic Name
# # #         epic_name_id = self.find_field_id(all_fields, "Epic Name")
# # #         if epic_name_id:
# # #             self._log(f"  Found 'Epic Name' → {epic_name_id}", "SUCCESS")
        
# # #         print()
# # #         self._log("=" * 50, "INFO")
# # #         self._log("PHASE 2: Adding fields to project screens", "INFO")
# # #         self._log("=" * 50, "INFO")
# # #         print()
# # #         #Add fields to project screens
# # #         if field_ids:
# # #             # Wait for Jira to fully register the fields
# # #             self._log("  Waiting for field registration...", "INFO")
# # #             time.sleep(3)
            
# # #             screens_updated, fields_added = self.add_fields_to_project_screens(
# # #                 project_key, project_id, field_ids
# # #             )
            
# # #             print()
# # #             if screens_updated > 0:
# # #                 self._log(f"  Summary: Updated {screens_updated} screens, {fields_added} field additions", "SUCCESS")
# # #             else:
# # #                 self._log("  Warning: No screens were updated", "WARN")
# # #                 self._log("  You may need to manually add fields to screens in Project Settings", "WARN")
        
# # #         return discovered, epic_name_id

# # #     # ==================== PROJECT AND ISSUE CREATION ====================

# # #     def create_project(self, name: str, key: str, template: str, lead_id: str) -> dict:
# # #         """Create a new Company-managed Jira project"""
# # #         url = f"{self.base_url}/rest/api/3/project"
        
# # #         payload = {
# # #             "key": key,
# # #             "name": name,
# # #             "projectTypeKey": "software",
# # #             "projectTemplateKey": template,
# # #             "leadAccountId": lead_id,
# # #             "assigneeType": "PROJECT_LEAD",
# # #             "description": f"Company-managed project: {name}",
# # #         }
        
# # #         r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
# # #         if r.status_code in (200, 201):
# # #             project_data = r.json()
# # #             self._log(f"Project '{name}' created! Key: {key}", "SUCCESS")
# # #             return project_data
# # #         else:
# # #             error_msg = r.text
# # #             try:
# # #                 error_json = r.json()
# # #                 if 'errors' in error_json:
# # #                     error_msg = json.dumps(error_json['errors'], indent=2)
# # #                 elif 'errorMessages' in error_json:
# # #                     error_msg = ', '.join(error_json['errorMessages'])
# # #             except Exception:
# # #                 pass
# # #             raise Exception(f"Failed to create project: {error_msg}")

# # #     def create_issue(self, project_key: str, issue_type: str, summary: str,
# # #                      description: str = None, fields_extra: dict = None) -> dict:
# # #         """Create a Jira issue"""
# # #         url = f"{self.base_url}/rest/api/3/issue"
        
# # #         fields = {
# # #             "project": {"key": project_key},
# # #             "summary": summary,
# # #             "issuetype": {"name": issue_type}
# # #         }
        
# # #         if description:
# # #             fields["description"] = {
# # #                 "type": "doc",
# # #                 "version": 1,
# # #                 "content": [{
# # #                     "type": "paragraph",
# # #                     "content": [{"type": "text", "text": description}]
# # #                 }]
# # #             }
        
# # #         if fields_extra:
# # #             fields.update(fields_extra)
        
# # #         try:
# # #             r = requests.post(url, headers=self.headers, json={"fields": fields}, timeout=30)
# # #             r.raise_for_status()
# # #             return r.json()
# # #         except requests.exceptions.HTTPError:
# # #             raise Exception(f"Failed to create {issue_type}: {r.text[:200]}")

# # #     def update_issue_fields(self, issue_key: str, fields: dict) -> bool:
# # #         """Update issue fields"""
# # #         url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
# # #         try:
# # #             r = requests.put(url, headers=self.headers, json={"fields": fields}, timeout=30)
# # #             return r.status_code in (200, 204)
# # #         except Exception:
# # #             return False

# # #     def link_to_parent(self, issue_key: str, parent_key: str) -> bool:
# # #         """Link issue to parent Epic"""
# # #         return self.update_issue_fields(issue_key, {"parent": {"key": parent_key}})

# # #     def generate_structure(self, project_key: str, custom_fields: dict,
# # #                            epic_name_field: Optional[str], lead_account_id: str) -> dict:
# # #         """Generate Epic/Story structure"""
        
# # #         print()
# # #         self._log("=" * 50, "INFO")
# # #         self._log(f"PHASE 3: Creating Epics and Stories", "INFO")
# # #         self._log("=" * 50, "INFO")
# # #         print()
        
# # #         epic_keys = {}
# # #         total_epics = len(EPICS)
# # #         total_stories = sum(len(s) for s in EPICS.values())
# # #         epic_count = 0
# # #         story_count = 0
        
# # #         for epic_name, story_list in EPICS.items():
# # #             epic_count += 1
            
# # #             try:
# # #                 fields_extra = {}
# # #                 if epic_name_field:
# # #                     fields_extra[epic_name_field] = epic_name
                
# # #                 epic = self.create_issue(project_key, "Epic", epic_name,  #creates the Epic in Jira.
# # #                                          f"Epic: {epic_name}", fields_extra)
# # #                 epic_key = epic.get("key")
# # #                 epic_keys[epic_name] = epic_key
                
# # #                 short_name = epic_name[:50] + "..." if len(epic_name) > 50 else epic_name
# # #                 self._log(f"[{epic_count}/{total_epics}] Epic: {short_name} → {epic_key}", "SUCCESS")
                
# # #             except Exception as e:
# # #                 self._log(f"Failed to create Epic: {e}", "ERROR")
# # #                 continue
            
# # #             for story_name in story_list:
# # #                 story_count += 1
                
# # #                 # Prepare custom field values Automatically fills in custom fields for the story:
# # #                 story_fields = {}
# # #                 today = datetime.utcnow().date()
                
# # #                 if "percent_complete" in custom_fields:
# # #                     story_fields[custom_fields["percent_complete"]] = "0"
# # #                 if "target_start" in custom_fields:
# # #                     story_fields[custom_fields["target_start"]] = str(today)
# # #                 if "target_end" in custom_fields:
# # #                     story_fields[custom_fields["target_end"]] = str(today + timedelta(days=7))
# # #                 if "owning" in custom_fields:
# # #                     story_fields[custom_fields["owning"]] = {"accountId": lead_account_id}
                
# # #                 try:
# # #                     # Try Creating Story with Custom Fields
# # #                     story = self.create_issue(project_key, "Story", story_name,
# # #                                               f"Story: {story_name}", story_fields)
# # #                     story_key = story.get("key")
# # #                     linked = self.link_to_parent(story_key, epic_key)
                    
# # #                     status = "✓" if linked else "○"
# # #                     self._log(f"  [{story_count}/{total_stories}] {status} {story_key}", "SUCCESS")
                    
# # #                 except Exception as e:
# # #                     # Retry without custom fields
# # #                     try:
# # #                         story = self.create_issue(project_key, "Story", story_name)
# # #                         story_key = story.get("key")
# # #                         self.link_to_parent(story_key, epic_key)
                        
# # #                         # Try to update fields separately
# # #                         if story_fields:
# # #                             time.sleep(0.2)
# # #                             self.update_issue_fields(story_key, story_fields)
                        
# # #                         self._log(f"  [{story_count}/{total_stories}] ○ {story_key} (retry)", "SUCCESS")
# # #                     except Exception:
# # #                         self._log(f"  Failed: {story_name[:30]}...", "ERROR")
        
# # #         return epic_keys
# # # def main():
# # #     """Main execution"""
# # #     JIRA_BASE_URL = input("Enter the JIRA BASE URL:")
# # #     JIRA_EMAIL = input("Enter the JIRA EMAIL:")
# # #     JIRA_API_TOKEN = getpass.getpass("Enter the JIRA API TOKEN:(hidden)")
# # #     print("\n" + "=" * 60)
# # #     print("  🚀 JIRA COMPANY-MANAGED PROJECT GENERATOR")
# # #     print("     (Fixed Screen Configuration)")
# # #     print("=" * 60 + "\n")
    
# # #     generator = JiraProjectGenerator(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN)
    
# # #     # Uncomment for verbose debug output:
# # #     # generator.debug_mode = True
    
# # #     generator._log("Testing connection...", "INFO")
# # #     success, user_info = generator.test_connection()
    
# # #     if not success:
# # #         generator._log(f"Connection failed: {user_info.get('error')}", "ERROR")
# # #         return
    
# # #     lead_id = user_info.get("accountId")
# # #     user_name = user_info.get("displayName", user_info.get("emailAddress"))
# # #     generator._log(f"Connected as: {user_name}", "SUCCESS")
    
# # #     print("\n" + "-" * 60 + "\n")
# # #     print("📋 PROJECT DETAILS\n")
    
# # #     while True:
# # #         project_name = input("Enter Project Name: ").strip()
# # #         if not project_name:
# # #             generator._log("Project name required!", "ERROR")
# # #             continue
        
# # #         suggested_key = generator.suggest_project_key(project_name)
# # #         key_input = input(f"Enter Project Key (suggested: {suggested_key}): ").strip().upper()
# # #         project_key = key_input if key_input else suggested_key #If condition is True, value gets A ele suggested
        
# # #         if not re.match(r'^[A-Z][A-Z0-9]{1,9}$', project_key):
# # #             generator._log("Invalid key! Must be 2-10 uppercase chars starting with letter.", "ERROR")
# # #             continue
        
# # #         if generator.check_project_exists(project_key):
# # #             generator._log(f"Project '{project_key}' already exists!", "ERROR")
# # #             if input("Try different key? (y/N): ").strip().lower() == 'y':
# # #                 continue
# # #             return
# # #         break
    
# # #     print("\n📐 SELECT TEMPLATE\n")
# # #     for k, (name, _) in VALID_TEMPLATES.items():
# # #         print(f"  {k}. {name}")
    
# # #     choice = input("\nChoose (1-3) [default: 2]: ").strip() or "2"
# # #     if choice not in VALID_TEMPLATES:
# # #         generator._log("Invalid choice!", "ERROR")
# # #         return
    
# # #     template_name, template_key = VALID_TEMPLATES[choice]
    
# # #     print("\n" + "-" * 60)
# # #     print("\n📊 SUMMARY\n")
# # #     print(f"  Project Name:  {project_name}")
# # #     print(f"  Project Key:   {project_key}")
# # #     print(f"  Template:      {template_name}")
# # #     print(f"  Epics:         {len(EPICS)}")
# # #     print(f"  Stories:       {sum(len(s) for s in EPICS.values())}")
# # #     print(f"  Custom Fields: {len(EXPECTED_FIELDS)}")
# # #     print()
    
# # #     if input("Proceed? (y/N): ").strip().lower() != 'y':
# # #         generator._log("Cancelled", "WARN")
# # #         return
    
# # #     print("\n" + "=" * 60)
    
# # #     # Create project
# # #     try:
# # #         generator._log("Creating project...", "INFO")
# # #         project = generator.create_project(project_name, project_key, template_key, lead_id)
# # #         project_id = project.get("id")
# # #     except Exception as e:
# # #         generator._log(f"Failed: {e}", "ERROR")
# # #         return
    
# # #     # Wait for project initialization
# # #     generator._log("Waiting for project initialization (10 seconds)...", "INFO")
# # #     time.sleep(10)  # Longer wait for screens to be created
    
# # #     # Setup fields
# # #     try:
# # #         all_fields = generator.fetch_all_fields() #Calls to retrieve all available field
# # #         custom_fields, epic_name_field = generator.setup_project_fields(
# # #             all_fields, project_key, project_id
# # #         )
# # #     except Exception as e:
# # #         generator._log(f"Field setup error: {e}", "ERROR")
# # #         custom_fields = {}
# # #         epic_name_field = None
    
# # #     # Generate structure
# # #     try:
# # #         epic_keys = generator.generate_structure(
# # #             project_key, custom_fields, epic_name_field, lead_id
# # #         )
# # #     except Exception as e:
# # #         generator._log(f"Structure error: {e}", "ERROR")
# # #         epic_keys = {}
    
# # #     # Summary
# # #     print("\n" + "=" * 60)
# # #     print("  ✨ COMPLETE!")
# # #     print("=" * 60)
# # #     print(f"\n🔗 {JIRA_BASE_URL}/projects/{project_key}")
# # #     print(f"📝 Created {len(epic_keys)} Epics")
    
# # #     if custom_fields:
# # #         print(f"\n🏷️ Custom Fields:")
# # #         for k, fid in custom_fields.items():
# # #             print(f"   • {EXPECTED_FIELDS[k]['name']} → {fid}")
    
# # #     print()


# # # if __name__ == "__main__":
# # #     try:
# # #         main()
# # #     except KeyboardInterrupt:
# # #         print("\n⚠️ Cancelled\n")
# # #         sys.exit(0)
# # #     except Exception as e:
# # #         print(f"\n❌ Error: {e}\n")
# # #         import traceback
# # #         traceback.print_exc()
# # #         sys.exit(1)
# # import base64
# # import re
# # import json
# # import time
# # import sys
# # import getpass
# # import requests
# # from datetime import datetime, timedelta
# # from typing import List, Dict, Optional, Tuple

# # # =============================================================================
# # # CONFIGURATION
# # # =============================================================================

# # VALID_TEMPLATES = {
# #     "1": ("Kanban", "com.pyxis.greenhopper.jira:gh-kanban-template"),
# #     "2": ("Scrum", "com.pyxis.greenhopper.jira:gh-scrum-template"),
# #     "3": ("Bug Tracking", "com.atlassian.jira-core-project-templates:jira-core-project-management"),
# # }

# # # Project structure to create
# # EPICS = {
# #     "ASSESSMENT & PLANNING (2 - 12 weeks, depending on project scope, sizing, access, onboarding)": [
# #         "Onboarding and Access - See Access Tab for Details",
# #         "Introductory Call",
# #         "Discuss NON-PRODUCTION environments",
# #         "Set up Weekly Touchpoint w/Atlassian (if above 1000 users)",
# #         "Discuss Atlassian Cloud Status",
# #         "Start Atlassian CLOUD Trial (if needed)",
# #         "Set up Weekly Touchpoint w/Project Team",
# #         "Set up Atlassian Guard (if needed/in scope)",
# #         "Open Ticket w/Atlassian for MOVE",
# #         "Refresh lower instance of Jira to current version",
# #         "Licensing Tier Jira",
# #         "Licensing Tier Confluence",
# #         "Discussion/Discovery Migration Scope for Confluence",
# #         "Discussion/Discovery Migration Scope for Jira",
# #         "Discussion/Discovery Integrations",
# #         "Discussion/Discovery User Management",
# #         "Start Atlassian Guard Trial (if needed/in scope)",
# #         "User Clean Up Tasks",
# #         "Jira - Add-on Assessment",
# #         "Confluence - Add-on Assessment",
# #         "Environment Assessment & Pre-Migration Checklist",
# #         "Develop Migration Approach & Draft Runbook",
# #         "Develop Testing Plan",
# #         "Develop Communications Plan",
# #         "Develop Training Plan (if needed)",
# #         "Review & Acceptance - Environment Assessment",
# #         "Review & Acceptance - Jira Projects Assessment",
# #         "Review & Acceptance - Confluence Spaces",
# #         "Review & Acceptance - Jira Add-ons",
# #         "Review & Acceptance - Atlassian Guard Setup",
# #         "Review & Acceptance - Confluence Addons",
# #         "Review & Acceptance - Confluence Macros",
# #         "Review & Acceptance - Integrations",
# #         "Review & Acceptance - Pre Migration Checklists (Jira & Confluence)",
# #         "Budget Review Meeting (T&M)",
# #         "Refresh Staging Environments (Jira and Confluence)",
# #         "<other tasks as identified>"
# #     ],
# #     "TEST MIGRATION (4 - 16 weeks, depending on scope, sizing, & capacity of Client)": [
# #         "Execute User Migration using JCMA",
# #         "Execute Complete test migration using JCMA",
# #         "Transformation Tasks - Scriptrunner",
# #         "Basic Application Integrity Tests",
# #         "Workflow Review & Migration Assistant Errors",
# #         "Working Session to review Migration Assistant Findings (if needed)",
# #         "Execute Add-on Remediation Plan",
# #         "Execute Confluence Migration using CCMA",
# #         "Post migration checks Jira & Confluence"
# #     ],
# #     "USER ACCEPTANCE TESTING (1 - 2 weeks, depending on scope, sizing, & capacity of Client)": [
# #         "Capula Project Team Testing",
# #         "Hold UAT Training (if needed)",
# #         "User Acceptance Testing",
# #         "Issue Resolution",
# #         "Go/No Go Decision (UAT Acceptance)"
# #     ],
# #     "PRODUCTION MIGRATION (TBD)": ["Finalize Migration Runbook", "See Migration Timeline Tab "],
# #     "POST MIGRATION SUPPORT (4 weeks)": ["<items as identified>"],
# # }

# # # Expected custom fields with their types
# # EXPECTED_FIELDS = {
# #     "percent_complete": {
# #         "name": "% Complete",
# #         "field_id": None,
# #         "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
# #         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
# #         "description": "Percentage of task completion"
# #     },
# #     "target_start": {
# #         "name": "Target Start Date",
# #         "field_id": None,
# #         "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
# #         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
# #         "description": "Target start date for the task"
# #     },
# #     "target_end": {
# #         "name": "Target End Date",
# #         "field_id": None,
# #         "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
# #         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
# #         "description": "Target end date for the task"
# #     },
# #     "owning": {
# #         "name": "Owning",
# #         "field_id": None,
# #         "type": "com.atlassian.jira.plugin.system.customfieldtypes:userpicker",
# #         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:userpickergroupsearcher",
# #         "description": "Owner of the task"
# #     },
# #     "confluence_page": {
# #         "name": "Confluence Page",
# #         "field_id": None,
# #         "type": "com.atlassian.jira.plugin.system.customfieldtypes:url",
# #         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:exacttextsearcher",
# #         "description": "Link to related Confluence documentation page"
# #     }
# # }


# # # =============================================================================
# # # MAIN CLASS
# # # =============================================================================

# # class JiraProjectGenerator:
# #     def __init__(self, base_url: str, email: str, api_token: str):
# #         self.base_url = base_url.rstrip('/')
# #         self.email = email
# #         self.api_token = api_token
# #         self.headers = self._get_auth_header()
# #         self.debug_mode = False
# #         self.confluence_field_id = None  # Will be set after field creation

# #     def _get_auth_header(self) -> dict:
# #         """Generate Basic Auth header for Jira/Confluence API"""
# #         token = f"{self.email}:{self.api_token}"
# #         b64 = base64.b64encode(token.encode()).decode()
# #         return {
# #             "Authorization": f"Basic {b64}",
# #             "Content-Type": "application/json",
# #             "Accept": "application/json"
# #         }

# #     def _log(self, message: str, level: str = "INFO"):
# #         """Pretty logging with emoji indicators"""
# #         icons = {
# #             "INFO": "🔵",
# #             "SUCCESS": "✅",
# #             "ERROR": "❌",
# #             "WARN": "⚠️",
# #             "QUESTION": "❓",
# #             "DEBUG": "🔍",
# #             "CONFLUENCE": "📄",
# #             "LINK": "🔗"
# #         }
# #         if level == "DEBUG" and not self.debug_mode:
# #             return
# #         print(f"{icons.get(level, '•')} {message}")

# #     # =========================================================================
# #     # JIRA CONNECTION & UTILITIES
# #     # =========================================================================

# #     def suggest_project_key(self, name: str) -> str:
# #         """Generate a suggested project key from project name"""
# #         name_clean = re.sub(r'[^A-Za-z0-9 ]+', '', name).strip()
# #         parts = name_clean.split()

# #         if len(parts) == 1:
# #             key = parts[0][:4].upper()
# #         else:
# #             key = ''.join(p[0] for p in parts if p)[:4].upper()

# #         if len(key) < 2:
# #             key = (key + "PR")[:2]

# #         return key[:10]

# #     def suggest_space_key(self, name: str) -> str:
# #         """Generate a suggested Confluence space key from space name"""
# #         name_clean = re.sub(r'[^A-Za-z0-9 ]+', '', name).strip()
# #         parts = name_clean.split()

# #         if len(parts) == 1:
# #             key = parts[0][:10].upper()
# #         else:
# #             key = ''.join(p[0] for p in parts if p)[:6].upper()

# #         if len(key) < 2:
# #             key = (key + "DOC")[:3]

# #         return key[:10]

# #     def check_project_exists(self, project_key: str) -> bool:
# #         """Check if a project with this key already exists"""
# #         try:
# #             url = f"{self.base_url}/rest/api/3/project/{project_key}"
# #             r = requests.get(url, headers=self.headers, timeout=10)
# #             return r.status_code == 200
# #         except Exception:
# #             return False

# #     def test_connection(self) -> Tuple[bool, dict]:
# #         """Test Jira API connection and get current user info"""
# #         try:
# #             url = f"{self.base_url}/rest/api/3/myself"
# #             r = requests.get(url, headers=self.headers, timeout=10)
# #             r.raise_for_status()
# #             return True, r.json()
# #         except requests.exceptions.RequestException as e:
# #             return False, {"error": str(e)}

# #     # =========================================================================
# #     # CONFLUENCE CONNECTION & SPACE MANAGEMENT
# #     # =========================================================================

# #     def test_confluence_connection(self) -> Tuple[bool, dict]:
# #         """Test Confluence API connection"""
# #         try:
# #             url = f"{self.base_url}/wiki/rest/api/user/current"
# #             r = requests.get(url, headers=self.headers, timeout=10)
# #             r.raise_for_status()
# #             return True, r.json()
# #         except requests.exceptions.RequestException as e:
# #             return False, {"error": str(e)}

# #     def check_confluence_space_exists(self, space_key: str) -> bool:
# #         """Check if a Confluence space with this key already exists"""
# #         try:
# #             url = f"{self.base_url}/wiki/rest/api/space/{space_key.upper()}"
# #             r = requests.get(url, headers=self.headers, timeout=10)
# #             return r.status_code == 200
# #         except Exception:
# #             return False

# #     def create_confluence_space(self, space_key: str, space_name: str, 
# #                                  description: str = None) -> dict:
# #         """Create a new Confluence space"""
# #         url = f"{self.base_url}/wiki/rest/api/space"
        
# #         payload = {
# #             "key": space_key.upper(),
# #             "name": space_name,
# #             "description": {
# #                 "plain": {
# #                     "value": description or f"Documentation space for: {space_name}",
# #                     "representation": "plain"
# #                 }
# #             }
# #         }
        
# #         r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
# #         if r.status_code in (200, 201):
# #             space_data = r.json()
# #             self._log(f"Confluence space '{space_name}' created! Key: {space_key.upper()}", "SUCCESS")
# #             return space_data
# #         else:
# #             error_msg = r.text
# #             try:
# #                 error_json = r.json()
# #                 if 'message' in error_json:
# #                     error_msg = error_json['message']
# #             except Exception:
# #                 pass
# #             raise Exception(f"Failed to create Confluence space: {error_msg}")

# #     def get_space_homepage_id(self, space_key: str) -> Optional[str]:
# #         """Get the homepage ID of a Confluence space"""
# #         try:
# #             url = f"{self.base_url}/wiki/rest/api/space/{space_key.upper()}"
# #             params = {"expand": "homepage"}
# #             r = requests.get(url, headers=self.headers, params=params, timeout=10)
# #             if r.status_code == 200:
# #                 data = r.json()
# #                 homepage = data.get("homepage", {})
# #                 return homepage.get("id")
# #         except Exception as e:
# #             self._log(f"Error getting space homepage: {e}", "DEBUG")
# #         return None

# #     # =========================================================================
# #     # CONFLUENCE PAGE MANAGEMENT
# #     # =========================================================================

# #     def create_confluence_page(self, space_key: str, title: str, 
# #                                 jira_issue_key: str,
# #                                 jira_issue_summary: str,
# #                                 parent_id: str = None) -> Optional[dict]:
# #         """
# #         Create a Confluence page with Jira issue reference.
# #         """
# #         url = f"{self.base_url}/wiki/rest/api/content"
        
# #         jira_link = f"{self.base_url}/browse/{jira_issue_key}"
        
# #         # Simple HTML content with clear Jira reference
# #         body_content = f"""
# # <h2>📋 Related Jira Issue</h2>
# # <p><strong>Issue:</strong> <a href="{jira_link}">{jira_issue_key}</a></p>
# # <p><strong>Summary:</strong> {jira_issue_summary}</p>

# # <hr/>

# # <h2>Overview</h2>
# # <p><em>Add overview documentation here...</em></p>

# # <h2>Details</h2>
# # <p><em>Add detailed information here...</em></p>

# # <h2>Notes</h2>
# # <ul>
# # <li><em>Add notes and updates here...</em></li>
# # </ul>

# # <h2>Attachments & References</h2>
# # <p><em>Add relevant files and links here...</em></p>
# # """
        
# #         payload = {
# #             "type": "page",
# #             "title": title,
# #             "space": {"key": space_key.upper()},
# #             "body": {
# #                 "storage": {
# #                     "value": body_content,
# #                     "representation": "storage"
# #                 }
# #             }
# #         }
        
# #         if parent_id:
# #             payload["ancestors"] = [{"id": str(parent_id)}]
        
# #         try:
# #             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
# #             if r.status_code in (200, 201):
# #                 return r.json()
# #             else:
# #                 error_msg = r.text[:200]
# #                 try:
# #                     error_json = r.json()
# #                     if 'message' in error_json:
# #                         error_msg = error_json['message']
# #                 except Exception:
# #                     pass
# #                 self._log(f"Failed to create page '{title[:30]}...': {error_msg}", "WARN")
# #                 return None
                
# #         except Exception as e:
# #             self._log(f"Error creating Confluence page: {e}", "WARN")
# #             return None

# #     def get_confluence_page_url(self, page_data: dict) -> str:
# #         """Extract the web URL from Confluence page data"""
# #         links = page_data.get("_links", {})
# #         base = links.get("base", f"{self.base_url}/wiki")
# #         webui = links.get("webui", "")
# #         return f"{base}{webui}"

# #     # =========================================================================
# #     # JIRA-CONFLUENCE LINKING - FIXED METHODS
# #     # =========================================================================

# #     def add_confluence_link_to_description(self, issue_key: str, 
# #                                             page_url: str, 
# #                                             page_title: str,
# #                                             original_description: str = None) -> bool:
# #         """
# #         Add Confluence page link directly to the issue description.
# #         This is the MOST VISIBLE method - appears at top of issue.
# #         """
# #         # Build description with Confluence link at the TOP
# #         description_adf = {
# #             "type": "doc",
# #             "version": 1,
# #             "content": [
# #                 {
# #                     "type": "panel",
# #                     "attrs": {
# #                         "panelType": "info"
# #                     },
# #                     "content": [
# #                         {
# #                             "type": "paragraph",
# #                             "content": [
# #                                 {
# #                                     "type": "text",
# #                                     "text": "📄 Documentation: ",
# #                                     "marks": [{"type": "strong"}]
# #                                 },
# #                                 {
# #                                     "type": "text",
# #                                     "text": page_title,
# #                                     "marks": [
# #                                         {
# #                                             "type": "link",
# #                                             "attrs": {"href": page_url}
# #                                         }
# #                                     ]
# #                                 }
# #                             ]
# #                         }
# #                     ]
# #                 },
# #                 {
# #                     "type": "paragraph",
# #                     "content": [
# #                         {
# #                             "type": "text",
# #                             "text": original_description or ""
# #                         }
# #                     ]
# #                 }
# #             ]
# #         }
        
# #         url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
# #         payload = {"fields": {"description": description_adf}}
        
# #         try:
# #             r = requests.put(url, headers=self.headers, json=payload, timeout=30)
# #             return r.status_code in (200, 204)
# #         except Exception as e:
# #             self._log(f"Error updating description: {e}", "DEBUG")
# #             return False

# #     def set_confluence_url_field(self, issue_key: str, page_url: str) -> bool:
# #         """
# #         Set the Confluence Page URL custom field.
# #         This creates a clickable link in the issue details.
# #         """
# #         if not self.confluence_field_id:
# #             return False
        
# #         url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
# #         payload = {
# #             "fields": {
# #                 self.confluence_field_id: page_url
# #             }
# #         }
        
# #         try:
# #             r = requests.put(url, headers=self.headers, json=payload, timeout=30)
# #             return r.status_code in (200, 204)
# #         except Exception as e:
# #             self._log(f"Error setting Confluence field: {e}", "DEBUG")
# #             return False

# #     def add_confluence_link_comment(self, issue_key: str, 
# #                                      page_url: str, 
# #                                      page_title: str) -> bool:
# #         """
# #         Add a pinned-style comment with the Confluence link.
# #         This is visible in the Activity section.
# #         """
# #         url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        
# #         payload = {
# #             "body": {
# #                 "type": "doc",
# #                 "version": 1,
# #                 "content": [
# #                     {
# #                         "type": "panel",
# #                         "attrs": {
# #                             "panelType": "note"
# #                         },
# #                         "content": [
# #                             {
# #                                 "type": "paragraph",
# #                                 "content": [
# #                                     {
# #                                         "type": "text",
# #                                         "text": "📄 DOCUMENTATION PAGE",
# #                                         "marks": [{"type": "strong"}]
# #                                     }
# #                                 ]
# #                             },
# #                             {
# #                                 "type": "paragraph",
# #                                 "content": [
# #                                     {
# #                                         "type": "text",
# #                                         "text": "Click here to view: "
# #                                     },
# #                                     {
# #                                         "type": "text",
# #                                         "text": page_title,
# #                                         "marks": [
# #                                             {
# #                                                 "type": "link",
# #                                                 "attrs": {"href": page_url}
# #                                             },
# #                                             {"type": "strong"}
# #                                         ]
# #                                     }
# #                                 ]
# #                             }
# #                         ]
# #                     }
# #                 ]
# #             }
# #         }
        
# #         try:
# #             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
# #             return r.status_code in (200, 201)
# #         except Exception as e:
# #             self._log(f"Error adding comment: {e}", "DEBUG")
# #             return False

# #     def link_confluence_to_jira(self, issue_key: str, 
# #                                  page_url: str, 
# #                                  page_title: str,
# #                                  original_description: str = None,
# #                                  add_to_description: bool = True,
# #                                  add_comment: bool = False,
# #                                  set_url_field: bool = True) -> dict:
# #         """
# #         Create visible links from Jira to Confluence using multiple methods.
        
# #         Returns dict with status of each method.
# #         """
# #         results = {
# #             "description": False,
# #             "url_field": False,
# #             "comment": False
# #         }
        
# #         # Method 1: Add to Description (Most Visible)
# #         if add_to_description:
# #             results["description"] = self.add_confluence_link_to_description(
# #                 issue_key, page_url, page_title, original_description
# #             )
        
# #         # Method 2: Set URL Custom Field
# #         if set_url_field and self.confluence_field_id:
# #             results["url_field"] = self.set_confluence_url_field(issue_key, page_url)
        
# #         # Method 3: Add Comment
# #         if add_comment:
# #             results["comment"] = self.add_confluence_link_comment(
# #                 issue_key, page_url, page_title
# #             )
        
# #         return results

# #     # =========================================================================
# #     # JIRA FIELD MANAGEMENT
# #     # =========================================================================

# #     def fetch_all_fields(self) -> List[dict]:
# #         """Fetch all Jira fields to discover custom field IDs"""
# #         url = f"{self.base_url}/rest/api/3/field"
# #         r = requests.get(url, headers=self.headers, timeout=30)
# #         r.raise_for_status()
# #         return r.json()

# #     def find_field_id(self, fields: List[dict], display_name: str) -> Optional[str]:
# #         """Find field ID by display name (case-insensitive)"""
# #         for f in fields:
# #             if f.get("name", "").strip().lower() == display_name.strip().lower():
# #                 return f.get("id")
# #         return None

# #     # =========================================================================
# #     # SCREEN DISCOVERY
# #     # =========================================================================

# #     def get_project_screens_by_name(self, project_key: str) -> List[dict]:
# #         """Find screens that belong to this project"""
# #         screens = []
# #         start_at = 0
# #         max_results = 100
        
# #         while True:
# #             url = f"{self.base_url}/rest/api/3/screens"
# #             params = {"startAt": start_at, "maxResults": max_results}
            
# #             try:
# #                 r = requests.get(url, headers=self.headers, params=params, timeout=30)
# #                 if r.status_code != 200:
# #                     break
                    
# #                 data = r.json()
# #                 values = data.get("values", [])
                
# #                 for screen in values:
# #                     screen_name = screen.get("name", "")
# #                     if (screen_name.startswith(f"{project_key}:") or 
# #                         screen_name.startswith(f"{project_key} ") or
# #                         f": {project_key}" in screen_name):
# #                         screens.append({
# #                             "id": screen.get("id"),
# #                             "name": screen_name,
# #                             "description": screen.get("description", "")
# #                         })
                
# #                 if len(values) < max_results:
# #                     break
# #                 start_at += max_results
                
# #             except Exception as e:
# #                 self._log(f"Error searching screens: {e}", "WARN")
# #                 break
        
# #         return screens

# #     def get_screen_scheme_for_project(self, project_key: str) -> Optional[dict]:
# #         """Get screen scheme by project key"""
# #         try:
# #             url = f"{self.base_url}/rest/api/3/screenscheme"
# #             params = {"startAt": 0, "maxResults": 100}
# #             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
# #             if r.status_code == 200:
# #                 schemes = r.json().get("values", [])
# #                 for scheme in schemes:
# #                     if project_key in scheme.get("name", ""):
# #                         return scheme
# #             return None
# #         except Exception:
# #             return None

# #     def get_screens_from_screen_scheme(self, screen_scheme_id: str) -> List[dict]:
# #         """Get screens from a screen scheme"""
# #         screens = []
# #         try:
# #             url = f"{self.base_url}/rest/api/3/screenscheme/{screen_scheme_id}"
# #             r = requests.get(url, headers=self.headers, timeout=30)
            
# #             if r.status_code == 200:
# #                 data = r.json()
# #                 screen_mappings = data.get("screens", {})
                
# #                 for operation, screen_id in screen_mappings.items():
# #                     if screen_id:
# #                         screens.append({
# #                             "id": screen_id,
# #                             "operation": operation,
# #                             "name": f"Screen {screen_id}"
# #                         })
# #         except Exception:
# #             pass
# #         return screens

# #     def get_all_project_screens(self, project_key: str, project_id: str) -> List[dict]:
# #         """Get all screens for a project"""
# #         all_screens = []
# #         seen_ids = set()
        
# #         named_screens = self.get_project_screens_by_name(project_key)
# #         for screen in named_screens:
# #             if screen["id"] not in seen_ids:
# #                 seen_ids.add(screen["id"])
# #                 all_screens.append(screen)
        
# #         screen_scheme = self.get_screen_scheme_for_project(project_key)
# #         if screen_scheme:
# #             scheme_screens = self.get_screens_from_screen_scheme(screen_scheme.get("id"))
# #             for screen in scheme_screens:
# #                 if screen["id"] not in seen_ids:
# #                     seen_ids.add(screen["id"])
# #                     all_screens.append(screen)
        
# #         itss_screens = self.get_screens_from_itss(project_id)
# #         for screen in itss_screens:
# #             if screen["id"] not in seen_ids:
# #                 seen_ids.add(screen["id"])
# #                 all_screens.append(screen)
        
# #         return all_screens

# #     def get_screens_from_itss(self, project_id: str) -> List[dict]:
# #         """Get screens through Issue Type Screen Scheme"""
# #         screens = []
        
# #         try:
# #             url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/project"
# #             params = {"projectId": project_id}
# #             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
# #             if r.status_code != 200:
# #                 return screens
            
# #             data = r.json()
# #             values = data.get("values", [])
# #             if not values:
# #                 return screens
            
# #             itss = values[0].get("issueTypeScreenScheme", {})
# #             itss_id = itss.get("id")
            
# #             if not itss_id:
# #                 return screens
            
# #             url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/{itss_id}/mapping"
# #             params = {"startAt": 0, "maxResults": 50}
# #             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
# #             if r.status_code != 200:
# #                 return screens
            
# #             mappings = r.json().get("values", [])
# #             screen_scheme_ids = set()
            
# #             for mapping in mappings:
# #                 ss_id = mapping.get("screenSchemeId")
# #                 if ss_id:
# #                     screen_scheme_ids.add(str(ss_id))
            
# #             for ss_id in screen_scheme_ids:
# #                 ss_screens = self.get_screens_from_screen_scheme(ss_id)
# #                 screens.extend(ss_screens)
            
# #         except Exception:
# #             pass
        
# #         return screens

# #     # =========================================================================
# #     # SCREEN TAB AND FIELD MANAGEMENT
# #     # =========================================================================

# #     def get_screen_tabs(self, screen_id: int) -> List[dict]:
# #         """Get all tabs for a screen"""
# #         try:
# #             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs"
# #             r = requests.get(url, headers=self.headers, timeout=30)
# #             if r.status_code == 200:
# #                 return r.json()
# #         except Exception:
# #             pass
# #         return []

# #     def get_tab_fields(self, screen_id: int, tab_id: int) -> List[str]:
# #         """Get field IDs on a screen tab"""
# #         try:
# #             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
# #             r = requests.get(url, headers=self.headers, timeout=30)
# #             if r.status_code == 200:
# #                 return [f.get("id") for f in r.json() if f.get("id")]
# #         except Exception:
# #             pass
# #         return []

# #     def add_field_to_screen_tab(self, screen_id: int, tab_id: int, field_id: str) -> bool:
# #         """Add a field to a screen tab"""
# #         try:
# #             existing = self.get_tab_fields(screen_id, tab_id)
# #             if field_id in existing:
# #                 return True
            
# #             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
# #             payload = {"fieldId": field_id}
# #             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
# #             return r.status_code in (200, 201, 204) or "already" in r.text.lower()
                
# #         except Exception:
# #             return False

# #     def add_fields_to_project_screens(self, project_key: str, project_id: str, 
# #                                        field_ids: List[str]) -> Tuple[int, int]:
# #         """Add custom fields to project screens"""
# #         screens_updated = 0
# #         total_added = 0
        
# #         project_screens = self.get_all_project_screens(project_key, project_id)
        
# #         if not project_screens:
# #             self._log("  No project-specific screens found!", "WARN")
# #             return 0, 0
        
# #         self._log(f"  Found {len(project_screens)} project screen(s) to update", "INFO")
        
# #         for screen in project_screens:
# #             screen_id = screen.get("id")
# #             screen_name = screen.get("name", f"Screen {screen_id}")
            
# #             tabs = self.get_screen_tabs(screen_id)
# #             if not tabs:
# #                 continue
            
# #             tab_id = tabs[0].get("id")
# #             tab_name = tabs[0].get("name", "Field Tab")
            
# #             fields_added = 0
# #             for field_id in field_ids:
# #                 if self.add_field_to_screen_tab(screen_id, tab_id, field_id):
# #                     fields_added += 1
# #                 time.sleep(0.1)
            
# #             if fields_added > 0:
# #                 self._log(f"    ✓ {screen_name}: Added {fields_added} fields to '{tab_name}'", "SUCCESS")
# #                 screens_updated += 1
# #                 total_added += fields_added
        
# #         return screens_updated, total_added

# #     # =========================================================================
# #     # FIELD CONTEXT MANAGEMENT
# #     # =========================================================================

# #     def get_field_contexts(self, field_id: str) -> List[dict]:
# #         """Get contexts for a custom field"""
# #         try:
# #             url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
# #             r = requests.get(url, headers=self.headers, timeout=30)
# #             if r.status_code == 200:
# #                 return r.json().get("values", [])
# #         except Exception:
# #             pass
# #         return []

# #     def add_project_to_field_context(self, field_id: str, project_id: str, 
# #                                       project_key: str) -> bool:
# #         """Add project to field context"""
# #         contexts = self.get_field_contexts(field_id)
        
# #         for ctx in contexts:
# #             if ctx.get("isGlobalContext", False):
# #                 return True
        
# #         for ctx in contexts:
# #             project_ids = [str(p) for p in ctx.get("projectIds", [])]
# #             if str(project_id) in project_ids:
# #                 return True
        
# #         if contexts:
# #             ctx_id = contexts[0].get("id")
# #             try:
# #                 url = f"{self.base_url}/rest/api/3/field/{field_id}/context/{ctx_id}/project"
# #                 payload = {"projectIds": [str(project_id)]}
# #                 r = requests.put(url, headers=self.headers, json=payload, timeout=30)
# #                 if r.status_code in (200, 204):
# #                     return True
# #             except Exception:
# #                 pass
        
# #         if not contexts:
# #             try:
# #                 url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
# #                 payload = {
# #                     "name": f"Context for {project_key}",
# #                     "projectIds": [str(project_id)]
# #                 }
# #                 r = requests.post(url, headers=self.headers, json=payload, timeout=30)
# #                 if r.status_code in (200, 201):
# #                     return True
# #             except Exception:
# #                 pass
        
# #         return True

# #     # =========================================================================
# #     # FIELD CREATION
# #     # =========================================================================

# #     def create_custom_field(self, field_name: str, field_type: str,
# #                             searcher_key: str, description: str) -> Optional[str]:
# #         """Create a new custom field"""
# #         url = f"{self.base_url}/rest/api/3/field"
        
# #         payload = {
# #             "name": field_name,
# #             "description": description,
# #             "type": field_type,
# #             "searcherKey": searcher_key
# #         }
        
# #         try:
# #             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
# #             if r.status_code in (200, 201):
# #                 result = r.json()
# #                 field_id = result.get("id")
# #                 self._log(f"  Created field '{field_name}' → {field_id}", "SUCCESS")
# #                 return field_id
# #             else:
# #                 self._log(f"  Failed to create '{field_name}': {r.text[:150]}", "ERROR")
# #                 return None
                
# #         except Exception as e:
# #             self._log(f"Error creating field: {e}", "ERROR")
# #             return None

# #     def find_or_create_field(self, field_config: dict, project_id: str, 
# #                               project_key: str, all_fields: List[dict]) -> Optional[str]:
# #         """Find existing field or create new one"""
# #         field_name = field_config["name"]
        
# #         existing_id = self.find_field_id(all_fields, field_name)
        
# #         if existing_id:
# #             self._log(f"  Found existing: '{field_name}' → {existing_id}", "SUCCESS")
# #             self.add_project_to_field_context(existing_id, project_id, project_key)
# #             return existing_id
        
# #         self._log(f"  Creating: '{field_name}'...", "INFO")
# #         field_id = self.create_custom_field(
# #             field_name,
# #             field_config["type"],
# #             field_config["searcherKey"],
# #             field_config["description"]
# #         )
        
# #         if field_id:
# #             all_fields.append({
# #                 "id": field_id,
# #                 "name": field_name,
# #                 "custom": True
# #             })
# #             time.sleep(0.5)
# #             self.add_project_to_field_context(field_id, project_id, project_key)
# #             return field_id
        
# #         return None

# #     # =========================================================================
# #     # MAIN SETUP METHOD
# #     # =========================================================================

# #     def setup_project_fields(self, all_fields: List[dict], 
# #                               project_key: str, project_id: str) -> Tuple[dict, Optional[str]]:
# #         """Set up custom fields including Confluence Page URL field"""
# #         discovered = {}
# #         field_ids = []
        
# #         print()
# #         self._log("=" * 50, "INFO")
# #         self._log("PHASE 1: Setting up custom fields", "INFO")
# #         self._log("=" * 50, "INFO")
# #         print()
        
# #         for key, config in EXPECTED_FIELDS.items():
# #             field_id = self.find_or_create_field(config, project_id, project_key, all_fields)
# #             if field_id:
# #                 discovered[key] = field_id
# #                 field_ids.append(field_id)
                
# #                 # Store Confluence field ID for later use
# #                 if key == "confluence_page":
# #                     self.confluence_field_id = field_id
        
# #         epic_name_id = self.find_field_id(all_fields, "Epic Name")
# #         if epic_name_id:
# #             self._log(f"  Found 'Epic Name' → {epic_name_id}", "SUCCESS")
        
# #         print()
# #         self._log("=" * 50, "INFO")
# #         self._log("PHASE 2: Adding fields to project screens", "INFO")
# #         self._log("=" * 50, "INFO")
# #         print()
        
# #         if field_ids:
# #             self._log("  Waiting for field registration...", "INFO")
# #             time.sleep(3)
            
# #             screens_updated, fields_added = self.add_fields_to_project_screens(
# #                 project_key, project_id, field_ids
# #             )
            
# #             print()
# #             if screens_updated > 0:
# #                 self._log(f"  Summary: Updated {screens_updated} screens, {fields_added} field additions", "SUCCESS")
# #             else:
# #                 self._log("  Warning: No screens were updated", "WARN")
        
# #         return discovered, epic_name_id

# #     # =========================================================================
# #     # PROJECT AND ISSUE CREATION
# #     # =========================================================================

# #     def create_project(self, name: str, key: str, template: str, lead_id: str) -> dict:
# #         """Create a new Jira project"""
# #         url = f"{self.base_url}/rest/api/3/project"
        
# #         payload = {
# #             "key": key,
# #             "name": name,
# #             "projectTypeKey": "software",
# #             "projectTemplateKey": template,
# #             "leadAccountId": lead_id,
# #             "assigneeType": "PROJECT_LEAD",
# #             "description": f"Company-managed project: {name}",
# #         }
        
# #         r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
# #         if r.status_code in (200, 201):
# #             self._log(f"Project '{name}' created! Key: {key}", "SUCCESS")
# #             return r.json()
# #         else:
# #             error_msg = r.text
# #             try:
# #                 error_json = r.json()
# #                 if 'errors' in error_json:
# #                     error_msg = json.dumps(error_json['errors'], indent=2)
# #                 elif 'errorMessages' in error_json:
# #                     error_msg = ', '.join(error_json['errorMessages'])
# #             except Exception:
# #                 pass
# #             raise Exception(f"Failed to create project: {error_msg}")

# #     def create_issue(self, project_key: str, issue_type: str, summary: str,
# #                      description: str = None, fields_extra: dict = None) -> dict:
# #         """Create a Jira issue"""
# #         url = f"{self.base_url}/rest/api/3/issue"
        
# #         fields = {
# #             "project": {"key": project_key},
# #             "summary": summary,
# #             "issuetype": {"name": issue_type}
# #         }
        
# #         if description:
# #             fields["description"] = {
# #                 "type": "doc",
# #                 "version": 1,
# #                 "content": [{
# #                     "type": "paragraph",
# #                     "content": [{"type": "text", "text": description}]
# #                 }]
# #             }
        
# #         if fields_extra:
# #             fields.update(fields_extra)
        
# #         try:
# #             r = requests.post(url, headers=self.headers, json={"fields": fields}, timeout=30)
# #             r.raise_for_status()
# #             return r.json()
# #         except requests.exceptions.HTTPError:
# #             raise Exception(f"Failed to create {issue_type}: {r.text[:200]}")

# #     def update_issue_fields(self, issue_key: str, fields: dict) -> bool:
# #         """Update issue fields"""
# #         url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
# #         try:
# #             r = requests.put(url, headers=self.headers, json={"fields": fields}, timeout=30)
# #             return r.status_code in (200, 204)
# #         except Exception:
# #             return False

# #     def link_to_parent(self, issue_key: str, parent_key: str) -> bool:
# #         """Link issue to parent Epic"""
# #         return self.update_issue_fields(issue_key, {"parent": {"key": parent_key}})

# #     # =========================================================================
# #     # MAIN STRUCTURE GENERATION
# #     # =========================================================================

# #     def generate_structure(self, project_key: str, custom_fields: dict,
# #                            epic_name_field: Optional[str], lead_account_id: str,
# #                            confluence_space_key: str = None,
# #                            confluence_parent_page_id: str = None,
# #                            link_method: str = "description") -> dict:
# #         """
# #         Generate Epic/Story structure with Confluence integration.
        
# #         link_method options:
# #         - "description": Add link to issue description (RECOMMENDED - Most visible)
# #         - "comment": Add link as comment
# #         - "both": Add to description AND comment
# #         """
        
# #         print()
# #         self._log("=" * 50, "INFO")
# #         self._log(f"PHASE 3: Creating Epics and Stories", "INFO")
# #         if confluence_space_key:
# #             self._log(f"         (with Confluence pages in space: {confluence_space_key})", "CONFLUENCE")
# #             self._log(f"         Link method: {link_method}", "LINK")
# #         self._log("=" * 50, "INFO")
# #         print()
        
# #         epic_keys = {}
# #         epic_page_ids = {}
        
# #         total_epics = len(EPICS)
# #         total_stories = sum(len(s) for s in EPICS.values())
# #         epic_count = 0
# #         story_count = 0
# #         pages_created = 0
# #         links_created = 0
        
# #         for epic_name, story_list in EPICS.items():
# #             epic_count += 1
            
# #             # ─────────────────────────────────────────────────────────────────
# #             # CREATE EPIC
# #             # ─────────────────────────────────────────────────────────────────
# #             try:
# #                 fields_extra = {}
# #                 if epic_name_field:
# #                     fields_extra[epic_name_field] = epic_name
                
# #                 epic = self.create_issue(project_key, "Epic", epic_name,
# #                                          f"Epic: {epic_name}", fields_extra)
# #                 epic_key = epic.get("key")
# #                 epic_keys[epic_name] = epic_key
                
# #                 short_name = epic_name[:50] + "..." if len(epic_name) > 50 else epic_name
# #                 self._log(f"[{epic_count}/{total_epics}] Epic: {short_name} → {epic_key}", "SUCCESS")
                
# #                 # Create Epic Confluence page
# #                 if confluence_space_key:
# #                     epic_page_title = f"{epic_key} - {epic_name[:80]}"
# #                     epic_page = self.create_confluence_page(
# #                         space_key=confluence_space_key,
# #                         title=epic_page_title,
# #                         jira_issue_key=epic_key,
# #                         jira_issue_summary=epic_name,
# #                         parent_id=confluence_parent_page_id
# #                     )
# #                     if epic_page:
# #                         epic_page_ids[epic_name] = epic_page.get("id")
# #                         pages_created += 1
# #                         page_url = self.get_confluence_page_url(epic_page)
                        
# #                         # Link Epic to Confluence page
# #                         result = self.link_confluence_to_jira(
# #                             issue_key=epic_key,
# #                             page_url=page_url,
# #                             page_title=epic_page_title,
# #                             original_description=f"Epic: {epic_name}",
# #                             add_to_description=(link_method in ["description", "both"]),
# #                             add_comment=(link_method in ["comment", "both"]),
# #                             set_url_field=True
# #                         )
# #                         if any(result.values()):
# #                             links_created += 1
                        
# #                         self._log(f"  📄 Epic page created & linked", "CONFLUENCE")
                
# #             except Exception as e:
# #                 self._log(f"Failed to create Epic: {e}", "ERROR")
# #                 continue
            
# #             # ─────────────────────────────────────────────────────────────────
# #             # CREATE STORIES
# #             # ─────────────────────────────────────────────────────────────────
# #             for story_name in story_list:
# #                 story_count += 1
                
# #                 # Prepare custom field values
# #                 story_fields = {}
# #                 today = datetime.utcnow().date()
                
# #                 if "percent_complete" in custom_fields:
# #                     story_fields[custom_fields["percent_complete"]] = "0"
# #                 if "target_start" in custom_fields:
# #                     story_fields[custom_fields["target_start"]] = str(today)
# #                 if "target_end" in custom_fields:
# #                     story_fields[custom_fields["target_end"]] = str(today + timedelta(days=7))
# #                 if "owning" in custom_fields:
# #                     story_fields[custom_fields["owning"]] = {"accountId": lead_account_id}
                
# #                 story_key = None
                
# #                 try:
# #                     story = self.create_issue(project_key, "Story", story_name,
# #                                               f"Story: {story_name}", story_fields)
# #                     story_key = story.get("key")
# #                     linked = self.link_to_parent(story_key, epic_key)
                    
# #                     status = "✓" if linked else "○"
# #                     self._log(f"  [{story_count}/{total_stories}] {status} {story_key}: {story_name[:40]}...", "SUCCESS")
                    
# #                 except Exception:
# #                     try:
# #                         story = self.create_issue(project_key, "Story", story_name)
# #                         story_key = story.get("key")
# #                         self.link_to_parent(story_key, epic_key)
                        
# #                         if story_fields:
# #                             time.sleep(0.2)
# #                             self.update_issue_fields(story_key, story_fields)
                        
# #                         self._log(f"  [{story_count}/{total_stories}] ○ {story_key} (retry)", "SUCCESS")
# #                     except Exception:
# #                         self._log(f"  Failed: {story_name[:30]}...", "ERROR")
# #                         continue
                
# #                 # ─────────────────────────────────────────────────────────────
# #                 # CREATE CONFLUENCE PAGE AND LINK TO STORY
# #                 # ─────────────────────────────────────────────────────────────
# #                 if confluence_space_key and story_key:
# #                     try:
# #                         parent_id = epic_page_ids.get(epic_name, confluence_parent_page_id)
# #                         page_title = f"{story_key} - {story_name}"
                        
# #                         page = self.create_confluence_page(
# #                             space_key=confluence_space_key,
# #                             title=page_title,
# #                             jira_issue_key=story_key,
# #                             jira_issue_summary=story_name,
# #                             parent_id=parent_id
# #                         )
                        
# #                         if page:
# #                             pages_created += 1
# #                             page_url = self.get_confluence_page_url(page)
                            
# #                             # Create visible links in Jira
# #                             result = self.link_confluence_to_jira(
# #                                 issue_key=story_key,
# #                                 page_url=page_url,
# #                                 page_title=page_title,
# #                                 original_description=f"Story: {story_name}",
# #                                 add_to_description=(link_method in ["description", "both"]),
# #                                 add_comment=(link_method in ["comment", "both"]),
# #                                 set_url_field=True
# #                             )
                            
# #                             if any(result.values()):
# #                                 links_created += 1
# #                                 methods_used = [k for k, v in result.items() if v]
# #                                 self._log(f"      🔗 Linked via: {', '.join(methods_used)}", "LINK")
# #                             else:
# #                                 self._log(f"      ⚠️ Page created but linking failed", "WARN")
                        
# #                         time.sleep(0.15)
                        
# #                     except Exception as e:
# #                         self._log(f"      Failed Confluence: {e}", "WARN")
        
# #         # Summary
# #         print()
# #         self._log("-" * 50, "INFO")
# #         self._log(f"Structure Summary:", "INFO")
# #         self._log(f"  • Epics created: {len(epic_keys)}", "SUCCESS")
# #         self._log(f"  • Stories created: {story_count}", "SUCCESS")
# #         if confluence_space_key:
# #             self._log(f"  • Confluence pages: {pages_created}", "CONFLUENCE")
# #             self._log(f"  • Issues linked: {links_created}", "LINK")
        
# #         return epic_keys


# # # =============================================================================
# # # MAIN FUNCTION
# # # =============================================================================

# # def main():
# #     """Main execution"""
    
# #     print("\n" + "=" * 60)
# #     print("  🚀 JIRA + CONFLUENCE PROJECT GENERATOR")
# #     print("     (with VISIBLE Confluence links in Jira)")
# #     print("=" * 60 + "\n")
    
# #     # =========================================================================
# #     # GET CREDENTIALS
# #     # =========================================================================
# #     print("📋 ATLASSIAN CREDENTIALS\n")
    
# #     ATLASSIAN_URL = input("Enter Atlassian URL (e.g., https://yoursite.atlassian.net): ").strip()
# #     ATLASSIAN_EMAIL = input("Enter Email: ").strip()
# #     ATLASSIAN_API_TOKEN = getpass.getpass("Enter API Token (hidden): ")
    
# #     if not all([ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN]):
# #         print("❌ All credentials are required!")
# #         return
    
# #     generator = JiraProjectGenerator(ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN)
# #     # generator.debug_mode = True  # Uncomment for verbose output
    
# #     # =========================================================================
# #     # TEST CONNECTIONS
# #     # =========================================================================
# #     print("\n" + "-" * 60 + "\n")
# #     print("🔌 TESTING CONNECTIONS\n")
    
# #     generator._log("Testing Jira connection...", "INFO")
# #     jira_success, jira_user = generator.test_connection()
    
# #     if not jira_success:
# #         generator._log(f"Jira connection failed: {jira_user.get('error')}", "ERROR")
# #         return
    
# #     lead_id = jira_user.get("accountId")
# #     user_name = jira_user.get("displayName", jira_user.get("emailAddress"))
# #     generator._log(f"Jira: Connected as {user_name}", "SUCCESS")
    
# #     generator._log("Testing Confluence connection...", "INFO")
# #     conf_success, conf_user = generator.test_confluence_connection()
    
# #     confluence_enabled = False
# #     if not conf_success:
# #         generator._log(f"Confluence connection failed: {conf_user.get('error')}", "ERROR")
# #         generator._log("Continuing without Confluence...", "WARN")
# #     else:
# #         generator._log(f"Confluence: Connected", "SUCCESS")
# #         confluence_enabled = True
    
# #     # =========================================================================
# #     # GET PROJECT DETAILS
# #     # =========================================================================
# #     print("\n" + "-" * 60 + "\n")
# #     print("📋 JIRA PROJECT DETAILS\n")
    
# #     while True:
# #         project_name = input("Enter Project Name: ").strip()
# #         if not project_name:
# #             generator._log("Project name required!", "ERROR")
# #             continue
        
# #         suggested_key = generator.suggest_project_key(project_name)
# #         key_input = input(f"Enter Project Key (suggested: {suggested_key}): ").strip().upper()
# #         project_key = key_input if key_input else suggested_key
        
# #         if not re.match(r'^[A-Z][A-Z0-9]{1,9}$', project_key):
# #             generator._log("Invalid key!", "ERROR")
# #             continue
        
# #         if generator.check_project_exists(project_key):
# #             generator._log(f"Project '{project_key}' already exists!", "ERROR")
# #             if input("Try different key? (y/N): ").strip().lower() == 'y':
# #                 continue
# #             return
# #         break
    
# #     # =========================================================================
# #     # SELECT TEMPLATE
# #     # =========================================================================
# #     print("\n📐 SELECT PROJECT TEMPLATE\n")
# #     for k, (name, _) in VALID_TEMPLATES.items():
# #         print(f"  {k}. {name}")
    
# #     choice = input("\nChoose (1-3) [default: 2]: ").strip() or "2"
# #     if choice not in VALID_TEMPLATES:
# #         generator._log("Invalid choice!", "ERROR")
# #         return
    
# #     template_name, template_key = VALID_TEMPLATES[choice]
    
# #     # =========================================================================
# #     # CONFLUENCE SPACE DETAILS
# #     # =========================================================================
# #     confluence_space_key = None
# #     confluence_space_name = None
# #     link_method = "description"
    
# #     if confluence_enabled:
# #         print("\n" + "-" * 60 + "\n")
# #         print("📄 CONFLUENCE SPACE DETAILS\n")
        
# #         create_space = input("Create Confluence space? (Y/n): ").strip().lower()
        
# #         if create_space != 'n':
# #             confluence_space_name = input(f"Space Name (default: {project_name} Docs): ").strip()
# #             if not confluence_space_name:
# #                 confluence_space_name = f"{project_name} Docs"
            
# #             suggested_space_key = generator.suggest_space_key(confluence_space_name)
# #             space_key_input = input(f"Space Key (suggested: {suggested_space_key}): ").strip().upper()
# #             confluence_space_key = space_key_input if space_key_input else suggested_space_key
            
# #             if generator.check_confluence_space_exists(confluence_space_key):
# #                 generator._log(f"Space '{confluence_space_key}' exists!", "WARN")
# #                 use_existing = input("Use existing? (Y/n): ").strip().lower()
# #                 if use_existing == 'n':
# #                     confluence_space_key = None
            
# #             if confluence_space_key:
# #                 print("\n🔗 LINK VISIBILITY METHOD\n")
# #                 print("  1. Description (RECOMMENDED - Link in issue description)")
# #                 print("  2. Comment (Link as a comment)")
# #                 print("  3. Both (Description + Comment)")
                
# #                 link_choice = input("\nChoose (1-3) [default: 1]: ").strip() or "1"
# #                 link_method = {"1": "description", "2": "comment", "3": "both"}.get(link_choice, "description")
    
# #     # =========================================================================
# #     # SUMMARY
# #     # =========================================================================
# #     print("\n" + "-" * 60)
# #     print("\n📊 SUMMARY\n")
# #     print(f"  JIRA PROJECT:")
# #     print(f"    Name:      {project_name}")
# #     print(f"    Key:       {project_key}")
# #     print(f"    Template:  {template_name}")
# #     print(f"    Epics:     {len(EPICS)}")
# #     print(f"    Stories:   {sum(len(s) for s in EPICS.values())}")
    
# #     if confluence_space_key:
# #         print(f"\n  CONFLUENCE:")
# #         print(f"    Space:     {confluence_space_name} ({confluence_space_key})")
# #         print(f"    Link via:  {link_method.upper()}")
# #         print(f"\n  WHERE YOU'LL SEE LINKS IN JIRA:")
# #         if link_method in ["description", "both"]:
# #             print(f"    ✓ Issue Description (top of issue)")
# #         print(f"    ✓ 'Confluence Page' custom field")
# #         if link_method in ["comment", "both"]:
# #             print(f"    ✓ Comments/Activity section")
    
# #     print()
    
# #     if input("Proceed? (y/N): ").strip().lower() != 'y':
# #         generator._log("Cancelled", "WARN")
# #         return
    
# #     print("\n" + "=" * 60)
    
# #     # =========================================================================
# #     # CREATE PROJECT
# #     # =========================================================================
# #     try:
# #         generator._log("Creating Jira project...", "INFO")
# #         project = generator.create_project(project_name, project_key, template_key, lead_id)
# #         project_id = project.get("id")
# #     except Exception as e:
# #         generator._log(f"Failed: {e}", "ERROR")
# #         return
    
# #     generator._log("Waiting for initialization (10s)...", "INFO")
# #     time.sleep(10)
    
# #     # =========================================================================
# #     # SETUP FIELDS
# #     # =========================================================================
# #     try:
# #         all_fields = generator.fetch_all_fields()
# #         custom_fields, epic_name_field = generator.setup_project_fields(
# #             all_fields, project_key, project_id
# #         )
# #     except Exception as e:
# #         generator._log(f"Field setup error: {e}", "ERROR")
# #         custom_fields = {}
# #         epic_name_field = None
    
# #     # =========================================================================
# #     # CREATE CONFLUENCE SPACE
# #     # =========================================================================
# #     confluence_parent_page_id = None
    
# #     if confluence_space_key and not generator.check_confluence_space_exists(confluence_space_key):
# #         print()
# #         generator._log("Creating Confluence space...", "CONFLUENCE")
        
# #         try:
# #             generator.create_confluence_space(
# #                 space_key=confluence_space_key,
# #                 space_name=confluence_space_name,
# #                 description=f"Documentation for {project_name} ({project_key})"
# #             )
# #             confluence_parent_page_id = generator.get_space_homepage_id(confluence_space_key)
# #         except Exception as e:
# #             generator._log(f"Failed: {e}", "ERROR")
# #             confluence_space_key = None
# #     elif confluence_space_key:
# #         confluence_parent_page_id = generator.get_space_homepage_id(confluence_space_key)
    
# #     # =========================================================================
# #     # GENERATE STRUCTURE
# #     # =========================================================================
# #     try:
# #         epic_keys = generator.generate_structure(
# #             project_key=project_key,
# #             custom_fields=custom_fields,
# #             epic_name_field=epic_name_field,
# #             lead_account_id=lead_id,
# #             confluence_space_key=confluence_space_key,
# #             confluence_parent_page_id=confluence_parent_page_id,
# #             link_method=link_method
# #         )
# #     except Exception as e:
# #         generator._log(f"Structure error: {e}", "ERROR")
# #         epic_keys = {}
    
# #     # =========================================================================
# #     # FINAL SUMMARY
# #     # =========================================================================
# #     print("\n" + "=" * 60)
# #     print("  ✨ COMPLETE!")
# #     print("=" * 60)
    
# #     print(f"\n🔗 JIRA PROJECT: {ATLASSIAN_URL}/projects/{project_key}")
    
# #     if confluence_space_key:
# #         print(f"📄 CONFLUENCE: {ATLASSIAN_URL}/wiki/spaces/{confluence_space_key}")
# #         print(f"\n📍 WHERE TO FIND CONFLUENCE LINKS IN JIRA:")
# #         print(f"   1. Open any Story in Jira")
# #         if link_method in ["description", "both"]:
# #             print(f"   2. Look at the DESCRIPTION (top) - blue info panel with link")
# #         print(f"   3. Check 'Confluence Page' field in Details section")
# #         if link_method in ["comment", "both"]:
# #             print(f"   4. Check Activity/Comments section")
    
# #     print()


# # if __name__ == "__main__":
# #     try:
# #         main()
# #     except KeyboardInterrupt:
# #         print("\n⚠️ Cancelled\n")
# #         sys.exit(0)
# #     except Exception as e:
# #         print(f"\n❌ Error: {e}\n")
# #         import traceback
# #         traceback.print_exc()
# #         sys.exit(1)
# import base64
# import re
# import json
# import time
# import sys
# import getpass
# import requests
# from datetime import datetime, timedelta
# from typing import List, Dict, Optional, Tuple

# # =============================================================================
# # IMPORT CONFLUENCE TEMPLATES
# # =============================================================================

# try:
#     from confluence_templates import (
#         get_template_for_story,
#         get_template_for_epic,
#         list_available_templates
#     )
#     TEMPLATES_AVAILABLE = True
# except ImportError:
#     TEMPLATES_AVAILABLE = False
#     print("⚠️  Warning: confluence_templates.py not found. Using basic templates.")


# # =============================================================================
# # CONFIGURATION
# # =============================================================================

# VALID_TEMPLATES = {
#     "1": ("Kanban", "com.pyxis.greenhopper.jira:gh-kanban-template"),
#     "2": ("Scrum", "com.pyxis.greenhopper.jira:gh-scrum-template"),
#     "3": ("Bug Tracking", "com.atlassian.jira-core-project-templates:jira-core-project-management"),
# }

# # Project structure to create
# EPICS = {
#     "ASSESSMENT & PLANNING (2 - 12 weeks, depending on project scope, sizing, access, onboarding)": [
#         "Onboarding and Access - See Access Tab for Details",
#         "Introductory Call",
#         "Discuss NON-PRODUCTION environments",
#         "Set up Weekly Touchpoint w/Atlassian (if above 1000 users)",
#         "Discuss Atlassian Cloud Status",
#         "Start Atlassian CLOUD Trial (if needed)",
#         "Set up Weekly Touchpoint w/Project Team",
#         "Set up Atlassian Guard (if needed/in scope)",
#         "Open Ticket w/Atlassian for MOVE",
#         "Refresh lower instance of Jira to current version",
#         "Licensing Tier Jira",
#         "Licensing Tier Confluence",
#         "Discussion/Discovery Migration Scope for Confluence",
#         "Discussion/Discovery Migration Scope for Jira",
#         "Discussion/Discovery Integrations",
#         "Discussion/Discovery User Management",
#         "Start Atlassian Guard Trial (if needed/in scope)",
#         "User Clean Up Tasks",
#         "Jira - Add-on Assessment",
#         "Confluence - Add-on Assessment",
#         "Environment Assessment & Pre-Migration Checklist",
#         "Develop Migration Approach & Draft Runbook",
#         "Develop Testing Plan",
#         "Develop Communications Plan",
#         "Develop Training Plan (if needed)",
#         "Review & Acceptance - Environment Assessment",
#         "Review & Acceptance - Jira Projects Assessment",
#         "Review & Acceptance - Confluence Spaces",
#         "Review & Acceptance - Jira Add-ons",
#         "Review & Acceptance - Atlassian Guard Setup",
#         "Review & Acceptance - Confluence Addons",
#         "Review & Acceptance - Confluence Macros",
#         "Review & Acceptance - Integrations",
#         "Review & Acceptance - Pre Migration Checklists (Jira & Confluence)",
#         "Budget Review Meeting (T&M)",
#         "Refresh Staging Environments (Jira and Confluence)",
#         "<other tasks as identified>"
#     ],
#     "TEST MIGRATION (4 - 16 weeks, depending on scope, sizing, & capacity of Client)": [
#         "Execute User Migration using JCMA",
#         "Execute Complete test migration using JCMA",
#         "Transformation Tasks - Scriptrunner",
#         "Basic Application Integrity Tests",
#         "Workflow Review & Migration Assistant Errors",
#         "Working Session to review Migration Assistant Findings (if needed)",
#         "Execute Add-on Remediation Plan",
#         "Execute Confluence Migration using CCMA",
#         "Post migration checks Jira & Confluence"
#     ],
#     "USER ACCEPTANCE TESTING (1 - 2 weeks, depending on scope, sizing, & capacity of Client)": [
#         "Capula Project Team Testing",
#         "Hold UAT Training (if needed)",
#         "User Acceptance Testing",
#         "Issue Resolution",
#         "Go/No Go Decision (UAT Acceptance)"
#     ],
#     "PRODUCTION MIGRATION (TBD)": ["Finalize Migration Runbook", "See Migration Timeline Tab "],
#     "POST MIGRATION SUPPORT (4 weeks)": ["<items as identified>"],
# }

# # Expected custom fields with their types
# EXPECTED_FIELDS = {
#     "percent_complete": {
#         "name": "% Complete",
#         "field_id": None,
#         "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
#         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
#         "description": "Percentage of task completion"
#     },
#     "target_start": {
#         "name": "Target Start Date",
#         "field_id": None,
#         "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
#         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
#         "description": "Target start date for the task"
#     },
#     "target_end": {
#         "name": "Target End Date",
#         "field_id": None,
#         "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
#         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
#         "description": "Target end date for the task"
#     },
#     "owning": {
#         "name": "Owning",
#         "field_id": None,
#         "type": "com.atlassian.jira.plugin.system.customfieldtypes:userpicker",
#         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:userpickergroupsearcher",
#         "description": "Owner of the task"
#     },
#     "confluence_page": {
#         "name": "Confluence Page",
#         "field_id": None,
#         "type": "com.atlassian.jira.plugin.system.customfieldtypes:url",
#         "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:exacttextsearcher",
#         "description": "Link to related Confluence documentation page"
#     }
# }


# # =============================================================================
# # MAIN CLASS
# # =============================================================================

# class JiraProjectGenerator:
#     def __init__(self, base_url: str, email: str, api_token: str):
#         self.base_url = base_url.rstrip('/')
#         self.email = email
#         self.api_token = api_token
#         self.headers = self._get_auth_header()
#         self.debug_mode = False
#         self.confluence_field_id = None

#     def _get_auth_header(self) -> dict:
#         """Generate Basic Auth header for Jira/Confluence API"""
#         token = f"{self.email}:{self.api_token}"
#         b64 = base64.b64encode(token.encode()).decode()
#         return {
#             "Authorization": f"Basic {b64}",
#             "Content-Type": "application/json",
#             "Accept": "application/json"
#         }

#     def _log(self, message: str, level: str = "INFO"):
#         """Pretty logging with emoji indicators"""
#         icons = {
#             "INFO": "🔵",
#             "SUCCESS": "✅",
#             "ERROR": "❌",
#             "WARN": "⚠️",
#             "QUESTION": "❓",
#             "DEBUG": "🔍",
#             "CONFLUENCE": "📄",
#             "LINK": "🔗",
#             "TEMPLATE": "📝"
#         }
#         if level == "DEBUG" and not self.debug_mode:
#             return
#         print(f"{icons.get(level, '•')} {message}")

#     # =========================================================================
#     # JIRA CONNECTION & UTILITIES
#     # =========================================================================

#     def suggest_project_key(self, name: str) -> str:
#         """Generate a suggested project key from project name"""
#         name_clean = re.sub(r'[^A-Za-z0-9 ]+', '', name).strip()
#         parts = name_clean.split()

#         if len(parts) == 1:
#             key = parts[0][:4].upper()
#         else:
#             key = ''.join(p[0] for p in parts if p)[:4].upper()

#         if len(key) < 2:
#             key = (key + "PR")[:2]

#         return key[:10]

#     def suggest_space_key(self, name: str) -> str:
#         """Generate a suggested Confluence space key from space name"""
#         name_clean = re.sub(r'[^A-Za-z0-9 ]+', '', name).strip()
#         parts = name_clean.split()

#         if len(parts) == 1:
#             key = parts[0][:10].upper()
#         else:
#             key = ''.join(p[0] for p in parts if p)[:6].upper()

#         if len(key) < 2:
#             key = (key + "DOC")[:3]

#         return key[:10]

#     def check_project_exists(self, project_key: str) -> bool:
#         """Check if a project with this key already exists"""
#         try:
#             url = f"{self.base_url}/rest/api/3/project/{project_key}"
#             r = requests.get(url, headers=self.headers, timeout=10)
#             return r.status_code == 200
#         except Exception:
#             return False

#     def test_connection(self) -> Tuple[bool, dict]:
#         """Test Jira API connection and get current user info"""
#         try:
#             url = f"{self.base_url}/rest/api/3/myself"
#             r = requests.get(url, headers=self.headers, timeout=10)
#             r.raise_for_status()
#             return True, r.json()
#         except requests.exceptions.RequestException as e:
#             return False, {"error": str(e)}

#     # =========================================================================
#     # CONFLUENCE CONNECTION & SPACE MANAGEMENT
#     # =========================================================================

#     def test_confluence_connection(self) -> Tuple[bool, dict]:
#         """Test Confluence API connection"""
#         try:
#             url = f"{self.base_url}/wiki/rest/api/user/current"
#             r = requests.get(url, headers=self.headers, timeout=10)
#             r.raise_for_status()
#             return True, r.json()
#         except requests.exceptions.RequestException as e:
#             return False, {"error": str(e)}

#     def check_confluence_space_exists(self, space_key: str) -> bool:
#         """Check if a Confluence space with this key already exists"""
#         try:
#             url = f"{self.base_url}/wiki/rest/api/space/{space_key.upper()}"
#             r = requests.get(url, headers=self.headers, timeout=10)
#             return r.status_code == 200
#         except Exception:
#             return False

#     def create_confluence_space(self, space_key: str, space_name: str, 
#                                  description: str = None) -> dict:
#         """Create a new Confluence space"""
#         url = f"{self.base_url}/wiki/rest/api/space"
        
#         payload = {
#             "key": space_key.upper(),
#             "name": space_name,
#             "description": {
#                 "plain": {
#                     "value": description or f"Documentation space for: {space_name}",
#                     "representation": "plain"
#                 }
#             }
#         }
        
#         r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
#         if r.status_code in (200, 201):
#             space_data = r.json()
#             self._log(f"Confluence space '{space_name}' created! Key: {space_key.upper()}", "SUCCESS")
#             return space_data
#         else:
#             error_msg = r.text
#             try:
#                 error_json = r.json()
#                 if 'message' in error_json:
#                     error_msg = error_json['message']
#             except Exception:
#                 pass
#             raise Exception(f"Failed to create Confluence space: {error_msg}")

#     def get_space_homepage_id(self, space_key: str) -> Optional[str]:
#         """Get the homepage ID of a Confluence space"""
#         try:
#             url = f"{self.base_url}/wiki/rest/api/space/{space_key.upper()}"
#             params = {"expand": "homepage"}
#             r = requests.get(url, headers=self.headers, params=params, timeout=10)
#             if r.status_code == 200:
#                 data = r.json()
#                 homepage = data.get("homepage", {})
#                 return homepage.get("id")
#         except Exception as e:
#             self._log(f"Error getting space homepage: {e}", "DEBUG")
#         return None

#     # =========================================================================
#     # CONFLUENCE PAGE MANAGEMENT - WITH TEMPLATE SUPPORT
#     # =========================================================================

#     def create_confluence_page(self, space_key: str, title: str, 
#                                 jira_issue_key: str,
#                                 jira_issue_summary: str,
#                                 parent_id: str = None,
#                                 is_epic: bool = False) -> Optional[dict]:
#         """
#         Create a Confluence page using the appropriate template.
        
#         Args:
#             space_key: Confluence space key
#             title: Page title
#             jira_issue_key: Jira issue key for linking
#             jira_issue_summary: Story/Epic summary for template selection
#             parent_id: Optional parent page ID
#             is_epic: True if this is an Epic page
        
#         Returns:
#             Page data dict or None if failed
#         """
#         url = f"{self.base_url}/wiki/rest/api/content"
        
#         # Get appropriate template content
#         if TEMPLATES_AVAILABLE:
#             if is_epic:
#                 template_func = get_template_for_epic()
#                 template_name = "epic"
#             else:
#                 template_func = get_template_for_story(jira_issue_summary)
#                 template_name = template_func.__name__.replace("template_", "")
            
#             body_content = template_func(
#                 jira_issue_key=jira_issue_key,
#                 jira_issue_summary=jira_issue_summary,
#                 jira_base_url=self.base_url
#             )
            
#             self._log(f"      Using template: {template_name}", "TEMPLATE")
#         else:
#             # Fallback basic template when confluence_templates.py is not available
#             jira_link = f"{self.base_url}/browse/{jira_issue_key}"
#             today = datetime.utcnow().strftime("%Y-%m-%d")
            
#             body_content = f"""
# <ac:structured-macro ac:name="info" ac:schema-version="1">
#   <ac:rich-text-body>
#     <p><strong>📋 Jira Issue:</strong> <a href="{jira_link}">{jira_issue_key}</a></p>
#     <p><strong>📅 Created:</strong> {today}</p>
#   </ac:rich-text-body>
# </ac:structured-macro>

# <h1>{jira_issue_summary}</h1>

# <hr/>

# <h2>📋 Overview</h2>
# <table>
#   <tbody>
#     <tr>
#       <th style="width: 150px;">Status</th>
#       <td><ac:structured-macro ac:name="status" ac:schema-version="1"><ac:parameter ac:name="title">NOT STARTED</ac:parameter><ac:parameter ac:name="colour">Grey</ac:parameter></ac:structured-macro></td>
#     </tr>
#     <tr>
#       <th>Owner</th>
#       <td><em>Assign owner</em></td>
#     </tr>
#     <tr>
#       <th>Target Date</th>
#       <td><em>Set target date</em></td>
#     </tr>
#     <tr>
#       <th>Jira Issue</th>
#       <td><a href="{jira_link}">{jira_issue_key}</a></td>
#     </tr>
#   </tbody>
# </table>

# <h2>📝 Description</h2>
# <p><em>Add detailed description here...</em></p>

# <h2>✅ Acceptance Criteria</h2>
# <ul>
#   <li><em>Criterion 1</em></li>
#   <li><em>Criterion 2</em></li>
#   <li><em>Criterion 3</em></li>
# </ul>

# <h2>📎 Attachments & References</h2>
# <p><em>Add relevant documents, links, and references here...</em></p>

# <h2>📝 Notes</h2>
# <p><em>Add notes and updates here...</em></p>

# <hr/>
# <p><em>Last updated: {today}</em></p>
# """
        
#         payload = {
#             "type": "page",
#             "title": title,
#             "space": {"key": space_key.upper()},
#             "body": {
#                 "storage": {
#                     "value": body_content,
#                     "representation": "storage"
#                 }
#             }
#         }
        
#         if parent_id:
#             payload["ancestors"] = [{"id": str(parent_id)}]
        
#         try:
#             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
#             if r.status_code in (200, 201):
#                 return r.json()
#             else:
#                 error_msg = r.text[:200]
#                 try:
#                     error_json = r.json()
#                     if 'message' in error_json:
#                         error_msg = error_json['message']
#                 except Exception:
#                     pass
#                 self._log(f"Failed to create page '{title[:30]}...': {error_msg}", "WARN")
#                 return None
                
#         except Exception as e:
#             self._log(f"Error creating Confluence page: {e}", "WARN")
#             return None

#     def get_confluence_page_url(self, page_data: dict) -> str:
#         """Extract the web URL from Confluence page data"""
#         links = page_data.get("_links", {})
#         base = links.get("base", f"{self.base_url}/wiki")
#         webui = links.get("webui", "")
#         return f"{base}{webui}"

#     # =========================================================================
#     # JIRA-CONFLUENCE LINKING
#     # =========================================================================

#     def add_confluence_link_to_description(self, issue_key: str, 
#                                             page_url: str, 
#                                             page_title: str,
#                                             original_description: str = None) -> bool:
#         """
#         Add Confluence page link directly to the issue description.
#         This is the MOST VISIBLE method - appears at top of issue.
#         """
#         description_adf = {
#             "type": "doc",
#             "version": 1,
#             "content": [
#                 {
#                     "type": "panel",
#                     "attrs": {
#                         "panelType": "info"
#                     },
#                     "content": [
#                         {
#                             "type": "paragraph",
#                             "content": [
#                                 {
#                                     "type": "text",
#                                     "text": "📄 Documentation: ",
#                                     "marks": [{"type": "strong"}]
#                                 },
#                                 {
#                                     "type": "text",
#                                     "text": page_title,
#                                     "marks": [
#                                         {
#                                             "type": "link",
#                                             "attrs": {"href": page_url}
#                                         }
#                                     ]
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "type": "paragraph",
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": original_description or ""
#                         }
#                     ]
#                 }
#             ]
#         }
        
#         url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
#         payload = {"fields": {"description": description_adf}}
        
#         try:
#             r = requests.put(url, headers=self.headers, json=payload, timeout=30)
#             return r.status_code in (200, 204)
#         except Exception as e:
#             self._log(f"Error updating description: {e}", "DEBUG")
#             return False

#     def set_confluence_url_field(self, issue_key: str, page_url: str) -> bool:
#         """
#         Set the Confluence Page URL custom field.
#         This creates a clickable link in the issue details.
#         """
#         if not self.confluence_field_id:
#             return False
        
#         url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
#         payload = {
#             "fields": {
#                 self.confluence_field_id: page_url
#             }
#         }
        
#         try:
#             r = requests.put(url, headers=self.headers, json=payload, timeout=30)
#             return r.status_code in (200, 204)
#         except Exception as e:
#             self._log(f"Error setting Confluence field: {e}", "DEBUG")
#             return False

#     def add_confluence_link_comment(self, issue_key: str, 
#                                      page_url: str, 
#                                      page_title: str) -> bool:
#         """
#         Add a styled comment with the Confluence link.
#         This is visible in the Activity section.
#         """
#         url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        
#         payload = {
#             "body": {
#                 "type": "doc",
#                 "version": 1,
#                 "content": [
#                     {
#                         "type": "panel",
#                         "attrs": {
#                             "panelType": "note"
#                         },
#                         "content": [
#                             {
#                                 "type": "paragraph",
#                                 "content": [
#                                     {
#                                         "type": "text",
#                                         "text": "📄 DOCUMENTATION PAGE",
#                                         "marks": [{"type": "strong"}]
#                                     }
#                                 ]
#                             },
#                             {
#                                 "type": "paragraph",
#                                 "content": [
#                                     {
#                                         "type": "text",
#                                         "text": "Click here to view: "
#                                     },
#                                     {
#                                         "type": "text",
#                                         "text": page_title,
#                                         "marks": [
#                                             {
#                                                 "type": "link",
#                                                 "attrs": {"href": page_url}
#                                             },
#                                             {"type": "strong"}
#                                         ]
#                                     }
#                                 ]
#                             }
#                         ]
#                     }
#                 ]
#             }
#         }
        
#         try:
#             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
#             return r.status_code in (200, 201)
#         except Exception as e:
#             self._log(f"Error adding comment: {e}", "DEBUG")
#             return False

#     def link_confluence_to_jira(self, issue_key: str, 
#                                  page_url: str, 
#                                  page_title: str,
#                                  original_description: str = None,
#                                  add_to_description: bool = True,
#                                  add_comment: bool = False,
#                                  set_url_field: bool = True) -> dict:
#         """
#         Create visible links from Jira to Confluence using multiple methods.
        
#         Returns dict with status of each method.
#         """
#         results = {
#             "description": False,
#             "url_field": False,
#             "comment": False
#         }
        
#         # Method 1: Add to Description (Most Visible)
#         if add_to_description:
#             results["description"] = self.add_confluence_link_to_description(
#                 issue_key, page_url, page_title, original_description
#             )
        
#         # Method 2: Set URL Custom Field
#         if set_url_field and self.confluence_field_id:
#             results["url_field"] = self.set_confluence_url_field(issue_key, page_url)
        
#         # Method 3: Add Comment
#         if add_comment:
#             results["comment"] = self.add_confluence_link_comment(
#                 issue_key, page_url, page_title
#             )
        
#         return results

#     # =========================================================================
#     # JIRA FIELD MANAGEMENT
#     # =========================================================================

#     def fetch_all_fields(self) -> List[dict]:
#         """Fetch all Jira fields to discover custom field IDs"""
#         url = f"{self.base_url}/rest/api/3/field"
#         r = requests.get(url, headers=self.headers, timeout=30)
#         r.raise_for_status()
#         return r.json()

#     def find_field_id(self, fields: List[dict], display_name: str) -> Optional[str]:
#         """Find field ID by display name (case-insensitive)"""
#         for f in fields:
#             if f.get("name", "").strip().lower() == display_name.strip().lower():
#                 return f.get("id")
#         return None

#     # =========================================================================
#     # SCREEN DISCOVERY
#     # =========================================================================

#     def get_project_screens_by_name(self, project_key: str) -> List[dict]:
#         """Find screens that belong to this project"""
#         screens = []
#         start_at = 0
#         max_results = 100
        
#         while True:
#             url = f"{self.base_url}/rest/api/3/screens"
#             params = {"startAt": start_at, "maxResults": max_results}
            
#             try:
#                 r = requests.get(url, headers=self.headers, params=params, timeout=30)
#                 if r.status_code != 200:
#                     break
                    
#                 data = r.json()
#                 values = data.get("values", [])
                
#                 for screen in values:
#                     screen_name = screen.get("name", "")
#                     if (screen_name.startswith(f"{project_key}:") or 
#                         screen_name.startswith(f"{project_key} ") or
#                         f": {project_key}" in screen_name):
#                         screens.append({
#                             "id": screen.get("id"),
#                             "name": screen_name,
#                             "description": screen.get("description", "")
#                         })
                
#                 if len(values) < max_results:
#                     break
#                 start_at += max_results
                
#             except Exception as e:
#                 self._log(f"Error searching screens: {e}", "WARN")
#                 break
        
#         return screens

#     def get_screen_scheme_for_project(self, project_key: str) -> Optional[dict]:
#         """Get screen scheme by project key"""
#         try:
#             url = f"{self.base_url}/rest/api/3/screenscheme"
#             params = {"startAt": 0, "maxResults": 100}
#             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
#             if r.status_code == 200:
#                 schemes = r.json().get("values", [])
#                 for scheme in schemes:
#                     if project_key in scheme.get("name", ""):
#                         return scheme
#             return None
#         except Exception:
#             return None

#     def get_screens_from_screen_scheme(self, screen_scheme_id: str) -> List[dict]:
#         """Get screens from a screen scheme"""
#         screens = []
#         try:
#             url = f"{self.base_url}/rest/api/3/screenscheme/{screen_scheme_id}"
#             r = requests.get(url, headers=self.headers, timeout=30)
            
#             if r.status_code == 200:
#                 data = r.json()
#                 screen_mappings = data.get("screens", {})
                
#                 for operation, screen_id in screen_mappings.items():
#                     if screen_id:
#                         screens.append({
#                             "id": screen_id,
#                             "operation": operation,
#                             "name": f"Screen {screen_id}"
#                         })
#         except Exception:
#             pass
#         return screens

#     def get_all_project_screens(self, project_key: str, project_id: str) -> List[dict]:
#         """Get all screens for a project"""
#         all_screens = []
#         seen_ids = set()
        
#         named_screens = self.get_project_screens_by_name(project_key)
#         for screen in named_screens:
#             if screen["id"] not in seen_ids:
#                 seen_ids.add(screen["id"])
#                 all_screens.append(screen)
        
#         screen_scheme = self.get_screen_scheme_for_project(project_key)
#         if screen_scheme:
#             scheme_screens = self.get_screens_from_screen_scheme(screen_scheme.get("id"))
#             for screen in scheme_screens:
#                 if screen["id"] not in seen_ids:
#                     seen_ids.add(screen["id"])
#                     all_screens.append(screen)
        
#         itss_screens = self.get_screens_from_itss(project_id)
#         for screen in itss_screens:
#             if screen["id"] not in seen_ids:
#                 seen_ids.add(screen["id"])
#                 all_screens.append(screen)
        
#         return all_screens

#     def get_screens_from_itss(self, project_id: str) -> List[dict]:
#         """Get screens through Issue Type Screen Scheme"""
#         screens = []
        
#         try:
#             url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/project"
#             params = {"projectId": project_id}
#             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
#             if r.status_code != 200:
#                 return screens
            
#             data = r.json()
#             values = data.get("values", [])
#             if not values:
#                 return screens
            
#             itss = values[0].get("issueTypeScreenScheme", {})
#             itss_id = itss.get("id")
            
#             if not itss_id:
#                 return screens
            
#             url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/{itss_id}/mapping"
#             params = {"startAt": 0, "maxResults": 50}
#             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
#             if r.status_code != 200:
#                 return screens
            
#             mappings = r.json().get("values", [])
#             screen_scheme_ids = set()
            
#             for mapping in mappings:
#                 ss_id = mapping.get("screenSchemeId")
#                 if ss_id:
#                     screen_scheme_ids.add(str(ss_id))
            
#             for ss_id in screen_scheme_ids:
#                 ss_screens = self.get_screens_from_screen_scheme(ss_id)
#                 screens.extend(ss_screens)
            
#         except Exception:
#             pass
        
#         return screens

#     # =========================================================================
#     # SCREEN TAB AND FIELD MANAGEMENT
#     # =========================================================================

#     def get_screen_tabs(self, screen_id: int) -> List[dict]:
#         """Get all tabs for a screen"""
#         try:
#             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs"
#             r = requests.get(url, headers=self.headers, timeout=30)
#             if r.status_code == 200:
#                 return r.json()
#         except Exception:
#             pass
#         return []

#     def get_tab_fields(self, screen_id: int, tab_id: int) -> List[str]:
#         """Get field IDs on a screen tab"""
#         try:
#             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
#             r = requests.get(url, headers=self.headers, timeout=30)
#             if r.status_code == 200:
#                 return [f.get("id") for f in r.json() if f.get("id")]
#         except Exception:
#             pass
#         return []

#     def add_field_to_screen_tab(self, screen_id: int, tab_id: int, field_id: str) -> bool:
#         """Add a field to a screen tab"""
#         try:
#             existing = self.get_tab_fields(screen_id, tab_id)
#             if field_id in existing:
#                 return True
            
#             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
#             payload = {"fieldId": field_id}
#             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
#             return r.status_code in (200, 201, 204) or "already" in r.text.lower()
                
#         except Exception:
#             return False

#     def add_fields_to_project_screens(self, project_key: str, project_id: str, 
#                                        field_ids: List[str]) -> Tuple[int, int]:
#         """Add custom fields to project screens"""
#         screens_updated = 0
#         total_added = 0
        
#         project_screens = self.get_all_project_screens(project_key, project_id)
        
#         if not project_screens:
#             self._log("  No project-specific screens found!", "WARN")
#             return 0, 0
        
#         self._log(f"  Found {len(project_screens)} project screen(s) to update", "INFO")
        
#         for screen in project_screens:
#             screen_id = screen.get("id")
#             screen_name = screen.get("name", f"Screen {screen_id}")
            
#             tabs = self.get_screen_tabs(screen_id)
#             if not tabs:
#                 continue
            
#             tab_id = tabs[0].get("id")
#             tab_name = tabs[0].get("name", "Field Tab")
            
#             fields_added = 0
#             for field_id in field_ids:
#                 if self.add_field_to_screen_tab(screen_id, tab_id, field_id):
#                     fields_added += 1
#                 time.sleep(0.1)
            
#             if fields_added > 0:
#                 self._log(f"    ✓ {screen_name}: Added {fields_added} fields to '{tab_name}'", "SUCCESS")
#                 screens_updated += 1
#                 total_added += fields_added
        
#         return screens_updated, total_added

#     # =========================================================================
#     # FIELD CONTEXT MANAGEMENT
#     # =========================================================================

#     def get_field_contexts(self, field_id: str) -> List[dict]:
#         """Get contexts for a custom field"""
#         try:
#             url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
#             r = requests.get(url, headers=self.headers, timeout=30)
#             if r.status_code == 200:
#                 return r.json().get("values", [])
#         except Exception:
#             pass
#         return []

#     def add_project_to_field_context(self, field_id: str, project_id: str, 
#                                       project_key: str) -> bool:
#         """Add project to field context"""
#         contexts = self.get_field_contexts(field_id)
        
#         for ctx in contexts:
#             if ctx.get("isGlobalContext", False):
#                 return True
        
#         for ctx in contexts:
#             project_ids = [str(p) for p in ctx.get("projectIds", [])]
#             if str(project_id) in project_ids:
#                 return True
        
#         if contexts:
#             ctx_id = contexts[0].get("id")
#             try:
#                 url = f"{self.base_url}/rest/api/3/field/{field_id}/context/{ctx_id}/project"
#                 payload = {"projectIds": [str(project_id)]}
#                 r = requests.put(url, headers=self.headers, json=payload, timeout=30)
#                 if r.status_code in (200, 204):
#                     return True
#             except Exception:
#                 pass
        
#         if not contexts:
#             try:
#                 url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
#                 payload = {
#                     "name": f"Context for {project_key}",
#                     "projectIds": [str(project_id)]
#                 }
#                 r = requests.post(url, headers=self.headers, json=payload, timeout=30)
#                 if r.status_code in (200, 201):
#                     return True
#             except Exception:
#                 pass
        
#         return True

#     # =========================================================================
#     # FIELD CREATION
#     # =========================================================================

#     def create_custom_field(self, field_name: str, field_type: str,
#                             searcher_key: str, description: str) -> Optional[str]:
#         """Create a new custom field"""
#         url = f"{self.base_url}/rest/api/3/field"
        
#         payload = {
#             "name": field_name,
#             "description": description,
#             "type": field_type,
#             "searcherKey": searcher_key
#         }
        
#         try:
#             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
#             if r.status_code in (200, 201):
#                 result = r.json()
#                 field_id = result.get("id")
#                 self._log(f"  Created field '{field_name}' → {field_id}", "SUCCESS")
#                 return field_id
#             else:
#                 self._log(f"  Failed to create '{field_name}': {r.text[:150]}", "ERROR")
#                 return None
                
#         except Exception as e:
#             self._log(f"Error creating field: {e}", "ERROR")
#             return None

#     def find_or_create_field(self, field_config: dict, project_id: str, 
#                               project_key: str, all_fields: List[dict]) -> Optional[str]:
#         """Find existing field or create new one"""
#         field_name = field_config["name"]
        
#         existing_id = self.find_field_id(all_fields, field_name)
        
#         if existing_id:
#             self._log(f"  Found existing: '{field_name}' → {existing_id}", "SUCCESS")
#             self.add_project_to_field_context(existing_id, project_id, project_key)
#             return existing_id
        
#         self._log(f"  Creating: '{field_name}'...", "INFO")
#         field_id = self.create_custom_field(
#             field_name,
#             field_config["type"],
#             field_config["searcherKey"],
#             field_config["description"]
#         )
        
#         if field_id:
#             all_fields.append({
#                 "id": field_id,
#                 "name": field_name,
#                 "custom": True
#             })
#             time.sleep(0.5)
#             self.add_project_to_field_context(field_id, project_id, project_key)
#             return field_id
        
#         return None

#     # =========================================================================
#     # MAIN SETUP METHOD
#     # =========================================================================

#     def setup_project_fields(self, all_fields: List[dict], 
#                               project_key: str, project_id: str) -> Tuple[dict, Optional[str]]:
#         """Set up custom fields including Confluence Page URL field"""
#         discovered = {}
#         field_ids = []
        
#         print()
#         self._log("=" * 50, "INFO")
#         self._log("PHASE 1: Setting up custom fields", "INFO")
#         self._log("=" * 50, "INFO")
#         print()
        
#         for key, config in EXPECTED_FIELDS.items():
#             field_id = self.find_or_create_field(config, project_id, project_key, all_fields)
#             if field_id:
#                 discovered[key] = field_id
#                 field_ids.append(field_id)
                
#                 # Store Confluence field ID for later use
#                 if key == "confluence_page":
#                     self.confluence_field_id = field_id
        
#         epic_name_id = self.find_field_id(all_fields, "Epic Name")
#         if epic_name_id:
#             self._log(f"  Found 'Epic Name' → {epic_name_id}", "SUCCESS")
        
#         print()
#         self._log("=" * 50, "INFO")
#         self._log("PHASE 2: Adding fields to project screens", "INFO")
#         self._log("=" * 50, "INFO")
#         print()
        
#         if field_ids:
#             self._log("  Waiting for field registration...", "INFO")
#             time.sleep(3)
            
#             screens_updated, fields_added = self.add_fields_to_project_screens(
#                 project_key, project_id, field_ids
#             )
            
#             print()
#             if screens_updated > 0:
#                 self._log(f"  Summary: Updated {screens_updated} screens, {fields_added} field additions", "SUCCESS")
#             else:
#                 self._log("  Warning: No screens were updated", "WARN")
        
#         return discovered, epic_name_id

#     # =========================================================================
#     # PROJECT AND ISSUE CREATION
#     # =========================================================================

#     def create_project(self, name: str, key: str, template: str, lead_id: str) -> dict:
#         """Create a new Jira project"""
#         url = f"{self.base_url}/rest/api/3/project"
        
#         payload = {
#             "key": key,
#             "name": name,
#             "projectTypeKey": "software",
#             "projectTemplateKey": template,
#             "leadAccountId": lead_id,
#             "assigneeType": "PROJECT_LEAD",
#             "description": f"Company-managed project: {name}",
#         }
        
#         r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
#         if r.status_code in (200, 201):
#             self._log(f"Project '{name}' created! Key: {key}", "SUCCESS")
#             return r.json()
#         else:
#             error_msg = r.text
#             try:
#                 error_json = r.json()
#                 if 'errors' in error_json:
#                     error_msg = json.dumps(error_json['errors'], indent=2)
#                 elif 'errorMessages' in error_json:
#                     error_msg = ', '.join(error_json['errorMessages'])
#             except Exception:
#                 pass
#             raise Exception(f"Failed to create project: {error_msg}")

#     def create_issue(self, project_key: str, issue_type: str, summary: str,
#                      description: str = None, fields_extra: dict = None) -> dict:
#         """Create a Jira issue"""
#         url = f"{self.base_url}/rest/api/3/issue"
        
#         fields = {
#             "project": {"key": project_key},
#             "summary": summary,
#             "issuetype": {"name": issue_type}
#         }
        
#         if description:
#             fields["description"] = {
#                 "type": "doc",
#                 "version": 1,
#                 "content": [{
#                     "type": "paragraph",
#                     "content": [{"type": "text", "text": description}]
#                 }]
#             }
        
#         if fields_extra:
#             fields.update(fields_extra)
        
#         try:
#             r = requests.post(url, headers=self.headers, json={"fields": fields}, timeout=30)
#             r.raise_for_status()
#             return r.json()
#         except requests.exceptions.HTTPError:
#             raise Exception(f"Failed to create {issue_type}: {r.text[:200]}")

#     def update_issue_fields(self, issue_key: str, fields: dict) -> bool:
#         """Update issue fields"""
#         url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
#         try:
#             r = requests.put(url, headers=self.headers, json={"fields": fields}, timeout=30)
#             return r.status_code in (200, 204)
#         except Exception:
#             return False

#     def link_to_parent(self, issue_key: str, parent_key: str) -> bool:
#         """Link issue to parent Epic"""
#         return self.update_issue_fields(issue_key, {"parent": {"key": parent_key}})

#     # =========================================================================
#     # MAIN STRUCTURE GENERATION
#     # =========================================================================

#     def generate_structure(self, project_key: str, custom_fields: dict,
#                            epic_name_field: Optional[str], lead_account_id: str,
#                            confluence_space_key: str = None,
#                            confluence_parent_page_id: str = None,
#                            link_method: str = "description") -> dict:
#         """
#         Generate Epic/Story structure with Confluence integration.
        
#         link_method options:
#         - "description": Add link to issue description (RECOMMENDED - Most visible)
#         - "comment": Add link as comment
#         - "both": Add to description AND comment
#         """
        
#         print()
#         self._log("=" * 50, "INFO")
#         self._log(f"PHASE 3: Creating Epics and Stories", "INFO")
#         if confluence_space_key:
#             self._log(f"         (with Confluence pages in space: {confluence_space_key})", "CONFLUENCE")
#             self._log(f"         Link method: {link_method}", "LINK")
#             if TEMPLATES_AVAILABLE:
#                 self._log(f"         Templates: ENABLED ✓", "TEMPLATE")
#             else:
#                 self._log(f"         Templates: Using fallback (confluence_templates.py not found)", "WARN")
#         self._log("=" * 50, "INFO")
#         print()
        
#         epic_keys = {}
#         epic_page_ids = {}
        
#         total_epics = len(EPICS)
#         total_stories = sum(len(s) for s in EPICS.values())
#         epic_count = 0
#         story_count = 0
#         pages_created = 0
#         links_created = 0
        
#         for epic_name, story_list in EPICS.items():
#             epic_count += 1
            
#             # ─────────────────────────────────────────────────────────────────
#             # CREATE EPIC
#             # ─────────────────────────────────────────────────────────────────
#             try:
#                 fields_extra = {}
#                 if epic_name_field:
#                     fields_extra[epic_name_field] = epic_name
                
#                 epic = self.create_issue(project_key, "Epic", epic_name,
#                                          f"Epic: {epic_name}", fields_extra)
#                 epic_key = epic.get("key")
#                 epic_keys[epic_name] = epic_key
                
#                 short_name = epic_name[:50] + "..." if len(epic_name) > 50 else epic_name
#                 self._log(f"[{epic_count}/{total_epics}] Epic: {short_name} → {epic_key}", "SUCCESS")
                
#                 # Create Epic Confluence page
#                 if confluence_space_key:
#                     epic_page_title = f"{epic_key} - {epic_name[:80]}"
#                     epic_page = self.create_confluence_page(
#                         space_key=confluence_space_key,
#                         title=epic_page_title,
#                         jira_issue_key=epic_key,
#                         jira_issue_summary=epic_name,
#                         parent_id=confluence_parent_page_id,
#                         is_epic=True  # Use Epic template
#                     )
#                     if epic_page:
#                         epic_page_ids[epic_name] = epic_page.get("id")
#                         pages_created += 1
#                         page_url = self.get_confluence_page_url(epic_page)
                        
#                         # Link Epic to Confluence page
#                         result = self.link_confluence_to_jira(
#                             issue_key=epic_key,
#                             page_url=page_url,
#                             page_title=epic_page_title,
#                             original_description=f"Epic: {epic_name}",
#                             add_to_description=(link_method in ["description", "both"]),
#                             add_comment=(link_method in ["comment", "both"]),
#                             set_url_field=True
#                         )
#                         if any(result.values()):
#                             links_created += 1
                        
#                         self._log(f"  📄 Epic page created & linked", "CONFLUENCE")
                
#             except Exception as e:
#                 self._log(f"Failed to create Epic: {e}", "ERROR")
#                 continue
            
#             # ─────────────────────────────────────────────────────────────────
#             # CREATE STORIES
#             # ─────────────────────────────────────────────────────────────────
#             for story_name in story_list:
#                 story_count += 1
                
#                 # Prepare custom field values
#                 story_fields = {}
#                 today = datetime.utcnow().date()
                
#                 if "percent_complete" in custom_fields:
#                     story_fields[custom_fields["percent_complete"]] = "0"
#                 if "target_start" in custom_fields:
#                     story_fields[custom_fields["target_start"]] = str(today)
#                 if "target_end" in custom_fields:
#                     story_fields[custom_fields["target_end"]] = str(today + timedelta(days=7))
#                 if "owning" in custom_fields:
#                     story_fields[custom_fields["owning"]] = {"accountId": lead_account_id}
                
#                 story_key = None
                
#                 try:
#                     story = self.create_issue(project_key, "Story", story_name,
#                                               f"Story: {story_name}", story_fields)
#                     story_key = story.get("key")
#                     linked = self.link_to_parent(story_key, epic_key)
                    
#                     status = "✓" if linked else "○"
#                     self._log(f"  [{story_count}/{total_stories}] {status} {story_key}: {story_name[:40]}...", "SUCCESS")
                    
#                 except Exception:
#                     try:
#                         story = self.create_issue(project_key, "Story", story_name)
#                         story_key = story.get("key")
#                         self.link_to_parent(story_key, epic_key)
                        
#                         if story_fields:
#                             time.sleep(0.2)
#                             self.update_issue_fields(story_key, story_fields)
                        
#                         self._log(f"  [{story_count}/{total_stories}] ○ {story_key} (retry)", "SUCCESS")
#                     except Exception:
#                         self._log(f"  Failed: {story_name[:30]}...", "ERROR")
#                         continue
                
#                 # ─────────────────────────────────────────────────────────────
#                 # CREATE CONFLUENCE PAGE FOR THIS STORY
#                 # ─────────────────────────────────────────────────────────────
#                 if confluence_space_key and story_key:
#                     try:
#                         parent_id = epic_page_ids.get(epic_name, confluence_parent_page_id)
#                         page_title = f"{story_key} - {story_name}"
                        
#                         # Create page using appropriate template based on story name
#                         page = self.create_confluence_page(
#                             space_key=confluence_space_key,
#                             title=page_title,
#                             jira_issue_key=story_key,
#                             jira_issue_summary=story_name,
#                             parent_id=parent_id,
#                             is_epic=False  # Use story template matching
#                         )
                        
#                         if page:
#                             pages_created += 1
#                             page_url = self.get_confluence_page_url(page)
                            
#                             # Create visible links in Jira
#                             result = self.link_confluence_to_jira(
#                                 issue_key=story_key,
#                                 page_url=page_url,
#                                 page_title=page_title,
#                                 original_description=f"Story: {story_name}",
#                                 add_to_description=(link_method in ["description", "both"]),
#                                 add_comment=(link_method in ["comment", "both"]),
#                                 set_url_field=True
#                             )
                            
#                             if any(result.values()):
#                                 links_created += 1
#                                 methods_used = [k for k, v in result.items() if v]
#                                 self._log(f"      🔗 Linked via: {', '.join(methods_used)}", "LINK")
#                             else:
#                                 self._log(f"      ⚠️ Page created but linking failed", "WARN")
                        
#                         time.sleep(0.15)
                        
#                     except Exception as e:
#                         self._log(f"      Failed Confluence: {e}", "WARN")
        
#         # Summary
#         print()
#         self._log("-" * 50, "INFO")
#         self._log(f"Structure Summary:", "INFO")
#         self._log(f"  • Epics created: {len(epic_keys)}", "SUCCESS")
#         self._log(f"  • Stories created: {story_count}", "SUCCESS")
#         if confluence_space_key:
#             self._log(f"  • Confluence pages: {pages_created}", "CONFLUENCE")
#             self._log(f"  • Issues linked: {links_created}", "LINK")
        
#         return epic_keys


# # =============================================================================
# # MAIN FUNCTION
# # =============================================================================

# def main():
#     """Main execution"""
    
#     print("\n" + "=" * 60)
#     print("  🚀 JIRA + CONFLUENCE PROJECT GENERATOR")
#     print("     (with Template Support)")
#     print("=" * 60 + "\n")
    
#     # Show template status
#     if TEMPLATES_AVAILABLE:
#         print("📝 Templates: LOADED from confluence_templates.py")
#         try:
#             templates = list_available_templates()
#             print(f"   Available templates: {len(templates)}")
#         except Exception:
#             pass
#     else:
#         print("⚠️  Templates: Using fallback (confluence_templates.py not found)")
#     print()
    
#     # =========================================================================
#     # GET CREDENTIALS
#     # =========================================================================
#     print("📋 ATLASSIAN CREDENTIALS\n")
    
#     ATLASSIAN_URL = input("Enter Atlassian URL (e.g., https://yoursite.atlassian.net): ").strip()
#     ATLASSIAN_EMAIL = input("Enter Email: ").strip()
#     ATLASSIAN_API_TOKEN = getpass.getpass("Enter API Token (hidden): ")
    
#     if not all([ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN]):
#         print("❌ All credentials are required!")
#         return
    
#     generator = JiraProjectGenerator(ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN)
#     # generator.debug_mode = True  # Uncomment for verbose output
    
#     # =========================================================================
#     # TEST CONNECTIONS
#     # =========================================================================
#     print("\n" + "-" * 60 + "\n")
#     print("🔌 TESTING CONNECTIONS\n")
    
#     generator._log("Testing Jira connection...", "INFO")
#     jira_success, jira_user = generator.test_connection()
    
#     if not jira_success:
#         generator._log(f"Jira connection failed: {jira_user.get('error')}", "ERROR")
#         return
    
#     lead_id = jira_user.get("accountId")
#     user_name = jira_user.get("displayName", jira_user.get("emailAddress"))
#     generator._log(f"Jira: Connected as {user_name}", "SUCCESS")
    
#     generator._log("Testing Confluence connection...", "INFO")
#     conf_success, conf_user = generator.test_confluence_connection()
    
#     confluence_enabled = False
#     if not conf_success:
#         generator._log(f"Confluence connection failed: {conf_user.get('error')}", "ERROR")
#         generator._log("Continuing without Confluence...", "WARN")
#     else:
#         generator._log(f"Confluence: Connected", "SUCCESS")
#         confluence_enabled = True
    
#     # =========================================================================
#     # GET PROJECT DETAILS
#     # =========================================================================
#     print("\n" + "-" * 60 + "\n")
#     print("📋 JIRA PROJECT DETAILS\n")
    
#     while True:
#         project_name = input("Enter Project Name: ").strip()
#         if not project_name:
#             generator._log("Project name required!", "ERROR")
#             continue
        
#         suggested_key = generator.suggest_project_key(project_name)
#         key_input = input(f"Enter Project Key (suggested: {suggested_key}): ").strip().upper()
#         project_key = key_input if key_input else suggested_key
        
#         if not re.match(r'^[A-Z][A-Z0-9]{1,9}$', project_key):
#             generator._log("Invalid key!", "ERROR")
#             continue
        
#         if generator.check_project_exists(project_key):
#             generator._log(f"Project '{project_key}' already exists!", "ERROR")
#             if input("Try different key? (y/N): ").strip().lower() == 'y':
#                 continue
#             return
#         break
    
#     # =========================================================================
#     # SELECT TEMPLATE
#     # =========================================================================
#     print("\n📐 SELECT PROJECT TEMPLATE\n")
#     for k, (name, _) in VALID_TEMPLATES.items():
#         print(f"  {k}. {name}")
    
#     choice = input("\nChoose (1-3) [default: 2]: ").strip() or "2"
#     if choice not in VALID_TEMPLATES:
#         generator._log("Invalid choice!", "ERROR")
#         return
    
#     template_name, template_key = VALID_TEMPLATES[choice]
    
#     # =========================================================================
#     # CONFLUENCE SPACE DETAILS
#     # =========================================================================
#     confluence_space_key = None
#     confluence_space_name = None
#     link_method = "description"
    
#     if confluence_enabled:
#         print("\n" + "-" * 60 + "\n")
#         print("📄 CONFLUENCE SPACE DETAILS\n")
        
#         create_space = input("Create Confluence space? (Y/n): ").strip().lower()
        
#         if create_space != 'n':
#             confluence_space_name = input(f"Space Name (default: {project_name} Docs): ").strip()
#             if not confluence_space_name:
#                 confluence_space_name = f"{project_name} Docs"
            
#             suggested_space_key = generator.suggest_space_key(confluence_space_name)
#             space_key_input = input(f"Space Key (suggested: {suggested_space_key}): ").strip().upper()
#             confluence_space_key = space_key_input if space_key_input else suggested_space_key
            
#             if generator.check_confluence_space_exists(confluence_space_key):
#                 generator._log(f"Space '{confluence_space_key}' exists!", "WARN")
#                 use_existing = input("Use existing? (Y/n): ").strip().lower()
#                 if use_existing == 'n':
#                     confluence_space_key = None
            
#             if confluence_space_key:
#                 print("\n🔗 LINK VISIBILITY METHOD\n")
#                 print("  1. Description (RECOMMENDED - Link in issue description)")
#                 print("  2. Comment (Link as a comment)")
#                 print("  3. Both (Description + Comment)")
                
#                 link_choice = input("\nChoose (1-3) [default: 1]: ").strip() or "1"
#                 link_method = {"1": "description", "2": "comment", "3": "both"}.get(link_choice, "description")
    
#     # =========================================================================
#     # SUMMARY
#     # =========================================================================
#     print("\n" + "-" * 60)
#     print("\n📊 SUMMARY\n")
#     print(f"  JIRA PROJECT:")
#     print(f"    Name:      {project_name}")
#     print(f"    Key:       {project_key}")
#     print(f"    Template:  {template_name}")
#     print(f"    Epics:     {len(EPICS)}")
#     print(f"    Stories:   {sum(len(s) for s in EPICS.values())}")
    
#     if confluence_space_key:
#         print(f"\n  CONFLUENCE:")
#         print(f"    Space:     {confluence_space_name} ({confluence_space_key})")
#         print(f"    Link via:  {link_method.upper()}")
#         if TEMPLATES_AVAILABLE:
#             print(f"    Templates: Using confluence_templates.py")
#         else:
#             print(f"    Templates: Fallback (basic)")
#         print(f"\n  WHERE YOU'LL SEE LINKS IN JIRA:")
#         if link_method in ["description", "both"]:
#             print(f"    ✓ Issue Description (top of issue)")
#         print(f"    ✓ 'Confluence Page' custom field")
#         if link_method in ["comment", "both"]:
#             print(f"    ✓ Comments/Activity section")
    
#     print()
    
#     if input("Proceed? (y/N): ").strip().lower() != 'y':
#         generator._log("Cancelled", "WARN")
#         return
    
#     print("\n" + "=" * 60)
    
#     # =========================================================================
#     # CREATE PROJECT
#     # =========================================================================
#     try:
#         generator._log("Creating Jira project...", "INFO")
#         project = generator.create_project(project_name, project_key, template_key, lead_id)
#         project_id = project.get("id")
#     except Exception as e:
#         generator._log(f"Failed: {e}", "ERROR")
#         return
    
#     generator._log("Waiting for initialization (10s)...", "INFO")
#     time.sleep(10)
    
#     # =========================================================================
#     # SETUP FIELDS
#     # =========================================================================
#     try:
#         all_fields = generator.fetch_all_fields()
#         custom_fields, epic_name_field = generator.setup_project_fields(
#             all_fields, project_key, project_id
#         )
#     except Exception as e:
#         generator._log(f"Field setup error: {e}", "ERROR")
#         custom_fields = {}
#         epic_name_field = None
    
#     # =========================================================================
#     # CREATE CONFLUENCE SPACE
#     # =========================================================================
#     confluence_parent_page_id = None
    
#     if confluence_space_key and not generator.check_confluence_space_exists(confluence_space_key):
#         print()
#         generator._log("Creating Confluence space...", "CONFLUENCE")
        
#         try:
#             generator.create_confluence_space(
#                 space_key=confluence_space_key,
#                 space_name=confluence_space_name,
#                 description=f"Documentation for {project_name} ({project_key})"
#             )
#             confluence_parent_page_id = generator.get_space_homepage_id(confluence_space_key)
#         except Exception as e:
#             generator._log(f"Failed: {e}", "ERROR")
#             confluence_space_key = None
#     elif confluence_space_key:
#         confluence_parent_page_id = generator.get_space_homepage_id(confluence_space_key)
    
#     # =========================================================================
#     # GENERATE STRUCTURE
#     # =========================================================================
#     try:
#         epic_keys = generator.generate_structure(
#             project_key=project_key,
#             custom_fields=custom_fields,
#             epic_name_field=epic_name_field,
#             lead_account_id=lead_id,
#             confluence_space_key=confluence_space_key,
#             confluence_parent_page_id=confluence_parent_page_id,
#             link_method=link_method
#         )
#     except Exception as e:
#         generator._log(f"Structure error: {e}", "ERROR")
#         epic_keys = {}
    
#     # =========================================================================
#     # FINAL SUMMARY
#     # =========================================================================
#     print("\n" + "=" * 60)
#     print("  ✨ COMPLETE!")
#     print("=" * 60)
    
#     print(f"\n🔗 JIRA PROJECT: {ATLASSIAN_URL}/projects/{project_key}")
    
#     if confluence_space_key:
#         print(f"📄 CONFLUENCE: {ATLASSIAN_URL}/wiki/spaces/{confluence_space_key}")
#         print(f"\n📝 TEMPLATES USED:")
#         if TEMPLATES_AVAILABLE:
#             print(f"   Templates loaded from confluence_templates.py")
#             print(f"   Each story page uses a template based on its name")
#         else:
#             print(f"   Fallback templates used (basic structure)")
    
#     if custom_fields:
#         print(f"\n🏷️ CUSTOM FIELDS:")
#         for k, fid in custom_fields.items():
#             print(f"   • {EXPECTED_FIELDS[k]['name']} → {fid}")
    
#     print()


# # =============================================================================
# # ENTRY POINT
# # =============================================================================

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\n⚠️ Cancelled\n")
#         sys.exit(0)
#     except Exception as e:
#         print(f"\n❌ Error: {e}\n")
#         import traceback
#         traceback.print_exc()
#         sys.exit(1)