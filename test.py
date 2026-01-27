import requests
import csv
import getpass
import re
from requests.auth import HTTPBasicAuth
from collections import defaultdict

# ==== CONFIGURATION ====
print("=== Confluence Complete Macro Scanner ===\n")

BASE_URL = input("Enter the base URL (e.g., https://company.atlassian.net/wiki): ").strip().rstrip('/')
USERNAME = input("Enter your username/email: ").strip()
API_TOKEN = getpass.getpass("Enter your API token (hidden): ")
TARGET_SPACE = input("Enter Space Key to create the report page: ").strip()
PAGE_TITLE = input("Enter the page title (e.g., Complete Macro Report): ").strip()
OUTPUT_FILE = "confluence-all-macros-report.csv"

auth = HTTPBasicAuth(USERNAME, API_TOKEN)

# ========================
# MACRO CATEGORIES
# ========================

MACRO_CATEGORIES = {
    "Formatting Macros": [
        "code", "noformat", "panel", "info", "note", "warning", "tip",
        "quote", "color", "bgcolor", "center", "div", "span", "html",
        "style", "css", "anchor", "tooltip", "highlight"
    ],
    "Layout Macros": [
        "section", "column", "layout", "layout-section", "layout-cell",
        "float", "align", "spacer", "horizontal-rule", "divider",
        "responsive-layout", "card", "cards", "deck"
    ],
    "Content Macros": [
        "excerpt", "excerpt-include", "include", "multi-excerpt",
        "multi-excerpt-include", "content-by-label", "recently-updated",
        "popular-labels", "related-labels", "content-report-table",
        "blog-posts", "change-history", "attachments", "gallery",
        "viewfile", "viewdoc", "viewpdf", "viewxls", "office",
        "widget", "iframe", "embed"
    ],
    "Navigation Macros": [
        "toc", "toc-zone", "children", "pagetree", "pagetreesearch",
        "livesearch", "search", "navmap", "listpages", "index",
        "space-index", "space-details", "page-info", "breadcrumbs",
        "recently-viewed", "favorite-pages"
    ],
    "Scaffolding Macros": [
        "text-data", "date-data", "number-data", "list-data", "user-data",
        "group-data", "content-data", "attachment-data", "get-data",
        "set-data", "live-template", "hidden-data", "repeating-data",
        "table-data", "eval", "run", "create", "edit"
    ],
    "Reporting Macros": [
        "chart", "jira", "jira-issues", "jira-chart", "confluence-dashboard",
        "roadmap", "timeline", "calendar", "tasks", "task-report",
        "contributors", "contributors-summary", "content-reporter",
        "page-properties", "page-properties-report", "details", "details-summary",
        "status", "time", "profile", "user-profile", "mention"
    ],
    "Interactive Macros": [
        "expand", "ui-expand", "tab", "tabs", "tab-group", "accordion",
        "toggle", "button", "scroll-title", "show-if", "hide-if",
        "visibility", "restrict", "permission"
    ],
    "Media Macros": [
        "image", "gallery", "video", "audio", "multimedia", "youtube",
        "vimeo", "wistia", "loom", "drawio", "gliffy", "lucidchart",
        "miro", "figma", "sketch", "balsamiq", "mockup"
    ],
    "Integration Macros": [
        "jira", "trello", "slack", "teams", "google-drive", "google-docs",
        "google-sheets", "google-slides", "dropbox", "box", "onedrive",
        "sharepoint", "github", "bitbucket", "gitlab", "jenkins",
        "bamboo", "opsgenie", "statuspage", "pagerduty"
    ],
    "Table Macros": [
        "table", "table-plus", "table-filter", "table-chart", "table-excerpt",
        "table-transformer", "pivot-table", "spreadsheet", "csv",
        "excel", "sql", "database"
    ],
    "Communication Macros": [
        "comment", "inline-comment", "vote", "poll", "survey", "form",
        "feedback", "rating", "like", "reactions", "share"
    ]
}

# ========================

def get_all_spaces():
    """Fetch all spaces"""
    all_spaces = []
    start = 0
    limit = 100
    
    while True:
        url = f"{BASE_URL}/rest/api/space"
        params = {"start": start, "limit": limit}
        
        resp = requests.get(url, params=params, auth=auth)
        
        if resp.status_code != 200:
            print(f"Error fetching spaces: {resp.status_code}")
            return []
        
        data = resp.json()
        results = data.get("results", [])
        all_spaces.extend(results)
        
        if len(results) < limit:
            break
        
        start += limit
    
    return all_spaces

def get_all_pages_with_body():
    """Fetch all pages with body content"""
    all_pages = []
    start = 0
    limit = 100
    
    print("\nFetching all pages...")
    
    while True:
        url = f"{BASE_URL}/rest/api/content"
        params = {
            "type": "page",
            "expand": "body.storage,space,version",
            "start": start,
            "limit": limit
        }
        
        resp = requests.get(url, params=params, auth=auth)
        
        if resp.status_code != 200:
            print(f"Error: {resp.status_code}")
            break
        
        data = resp.json()
        results = data.get("results", [])
        all_pages.extend(results)
        
        print(f"  Fetched {len(all_pages)} pages...")
        
        if len(results) < limit:
            break
        
        start += limit
    
    return all_pages

def extract_all_macros(page):
    """Extract all macro names and details from a page"""
    body = page.get("body", {}).get("storage", {}).get("value", "")
    page_title = page.get("title", "Unknown")
    page_id = page.get("id", "")
    space_key = page.get("space", {}).get("key", "Unknown")
    
    # Find all macros
    macros = re.findall(r'<ac:structured-macro[^>]*ac:name="([^"]+)"', body)
    
    macro_list = []
    for macro in macros:
        macro_list.append({
            "macro_name": macro,
            "page_title": page_title,
            "page_id": page_id,
            "space_key": space_key
        })
    
    return macro_list

def categorize_macro(macro_name):
    """Determine category for a macro"""
    macro_lower = macro_name.lower()
    
    for category, macros in MACRO_CATEGORIES.items():
        if macro_lower in [m.lower() for m in macros]:
            return category
    
    return "Third-Party / Custom Macros"

def collect_macro_data():
    """Collect all macro data from Confluence"""
    print(f"\nConnecting to: {BASE_URL}\n")
    
    # Get all pages
    pages = get_all_pages_with_body()
    
    if not pages:
        print("No pages found.")
        return {}, {}
    
    print(f"\nTotal pages fetched: {len(pages)}")
    print("\nScanning for macros...\n")
    
    # Collect all macros
    macro_usage = defaultdict(lambda: {
        "count": 0,
        "pages": [],
        "spaces": set()
    })
    
    all_macro_instances = []
    
    for page in pages:
        macros = extract_all_macros(page)
        
        for m in macros:
            macro_name = m["macro_name"]
            macro_usage[macro_name]["count"] += 1
            macro_usage[macro_name]["pages"].append(m["page_title"])
            macro_usage[macro_name]["spaces"].add(m["space_key"])
            all_macro_instances.append(m)
    
    return macro_usage, all_macro_instances

def build_comprehensive_report(macro_usage):
    """Build categorized report"""
    
    # Categorize all macros
    categorized = defaultdict(list)
    
    for macro_name, data in macro_usage.items():
        category = categorize_macro(macro_name)
        categorized[category].append({
            "name": macro_name,
            "count": data["count"],
            "spaces": len(data["spaces"]),
            "pages": data["pages"][:5]  # First 5 pages as examples
        })
    
    # Sort macros within each category by usage count
    for category in categorized:
        categorized[category] = sorted(
            categorized[category],
            key=lambda x: -x["count"]
        )
    
    return categorized

def build_confluence_page_html(categorized, macro_usage):
    """Build complete HTML for Confluence page"""
    
    total_macros = len(macro_usage)
    total_usage = sum(m["count"] for m in macro_usage.values())
    
    html = f"""
    <h1>Complete Macro Usage Report</h1>
    
    <ac:structured-macro ac:name="info">
        <ac:rich-text-body>
            <p><strong>Total Unique Macros:</strong> {total_macros}</p>
            <p><strong>Total Macro Instances:</strong> {total_usage}</p>
            <p><strong>Categories Found:</strong> {len(categorized)}</p>
        </ac:rich-text-body>
    </ac:structured-macro>
    
    <h2>Summary by Category</h2>
    <table>
        <thead>
            <tr>
                <th>Category</th>
                <th>Unique Macros</th>
                <th>Total Usage</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for category in sorted(categorized.keys()):
        macros = categorized[category]
        unique_count = len(macros)
        total_count = sum(m["count"] for m in macros)
        
        html += f"""
            <tr>
                <td>{category}</td>
                <td>{unique_count}</td>
                <td>{total_count}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    
    <hr />
    """
    
    # Detailed tables for each category
    for category in sorted(categorized.keys()):
        macros = categorized[category]
        
        if not macros:
            continue
        
        category_total = sum(m["count"] for m in macros)
        
        html += f"""
        <h2>{category}</h2>
        <p><em>Total macros: {len(macros)} | Total usage: {category_total}</em></p>
        
        <table>
            <thead>
                <tr>
                    <th>S/No</th>
                    <th>Macro Name</th>
                    <th>Usage Count</th>
                    <th>Spaces Used In</th>
                    <th>Example Pages</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for idx, macro in enumerate(macros, 1):
            example_pages = ", ".join(macro["pages"][:3])
            if len(macro["pages"]) > 3:
                example_pages += f" (+{len(macro['pages']) - 3} more)"
            
            html += f"""
                <tr>
                    <td>{idx}</td>
                    <td><code>{macro['name']}</code></td>
                    <td>{macro['count']}</td>
                    <td>{macro['spaces']}</td>
                    <td>{example_pages}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        <br />
        """
    
    # Add footer
    html += """
    <hr />
    <ac:structured-macro ac:name="note">
        <ac:rich-text-body>
            <p><strong>Notes:</strong></p>
            <ul>
                <li>Third-Party / Custom Macros are from installed apps or custom plugins</li>
                <li>Usage Count = Total number of times macro appears across all pages</li>
                <li>Review Third-Party macros for cloud migration compatibility</li>
            </ul>
        </ac:rich-text-body>
    </ac:structured-macro>
    """
    
    return html

def create_confluence_page(space_key, title, content):
    """Create a new page in Confluence"""
    url = f"{BASE_URL}/rest/api/content"
    
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    resp = requests.post(url, json=payload, auth=auth, headers=headers)
    
    return resp

def save_to_csv(categorized, macro_usage):
    """Save all macro data to CSV"""
    
    rows = []
    
    for category in sorted(categorized.keys()):
        for macro in categorized[category]:
            rows.append({
                "Category": category,
                "Macro Name": macro["name"],
                "Usage Count": macro["count"],
                "Spaces Used In": macro["spaces"],
                "Example Pages": "; ".join(macro["pages"][:5])
            })
    
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Category", "Macro Name", "Usage Count", "Spaces Used In", "Example Pages"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ CSV exported as: {OUTPUT_FILE}")

def main():
    # Step 1: Collect all macro data
    macro_usage, all_instances = collect_macro_data()
    
    if not macro_usage:
        print("No macros found. Exiting.")
        return
    
    # Step 2: Categorize macros
    print("\nCategorizing macros...")
    categorized = build_comprehensive_report(macro_usage)
    
    # Step 3: Display summary
    print("\n" + "=" * 70)
    print("MACRO SUMMARY BY CATEGORY")
    print("=" * 70)
    print(f"{'Category':<35} {'Unique':<10} {'Total Usage'}")
    print("-" * 70)
    
    for category in sorted(categorized.keys()):
        macros = categorized[category]
        unique_count = len(macros)
        total_count = sum(m["count"] for m in macros)
        print(f"{category:<35} {unique_count:<10} {total_count}")
    
    print("-" * 70)
    print(f"{'TOTAL':<35} {len(macro_usage):<10} {sum(m['count'] for m in macro_usage.values())}")
    print("=" * 70)
    
    # Step 4: Save to CSV
    save_to_csv(categorized, macro_usage)
    
    # Step 5: Create Confluence page
    print("\nCreating Confluence page...")
    page_html = build_confluence_page_html(categorized, macro_usage)
    
    resp = create_confluence_page(TARGET_SPACE, PAGE_TITLE, page_html)
    
    if resp.status_code == 200:
        page_data = resp.json()
        page_id = page_data.get("id")
        page_url = f"{BASE_URL}/pages/viewpage.action?pageId={page_id}"
        
        print(f"\n✓ Page created successfully!")
        print(f"✓ Page URL: {page_url}")
    else:
        print(f"\n✗ Failed to create page: {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    main()