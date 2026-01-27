# #!/usr/bin/env python3
# """
# Jira Project Generator - Company-Managed Projects
# Automatically creates Company-managed Jira projects with Epics and Storiesf
# Custom fields are scoped ONLY to the created project
# Uses .env file for credentials
# """

# import requests
# import base64
# import json
# import re
# import sys
# import os
# import time
# from datetime import datetime, timedelta
# from typing import Dict, List, Optional, Tuple
# from pathlib import Path

# try:
#     from dotenv import load_dotenv
# except ImportError:
#     print("\n❌ Error: python-dotenv package not found!")
#     print("Install it with: pip install python-dotenv")
#     print()
#     sys.exit(1)

# load_dotenv()

# # ---------- CREDENTIALS (from .env file) ----------
# JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
# JIRA_EMAIL = os.getenv("JIRA_EMAIL")
# JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# # Company-managed project templates
# VALID_TEMPLATES = {
#     "1": ("Kanban", "com.pyxis.greenhopper.jira:gh-kanban-template"),
#     "2": ("Scrum", "com.pyxis.greenhopper.jira:gh-scrum-template"),
#     "3": ("Bug Tracking", "com.atlassian.jira-core-project-templates:jira-core-project-management"),
# }

# # Project structure to create
# EPICS = {
#     "ASSESSMENT & PLANNING (2 - 12 weeks, depending on project scope, sizing, access, onboarding)": [
#   "Onboarding and Access - See Access Tab for Details",
#   "Introductory Call",
#   "Discuss NON-PRODUCTION environments",
#   "Set up Weekly Touchpoint w/Atlassian (if above 1000 users)",
#   "Discuss Atlassian Cloud Status",
#   "Start Atlassian CLOUD Trial (if needed)",
#   "Set up Weekly Touchpoint w/Project Team",
#   "Set up Atlassian Guard (if needed/in scope)",
#   "Open Ticket w/Atlassian for MOVE",
#   "Refresh lower instance of Jira to current version",
#   "Licensing Tier Jira",
#   "Licensing Tier Confluence",
#   "Discussion/Discovery Migration Scope for Confluence",
#   "Discussion/Discovery Migration Scope for Jira",
#   "Discussion/Discovery Integrations",
#   "Discussion/Discovery User Management",
#   "Start Atlassian Guard Trial (if needed/in scope)",
#   "User Clean Up Tasks",
#   "Jira - Add-on Assessment",
#   "Confluence - Add-on Assessment",
#   "Environment Assessment & Pre-Migration Checklist",
#   "Develop Migration Approach & Draft Runbook",
#   "Develop Testing Plan",
#   "Develop Communications Plan",
#   "Develop Training Plan (if needed)",
#   "Review & Acceptance - Environment Assessment",
#   "Review & Acceptance - Jira Projects Assessment",
#   "Review & Acceptance - Confluence Spaces",
#   "Review & Acceptance - Jira Add-ons",
#   "Review & Acceptance - Atlassian Guard Setup",
#   "Review & Acceptance - Confluence Addons",
#   "Review & Acceptance - Confluence Macros",
#   "Review & Acceptance - Integrations",
#   "Review & Acceptance - Pre Migration Checklists (Jira & Confluence)",
#   "Budget Review Meeting (T&M)",
#   "Refresh Staging Environments (Jira and Confluence)",
#   "<other tasks as identified>"
# ],
#     "TEST MIGRATION (4 - 16 weeks, depending on scope, sizing, & capacity of Client)": [
#   "Execute User Migration using JCMA",
#   "Execute Complete test migration using JCMA",
#   "Transformation Tasks - Scriptrunner",
#   "Basic Application Integrity Tests",
#   "Workflow Review & Migration Assistant Errors",
#   "Working Session to review Migration Assistant Findings (if needed)",
#   "Execute Add-on Remediation Plan",
#   "Execute Confluence Migration using CCMA",
#   "Post migration checks Jira & Confluence"
# ],
#     "USER ACCEPTANCE TESTING (1 - 2 weeks, depending on scope, sizing, & capacity of Client)": [
#   "Capula Project Team Testing",
#   "Hold UAT Training (if needed)",
#   "User Acceptance Testing",
#   "Issue Resolution",
#   "Go/No Go Decision (UAT Acceptance)"
# ],
#     "PRODUCTION MIGRATION (TBD)	": ["Finalize Migration Runbook","See Migration Timeline Tab "],
#     "POST MIGRATION SUPPORT (4 weeks)" :["<items as identified>"],
# }

# # Expected custom fields with their types
# # These will be created as PROJECT-SPECIFIC fields
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
#     }
# }


# class JiraProjectGenerator:
#     def __init__(self, base_url: str, email: str, api_token: str):
#         self.base_url = base_url.rstrip('/')
#         self.email = email
#         self.api_token = api_token
#         self.headers = self._get_auth_header()
        
#     def _get_auth_header(self) -> dict:
#         """Generate Basic Auth header for Jira API"""
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
#             "DEBUG": "🔍"
#         }
#         print(f"{icons.get(level, '•')} {message}")
    
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
    
#     def check_project_exists(self, project_key: str) -> bool:
#         """Check if a project with this key already exists"""
#         try:
#             url = f"{self.base_url}/rest/api/3/project/{project_key}"
#             r = requests.get(url, headers=self.headers, timeout=10)
#             return r.status_code == 200
#         except Exception:
#             return False
    
#     def test_connection(self) -> Tuple[bool, dict]: #A temp connection to check API is working fine
#         """Test API connection and get current user info"""
#         try:
#             url = f"{self.base_url}/rest/api/3/myself"
#             r = requests.get(url, headers=self.headers, timeout=10)
#             r.raise_for_status()
#             return True, r.json()
#         except requests.exceptions.RequestException as e:
#             return False, {"error": str(e)}
    
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

#     # ==================== PROJECT-SPECIFIC FIELD MANAGEMENT ====================
    
#     def get_field_contexts(self, field_id: str) -> List[dict]:
#         """Get all contexts for a custom field"""
#         try:
#             url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
#             params = {"maxResults": 100}
#             r = requests.get(url, headers=self.headers, params=params, timeout=30)
#             if r.status_code == 200:
#                 return r.json().get("values", [])
#         except Exception as e:
#             self._log(f"    Error getting field contexts: {e}", "WARN")
#         return []

#     def get_project_screens_by_scheme(self, project_key: str, project_id: str) -> List[dict]:
#         """
#         Get screens that are specifically used by this project through its screen scheme.
#         """
#         screens = []
        
#         try:
#             # Get issue type screen scheme for the project
#             url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/project"
#             params = {"projectId": project_id}
#             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
#             if r.status_code != 200:
#                 self._log(f"    Could not get issue type screen scheme", "DEBUG")
#                 return screens
            
#             data = r.json()
#             values = data.get("values", [])
            
#             if not values:
#                 self._log(f"    No issue type screen scheme found", "DEBUG")
#                 return screens
            
#             itss = values[0].get("issueTypeScreenScheme", {})
#             itss_id = itss.get("id")
            
#             if not itss_id:
#                 return screens
            
#             self._log(f"    Found Issue Type Screen Scheme: {itss.get('name')} (ID: {itss_id})", "DEBUG")
            
#             # Get mappings from issue type screen scheme
#             url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/{itss_id}/mapping"
#             params = {"maxResults": 50}
#             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
#             if r.status_code != 200:
#                 return screens
            
#             mappings = r.json().get("values", [])
#             screen_scheme_ids = set()
            
#             for mapping in mappings:
#                 ss_id = mapping.get("screenSchemeId")
#                 if ss_id:
#                     screen_scheme_ids.add(ss_id)
            
#             self._log(f"    Found {len(screen_scheme_ids)} screen scheme(s)", "DEBUG")
            
#             # Get screens from each screen scheme
#             for ss_id in screen_scheme_ids:
#                 url = f"{self.base_url}/rest/api/3/screenscheme/{ss_id}"
#                 r = requests.get(url, headers=self.headers, timeout=30)
                
#                 if r.status_code == 200:
#                     ss_data = r.json()
#                     ss_screens = ss_data.get("screens", {})
                    
#                     for screen_type, screen_id in ss_screens.items():
#                         if screen_id:
#                             screens.append({
#                                 "id": screen_id,
#                                 "type": screen_type,
#                                 "screen_scheme_id": ss_id
#                             })
            
#             self._log(f"    Found {len(screens)} screen(s) for project", "DEBUG")
            
#         except Exception as e:
#             self._log(f"    Error getting project screens: {e}", "WARN")
        
#         return screens

#     def get_screen_tabs(self, screen_id: int) -> List[dict]:
#         """Get all tabs for a screen"""
#         try:
#             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs"
#             r = requests.get(url, headers=self.headers, timeout=30)
#             if r.status_code == 200:
#                 return r.json()
#         except Exception as e:
#             self._log(f"    Error getting screen tabs: {e}", "WARN")
#         return []

#     def get_tab_fields(self, screen_id: int, tab_id: int) -> List[str]:
#         """Get all field IDs already on a screen tab"""
#         try:
#             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
#             r = requests.get(url, headers=self.headers, timeout=30)
#             if r.status_code == 200:
#                 fields = r.json()
#                 return [f.get("id") for f in fields]
#         except Exception as e:
#             self._log(f"    Error getting tab fields: {e}", "WARN")
#         return []

#     def add_field_to_screen_tab(self, screen_id: int, tab_id: int, field_id: str) -> bool:
#         """Add a field to a specific screen tab"""
#         try:
#             # Check if field already exists on tab
#             existing_fields = self.get_tab_fields(screen_id, tab_id)
#             if field_id in existing_fields:
#                 return True  # Already there
            
#             url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
#             payload = {"fieldId": field_id}
#             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
#             if r.status_code in (200, 201, 204):
#                 return True
#             elif r.status_code == 400:
#                 error_text = r.text.lower()
#                 if "already" in error_text:
#                     return True
#                 return False
#             else:
#                 return False
                
#         except Exception as e:
#             self._log(f"    Error adding field to screen: {e}", "WARN")
#             return False

#     def add_fields_to_project_screens_only(self, project_key: str, project_id: str, 
#                                             field_ids: List[str]) -> int:
#         """
#         Add custom fields ONLY to screens used by this specific project.
#         Does NOT add to default/global screens.
#         """
#         added_count = 0
        
#         # Get project-specific screens
#         project_screens = self.get_project_screens_by_scheme(project_key, project_id)
        
#         if not project_screens:
#             self._log(f"    No project-specific screens found, trying fallback...", "WARN")
#             # Fallback: try to find screens by project name
#             project_screens = self.find_screens_by_project_name(project_key)
        
#         if not project_screens:
#             self._log(f"    Could not find any screens for project {project_key}", "WARN")
#             return 0
        
#         self._log(f"    Adding fields to {len(project_screens)} project screen(s)...", "INFO")
        
#         for screen in project_screens:
#             screen_id = screen.get("id")
#             screen_type = screen.get("type", "unknown")
            
#             tabs = self.get_screen_tabs(screen_id)
#             if not tabs:
#                 continue
            
#             # Add to first tab
#             tab_id = tabs[0].get("id")
            
#             fields_added = 0
#             for field_id in field_ids:
#                 if self.add_field_to_screen_tab(screen_id, tab_id, field_id):
#                     fields_added += 1
            
#             if fields_added > 0:
#                 self._log(f"      Screen {screen_id} ({screen_type}): Added {fields_added} fields", "SUCCESS")
#                 added_count += fields_added
        
#         return added_count

#     def find_screens_by_project_name(self, project_key: str) -> List[dict]:
#         """Fallback: Find screens that might be named after the project"""
#         screens = []
        
#         try:
#             url = f"{self.base_url}/rest/api/3/screens"
#             params = {"maxResults": 100}
#             r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
#             if r.status_code == 200:
#                 all_screens = r.json().get("values", [])
                
#                 for screen in all_screens:
#                     screen_name = screen.get("name", "").lower()
                    
#                     # Only match screens with project key in name
#                     if project_key.lower() in screen_name:
#                         screens.append({
#                             "id": screen.get("id"),
#                             "name": screen.get("name"),
#                             "type": "project-named"
#                         })
        
#         except Exception as e:
#             self._log(f"    Error searching screens: {e}", "WARN")
        
#         return screens

#     def create_custom_field(self, field_name: str, field_type: str,
#                             searcher_key: str, description: str) -> Optional[str]:
#         """
#         Create a new custom field with the exact name provided (no project suffix).
#         """
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
#                 error_msg = r.text[:200]
#                 self._log(f"  Failed to create field '{field_name}': {error_msg}", "ERROR")
#                 return None
                
#         except Exception as e:
#             self._log(f"  Error creating field '{field_name}': {e}", "ERROR")
#             return None

#     def scope_field_to_project_only(self, field_id: str, project_id: str, 
#                                      project_key: str, field_name: str) -> bool:
#         """
#         Scope an existing field to a specific project only by:
#         1. Getting the default context
#         2. Removing the default/global context (if possible)
#         3. Creating a project-specific context
#         """
#         try:
#             contexts = self.get_field_contexts(field_id)
            
#             # Find the default global context
#             default_context_id = None
#             for context in contexts:
#                 if context.get("isGlobalContext", False) or context.get("isAnyIssueType", False):
#                     default_context_id = context.get("id")
#                     break
            
#             # Create project-specific context
#             url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
#             payload = {
#                 "name": f"{field_name} - {project_key}",
#                 "description": f"Limits field '{field_name}' to project {project_key} only",
#                 "projectIds": [project_id],
#                 "isGlobalContext": False
#             }
            
#             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
#             if r.status_code in (200, 201):
#                 new_context = r.json()
#                 new_context_id = new_context.get("id")
#                 self._log(f"    → Created project context (ID: {new_context_id})", "DEBUG")
                
#                 # Try to delete the default global context
#                 if default_context_id:
#                     delete_success = self.delete_field_context(field_id, default_context_id)
#                     if delete_success:
#                         self._log(f"    → Removed global context", "DEBUG")
#                         return True
#                     else:
#                         self._log(f"    → Could not remove global context (field may appear in other projects)", "WARN")
#                         return True  # Still partially successful
                
#                 return True
#             else:
#                 error_text = r.text[:150]
#                 self._log(f"    → Failed to create project context: {error_text}", "WARN")
                
#                 # If we can't create a new context, try to modify the existing one
#                 if default_context_id:
#                     return self.update_context_to_project_only(field_id, default_context_id, project_id)
#                 return False
                
#         except Exception as e:
#             self._log(f"    → Error scoping field: {e}", "WARN")
#             return False

#     def delete_field_context(self, field_id: str, context_id: int) -> bool:
#         """Delete a field context"""
#         try:
#             url = f"{self.base_url}/rest/api/3/field/{field_id}/context/{context_id}"
#             r = requests.delete(url, headers=self.headers, timeout=30)
#             return r.status_code in (200, 204)
#         except Exception:
#             return False

#     def update_context_to_project_only(self, field_id: str, context_id: int, 
#                                         project_id: str) -> bool:
#         """Update existing context to be project-specific"""
#         try:
#             # Add only our project to the context
#             add_url = f"{self.base_url}/rest/api/3/field/{field_id}/context/{context_id}/project"
#             payload = {"projectIds": [project_id]}
#             r = requests.put(add_url, headers=self.headers, json=payload, timeout=30)
#             return r.status_code in (200, 204)
#         except Exception:
#             return False

#     def find_or_create_project_field(self, field_config: dict, project_id: str, 
#                                       project_key: str, all_fields: List[dict]) -> Optional[str]:
#         """
#         Find an existing field by name or create a new one, then scope it to the project.
#         Field names do NOT include project key suffix.
#         """
#         field_name = field_config["name"]
        
#         # Check if field already exists with exact name
#         existing_id = self.find_field_id(all_fields, field_name)
        
#         if existing_id:
#             self._log(f"  Found existing field: '{field_name}' → {existing_id}", "SUCCESS")
#             # Scope existing field to this project
#             self._log(f"    → Scoping to project {project_key}...", "INFO")
#             self.scope_field_to_project_only(existing_id, project_id, project_key, field_name)
#             return existing_id
        
#         # Create new field with exact name (no project suffix)
#         self._log(f"  Creating field: '{field_name}'...", "INFO")
#         field_id = self.create_custom_field(
#             field_name,
#             field_config["type"],
#             field_config["searcherKey"],
#             field_config["description"]
#         )
        
#         if field_id:
#             # Scope the newly created field to this project only
#             time.sleep(0.5)  # Brief pause for field creation to complete
#             self._log(f"    → Scoping to project {project_key}...", "INFO")
#             if self.scope_field_to_project_only(field_id, project_id, project_key, field_name):
#                 self._log(f"    → Scoped to project {project_key} only", "SUCCESS")
#             else:
#                 self._log(f"    → Warning: Could not fully scope to project only", "WARN")
            
#             return field_id
        
#         return None

#     # ==================== MAIN DISCOVERY METHOD ====================
    
#     def discover_and_create_project_fields(self, all_fields: List[dict], 
#                                             project_key: str, project_id: str) -> Tuple[dict, Optional[str]]:
#         """
#         Discover/create custom fields and scope them ONLY to this project.
#         Field names are clean (no project key suffix).
#         """
#         discovered = {}
#         field_ids_for_screens = []
        
#         self._log(f"\nSetting up custom fields for project {project_key}...", "INFO")
#         print()
        
#         for key, field_config in EXPECTED_FIELDS.items():
#             field_name = field_config["name"]
            
#             self._log(f"  Processing '{field_name}'...", "INFO")
            
#             # Find or create field, then scope to project
#             field_id = self.find_or_create_project_field(
#                 field_config, project_id, project_key, all_fields
#             )
            
#             if field_id:
#                 discovered[key] = field_id
#                 field_ids_for_screens.append(field_id)
                
#                 # Update all_fields list for future reference
#                 if not self.find_field_id(all_fields, field_name):
#                     all_fields.append({
#                         "id": field_id,
#                         "name": field_name,
#                         "custom": True
#                     })
        
#         print()
        
#         # Find Epic Name field (this is a system field, not project-specific)
#         epic_name_id = self.find_field_id(all_fields, "Epic Name")
#         if epic_name_id:
#             self._log(f"  Found 'Epic Name' → {epic_name_id}", "SUCCESS")
        
#         # Add fields to project-specific screens only
#         if field_ids_for_screens:
#             self._log(f"\nAdding fields to project screens...", "INFO")
#             screen_count = self.add_fields_to_project_screens_only(
#                 project_key, project_id, field_ids_for_screens
#             )
#             self._log(f"  Total screen field additions: {screen_count}", "INFO")
        
#         return discovered, epic_name_id

#     # ==================== PROJECT AND ISSUE CREATION ====================
    
#     def create_project(self, name: str, key: str, template: str, lead_id: str) -> dict:
#         """Create a new Company-managed Jira project"""
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
#             project_data = r.json()
#             self._log(f"Project '{name}' created successfully! Key: {key}", "SUCCESS")
            
#             project_style = project_data.get("style", "unknown")
#             self._log(f"  Project style: {project_style}", "INFO")
            
#             return project_data
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
#                     description: str = None, fields_extra: dict = None) -> dict:
#         """Create a Jira issue (Epic or Story) with custom fields"""
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
#                 "content": [
#                     {
#                         "type": "paragraph",
#                         "content": [
#                             {
#                                 "type": "text",
#                                 "text": description
#                             }
#                         ]
#                     }
#                 ]
#             }
        
#         if fields_extra:
#             for field_id, field_value in fields_extra.items():
#                 fields[field_id] = field_value
        
#         payload = {"fields": fields}
        
#         try:
#             r = requests.post(url, headers=self.headers, json=payload, timeout=30)
#             r.raise_for_status()
#             return r.json()
#         except requests.exceptions.HTTPError:
#             error_detail = ""
#             try:
#                 error_json = r.json()
#                 error_detail = json.dumps(error_json, indent=2)
#             except Exception:
#                 error_detail = r.text
#             raise Exception(f"Failed to create {issue_type}: {error_detail}")
    
#     def update_issue_fields(self, issue_key: str, fields: dict) -> Tuple[bool, List[str]]:
#         """Update issue fields after creation"""
#         url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
#         failed_fields = []
        
#         for field_id, field_value in fields.items():
#             payload = {
#                 "fields": {
#                     field_id: field_value
#                 }
#             }
            
#             try:
#                 r = requests.put(url, headers=self.headers, json=payload, timeout=30)
#                 if r.status_code not in (200, 204):
#                     failed_fields.append(field_id)
#             except Exception:
#                 failed_fields.append(field_id)
        
#         return len(failed_fields) == 0, failed_fields
    
#     def link_to_parent(self, issue_key: str, parent_key: str) -> bool:
#         """Link an issue to a parent Epic"""
#         url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
#         payload = {
#             "fields": {
#                 "parent": {"key": parent_key}
#             }
#         }
        
#         try:
#             r = requests.put(url, headers=self.headers, json=payload, timeout=30)
#             return r.status_code in (200, 204)
#         except Exception:
#             return False
    
#     def generate_structure(self, project_key: str, custom_fields: dict,
#                           epic_name_field: Optional[str], lead_account_id: str):
#         """Generate the complete Epic/Story structure"""
        
#         self._log(f"\nGenerating project structure for {project_key}...", "INFO")
#         print()
        
#         epic_keys = {}
#         total_epics = len(EPICS)
#         total_stories = sum(len(stories) for stories in EPICS.values())
        
#         epic_count = 0
#         story_count = 0
        
#         for epic_name, story_list in EPICS.items():
#             epic_count += 1
            
#             try:
#                 fields_extra = {}
#                 if epic_name_field:
#                     fields_extra[epic_name_field] = epic_name
                
#                 epic_issue = self.create_issue(
#                     project_key,
#                     "Epic",
#                     epic_name,
#                     f"Epic: {epic_name}",
#                     fields_extra
#                 )
#                 epic_key = epic_issue.get("key")
#                 epic_keys[epic_name] = epic_key
#                 self._log(f"[{epic_count}/{total_epics}] Epic '{epic_name}' → {epic_key}", "SUCCESS")
                
#                 if epic_name_field and fields_extra:
#                     time.sleep(0.3)
#                     success, failed = self.update_issue_fields(epic_key, {epic_name_field: epic_name})
#                     if success:
#                         self._log(f"  → Epic Name field updated", "SUCCESS")
                
#             except Exception as e:
#                 self._log(f"Failed to create Epic '{epic_name}': {e}", "ERROR")
#                 continue
            
#             for story in story_list:
#                 story_count += 1
                
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
                
#                 try:
#                     story_issue = self.create_issue(
#                         project_key,
#                         "Story",
#                         story,
#                         f"Story: {story}",
#                         fields_extra=story_fields
#                     )
#                     story_key = story_issue.get("key")
                    
#                     linked = self.link_to_parent(story_key, epic_key)
                    
#                     link_status = "→ linked to Epic" if linked else ""
#                     fields_status = f"→ {len(story_fields)} custom fields" if story_fields else ""
                    
#                     self._log(f"  [{story_count}/{total_stories}] Story '{story}' → {story_key} {link_status} {fields_status}", "SUCCESS")
                    
#                 except Exception as e:
#                     self._log(f"  Failed to create Story '{story}': {e}", "ERROR")
                    
#                     try:
#                         self._log(f"    Retrying without custom fields...", "INFO")
#                         story_issue = self.create_issue(
#                             project_key,
#                             "Story",
#                             story,
#                             f"Story: {story}"
#                         )
#                         story_key = story_issue.get("key")
#                         linked = self.link_to_parent(story_key, epic_key)
                        
#                         if story_fields:
#                             time.sleep(0.3)
#                             success, failed = self.update_issue_fields(story_key, story_fields)
#                             field_status = "→ custom fields updated" if success else "→ custom fields failed"
#                         else:
#                             field_status = ""
                        
#                         link_status = "→ linked to Epic" if linked else ""
#                         self._log(f"  [{story_count}/{total_stories}] Story '{story}' → {story_key} {link_status} {field_status}", "SUCCESS")
#                     except Exception as retry_error:
#                         self._log(f"  Retry also failed: {retry_error}", "ERROR")
        
#         return epic_keys


# def check_env_file():
#     """Check if .env file exists and has required variables"""
#     env_path = Path(".env")
    
#     if not env_path.exists():
#         print("\n❌ Error: .env file not found!")
#         print("\nCreating a template .env file for you...")
        
#         template = """# Jira Configuration
# JIRA_BASE_URL=https://your-domain.atlassian.net
# JIRA_EMAIL=your-email@example.com
# JIRA_API_TOKEN=your_api_token_here
# """
        
#         env_path.write_text(template)
#         print("✅ Created .env file")
#         print("\n📝 Please edit the .env file and add your credentials:")
#         print("   1. JIRA_BASE_URL - Your Jira instance URL")
#         print("   2. JIRA_EMAIL - Your Jira email")
#         print("   3. JIRA_API_TOKEN - Your Jira API token")
#         print("\n   Get your API token from: https://id.atlassian.com/manage-profile/security/api-tokens")
#         print()
#         return False
    
#     if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
#         print("\n❌ Error: Missing required environment variables in .env file!")
#         print("\nRequired variables:")
#         print("  - JIRA_BASE_URL")
#         print("  - JIRA_EMAIL")
#         print("  - JIRA_API_TOKEN")
#         print("\nPlease check your .env file and ensure all variables are set.")
#         print()
#         return False
    
#     if JIRA_API_TOKEN == "your_api_token_here":
#         print("\n❌ Error: Please update JIRA_API_TOKEN in .env file with your actual token!")
#         print("\nGet your API token from: https://id.atlassian.com/manage-profile/security/api-tokens")
#         print()
#         return False
    
#     return True


# def main():
#     """Main execution flow"""
    
#     if not check_env_file():
#         sys.exit(1)
    
#     print("\n" + "="*60)
#     print("  🚀 JIRA COMPANY-MANAGED PROJECT GENERATOR")
#     print("     (Project-Specific Custom Fields)")
#     print("="*60 + "\n")
    
#     generator = JiraProjectGenerator(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN)
    
#     generator._log("Testing connection to Jira...", "INFO")
#     success, user_info = generator.test_connection()
    
#     if not success:
#         generator._log(f"Connection failed: {user_info.get('error')}", "ERROR")
#         generator._log("Please check your credentials in .env file", "ERROR")
#         return
    
#     lead_id = user_info.get("accountId")
#     user_name = user_info.get("displayName", user_info.get("emailAddress"))
#     generator._log(f"Connected as: {user_name}", "SUCCESS")
    
#     print("\n" + "-"*60)
    
#     print("\n📋 PROJECT DETAILS\n")
    
#     while True:
#         project_name = input("Enter Project Name: ").strip()
#         if not project_name:
#             generator._log("Project name is required!", "ERROR")
#             continue
        
#         suggested_key = generator.suggest_project_key(project_name)
#         project_key_input = input(f"Enter Project Key (suggested: {suggested_key}): ").strip().upper()
#         project_key = project_key_input if project_key_input else suggested_key
        
#         if not re.match(r'^[A-Z][A-Z0-9]{1,9}$', project_key):
#             generator._log("Invalid project key! Must be 2-10 uppercase letters/numbers, starting with a letter.", "ERROR")
#             continue
        
#         if generator.check_project_exists(project_key):
#             generator._log(f"Project key '{project_key}' already exists!", "ERROR")
#             retry = input("Would you like to try a different key? (y/N): ").strip().lower()
#             if retry == 'y':
#                 continue
#             else:
#                 generator._log("Operation cancelled", "WARN")
#                 return
        
#         break
    
#     print("\n📐 SELECT PROJECT TEMPLATE (Company-managed)\n")
#     for key, (name, _) in VALID_TEMPLATES.items():
#         print(f"  {key}. {name}")
    
#     template_choice = input("\nChoose template (1-3) [default: 2-Scrum]: ").strip() or "2"
    
#     if template_choice not in VALID_TEMPLATES:
#         generator._log("Invalid template choice!", "ERROR")
#         return
    
#     template_name, template_key = VALID_TEMPLATES[template_choice]
    
#     print("\n" + "-"*60)
#     print("\n📊 SUMMARY\n")
#     print(f"  Project Name:  {project_name}")
#     print(f"  Project Key:   {project_key}")
#     print(f"  Template:      {template_name} (Company-managed)")
#     print(f"  Epics:         {len(EPICS)}")
#     print(f"  Stories:       {sum(len(s) for s in EPICS.values())}")
#     print(f"  Custom Fields: {len(EXPECTED_FIELDS)} (scoped to this project)")
#     print()
    
#     print("📝 Custom fields to be configured:")
#     for key, config in EXPECTED_FIELDS.items():
#         print(f"     • {config['name']}")
#     print()
    
#     confirm = input("Proceed with creation? (y/N): ").strip().lower()
    
#     if confirm != 'y':
#         generator._log("Operation cancelled", "WARN")
#         return
    
#     print("\n" + "="*60 + "\n")
    
#     # Step 1: Create Project
#     try:
#         generator._log("Creating Company-managed Jira project...", "INFO")
#         project = generator.create_project(project_name, project_key, template_key, lead_id)
#         project_id = project.get("id")
#     except Exception as e:
#         generator._log(f"Project creation failed: {e}", "ERROR")
#         return
    
#     # Step 2: Wait for project to initialize
#     generator._log("Waiting for project initialization...", "INFO")
#     time.sleep(3)
    
#     # Step 3: Create/configure project-specific custom fields
#     try:
#         all_fields = generator.fetch_all_fields()
#         custom_fields, epic_name_field = generator.discover_and_create_project_fields(
#             all_fields, 
#             project_key,
#             project_id
#         )
        
#         if custom_fields:
#             generator._log("Waiting for field configurations to apply...", "INFO")
#             time.sleep(2)
#     except Exception as e:
#         generator._log(f"Field setup failed: {e}", "ERROR")
#         generator._log("Continuing without custom fields...", "WARN")
#         custom_fields = {}
#         epic_name_field = None
    
#     # Step 4: Generate Epics and Stories
#     try:
#         epic_keys = generator.generate_structure(
#             project_key,
#             custom_fields,
#             epic_name_field,
#             lead_id
#         )
#     except Exception as e:
#         generator._log(f"Structure generation encountered errors: {e}", "ERROR")
#         epic_keys = {}
    
#     # Summary
#     print("\n" + "="*60)
#     print("  ✨ PROJECT GENERATION COMPLETE!")
#     print("="*60)
#     print(f"\n🔗 View your project at:")
#     print(f"   {JIRA_BASE_URL}/projects/{project_key}\n")
#     print(f"📝 Created {len(epic_keys)} Epics with their Stories")
    
#     if custom_fields:
#         print(f"\n🏷️  Custom Fields Configured for {project_key}:")
#         for key, field_id in custom_fields.items():
#             field_name = EXPECTED_FIELDS[key]["name"]
#             print(f"     • {field_name} → {field_id}")
    
#     print("\n" + "-"*60)
#     print(f"ℹ️  Custom fields are scoped to project {project_key} only.")
#     print()


# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\n\n⚠️  Operation cancelled by user\n")
#         sys.exit(0)
#     except Exception as e:
#         print(f"\n❌ Unexpected error: {e}\n")
#         import traceback
#         traceback.print_exc()
#         sys.exit(1)
#!/usr/bin/env python3
"""
Jira Project Generator - Company-Managed Projects
Automatically creates Company-managed Jira projects with Epics and Stories
Custom fields are added to project-specific screens
Uses .env file for credentials

FIXED VERSION - Proper screen discovery and field context handling
"""

import requests
import base64
import json
import re
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import getpass

try:
    from dotenv import load_dotenv
except ImportError:
    print("\n❌ Error: python-dotenv package not found!")
    print("Install it with: pip install python-dotenv")
    print()
    sys.exit(1)

load_dotenv()

# ---------- CREDENTIALS (from .env file) ----------
# JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
# JIRA_EMAIL = os.getenv("JIRA_EMAIL")
# JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Company-managed project templates
VALID_TEMPLATES = {
    "1": ("Kanban", "com.pyxis.greenhopper.jira:gh-kanban-template"),
    "2": ("Scrum", "com.pyxis.greenhopper.jira:gh-scrum-template"),
    "3": ("Bug Tracking", "com.atlassian.jira-core-project-templates:jira-core-project-management"),
}

# Project structure to create
EPICS = {
    "ASSESSMENT & PLANNING (2 - 12 weeks, depending on project scope, sizing, access, onboarding)": [
        "Onboarding and Access - See Access Tab for Details",
        "Introductory Call",
        "Discuss NON-PRODUCTION environments",
        "Set up Weekly Touchpoint w/Atlassian (if above 1000 users)",
        "Discuss Atlassian Cloud Status",
        "Start Atlassian CLOUD Trial (if needed)",
        "Set up Weekly Touchpoint w/Project Team",
        "Set up Atlassian Guard (if needed/in scope)",
        "Open Ticket w/Atlassian for MOVE",
        "Refresh lower instance of Jira to current version",
        "Licensing Tier Jira",
        "Licensing Tier Confluence",
        "Discussion/Discovery Migration Scope for Confluence",
        "Discussion/Discovery Migration Scope for Jira",
        "Discussion/Discovery Integrations",
        "Discussion/Discovery User Management",
        "Start Atlassian Guard Trial (if needed/in scope)",
        "User Clean Up Tasks",
        "Jira - Add-on Assessment",
        "Confluence - Add-on Assessment",
        "Environment Assessment & Pre-Migration Checklist",
        "Develop Migration Approach & Draft Runbook",
        "Develop Testing Plan",
        "Develop Communications Plan",
        "Develop Training Plan (if needed)",
        "Review & Acceptance - Environment Assessment",
        "Review & Acceptance - Jira Projects Assessment",
        "Review & Acceptance - Confluence Spaces",
        "Review & Acceptance - Jira Add-ons",
        "Review & Acceptance - Atlassian Guard Setup",
        "Review & Acceptance - Confluence Addons",
        "Review & Acceptance - Confluence Macros",
        "Review & Acceptance - Integrations",
        "Review & Acceptance - Pre Migration Checklists (Jira & Confluence)",
        "Budget Review Meeting (T&M)",
        "Refresh Staging Environments (Jira and Confluence)",
        "<other tasks as identified>"
    ],
    "TEST MIGRATION (4 - 16 weeks, depending on scope, sizing, & capacity of Client)": [
        "Execute User Migration using JCMA",
        "Execute Complete test migration using JCMA",
        "Transformation Tasks - Scriptrunner",
        "Basic Application Integrity Tests",
        "Workflow Review & Migration Assistant Errors",
        "Working Session to review Migration Assistant Findings (if needed)",
        "Execute Add-on Remediation Plan",
        "Execute Confluence Migration using CCMA",
        "Post migration checks Jira & Confluence"
    ],
    "USER ACCEPTANCE TESTING (1 - 2 weeks, depending on scope, sizing, & capacity of Client)": [
        "Capula Project Team Testing",
        "Hold UAT Training (if needed)",
        "User Acceptance Testing",
        "Issue Resolution",
        "Go/No Go Decision (UAT Acceptance)"
    ],
    "PRODUCTION MIGRATION (TBD)": ["Finalize Migration Runbook", "See Migration Timeline Tab "],
    "POST MIGRATION SUPPORT (4 weeks)": ["<items as identified>"],
}

# Expected custom fields with their types
EXPECTED_FIELDS = {
    "percent_complete": {
        "name": "% Complete",
        "field_id": None,
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
        "description": "Percentage of task completion"
    },
    "target_start": {
        "name": "Target Start Date",
        "field_id": None,
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
        "description": "Target start date for the task"
    },
    "target_end": {
        "name": "Target End Date",
        "field_id": None,
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
        "description": "Target end date for the task"
    },
    "owning": {
        "name": "Owning",
        "field_id": None,
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:userpicker",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:userpickergroupsearcher",
        "description": "Owner of the task"
    }
}


class JiraProjectGenerator:
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.headers = self._get_auth_header()
        self.debug_mode = False  # Set to True for verbose output

    def _get_auth_header(self) -> dict:
        """Generate Basic Auth header for Jira API"""
        token = f"{self.email}:{self.api_token}"
        b64 = base64.b64encode(token.encode()).decode()
        return {
            "Authorization": f"Basic {b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _log(self, message: str, level: str = "INFO"):
        """Pretty logging with emoji indicators"""
        icons = {
            "INFO": "🔵",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARN": "⚠️",
            "QUESTION": "❓",
            "DEBUG": "🔍"
        }
        # Only show DEBUG messages if debug_mode is True
        if level == "DEBUG" and not self.debug_mode:
            return
        print(f"{icons.get(level, '•')} {message}")

    def suggest_project_key(self, name: str) -> str:
        """Generate a suggested project key from project name"""
        name_clean = re.sub(r'[^A-Za-z0-9 ]+', '', name).strip()
        parts = name_clean.split()

        if len(parts) == 1:
            key = parts[0][:4].upper()
        else:
            key = ''.join(p[0] for p in parts if p)[:4].upper()

        if len(key) < 2:
            key = (key + "PR")[:2]

        return key[:10]

    def check_project_exists(self, project_key: str) -> bool:
        """Check if a project with this key already exists"""
        try:
            url = f"{self.base_url}/rest/api/3/project/{project_key}"
            r = requests.get(url, headers=self.headers, timeout=10)
            return r.status_code == 200
        except Exception:
            return False

    def test_connection(self) -> Tuple[bool, dict]:
        """Test API connection and get current user info"""
        try:
            url = f"{self.base_url}/rest/api/3/myself"
            r = requests.get(url, headers=self.headers, timeout=10)
            r.raise_for_status()
            return True, r.json()
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}

    def fetch_all_fields(self) -> List[dict]:
        """Fetch all Jira fields to discover custom field IDs"""
        url = f"{self.base_url}/rest/api/3/field"
        r = requests.get(url, headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()

    def find_field_id(self, fields: List[dict], display_name: str) -> Optional[str]:
        """Find field ID by display name (case-insensitive)"""
        for f in fields:
            if f.get("name", "").strip().lower() == display_name.strip().lower():
                return f.get("id")
        return None

    # ==================== SCREEN DISCOVERY - FIXED ====================

    def get_project_screens_by_name(self, project_key: str) -> List[dict]:
        """
        Find screens that belong to this project by searching for project key in screen name.
        This is the most reliable method for company-managed projects.
        """
        screens = []
        start_at = 0
        max_results = 100
        
        self._log(f"  Searching for screens containing '{project_key}'...", "DEBUG")
        
        while True:
            url = f"{self.base_url}/rest/api/3/screens"
            params = {"startAt": start_at, "maxResults": max_results}
            
            try:
                r = requests.get(url, headers=self.headers, params=params, timeout=30)
                if r.status_code != 200:
                    break
                    
                data = r.json()
                values = data.get("values", [])
                
                for screen in values:
                    screen_name = screen.get("name", "")
                    # Match screens that start with project key or contain ": Project Key"
                    if (screen_name.startswith(f"{project_key}:") or 
                        screen_name.startswith(f"{project_key} ") or
                        f": {project_key}" in screen_name):
                        screens.append({
                            "id": screen.get("id"),
                            "name": screen_name,
                            "description": screen.get("description", "")
                        })
                        self._log(f"    Found: {screen_name} (ID: {screen.get('id')})", "DEBUG")
                
                if len(values) < max_results:
                    break
                start_at += max_results
                
            except Exception as e:
                self._log(f"Error searching screens: {e}", "WARN")
                break
        
        return screens

    def get_screen_scheme_for_project(self, project_key: str) -> Optional[dict]:
        """Get screen scheme info by searching for project-named scheme"""
        try:
            url = f"{self.base_url}/rest/api/3/screenscheme"
            params = {"startAt": 0, "maxResults": 100}
            r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if r.status_code == 200:
                schemes = r.json().get("values", [])
                for scheme in schemes:
                    scheme_name = scheme.get("name", "")
                    if project_key in scheme_name:
                        self._log(f"  Found Screen Scheme: {scheme_name}", "DEBUG")
                        return scheme
            return None
        except Exception as e:
            self._log(f"Error getting screen schemes: {e}", "WARN")
            return None

    def get_screens_from_screen_scheme(self, screen_scheme_id: str) -> List[dict]:
        """Get all screens from a screen scheme"""
        screens = []
        try:
            url = f"{self.base_url}/rest/api/3/screenscheme/{screen_scheme_id}"
            r = requests.get(url, headers=self.headers, timeout=30)
            
            if r.status_code == 200:
                data = r.json()
                screen_mappings = data.get("screens", {})
                
                for operation, screen_id in screen_mappings.items():
                    if screen_id:
                        screens.append({
                            "id": screen_id,
                            "operation": operation,
                            "name": f"Screen {screen_id}"
                        })
            return screens
        except Exception as e:
            self._log(f"Error getting screens from scheme: {e}", "WARN")
            return screens

    def get_all_project_screens(self, project_key: str, project_id: str) -> List[dict]:
        """
        Get all screens for a project using multiple methods:
        1. Search by project key in screen name (most reliable)
        2. Get from screen scheme if found
        3. Use issue type screen scheme mappings
        """
        all_screens = []
        seen_ids = set()
        
        # Method 1: Search by project key in screen name
        self._log("  Method 1: Searching screens by project key...", "DEBUG")
        named_screens = self.get_project_screens_by_name(project_key)
        for screen in named_screens:
            if screen["id"] not in seen_ids:
                seen_ids.add(screen["id"])
                all_screens.append(screen)
        
        if named_screens:
            self._log(f"  Found {len(named_screens)} screen(s) by name", "INFO")
        
        # Method 2: Get from screen scheme
        self._log("  Method 2: Checking screen schemes...", "DEBUG")
        screen_scheme = self.get_screen_scheme_for_project(project_key)
        if screen_scheme:
            scheme_screens = self.get_screens_from_screen_scheme(screen_scheme.get("id"))
            for screen in scheme_screens:
                if screen["id"] not in seen_ids:
                    seen_ids.add(screen["id"])
                    all_screens.append(screen)
            self._log(f"  Found {len(scheme_screens)} screen(s) from screen scheme", "DEBUG")
        
        # Method 3: Try issue type screen scheme
        self._log("  Method 3: Checking issue type screen scheme...", "DEBUG")
        itss_screens = self.get_screens_from_itss(project_id)
        for screen in itss_screens:
            if screen["id"] not in seen_ids:
                seen_ids.add(screen["id"])
                all_screens.append(screen)
        
        if itss_screens:
            self._log(f"  Found {len(itss_screens)} screen(s) from ITSS", "DEBUG")
        
        return all_screens

    def get_screens_from_itss(self, project_id: str) -> List[dict]:
        """Get screens through Issue Type Screen Scheme chain"""
        screens = []
        
        try:
            # Step 1: Get Issue Type Screen Scheme for project
            url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/project"
            params = {"projectId": project_id}
            r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if r.status_code != 200:
                return screens
            
            data = r.json()
            values = data.get("values", [])
            if not values:
                return screens
            
            itss = values[0].get("issueTypeScreenScheme", {})
            itss_id = itss.get("id")
            
            if not itss_id:
                return screens
            
            # Step 2: Get screen scheme mappings
            url = f"{self.base_url}/rest/api/3/issuetypescreenscheme/{itss_id}/mapping"
            params = {"startAt": 0, "maxResults": 50}
            r = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if r.status_code != 200:
                return screens
            
            mappings = r.json().get("values", [])
            screen_scheme_ids = set()
            
            for mapping in mappings:
                ss_id = mapping.get("screenSchemeId")
                if ss_id:
                    screen_scheme_ids.add(str(ss_id))
            
            # Step 3: Get screens from each screen scheme
            for ss_id in screen_scheme_ids:
                ss_screens = self.get_screens_from_screen_scheme(ss_id)
                screens.extend(ss_screens)
            
        except Exception as e:
            self._log(f"Error in ITSS lookup: {e}", "DEBUG")
        
        return screens

    # ==================== SCREEN TAB AND FIELD MANAGEMENT ====================

    def get_screen_tabs(self, screen_id: int) -> List[dict]:
        """Get all tabs for a screen"""
        try:
            url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs"
            r = requests.get(url, headers=self.headers, timeout=30)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            self._log(f"Error getting screen tabs: {e}", "WARN")
        return []

    def get_tab_fields(self, screen_id: int, tab_id: int) -> List[str]:
        """Get all field IDs already on a screen tab"""
        try:
            url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
            r = requests.get(url, headers=self.headers, timeout=30)
            if r.status_code == 200:
                fields = r.json()
                return [f.get("id") for f in fields if f.get("id")]
        except Exception as e:
            self._log(f"Error getting tab fields: {e}", "WARN")
        return []

    def add_field_to_screen_tab(self, screen_id: int, tab_id: int, field_id: str) -> bool:
        """Add a field to a specific screen tab"""
        try:
            # Check if field already exists
            existing = self.get_tab_fields(screen_id, tab_id)
            if field_id in existing:
                return True
            
            url = f"{self.base_url}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
            payload = {"fieldId": field_id}
            r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if r.status_code in (200, 201, 204):
                return True
            elif r.status_code == 400 and "already" in r.text.lower():
                return True
            else:
                self._log(f"    Could not add {field_id} to screen {screen_id}: {r.text[:100]}", "DEBUG")
                return False
                
        except Exception as e:
            self._log(f"Error adding field: {e}", "WARN")
            return False

    def add_fields_to_project_screens(self, project_key: str, project_id: str, 
                                       field_ids: List[str]) -> Tuple[int, int]:
        """
        Add custom fields to project-specific screens only.
        Returns (screens_updated, total_fields_added)
        """
        screens_updated = 0
        total_added = 0
        
        # Get project-specific screens
        project_screens = self.get_all_project_screens(project_key, project_id)
        
        if not project_screens:
            self._log("  No project-specific screens found!", "WARN")
            self._log("  Fields will need to be added manually to screens.", "WARN")
            return 0, 0
        
        self._log(f"  Found {len(project_screens)} project screen(s) to update", "INFO")
        
        for screen in project_screens:
            screen_id = screen.get("id")
            screen_name = screen.get("name", f"Screen {screen_id}")
            
            tabs = self.get_screen_tabs(screen_id)
            if not tabs:
                self._log(f"    {screen_name}: No tabs found", "WARN")
                continue
            
            # Add to first tab
            tab_id = tabs[0].get("id")
            tab_name = tabs[0].get("name", "Field Tab")
            
            fields_added = 0
            for field_id in field_ids:
                if self.add_field_to_screen_tab(screen_id, tab_id, field_id):
                    fields_added += 1
                time.sleep(0.1)  # Rate limiting
            
            if fields_added > 0:
                self._log(f"    ✓ {screen_name}: Added {fields_added} fields to '{tab_name}'", "SUCCESS")
                screens_updated += 1
                total_added += fields_added
            else:
                self._log(f"    • {screen_name}: Fields already present", "INFO")
        
        return screens_updated, total_added

    # ==================== FIELD CONTEXT MANAGEMENT - FIXED ====================

    def get_field_contexts(self, field_id: str) -> List[dict]:
        """Get all contexts for a custom field"""
        try:
            url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
            params = {"maxResults": 100}
            r = requests.get(url, headers=self.headers, params=params, timeout=30)
            if r.status_code == 200:
                return r.json().get("values", [])
        except Exception as e:
            self._log(f"Error getting contexts: {e}", "DEBUG")
        return []

    def add_project_to_field_context(self, field_id: str, project_id: str, 
                                      project_key: str) -> bool:
        """
        Add project to an existing field context or create a new one.
        Uses the correct Jira Cloud API format.
        """
        contexts = self.get_field_contexts(field_id)
        
        # Check if there's already a global context (field available everywhere)
        for ctx in contexts:
            if ctx.get("isGlobalContext", False):
                self._log(f"    Field has global context - available in all projects", "DEBUG")
                return True
        
        # Check if project already in a context
        for ctx in contexts:
            project_ids = [str(p) for p in ctx.get("projectIds", [])]
            if str(project_id) in project_ids:
                self._log(f"    Project already in context", "DEBUG")
                return True
        
        # Try to add project to an existing non-global context
        if contexts:
            first_context = contexts[0]
            ctx_id = first_context.get("id")
            
            try:
                url = f"{self.base_url}/rest/api/3/field/{field_id}/context/{ctx_id}/project"
                payload = {"projectIds": [str(project_id)]}
                r = requests.put(url, headers=self.headers, json=payload, timeout=30)
                
                if r.status_code in (200, 204):
                    self._log(f"    Added project to existing context", "DEBUG")
                    return True
                else:
                    self._log(f"    Could not add to context: {r.status_code}", "DEBUG")
            except Exception as e:
                self._log(f"    Context update error: {e}", "DEBUG")
        
        # If no contexts exist, try to create one
        if not contexts:
            try:
                url = f"{self.base_url}/rest/api/3/field/{field_id}/context"
                # Note: For Jira Cloud, we might need issue type IDs as well
                payload = {
                    "name": f"Context for {project_key}",
                    "projectIds": [str(project_id)]
                }
                r = requests.post(url, headers=self.headers, json=payload, timeout=30)
                
                if r.status_code in (200, 201):
                    self._log(f"    Created new context for project", "DEBUG")
                    return True
                else:
                    self._log(f"    Could not create context: {r.text[:100]}", "DEBUG")
            except Exception as e:
                self._log(f"    Context creation error: {e}", "DEBUG")
        
        # Fields with global context or standard fields should work without explicit context
        return True

    # ==================== FIELD CREATION ====================

    def create_custom_field(self, field_name: str, field_type: str,
                            searcher_key: str, description: str) -> Optional[str]:
        """Create a new custom field"""
        url = f"{self.base_url}/rest/api/3/field"
        
        payload = {
            "name": field_name,
            "description": description,
            "type": field_type,
            "searcherKey": searcher_key
        }
        
        try:
            r = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if r.status_code in (200, 201):
                result = r.json()
                field_id = result.get("id")
                self._log(f"  Created field '{field_name}' → {field_id}", "SUCCESS")
                return field_id
            else:
                self._log(f"  Failed to create '{field_name}': {r.text[:150]}", "ERROR")
                return None
                
        except Exception as e:
            self._log(f"Error creating field: {e}", "ERROR")
            return None

    def find_or_create_field(self, field_config: dict, project_id: str, 
                              project_key: str, all_fields: List[dict]) -> Optional[str]:
        """Find existing field or create new one"""
        field_name = field_config["name"]
        
        # Check if exists
        existing_id = self.find_field_id(all_fields, field_name)
        
        if existing_id:
            self._log(f"  Found existing: '{field_name}' → {existing_id}", "SUCCESS")
            # Ensure project has access
            self.add_project_to_field_context(existing_id, project_id, project_key)
            return existing_id
        
        # Create new
        self._log(f"  Creating: '{field_name}'...", "INFO")
        field_id = self.create_custom_field(
            field_name,
            field_config["type"],
            field_config["searcherKey"],
            field_config["description"]
        )
        
        if field_id:
            # Add to fields list
            all_fields.append({
                "id": field_id,
                "name": field_name,
                "custom": True
            })
            time.sleep(0.5)
            self.add_project_to_field_context(field_id, project_id, project_key)
            return field_id
        
        return None

    # ==================== MAIN SETUP METHOD ====================

    def setup_project_fields(self, all_fields: List[dict], 
                              project_key: str, project_id: str) -> Tuple[dict, Optional[str]]:
        """
        Main method to set up custom fields:
        1. Find or create each field
        2. Ensure project can access fields  
        3. Add fields to project screens
        """
        discovered = {}
        field_ids = []
        
        print()
        self._log("=" * 50, "INFO")
        self._log("PHASE 1: Setting up custom fields", "INFO")
        self._log("=" * 50, "INFO")
        print()
        
        for key, config in EXPECTED_FIELDS.items():
            field_id = self.find_or_create_field(config, project_id, project_key, all_fields)
            if field_id:
                discovered[key] = field_id
                field_ids.append(field_id)
        
        # Find Epic Name
        epic_name_id = self.find_field_id(all_fields, "Epic Name")
        if epic_name_id:
            self._log(f"  Found 'Epic Name' → {epic_name_id}", "SUCCESS")
        
        print()
        self._log("=" * 50, "INFO")
        self._log("PHASE 2: Adding fields to project screens", "INFO")
        self._log("=" * 50, "INFO")
        print()
        
        if field_ids:
            # Wait for Jira to fully register the fields
            self._log("  Waiting for field registration...", "INFO")
            time.sleep(3)
            
            screens_updated, fields_added = self.add_fields_to_project_screens(
                project_key, project_id, field_ids
            )
            
            print()
            if screens_updated > 0:
                self._log(f"  Summary: Updated {screens_updated} screens, {fields_added} field additions", "SUCCESS")
            else:
                self._log("  Warning: No screens were updated", "WARN")
                self._log("  You may need to manually add fields to screens in Project Settings", "WARN")
        
        return discovered, epic_name_id

    # ==================== PROJECT AND ISSUE CREATION ====================

    def create_project(self, name: str, key: str, template: str, lead_id: str) -> dict:
        """Create a new Company-managed Jira project"""
        url = f"{self.base_url}/rest/api/3/project"
        
        payload = {
            "key": key,
            "name": name,
            "projectTypeKey": "software",
            "projectTemplateKey": template,
            "leadAccountId": lead_id,
            "assigneeType": "PROJECT_LEAD",
            "description": f"Company-managed project: {name}",
        }
        
        r = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
        if r.status_code in (200, 201):
            project_data = r.json()
            self._log(f"Project '{name}' created! Key: {key}", "SUCCESS")
            return project_data
        else:
            error_msg = r.text
            try:
                error_json = r.json()
                if 'errors' in error_json:
                    error_msg = json.dumps(error_json['errors'], indent=2)
                elif 'errorMessages' in error_json:
                    error_msg = ', '.join(error_json['errorMessages'])
            except Exception:
                pass
            raise Exception(f"Failed to create project: {error_msg}")

    def create_issue(self, project_key: str, issue_type: str, summary: str,
                     description: str = None, fields_extra: dict = None) -> dict:
        """Create a Jira issue"""
        url = f"{self.base_url}/rest/api/3/issue"
        
        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type}
        }
        
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description}]
                }]
            }
        
        if fields_extra:
            fields.update(fields_extra)
        
        try:
            r = requests.post(url, headers=self.headers, json={"fields": fields}, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError:
            raise Exception(f"Failed to create {issue_type}: {r.text[:200]}")

    def update_issue_fields(self, issue_key: str, fields: dict) -> bool:
        """Update issue fields"""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
        try:
            r = requests.put(url, headers=self.headers, json={"fields": fields}, timeout=30)
            return r.status_code in (200, 204)
        except Exception:
            return False

    def link_to_parent(self, issue_key: str, parent_key: str) -> bool:
        """Link issue to parent Epic"""
        return self.update_issue_fields(issue_key, {"parent": {"key": parent_key}})

    def generate_structure(self, project_key: str, custom_fields: dict,
                           epic_name_field: Optional[str], lead_account_id: str) -> dict:
        """Generate Epic/Story structure"""
        
        print()
        self._log("=" * 50, "INFO")
        self._log(f"PHASE 3: Creating Epics and Stories", "INFO")
        self._log("=" * 50, "INFO")
        print()
        
        epic_keys = {}
        total_epics = len(EPICS)
        total_stories = sum(len(s) for s in EPICS.values())
        epic_count = 0
        story_count = 0
        
        for epic_name, story_list in EPICS.items():
            epic_count += 1
            
            try:
                fields_extra = {}
                if epic_name_field:
                    fields_extra[epic_name_field] = epic_name
                
                epic = self.create_issue(project_key, "Epic", epic_name, 
                                         f"Epic: {epic_name}", fields_extra)
                epic_key = epic.get("key")
                epic_keys[epic_name] = epic_key
                
                short_name = epic_name[:50] + "..." if len(epic_name) > 50 else epic_name
                self._log(f"[{epic_count}/{total_epics}] Epic: {short_name} → {epic_key}", "SUCCESS")
                
            except Exception as e:
                self._log(f"Failed to create Epic: {e}", "ERROR")
                continue
            
            for story_name in story_list:
                story_count += 1
                
                # Prepare custom field values
                story_fields = {}
                today = datetime.utcnow().date()
                
                if "percent_complete" in custom_fields:
                    story_fields[custom_fields["percent_complete"]] = "0"
                if "target_start" in custom_fields:
                    story_fields[custom_fields["target_start"]] = str(today)
                if "target_end" in custom_fields:
                    story_fields[custom_fields["target_end"]] = str(today + timedelta(days=7))
                if "owning" in custom_fields:
                    story_fields[custom_fields["owning"]] = {"accountId": lead_account_id}
                
                try:
                    # Try with custom fields first
                    story = self.create_issue(project_key, "Story", story_name,
                                              f"Story: {story_name}", story_fields)
                    story_key = story.get("key")
                    linked = self.link_to_parent(story_key, epic_key)
                    
                    status = "✓" if linked else "○"
                    self._log(f"  [{story_count}/{total_stories}] {status} {story_key}", "SUCCESS")
                    
                except Exception as e:
                    # Retry without custom fields
                    try:
                        story = self.create_issue(project_key, "Story", story_name)
                        story_key = story.get("key")
                        self.link_to_parent(story_key, epic_key)
                        
                        # Try to update fields separately
                        if story_fields:
                            time.sleep(0.2)
                            self.update_issue_fields(story_key, story_fields)
                        
                        self._log(f"  [{story_count}/{total_stories}] ○ {story_key} (retry)", "SUCCESS")
                    except Exception:
                        self._log(f"  Failed: {story_name[:30]}...", "ERROR")
        
        return epic_keys


# def check_env_file():
#     """Check .env file"""
#     env_path = Path(".env")
    
#     if not env_path.exists():
#         print("\n❌ Error: .env file not found!")
#         template = """# Jira Configuration
# JIRA_BASE_URL=https://your-domain.atlassian.net
# JIRA_EMAIL=your-email@example.com
# JIRA_API_TOKEN=your_api_token_here
# """
#         env_path.write_text(template)
#         print("✅ Created .env template - please edit it with your credentials")
#         return False
    
#     if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
#         print("\n❌ Missing environment variables in .env!")
#         return False
    
#     if JIRA_API_TOKEN == "your_api_token_here":
#         print("\n❌ Please update JIRA_API_TOKEN in .env!")
#         return False
    
#     return True


def main():
    """Main execution"""
    # if not check_env_file():
    #     sys.exit(1)
    JIRA_BASE_URL = input("Enter the JIRA BASE URL:")
    JIRA_EMAIL = input("Enter the JIRA EMAIL:")
    JIRA_API_TOKEN = getpass.getpass("Enter the JIRA API TOKEN:(hidden)")
    print("\n" + "=" * 60)
    print("  🚀 JIRA COMPANY-MANAGED PROJECT GENERATOR")
    print("     (Fixed Screen Configuration)")
    print("=" * 60 + "\n")
    
    generator = JiraProjectGenerator(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN)
    
    # Uncomment for verbose debug output:
    # generator.debug_mode = True
    
    generator._log("Testing connection...", "INFO")
    success, user_info = generator.test_connection()
    
    if not success:
        generator._log(f"Connection failed: {user_info.get('error')}", "ERROR")
        return
    
    lead_id = user_info.get("accountId")
    user_name = user_info.get("displayName", user_info.get("emailAddress"))
    generator._log(f"Connected as: {user_name}", "SUCCESS")
    
    print("\n" + "-" * 60 + "\n")
    print("📋 PROJECT DETAILS\n")
    
    while True:
        project_name = input("Enter Project Name: ").strip()
        if not project_name:
            generator._log("Project name required!", "ERROR")
            continue
        
        suggested_key = generator.suggest_project_key(project_name)
        key_input = input(f"Enter Project Key (suggested: {suggested_key}): ").strip().upper()
        project_key = key_input if key_input else suggested_key
        
        if not re.match(r'^[A-Z][A-Z0-9]{1,9}$', project_key):
            generator._log("Invalid key! Must be 2-10 uppercase chars starting with letter.", "ERROR")
            continue
        
        if generator.check_project_exists(project_key):
            generator._log(f"Project '{project_key}' already exists!", "ERROR")
            if input("Try different key? (y/N): ").strip().lower() == 'y':
                continue
            return
        break
    
    print("\n📐 SELECT TEMPLATE\n")
    for k, (name, _) in VALID_TEMPLATES.items():
        print(f"  {k}. {name}")
    
    choice = input("\nChoose (1-3) [default: 2]: ").strip() or "2"
    if choice not in VALID_TEMPLATES:
        generator._log("Invalid choice!", "ERROR")
        return
    
    template_name, template_key = VALID_TEMPLATES[choice]
    
    print("\n" + "-" * 60)
    print("\n📊 SUMMARY\n")
    print(f"  Project Name:  {project_name}")
    print(f"  Project Key:   {project_key}")
    print(f"  Template:      {template_name}")
    print(f"  Epics:         {len(EPICS)}")
    print(f"  Stories:       {sum(len(s) for s in EPICS.values())}")
    print(f"  Custom Fields: {len(EXPECTED_FIELDS)}")
    print()
    
    if input("Proceed? (y/N): ").strip().lower() != 'y':
        generator._log("Cancelled", "WARN")
        return
    
    print("\n" + "=" * 60)
    
    # Create project
    try:
        generator._log("Creating project...", "INFO")
        project = generator.create_project(project_name, project_key, template_key, lead_id)
        project_id = project.get("id")
    except Exception as e:
        generator._log(f"Failed: {e}", "ERROR")
        return
    
    # Wait for project initialization
    generator._log("Waiting for project initialization (10 seconds)...", "INFO")
    time.sleep(10)  # Longer wait for screens to be created
    
    # Setup fields
    try:
        all_fields = generator.fetch_all_fields()
        custom_fields, epic_name_field = generator.setup_project_fields(
            all_fields, project_key, project_id
        )
    except Exception as e:
        generator._log(f"Field setup error: {e}", "ERROR")
        custom_fields = {}
        epic_name_field = None
    
    # Generate structure
    try:
        epic_keys = generator.generate_structure(
            project_key, custom_fields, epic_name_field, lead_id
        )
    except Exception as e:
        generator._log(f"Structure error: {e}", "ERROR")
        epic_keys = {}
    
    # Summary
    print("\n" + "=" * 60)
    print("  ✨ COMPLETE!")
    print("=" * 60)
    print(f"\n🔗 {JIRA_BASE_URL}/projects/{project_key}")
    print(f"📝 Created {len(epic_keys)} Epics")
    
    if custom_fields:
        print(f"\n🏷️ Custom Fields:")
        for k, fid in custom_fields.items():
            print(f"   • {EXPECTED_FIELDS[k]['name']} → {fid}")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Cancelled\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)