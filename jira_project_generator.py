import base64
import re
import json
import time
import sys
import getpass
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

# =============================================================================
# IMPORT TEMPLATES
# =============================================================================
try:
    from confluence_templates import get_template_by_name, list_available_templates
    TEMPLATES_AVAILABLE = True
except ImportError:
    TEMPLATES_AVAILABLE = False

# =============================================================================
# CONFIGURATION
# =============================================================================

VALID_TEMPLATES = {
    "1": ("Kanban", "com.pyxis.greenhopper.jira:gh-kanban-template"),
    "2": ("Scrum", "com.pyxis.greenhopper.jira:gh-scrum-template"),
    "3": ("Bug Tracking", "com.atlassian.jira-core-project-templates:jira-core-project-management"),
}

EPICS = {
    "ASSESSMENT & PLANNING": [
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
    "TEST MIGRATION": [
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
    "USER ACCEPTANCE TESTING": [
        "Capula Project Team Testing",
        "Hold UAT Training (if needed)",
        "User Acceptance Testing",
        "Issue Resolution",
        "Go/No Go Decision (UAT Acceptance)"
    ],
    "PRODUCTION MIGRATION": [
        "Finalize Migration Runbook",
        "See Migration Timeline Tab"
    ],
    "POST MIGRATION SUPPORT": [
        "<items as identified>"
    ],
}

CONFLUENCE_PAGES = [
    "Project Overview",
    "Project Team",
    "Access Requirement",
    "Jira Project",
    "High Level Project Tracker",
    "Environment Details",
    "Roadmap",
    "Confluence Spaces",
    "Jira Add-Ons",
    "Jira App Usage Stats",
    "Automation Rules Stats",
    "Confluence Add-Ons",
    "Confluence Macros Assessments",
    "Scaffolding Nested Macro",
    "Integrated Inventory",
    "Jira Users Assessments",
    "Scaffolding Pages Restrictions",
    "Duplicate Emails",
    "Custom Fields",
    "Workflow",
    "Permission Scheme in Server",
    "Confluence Users Assessments",
    "Advanced Roadmaps",
    "Public Settings",
    "Test Runbook",
    "Prod Runbook Jira",
    "Prod Runbook Confluence",
    "Migrations Stats",
    "Atlassian Tickets",
    "Test Plan",
]

EXPECTED_FIELDS = {
    "percent_complete": {
        "name": "% Complete",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
        "description": "Percentage of task completion"
    },
    "target_start": {
        "name": "Target Start Date",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
        "description": "Target start date for the task"
    },
    "target_end": {
        "name": "Target End Date",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
        "description": "Target end date for the task"
    },
    "owning": {
        "name": "Owning",
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
        token = f"{email}:{api_token}"
        b64 = base64.b64encode(token.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _log(self, msg: str, level: str = "INFO"):
        icons = {"INFO": "", "SUCCESS": "✅", "ERROR": "❌",
                 "WARN": "", "CONFLUENCE": ""}
        print(f"{icons.get(level, '•')} {msg}")

    # ── Jira Connection ──────────────────────────────────────────────────────

    def test_connection(self) -> Tuple[bool, dict]:
        try:
            r = requests.get(f"{self.base_url}/rest/api/3/myself",
                             headers=self.headers, timeout=10)
            r.raise_for_status()
            return True, r.json()
        except Exception as e:
            return False, {"error": str(e)}

    def check_project_exists(self, key: str) -> bool:
        try:
            r = requests.get(f"{self.base_url}/rest/api/3/project/{key}",
                             headers=self.headers, timeout=10)
            return r.status_code == 200
        except Exception:
            return False

    def suggest_project_key(self, name: str) -> str:
        clean = re.sub(r'[^A-Za-z0-9 ]+', '', name).strip().split()
        if len(clean) == 1:
            key = clean[0][:4].upper()
        else:
            key = ''.join(p[0] for p in clean if p)[:4].upper()
        return (key if len(key) >= 2 else (key + "PR")[:2])[:10]

    # ── Jira Project Creation ────────────────────────────────────────────────

    def create_project(self, name: str, key: str, template: str, lead_id: str) -> dict:
        payload = {
            "key": key, "name": name,
            "projectTypeKey": "software",
            "projectTemplateKey": template,
            "leadAccountId": lead_id,
            "assigneeType": "PROJECT_LEAD",
            "description": f"Company-managed project: {name}",
        }
        r = requests.post(f"{self.base_url}/rest/api/3/project",
                          headers=self.headers, json=payload, timeout=30)
        if r.status_code in (200, 201):
            self._log(f"Project '{name}' created → {key}", "SUCCESS")
            return r.json()
        raise Exception(f"Failed to create project: {r.text[:300]}")

    # ── Jira Fields ──────────────────────────────────────────────────────────

    def fetch_all_fields(self) -> List[dict]:
        r = requests.get(f"{self.base_url}/rest/api/3/field",
                         headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()

    def find_field_id(self, fields: List[dict], name: str) -> Optional[str]:
        for f in fields:
            if f.get("name", "").strip().lower() == name.strip().lower():
                return f.get("id")
        return None

    def create_custom_field(self, name: str, ftype: str,
                            searcher: str, desc: str) -> Optional[str]:
        payload = {"name": name, "description": desc,
                   "type": ftype, "searcherKey": searcher}
        r = requests.post(f"{self.base_url}/rest/api/3/field",
                          headers=self.headers, json=payload, timeout=30)
        if r.status_code in (200, 201):
            fid = r.json().get("id")
            self._log(f"  Created '{name}' → {fid}", "SUCCESS")
            return fid
        self._log(f"  Failed '{name}': {r.text[:100]}", "ERROR")
        return None

    def get_field_contexts(self, field_id: str) -> List[dict]:
        try:
            r = requests.get(f"{self.base_url}/rest/api/3/field/{field_id}/context",
                             headers=self.headers, timeout=30)
            if r.status_code == 200:
                return r.json().get("values", [])
        except Exception:
            pass
        return []

    def add_project_to_field_context(self, field_id: str, project_id: str, project_key: str) -> bool:
        contexts = self.get_field_contexts(field_id)
        for ctx in contexts:
            if ctx.get("isGlobalContext", False):
                return True
        for ctx in contexts:
            if str(project_id) in [str(p) for p in ctx.get("projectIds", [])]:
                return True
        if contexts:
            try:
                url = f"{self.base_url}/rest/api/3/field/{field_id}/context/{contexts[0]['id']}/project"
                r = requests.put(url, headers=self.headers,
                                 json={"projectIds": [str(project_id)]}, timeout=30)
                if r.status_code in (200, 204):
                    return True
            except Exception:
                pass
        return True

    def find_or_create_field(self, config: dict, project_id: str,
                              project_key: str, all_fields: List[dict]) -> Optional[str]:
        existing = self.find_field_id(all_fields, config["name"])
        if existing:
            self._log(f"  Found '{config['name']}' → {existing}", "SUCCESS")
            self.add_project_to_field_context(existing, project_id, project_key)
            return existing
        fid = self.create_custom_field(config["name"], config["type"],
                                        config["searcherKey"], config["description"])
        if fid:
            all_fields.append({"id": fid, "name": config["name"], "custom": True})
            time.sleep(0.5)
            self.add_project_to_field_context(fid, project_id, project_key)
        return fid

    # ── Screens ──────────────────────────────────────────────────────────────

    def get_project_screens(self, project_key: str, project_id: str) -> List[dict]:
        screens, seen = [], set()
        start_at = 0
        while True:
            try:
                r = requests.get(f"{self.base_url}/rest/api/3/screens",
                                 headers=self.headers,
                                 params={"startAt": start_at, "maxResults": 100},
                                 timeout=30)
                if r.status_code != 200:
                    break
                values = r.json().get("values", [])
                for s in values:
                    n = s.get("name", "")
                    if (n.startswith(f"{project_key}:") or
                        n.startswith(f"{project_key} ") or
                        f": {project_key}" in n):
                        if s["id"] not in seen:
                            seen.add(s["id"])
                            screens.append(s)
                if len(values) < 100:
                    break
                start_at += 100
            except Exception:
                break

        # Also check ITSS
        try:
            r = requests.get(f"{self.base_url}/rest/api/3/issuetypescreenscheme/project",
                             headers=self.headers,
                             params={"projectId": project_id}, timeout=30)
            if r.status_code == 200:
                vals = r.json().get("values", [])
                if vals:
                    itss_id = vals[0].get("issueTypeScreenScheme", {}).get("id")
                    if itss_id:
                        r2 = requests.get(
                            f"{self.base_url}/rest/api/3/issuetypescreenscheme/{itss_id}/mapping",
                            headers=self.headers,
                            params={"startAt": 0, "maxResults": 50}, timeout=30)
                        if r2.status_code == 200:
                            for m in r2.json().get("values", []):
                                ss_id = m.get("screenSchemeId")
                                if ss_id:
                                    r3 = requests.get(
                                        f"{self.base_url}/rest/api/3/screenscheme/{ss_id}",
                                        headers=self.headers, timeout=30)
                                    if r3.status_code == 200:
                                        for op, sid in r3.json().get("screens", {}).items():
                                            if sid and sid not in seen:
                                                seen.add(sid)
                                                screens.append({"id": sid, "name": f"Screen {sid}"})
        except Exception:
            pass
        return screens

    def add_fields_to_screens(self, project_key: str, project_id: str,
                               field_ids: List[str]) -> Tuple[int, int]:
        updated, added = 0, 0
        for screen in self.get_project_screens(project_key, project_id):
            sid = screen.get("id")
            try:
                r = requests.get(f"{self.base_url}/rest/api/3/screens/{sid}/tabs",
                                 headers=self.headers, timeout=30)
                if r.status_code != 200:
                    continue
                tabs = r.json()
                if not tabs:
                    continue
                tid = tabs[0]["id"]
                r2 = requests.get(
                    f"{self.base_url}/rest/api/3/screens/{sid}/tabs/{tid}/fields",
                    headers=self.headers, timeout=30)
                existing = [f.get("id") for f in r2.json()] if r2.status_code == 200 else []
                count = 0
                for fid in field_ids:
                    if fid in existing:
                        count += 1
                        continue
                    r3 = requests.post(
                        f"{self.base_url}/rest/api/3/screens/{sid}/tabs/{tid}/fields",
                        headers=self.headers, json={"fieldId": fid}, timeout=30)
                    if r3.status_code in (200, 201, 204) or "already" in r3.text.lower():
                        count += 1
                    time.sleep(0.1)
                if count:
                    updated += 1
                    added += count
            except Exception:
                pass
        return updated, added

    # ── Jira Issues ──────────────────────────────────────────────────────────

    def create_issue(self, project_key: str, issue_type: str, summary: str,
                     description: str = None, extra: dict = None) -> dict:
        fields = {"project": {"key": project_key},
                  "summary": summary, "issuetype": {"name": issue_type}}
        if description:
            fields["description"] = {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph",
                             "content": [{"type": "text", "text": description}]}]
            }
        if extra:
            fields.update(extra)
        r = requests.post(f"{self.base_url}/rest/api/3/issue",
                          headers=self.headers, json={"fields": fields}, timeout=30)
        r.raise_for_status()
        return r.json()

    def update_issue(self, key: str, fields: dict) -> bool:
        r = requests.put(f"{self.base_url}/rest/api/3/issue/{key}",
                         headers=self.headers, json={"fields": fields}, timeout=30)
        return r.status_code in (200, 204)

    # ── Confluence ───────────────────────────────────────────────────────────

    def test_confluence(self) -> Tuple[bool, dict]:
        try:
            r = requests.get(f"{self.base_url}/wiki/rest/api/user/current",
                             headers=self.headers, timeout=10)
            r.raise_for_status()
            return True, r.json()
        except Exception as e:
            return False, {"error": str(e)}

    def space_exists(self, key: str) -> bool:
        try:
            r = requests.get(f"{self.base_url}/wiki/rest/api/space/{key.upper()}",
                             headers=self.headers, timeout=10)
            return r.status_code == 200
        except Exception:
            return False

    def create_space(self, key: str, name: str, desc: str = None) -> dict:
        payload = {
            "key": key.upper(), "name": name,
            "description": {"plain": {
                "value": desc or f"Documentation for {name}",
                "representation": "plain"
            }}
        }
        r = requests.post(f"{self.base_url}/wiki/rest/api/space",
                          headers=self.headers, json=payload, timeout=30)
        if r.status_code in (200, 201):
            self._log(f"Space '{name}' created → {key.upper()}", "SUCCESS")
            return r.json()
        raise Exception(f"Failed: {r.text[:200]}")

    def get_homepage_id(self, key: str) -> Optional[str]:
        try:
            r = requests.get(f"{self.base_url}/wiki/rest/api/space/{key.upper()}",
                             headers=self.headers, params={"expand": "homepage"}, timeout=10)
            if r.status_code == 200:
                return r.json().get("homepage", {}).get("id")
        except Exception:
            pass
        return None

    def create_page(self, space_key: str, title: str,
                     body: str, parent_id: str = None) -> Optional[dict]:
        payload = {
            "type": "page", "title": title,
            "space": {"key": space_key.upper()},
            "body": {"storage": {"value": body, "representation": "storage"}}
        }
        if parent_id:
            payload["ancestors"] = [{"id": str(parent_id)}]
        try:
            r = requests.post(f"{self.base_url}/wiki/rest/api/content",
                              headers=self.headers, json=payload, timeout=30)
            if r.status_code in (200, 201):
                return r.json()
            self._log(f"Failed page '{title}': {r.text[:150]}", "WARN")
        except Exception as e:
            self._log(f"Error page '{title}': {e}", "WARN")
        return None

    def get_page_url(self, page: dict) -> str:
        links = page.get("_links", {})
        return f"{links.get('base', self.base_url + '/wiki')}{links.get('webui', '')}"

    # ── Create All 30 Pages ──────────────────────────────────────────────────

    def create_all_pages(self, space_key: str, parent_id: str = None) -> dict:
        print()
        self._log("=" * 50, "INFO")
        self._log("CREATING 30 CONFLUENCE PAGES", "CONFLUENCE")
        self._log("=" * 50, "INFO")
        print()

        created = {}
        total = len(CONFLUENCE_PAGES)

        for i, name in enumerate(CONFLUENCE_PAGES, 1):
            body = None
            tmpl = "fallback"

            if TEMPLATES_AVAILABLE:
                func = get_template_by_name(name)
                if func:
                    body = func()
                    tmpl = func.__name__

            if not body:
                today = datetime.utcnow().strftime("%Y-%m-%d")
                body = f"""<ac:structured-macro ac:name="info" ac:schema-version="1">
  <ac:rich-text-body><p><strong>📅 Created:</strong> {today}</p></ac:rich-text-body>
</ac:structured-macro>
<h1>{name}</h1><hr/><p><em>Add content here...</em></p>"""

            page = self.create_page(space_key, name, body, parent_id)
            if page:
                url = self.get_page_url(page)
                created[name] = url
                self._log(f"  [{i}/{total}] {name}", "SUCCESS")
            else:
                self._log(f"  [{i}/{total}] FAILED: {name}", "ERROR")
            time.sleep(0.15)

        print()
        self._log(f"Pages created: {len(created)}/{total}", "CONFLUENCE")
        return created

    # ── Create Jira Structure ────────────────────────────────────────────────

    def create_jira_structure(self, project_key: str, custom_fields: dict,
                               epic_name_field: Optional[str],
                               lead_id: str) -> dict:
        print()
        self._log("=" * 50, "INFO")
        self._log("CREATING EPICS AND STORIES", "INFO")
        self._log("=" * 50, "INFO")
        print()

        epic_keys = {}
        total_epics = len(EPICS)
        total_stories = sum(len(s) for s in EPICS.values())
        sc = 0

        for ec, (epic_name, stories) in enumerate(EPICS.items(), 1):
            try:
                extra = {}
                if epic_name_field:
                    extra[epic_name_field] = epic_name
                epic = self.create_issue(project_key, "Epic", epic_name,
                                         f"Epic: {epic_name}", extra)
                ek = epic["key"]
                epic_keys[epic_name] = ek
                self._log(f"[{ec}/{total_epics}] Epic: {epic_name[:50]} → {ek}", "SUCCESS")
            except Exception as e:
                self._log(f"Failed Epic: {e}", "ERROR")
                continue

            for story_name in stories:
                sc += 1
                sf = {}
                today = datetime.utcnow().date()
                if "percent_complete" in custom_fields:
                    sf[custom_fields["percent_complete"]] = "0"
                if "target_start" in custom_fields:
                    sf[custom_fields["target_start"]] = str(today)
                if "target_end" in custom_fields:
                    sf[custom_fields["target_end"]] = str(today + timedelta(days=7))
                if "owning" in custom_fields:
                    sf[custom_fields["owning"]] = {"accountId": lead_id}

                try:
                    story = self.create_issue(project_key, "Story", story_name,
                                              f"Story: {story_name}", sf)
                    sk = story["key"]
                    linked = self.update_issue(sk, {"parent": {"key": ek}})
                    mark = "✓" if linked else "○"
                    self._log(f"  [{sc}/{total_stories}] {mark} {sk}: {story_name[:45]}", "SUCCESS")
                except Exception:
                    try:
                        story = self.create_issue(project_key, "Story", story_name)
                        sk = story["key"]
                        self.update_issue(sk, {"parent": {"key": ek}})
                        if sf:
                            time.sleep(0.2)
                            self.update_issue(sk, sf)
                        self._log(f"  [{sc}/{total_stories}] ○ {sk} (retry)", "SUCCESS")
                    except Exception:
                        self._log(f"  Failed: {story_name[:30]}", "ERROR")

        print()
        self._log(f"Epics: {len(epic_keys)} | Stories: {sc}", "SUCCESS")
        return epic_keys


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 60)
    print("  JIRA PROJECT + CONFLUENCE PAGES GENERATOR")
    print("     (Separate - No Linking)")
    print("=" * 60 + "\n")

    if TEMPLATES_AVAILABLE:
        print(f" Templates loaded: {len(list_available_templates())} pages\n")
    else:
        print(" confluence_templates.py not found, using fallback\n")

    # ── Credentials ──────────────────────────────────────────────────────────
    print(" CREDENTIALS\n")
    url = input("Atlassian URL (e.g. https://yoursite.atlassian.net): ").strip()
    email = input("Email: ").strip()
    token = getpass.getpass("API Token (hidden): ")

    if not all([url, email, token]):
        print(" All fields required!")
        return

    gen = JiraProjectGenerator(url, email, token)

    # ── Test Connections ─────────────────────────────────────────────────────
    print("\n TESTING CONNECTIONS\n")

    ok, user = gen.test_connection()
    if not ok:
        gen._log(f"Jira failed: {user.get('error')}", "ERROR")
        return
    lead_id = user["accountId"]
    gen._log(f"Jira: {user.get('displayName', email)}", "SUCCESS")

    conf_ok, _ = gen.test_confluence()
    if conf_ok:
        gen._log("Confluence: Connected", "SUCCESS")
    else:
        gen._log("Confluence: Failed - skipping pages", "WARN")

    # ── Jira Project Details ─────────────────────────────────────────────────
    print("\n JIRA PROJECT\n")

    while True:
        pname = input("Project Name: ").strip()
        if not pname:
            continue
        sug = gen.suggest_project_key(pname)
        pkey = (input(f"Project Key (suggested: {sug}): ").strip().upper() or sug)
        if not re.match(r'^[A-Z][A-Z0-9]{1,9}$', pkey):
            gen._log("Invalid key!", "ERROR")
            continue
        if gen.check_project_exists(pkey):
            gen._log(f"'{pkey}' exists!", "ERROR")
            continue
        break

    print("\n TEMPLATE\n")
    for k, (n, _) in VALID_TEMPLATES.items():
        print(f"  {k}. {n}")
    tc = input("\nChoose (1-3) [2]: ").strip() or "2"
    if tc not in VALID_TEMPLATES:
        gen._log("Invalid!", "ERROR")
        return
    tname, tkey = VALID_TEMPLATES[tc]

    # ── Confluence Space Details ─────────────────────────────────────────────
    space_key = None
    space_name = None

    if conf_ok:
        print("\n CONFLUENCE SPACE\n")
        if input("Create Confluence space with 30 doc pages? (Y/n): ").strip().lower() != 'n':
            space_name = input(f"Space Name [{pname} Docs]: ").strip() or f"{pname} Docs"
            clean = re.sub(r'[^A-Za-z0-9 ]+', '', space_name).strip().split()
            sug_sk = (''.join(p[0] for p in clean)[:6] if len(clean) > 1 else clean[0][:6]).upper()
            space_key = (input(f"Space Key [{sug_sk}]: ").strip().upper() or sug_sk)

            if gen.space_exists(space_key):
                gen._log(f"'{space_key}' exists!", "WARN")
                if input("Use existing? (Y/n): ").strip().lower() == 'n':
                    space_key = None

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "-" * 50)
    print("\n SUMMARY\n")
    print(f"  Jira:  {pname} ({pkey}) - {tname}")
    print(f"  Epics: {len(EPICS)} | Stories: {sum(len(s) for s in EPICS.values())}")
    if space_key:
        print(f"  Confluence: {space_name} ({space_key}) - {len(CONFLUENCE_PAGES)} pages")
        print(f"    No auto-linking between Jira and Confluence")
    print()

    if input("Proceed? (y/N): ").strip().lower() != 'y':
        gen._log("Cancelled", "WARN")
        return

    # ── Create Jira Project ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    try:
        project = gen.create_project(pname, pkey, tkey, lead_id)
        pid = project["id"]
    except Exception as e:
        gen._log(f"Failed: {e}", "ERROR")
        return

    gen._log("Waiting 10s for init...", "INFO")
    time.sleep(10)

    # ── Setup Fields ─────────────────────────────────────────────────────────
    print()
    gen._log("SETTING UP CUSTOM FIELDS", "INFO")
    print()
    custom_fields = {}
    field_ids = []
    try:
        all_fields = gen.fetch_all_fields()
        for key, cfg in EXPECTED_FIELDS.items():
            fid = gen.find_or_create_field(cfg, pid, pkey, all_fields)
            if fid:
                custom_fields[key] = fid
                field_ids.append(fid)
        epic_name_field = gen.find_field_id(all_fields, "Epic Name")
        if epic_name_field:
            gen._log(f"  Found 'Epic Name' → {epic_name_field}", "SUCCESS")
    except Exception as e:
        gen._log(f"Field error: {e}", "ERROR")
        epic_name_field = None

    if field_ids:
        gen._log("Adding fields to screens...", "INFO")
        time.sleep(3)
        su, sa = gen.add_fields_to_screens(pkey, pid, field_ids)
        if su:
            gen._log(f"  Updated {su} screens, {sa} additions", "SUCCESS")

    # ── Create Jira Structure ────────────────────────────────────────────────
    gen.create_jira_structure(pkey, custom_fields, epic_name_field, lead_id)

    # ── Create Confluence Pages (SEPARATE) ───────────────────────────────────
    created_pages = {}
    if space_key:
        if not gen.space_exists(space_key):
            try:
                gen.create_space(space_key, space_name,
                                 f"Documentation for {pname}")
            except Exception as e:
                gen._log(f"Space failed: {e}", "ERROR")
                space_key = None

        if space_key:
            parent_id = gen.get_homepage_id(space_key)
            created_pages = gen.create_all_pages(space_key, parent_id)

    # ── Done ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  COMPLETE!")
    print("=" * 60)
    print(f"\n Jira:       {url}/projects/{pkey}")
    if space_key:
        print(f" Confluence: {url}/wiki/spaces/{space_key}")
        print(f"\n Pages ({len(created_pages)}):")
        for name, purl in created_pages.items():
            print(f"   • {name}")
    if custom_fields:
        print(f"\n Fields:")
        for k, fid in custom_fields.items():
            print(f"   • {EXPECTED_FIELDS[k]['name']} → {fid}")
    print(f"\n Jira ↔ Confluence NOT linked. Link manually as needed.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Cancelled\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
