# Jira Project Generator — Company-Managed Projects

A Python automation tool that creates fully structured Jira **company-managed projects** with Epics, Stories, and project-specific custom fields.

All Jira credentials (URL, email, API token) are collected **interactively** with no configuration files required. API tokens are hidden using secure input.

---

## Table of Contents

- [Features](#features)
- [Project Structure Created](#project-structure-created)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Custom Fields Created](#custom-fields-created)
- [Example Output](#example-output)
- [Customization](#customization)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [Support](#support)
- [License](#license)

---

## Features

### Company-Managed Project Creation

Templates supported:
- Kanban
- Scrum
- Bug Tracking

### Full Project Structure Generation

Automatically creates:
- **5 Epics**
- **51 Stories**
- Story-to-Epic linking
- Custom fields populated for each issue

### Project-Scoped Custom Fields

Four custom fields visible only in your project:
- **% Complete** (Text field)
- **Target Start Date** (Date)
- **Target End Date** (Date)
- **Owning** (User picker)

### Automatic Field Configuration

- Fields created automatically
- Scoped to your project only
- Added to screens
- Populated with default values

---

## Project Structure Created

The script generates 5 migration-related Epics:

| Epic | Story Count |
|------|-------------|
| ASSESSMENT & PLANNING | 36 |
| TEST MIGRATION | 8 |
| USER ACCEPTANCE TESTING | 4 |
| PRODUCTION MIGRATION | 2 |
| POST MIGRATION SUPPORT | 1 |

**Total:** 5 Epics + 51 Stories (all linked and initialized)

---

## Prerequisites

### 1. Python Version

Python 3.7 or higher is required.

### 2. Required Packages

```bash
pip install requests
```

### 3. Jira Base URL and Email

- **Base URL:** Found in your browser address bar (e.g., `https://your-domain.atlassian.net`)
- **Email:** Your authorized Jira account email

### 4. Jira API Token

1. Visit the [Atlassian API Token page](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Copy the generated token

### 5. Jira Permissions

Your account needs:
- Project creation permissions
- Custom field creation permissions
- Admin/Global admin role (recommended)

---

## Installation

### Option 1: Using Shell Script

```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Option 2: Manual Setup

1. **Download the script**

   ```bash
   # Save the file as jira_project_generator.py
   ```

2. **Install dependencies**

   ```bash
   pip install requests
   ```

3. **Run the script**

   ```bash
   python jira_project_generator.py
   ```

> **Note:** No `.env` file is required. All credentials are entered interactively.

---

## Usage

### Step 1: Run the Script

```bash
python jira_project_generator.py
```

### Step 2: Enter Credentials

```
Enter Jira Base URL (e.g., https://your-domain.atlassian.net):
Enter Jira Email:
Enter Jira API Token: ***************
```

> API token input is securely hidden using `getpass`.

### Step 3: Enter Project Details

**Project Name:**
```
Enter Project Name: My Migration Project
```

**Project Key:**
```
Enter Project Key (e.g., MMPR): MMPR
```

**Template Selection:**
```
SELECT PROJECT TEMPLATE (Company-managed)

  1. Kanban
  2. Scrum
  3. Bug Tracking

Choose template (1-3) [default: 2]: 2
```

### Step 4: Confirm and Create

```
SUMMARY

  Project Name:  My Migration Project
  Project Key:   MMPR
  Template:      Scrum (Company-managed)
  Epics:         5
  Stories:       51
  Custom Fields: 4

Proceed with creation? (y/N): y
```

---

## Custom Fields Created

| Field Name | Type | Purpose |
|------------|------|---------|
| % Complete | Text | Track percentage completed |
| Target Start Date | Date | Planned start date |
| Target End Date | Date | Planned end date |
| Owning | User Picker | Issue owner |

Each field is:
- Created automatically
- Scoped only to your new project
- Added to required screens

---

## Example Output

```
🚀 JIRA PROJECT GENERATOR

🔵 Testing connection to Jira...
✅ Connected as: John Doe

📂 Creating project...
✅ Project created: MMPR

🛠️ Creating custom fields...
  ▸ % Complete → customfield_10100
  ▸ Target Start Date → customfield_10101
  ▸ Target End Date → customfield_10102
  ▸ Owning → customfield_10103

📑 Adding fields to screens...
✔ Done

📘 Creating Epics and Stories...
  ✔ Epic 1/5: ASSESSMENT & PLANNING → MMPR-1
      ✔ Story 1/36 → MMPR-2
      ✔ Story 2/36 → MMPR-3
      ...

✨ PROJECT GENERATION COMPLETE!

🔗 View your project at:
   https://your-domain.atlassian.net/projects/MMPR
```

---

## Customization

### Modify Epics and Stories

Update the `EPICS` dictionary in the script:

```python
EPICS = {
    "Epic Name": [
        "Story A",
        "Story B"
    ],
    "Another Epic": [
        "Story C",
        "Story D"
    ]
}
```

### Add Custom Fields

Modify the `EXPECTED_FIELDS` structure:

```python
EXPECTED_FIELDS = {
    "your_field_key": {
        "name": "Your Field Name",
        "field_id": None,
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
        "description": "Your field description"
    }
}
```

**Common field types:**

| Type Key | Description |
|----------|-------------|
| `textfield` | Single line text |
| `textarea` | Multi-line text |
| `datepicker` | Date field |
| `userpicker` | User selection |
| `select` | Dropdown list |

---

## Security Notes

- API token input is **hidden** using `getpass`
- No credentials stored anywhere
- No `.env` or config files required
- Safe to run on shared environments
- Rotate Jira API tokens regularly

---

## Troubleshooting

### Connection Failed

**Possible causes:**
- Wrong Jira URL
- Invalid API token
- Incorrect email
- Network restrictions

**Solution:** Verify all credentials and network access.

### Project Key Already Exists

**Solution:** Use a different project key. Check existing projects at your Jira instance.

### Custom Fields Not Visible

**Possible causes:**
- Screen configuration issues
- Field contexts not applied correctly

**Solution:** Check screens manually or re-run the script.

### Failed to Create Epic/Story

**Possible causes:**
- Issue type scheme misconfiguration
- Epic issue type not enabled
- Permission issues

**Solution:** Verify project permissions and issue type settings.

---

## Limitations

- Only works with **company-managed** Jira projects
- Requires admin or high-level permissions
- Maximum number of custom fields per Jira instance may apply
- Cannot modify team-managed projects
- Custom field names are fixed (customizable in code)

---

## Support

| Issue Type | Resource |
|------------|----------|
| Script issues | Review console logs and error messages |
| Jira API issues | [Atlassian REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) |
| Permission issues | Contact your Jira administrator |

---


