from datetime import datetime

PAGE_REGISTRY = {}


def register_page(name):
    def decorator(func):
        PAGE_REGISTRY[name] = func
        return func
    return decorator


def list_available_templates():
    return list(PAGE_REGISTRY.keys())


def get_template_by_name(name):
    return PAGE_REGISTRY.get(name)


def _header(title):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return f"""<ac:structured-macro ac:name="info" ac:schema-version="1">
  <ac:rich-text-body><p><strong>📅 Created:</strong> {today}</p></ac:rich-text-body>
</ac:structured-macro>"""


# 1 - 30: PAGE TEMPLATES
@register_page("Project Overview")
def template_project_overview(**kw):
    return _header("Project Overview") + """
<h1>Project Overview</h1><hr/>
<h2>Project Name:</h2><hr/>
<h2>Objective:</h2><hr/><br><br><br><br><br><br><br>
</h2><hr/>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 50%;">
    <tr>
        <th style="background-color:red; color:white;">Milestones</th>
        <th style="background-color:red; color:white;">Deliverables</th>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
</table>
<hr/>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 50%;">
    <tr>
        <th style="background-color:black; color:white;">Service</th>
        <th style="background-color:black; color:white;">Milestone</th>
        <th style="background-color:black; color:white;">Roles Required Capacity Dedicated</th>
        <th style="background-color:black; color:white;">Duration</th>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
    <tr>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
        <td style="background-color:grey">  </td>
    </tr>
</table>
"""

@register_page("Project Team")
def template_project_team(**kw):
    return _header("Project Team") + """
<h1>Project Team</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 70%;">
    <tr>
        <th style="background-color:black; color:white;">Name</th>
        <th style="background-color:black; color:white;">Organization</th>
        <th style="background-color:black; color:white;">Role</th>
        <th style="background-color:black; color:white;">Email</th>
        <th style="background-color:black; color:white;">TimeZone</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""
@register_page("Access Requirement")
def template_access_requirement(**kw):
    return _header("Access Requirement") + """
<h1>Access Requirement</h1><hr/>

<h2>ACCESS REQUIREMENTS</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 80%;">
    <tr>
        <th style="background-color:black; color:white;">ITEMS</th>
        <th style="background-color:black; color:white;">A1</th>
        <th style="background-color:black; color:white;">A2</th>
        <th style="background-color:black; color:white;">A3</th>
        <th style="background-color:black; color:white;">A4</th>
        <th style="background-color:black; color:white;">NOTES</th>
    </tr>
    <tr>
        <td style="background-color:grey;">ORGANIZATION ACCESS</td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Jira Project")
def template_jira_project(**kw):
    return _header("Jira Project") + """
<h1>Jira Project</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
    <tr>
        <th style="background-color:black; color:white;">Project Name</th>
        <th style="background-color:black; color:white;">Project Key</th>
        <th style="background-color:black; color:white;">Project Type</th>
        <th style="background-color:black; color:white;">Project Lead</th>
        <th style="background-color:black; color:white;">Last Issue Updated</th>
        <th style="background-color:black; color:white;">Issue Count</th>
        <th style="background-color:black; color:white;">Keep/Discard</th>
        <th style="background-color:black; color:white;">Comment</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""
@register_page("High Level Project Tracker")
def template_high_level_project_tracker(**kw):
    return _header("High Level Project Tracker") + """
<h1>High Level Project Tracker</h1><hr/>

<h2>Capula & Cprime Project Plan/Tracker</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
    <tr>
        <th style="background-color:black; color:white;">Milestones & Tasks</th>
        <th style="background-color:black; color:white;">% Complete</th>
        <th style="background-color:black; color:white;">Target Start Date</th>
        <th style="background-color:black; color:white;">Target End Date</th>
        <th style="background-color:black; color:white;">Status</th>
        <th style="background-color:black; color:white;">Owning Resource Name(s)</th>
        <th style="background-color:black; color:white;">Comments</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Environment Details")
def template_environment_details(**kw):
    return _header("Environment Details") + """
<h1>Environment Details</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 60%;">
    <tr>
        <th style="background-color:black; color:white;">Application</th>
        <th style="background-color:black; color:white;">Jira</th>
        <th style="background-color:black; color:white;">Confluence</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Roadmap")
def template_roadmap(**kw):
    return _header("Roadmap") + """
<h1>Roadmap</h1><hr/>

<h2>ORIGINAL MIGRATION ROADMAP JIRA AND CONFLUENCE</h2>

<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; font-size: 12px;">
    <table border="1" cellspacing="0" cellpadding="5">
    <tr>
        <th colspan="4" style="background-color:black; color:white;">Jan</th>
        <th colspan="4" style="background-color:black; color:white;">Feb</th>
        <th colspan="4" style="background-color:black; color:white;">Mar</th>
        <th colspan="4" style="background-color:black; color:white;">Apr</th>
        <th colspan="4" style="background-color:black; color:white;">May</th>
        <th colspan="4" style="background-color:black; color:white;">Jun</th>
        <th colspan="4" style="background-color:black; color:white;">Jul</th>
        <th colspan="4" style="background-color:black; color:white;">Aug</th>
        <th colspan="4" style="background-color:black; color:white;">Sep</th>
        <th colspan="4" style="background-color:black; color:white;">Oct</th>
    </tr>
    <tr>
        <!-- January Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>

        <!-- February Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>

        <!-- March Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>

        <!-- April Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>

        <!-- May Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>

        <!-- June Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>

        <!-- July Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>

        <!-- August Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>

        <!-- September Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>

        <!-- October Weeks -->
        <td style="background-color:grey;">Week1</td>
        <td style="background-color:grey;">Week2</td>
        <td style="background-color:grey;">Week3</td>
        <td style="background-color:grey;">Week4</td>
    </tr>
</table>

</table>

<h2>PREPARE & DEVELOP - Actions and rough estimates</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 70%;">
    <tr>
        <th style="background-color:black; color:white;">Action Description</th>
        <th style="background-color:black; color:white;">Estimate (h)</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>

<h2>TEST AND UAT - Actions and rough estimates</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 70%;">
    <tr>
        <th style="background-color:black; color:white;">Action Description</th>
        <th style="background-color:black; color:white;">Estimate (h)</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Confluence Spaces")
def template_confluence_spaces(**kw):
    return _header("Confluence Spaces") + """
<h1>Confluence Spaces</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
    <tr>
        <th style="background-color:black; color:white;">Space ID</th>
        <th style="background-color:black; color:white;">Space Key</th>
        <th style="background-color:black; color:white;">Space Name</th>
        <th style="background-color:black; color:white;">Creation Date</th>
        <th style="background-color:black; color:white;">Last Updated Date</th>
        <th style="background-color:black; color:white;">Space Type</th>
        <th style="background-color:black; color:white;">Space Status</th>
        <th style="background-color:black; color:white;">Keep/Discard</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Jira Add-Ons")
def template_jira_addons(**kw):
    return _header("Jira Add-Ons") + """
<h1>Jira Add-Ons</h1><hr/>

<h2>Jira Add-on List</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
    <tr>
        <th style="background-color:black; color:white;">S/No</th>
        <th style="background-color:black; color:white;">Application Name</th>
        <th style="background-color:black; color:white;">Vendor</th>
        <th style="background-color:black; color:white;">Currently Enabled?</th>
        <th style="background-color:black; color:white;">License Status</th>
        <th style="background-color:black; color:white;">Available In Cloud</th>
        <th style="background-color:black; color:white;">Should be migrated?</th>
        <th style="background-color:black; color:white;">Marketplace Link</th>
        <th style="background-color:black; color:white;">Migration Path</th>
        <th style="background-color:black; color:white;">Usage</th>
        <th style="background-color:black; color:white;">Business-Critical and Required in Cloud? Keep / Discard?</th>
        <th style="background-color:black; color:white;">Notes & Recommendations - for Cloud</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""
@register_page("Jira App Usage Stats")
def template_jira_app_usage_stats(**kw):
    return _header("Jira App Usage Stats") + """
<h1>Jira App Usage Stats</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
    <tr>
        <th style="background-color:black; color:white;">Application Name</th>
        <th style="background-color:black; color:white;">URL</th>
        <th style="background-color:black; color:white;">Common Usage Data (20/02/2025)</th>
        <th style="background-color:black; color:white;">User Interactions (20/02/2025)</th>
        <th style="background-color:black; color:white;">Custom Fields (20/02/2025)</th>
        <th style="background-color:black; color:white;">Workflows (20/02/2025)</th>
        <th style="background-color:black; color:white;">Dashboards (20/02/2025)</th>
        <th style="background-color:black; color:white;">Comments / Recommendations</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Automation Rules Stats")
def template_automation_rules_stats(**kw):
    return _header("Automation Rules Stats") + """
<h1>Automation Rules Stats</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 30%;">
    <tr>
        <th style="background-color:black; color:white;">Project</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Confluence Add-Ons")
def template_confluence_addons(**kw):
    return _header("Confluence Add-Ons") + """
<h1>Confluence Add-Ons</h1><hr/>

<h2>Confluence Add-on List</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
    <tr>
        <th style="background-color:black; color:white;">S/No</th>
        <th style="background-color:black; color:white;">Application Name</th>
        <th style="background-color:black; color:white;">Vendor</th>
        <th style="background-color:black; color:white;">Currently Enabled?</th>
        <th style="background-color:black; color:white;">License Status</th>
        <th style="background-color:black; color:white;">Available In Cloud</th>
        <th style="background-color:black; color:white;">Should be migrated?</th>
        <th style="background-color:black; color:white;">Usage (pages)</th>
        <th style="background-color:black; color:white;">Ability to Migrate? Migration Path</th>
        <th style="background-color:black; color:white;">Marketplace Link</th>
        <th style="background-color:black; color:white;">Views (last 60 days from 09/02/2024)</th>
        <th style="background-color:black; color:white;">Business-Critical and Required in Cloud? Keep Notes & Recommendations - for Cloud / Discard?</th>
        <th style="background-color:black; color:white;"></th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Confluence Macros Assessments")
def template_confluence_macros_assessments(**kw):
    return _header("Confluence Macros Assessments") + """
<h1>Confluence Macros Assessments</h1><hr/>

<h2>Confluence Macros List</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 60%;">
    <tr>
        <th style="background-color:black; color:white;">App Name</th>
        <th style="background-color:black; color:white;">App Total No of Pages Additional Analysis</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Scaffolding Nested Macro")
def template_scaffolding_nested_macro(**kw):
    return _header("Scaffolding Nested Macro") + """
<h1>Scaffolding Nested Macro</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 50%;">
    <tr>
        <th style="background-color:black; color:white;">Space Key</th>
        <th style="background-color:black; color:white;">Page ID</th>
        <th style="background-color:black; color:white;">Message</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Integrated Inventory")
def template_integrated_inventory(**kw):
    return _header("Integrated Inventory") + """
<h1>Integrated Inventory</h1><hr/>

<h2>Integration Inventory</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 80%;">
    <tr>
        <th style="background-color:black; color:white;">Item</th>
        <th style="background-color:black; color:white;">Instance</th>
        <th style="background-color:black; color:white;">Type</th>
        <th style="background-color:black; color:white;">Direction</th>
        <th style="background-color:black; color:white;">Usage</th>
        <th style="background-color:black; color:white;">Integration Owner</th>
        <th style="background-color:black; color:white;">Notes</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Jira Users Assessments")
def template_jira_users_assessments(**kw):
    return _header("Jira Users Assessments") + """
<h1>Jira Users Assessments</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 70%;">
    <tr>
        <th style="background-color:black; color:white;">Username</th>
        <th style="background-color:black; color:white;">Display Name</th>
        <th style="background-color:black; color:white;">Current Email</th>
        <th style="background-color:black; color:white;">New Email</th>
        <th style="background-color:black; color:white;">Directory</th>
        <th style="background-color:black; color:white;">Status</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Scaffolding Pages Restrictions")
def template_scaffolding_pages_restrictions(**kw):
    return _header("Scaffolding Pages Restrictions") + """
<h1>Scaffolding Pages Restrictions</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
    <tr>
        <th style="background-color:black; color:white;">PAGE ID</th>
        <th style="background-color:black; color:white;">PAGE RESTRICTION TYPE</th>
        <th style="background-color:black; color:white;">USER'S PERMISSION TYPE</th>
        <th style="background-color:black; color:white;">ACCOUNT TYPE</th>
        <th style="background-color:black; color:white;">USER OR GROUP NAME</th>
        <th style="background-color:black; color:white;">CREATOR</th>
        <th style="background-color:black; color:white;">CREATION DATE</th>
        <th style="background-color:black; color:white;">LAST MODIFIER</th>
        <th style="background-color:black; color:white;">LAST MODIFIED DATE</th>
        <th style="background-color:black; color:white;">LINK</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Duplicate Emails")
def template_duplicate_emails(**kw):
    return _header("Duplicate Emails") + """
<h1>Duplicate Emails</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 80%;">
    <tr>
        <th style="background-color:black; color:white;">Username</th>
        <th style="background-color:black; color:white;">Current Email</th>
        <th style="background-color:black; color:white;">New Email</th>
        <th style="background-color:black; color:white;">Last Authenticated</th>
        <th style="background-color:black; color:white;">Directory</th>
        <th style="background-color:black; color:white;">During Migration</th>
        <th style="background-color:black; color:white;">Contents Count</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Custom Fields")
def template_custom_fields(**kw):
    return _header("Custom Fields") + """
<h1>Custom Fields</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 90%;">
    <tr>
        <th style="background-color:black; color:white;">Name</th>
        <th style="background-color:black; color:white;">Type</th>
        <th style="background-color:black; color:white;">Available Contexts</th>
        <th style="background-color:black; color:white;">Screens</th>
        <th style="background-color:black; color:white;">Last Value Update</th>
        <th style="background-color:black; color:white;">Issues</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Workflow")
def template_workflow(**kw):
    return _header("Workflow") + """
<h1>Workflow</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 90%;">
    <tr>
        <th style="background-color:black; color:white;">Name</th>
        <th style="background-color:black; color:white;">Last Modified</th>
        <th style="background-color:black; color:white;">Last Modified By</th>
        <th style="background-color:black; color:white;">Assigned Schemes</th>
        <th style="background-color:black; color:white;">Steps</th>
        <th style="background-color:black; color:white;">Actions</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Permission Scheme in Server")
def template_permission_scheme_in_server(**kw):
    return _header("Permission Scheme in Server") + """
<h1>Permission Scheme in Server</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 60%;">
    <tr>
        <th style="background-color:black; color:white;">Name</th>
        <th style="background-color:black; color:white;">Projects</th>
        <th style="background-color:black; color:white;">Actions</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Confluence Users Assessments")
def template_confluence_users_assessments(**kw):
    return _header("Confluence Users Assessments") + """
<h1>Confluence Users Assessments</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 80%;">
    <tr>
        <th style="background-color:black; color:white;">Username</th>
        <th style="background-color:black; color:white;">Current Email</th>
        <th style="background-color:black; color:white;">New Email</th>
        <th style="background-color:black; color:white;">Last Authenticated</th>
        <th style="background-color:black; color:white;">Directory</th>
        <th style="background-color:black; color:white;">During Migration</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Advanced Roadmaps")
def template_advanced_roadmaps(**kw):
    return _header("Advanced Roadmaps") + """
<h1>Advanced Roadmaps</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 50%;">
    <tr>
        <th style="background-color:black; color:white;">Program</th>
        <th style="background-color:black; color:white;">Plan</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Public Settings")
def template_public_settings(**kw):
    return _header("Public Settings") + """
<h1>Public Settings</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 50%;">
    <tr>
        <th style="background-color:black; color:white;">Projects Set to Anyone</th>
        <th style="background-color:black; color:white;">Name</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Test Runbook")
def template_test_runbook(**kw):
    return _header("Test Runbook") + """
<h1>Test Runbook</h1><hr/>

<h2> (Commencing from 07/04/2025)</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 90%;">
    <tr>
        <th style="background-color:black; color:white;">       </th>
        <th style="background-color:black; color:white;">Product</th>
        <th style="background-color:black; color:white;">Status</th>
        <th style="background-color:black; color:white;">Start Date</th>
        <th style="background-color:black; color:white;">End Date</th>
        <th style="background-color:black; color:white;">Duration (mins)</th>
        <th style="background-color:black; color:white;">Responsibility</th>
        <th style="background-color:black; color:white;">Comments</th>
    </tr>
    <tr>
        <td style="background-color:grey;">Week of Migration</td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Prod Runbook Jira")
def template_prod_runbook_jira(**kw):
    return _header("Prod Runbook Jira") + """
<h1>Prod Runbook Jira</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 90%;">
    <tr>
        <th style="background-color:black; color:white;">     </th>
        <th style="background-color:black; color:white;">Status</th>
        <th style="background-color:black; color:white;">Start Date</th>
        <th style="background-color:black; color:white;">End Date</th>
        <th style="background-color:black; color:white;">Duration (mins)</th>
        <th style="background-color:black; color:white;">Responsibility</th>
        <th style="background-color:black; color:white;">Comments</th>
    </tr>
    <tr>
        <td style="background-color:grey;">Week of Migration</td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Prod Runbook Confluence")
def template_prod_runbook_confluence(**kw):
    return _header("Prod Runbook Confluence") + """

<h2>Week of Migration</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 90%;">
    <tr>
        <th style="background-color:black; color:white;">     </th>
        <th style="background-color:black; color:white;">Status</th>
        <th style="background-color:black; color:white;">Start Date</th>
        <th style="background-color:black; color:white;">End Date</th>
        <th style="background-color:black; color:white;">Duration (mins)</th>
        <th style="background-color:black; color:white;">Responsibility</th>
        <th style="background-color:black; color:white;">Comments</th>
    </tr>
    <tr>
        <td style="background-color:grey;">Prod Runbook Confluence</td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Migrations Stats")
def template_migrations_stats(**kw):
    return _header("Migrations Stats") + """
<h1>Migrations Stats</h1><hr/>
<!-- ADD YOUR CONTENT BELOW -->
"""

@register_page("Atlassian Tickets")
def template_atlassian_tickets(**kw):
    return _header("Atlassian Tickets") + """
<h1>Atlassian Tickets</h1><hr/>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 80%;">
    <tr>
        <th style="background-color:black; color:white;">Ticket Raised</th>
        <th style="background-color:black; color:white;">Description</th>
        <th style="background-color:black; color:white;">URL</th>
        <th style="background-color:black; color:white;">Status</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""

@register_page("Test Plan")
def template_test_plan(**kw):
    return _header("Test Plan") + """
<h1>Test Plan</h1><hr/>

<h2>SAMPLE UAT TEST CASES</h2>

<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 90%;">
    <tr>
        <th style="background-color:black; color:white;">Test Case</th>
        <th style="background-color:black; color:white;">Description</th>
        <th style="background-color:black; color:white;">Area</th>
        <th style="background-color:black; color:white;">Product</th>
        <th style="background-color:black; color:white;">Status</th>
        <th style="background-color:black; color:white;">Notes</th>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
    <tr>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
        <td style="background-color:grey;"></td>
    </tr>
</table>
"""
