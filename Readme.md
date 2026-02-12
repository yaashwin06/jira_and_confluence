# Jira Project + Confluence Pages Generator

A Python automation tool for creating comprehensive Jira projects with custom fields, epics, stories, and associated Confluence documentation spaces. Designed for Atlassian Cloud instances, this tool streamlines project initialization and documentation setup.

## Overview

This script automates the creation of:
- **Jira Project**: Company-managed software project with custom template
- **Custom Fields**: 4 custom fields (% Complete, Target Start/End Dates, Owning)
- **Project Structure**: 5 epics with 50+ pre-configured stories
- **Confluence Space**: Documentation space with 30 pre-configured pages
- **Field Integration**: Automatic addition of custom fields to project screens

## Features

### Jira Automation
- ✅ Project creation with template selection (Kanban, Scrum, Bug Tracking)
- ✅ Custom field creation and context management
- ✅ Automated screen configuration
- ✅ Hierarchical epic and story structure
- ✅ Smart project key suggestion
- ✅ Duplicate project detection

### Confluence Automation
- ✅ Space creation with custom key
- ✅ 30 pre-configured documentation pages
- ✅ Hierarchical page structure (parent-child relationships)
- ✅ Template support for specialized page content
- ✅ Fallback content generation

### Project Structure

The script creates **5 epics** with **50+ stories** organized as follows:

1. **ASSESSMENT & PLANNING** (37 stories)
   - Onboarding and access setup
   - Environment assessment
   - License configuration
   - Migration planning
   - Add-on assessment

2. **TEST MIGRATION** (9 stories)
   - User migration
   - Test execution
   - Integrity testing
   - Add-on remediation

3. **USER ACCEPTANCE TESTING** (5 stories)
   - UAT coordination
   - Issue resolution
   - Go/No-Go decision

4. **PRODUCTION MIGRATION** (2 stories)
   - Runbook finalization
   - Timeline management

5. **POST MIGRATION SUPPORT** (1+ story)
   - Ongoing support tasks

### Custom Fields

Four custom fields are automatically created and added to project screens:

| Field Name | Type | Purpose |
|------------|------|---------|
| **% Complete** | Text Field | Track task completion percentage |
| **Target Start Date** | Date Picker | Set planned start dates |
| **Target End Date** | Date Picker | Set planned end dates |
| **Owning** | User Picker | Assign task ownership |

### Confluence Pages

30 documentation pages are created, including:

- Project Overview & Team
- Access Requirements
- Environment Details
- Project Trackers & Roadmaps
- Jira & Confluence Assessments
- Add-ons & Integration Inventory
- User Assessments
- Custom Fields & Workflows
- Migration Runbooks (Test & Production)
- Test Plans & Statistics

## Prerequisites

### System Requirements
- Python 3.7 or higher
- Internet connection
- Atlassian Cloud instance (Jira + Confluence)

### Python Dependencies
```bash
pip install requests
```

### Atlassian Requirements
- Atlassian Cloud account
- API token with appropriate permissions
- Jira Software access
- Confluence access (optional, for page creation)

## Installation

1. **Clone or download the script:**
```bash
git clone <repository-url>
cd jira-confluence-generator
```

2. **Install dependencies:**
```bash
pip install requests
```

3. **Optional: Add template file**
   - Place `confluence_templates.py` in the same directory for enhanced page content
   - Script works with fallback content if templates are unavailable

## Configuration

### API Token Setup

1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Give it a descriptive name (e.g., "Jira Generator Script")
4. Copy the token (you won't see it again!)
5. Store it securely

### Permissions Required

Your Atlassian account needs:
- **Jira**: 
  - Create projects
  - Administer projects
  - Create custom fields
  - Browse projects
- **Confluence**:
  - Create spaces
  - Create pages
  - Edit space permissions

## Usage

### Basic Workflow

1. **Run the script:**
```bash
python jira_project_generator.py
```

2. **Provide credentials:**
   - Atlassian URL (e.g., `https://yourcompany.atlassian.net`)
   - Email address
   - API token (input is hidden)

3. **Configure project:**
   - Project name
   - Project key (auto-suggested)
   - Template selection (Kanban/Scrum/Bug Tracking)

4. **Configure Confluence (optional):**
   - Space name
   - Space key (auto-suggested)
   - Confirm or skip space creation

5. **Review and confirm:**
   - Review summary of what will be created
   - Type `y` to proceed

### Example Session

```
JIRA PROJECT + CONFLUENCE PAGES GENERATOR
(Separate - No Linking)

CREDENTIALS
Atlassian URL: https://mycompany.atlassian.net
Email: admin@mycompany.com
API Token: ****************

TESTING CONNECTIONS
✅ Jira: John Admin
✅ Confluence: Connected

JIRA PROJECT
Project Name: Digital Transformation 2025
Project Key (suggested: DT): DT2025

TEMPLATE
1. Kanban
2. Scrum
3. Bug Tracking
Choose (1-3) [2]: 2

CONFLUENCE SPACE
Create Confluence space with 30 doc pages? (Y/n): y
Space Name [Digital Transformation 2025 Docs]: 
Space Key [DT2025]: DTDOCS

SUMMARY
Jira:  Digital Transformation 2025 (DT2025) - Scrum
Epics: 5 | Stories: 54
Confluence: Digital Transformation 2025 Docs (DTDOCS) - 30 pages
  No auto-linking between Jira and Confluence

Proceed? (y/N): y
```

## Advanced Features

### Template System

If `confluence_templates.py` is present, the script uses specialized templates for each page type:

```python
from confluence_templates import get_template_by_name, list_available_templates

# The script automatically loads templates when available
# Falls back to default content if templates are missing
```

### Custom Field Context Management

The script intelligently handles field contexts:
- Detects global contexts
- Adds projects to existing contexts
- Creates new contexts when needed

### Screen Integration

Custom fields are automatically added to:
- All project-specific screens
- Screens linked via Issue Type Screen Schemes
- Both default and custom screen schemes

### Error Handling

Robust error handling includes:
- Connection validation before operations
- Duplicate detection (projects, spaces, fields)
- Retry logic for transient failures
- Graceful degradation (continues on non-critical errors)
- Detailed error messages with truncated API responses

## Project Structure Details

### Epic Categories

Each epic represents a major phase:
- **ASSESSMENT & PLANNING**: Pre-migration preparation
- **TEST MIGRATION**: Trial runs and testing
- **USER ACCEPTANCE TESTING**: Validation phase
- **PRODUCTION MIGRATION**: Final cutover
- **POST MIGRATION SUPPORT**: Ongoing maintenance

### Story Naming Convention

Stories use descriptive names that indicate:
- Action required (e.g., "Execute", "Discuss", "Review")
- Target system or component
- Purpose or outcome

### Custom Field Defaults

Stories are created with default values:
- **% Complete**: 0
- **Target Start Date**: Today
- **Target End Date**: 7 days from today
- **Owning**: Project lead

## Output

### Success Indicators

The script provides real-time feedback:
```
✅ Project 'Digital Transformation 2025' created → DT2025
✅ Found '% Complete' → customfield_10037
✅ Created 'Target Start Date' → customfield_10038
✅ [1/5] Epic: ASSESSMENT & PLANNING → DT2025-1
  ✅ [1/54] ✓ DT2025-2: Onboarding and Access
  ✅ [2/54] ✓ DT2025-3: Introductory Call
```

### Final Summary

Upon completion, you'll see:
```
COMPLETE!
==========================================================
Jira:       https://mycompany.atlassian.net/projects/DT2025
Confluence: https://mycompany.atlassian.net/wiki/spaces/DTDOCS

Pages (30):
  • Project Overview
  • Project Team
  • Access Requirement
  [...]

🏷️ Fields:
  • % Complete → customfield_10037
  • Target Start Date → customfield_10038
  • Target End Date → customfield_10039
  • Owning → customfield_10040

Jira ↔ Confluence NOT linked. Link manually as needed.
```

## Troubleshooting

### Common Issues

**"Failed to create project"**
- Verify API token has project creation permissions
- Check if project key already exists
- Ensure you have Jira Software license

**"Field creation failed"**
- API token needs field administration permissions
- Field name might conflict with existing field
- Check Jira instance field limits

**"Confluence space creation failed"**
- Verify Confluence is included in your license
- Check space key doesn't already exist
- Ensure space key follows naming rules (alphanumeric, max 10 chars)

**"Cannot add fields to screens"**
- Fields may already exist on screens (not an error)
- Screen access permissions required
- Wait 10-15 seconds after field creation before retry

### Rate Limiting

The script includes built-in delays:
- 10 seconds after project creation (initialization time)
- 3 seconds before screen updates
- 0.15-0.5 seconds between API calls
- Automatic retry logic for failed field additions

### Debug Mode

For detailed error information:
```python
# The script automatically prints stack traces on unhandled exceptions
# Check console output for full error details
```

## Customization

### Modifying Epic Structure

Edit the `EPICS` dictionary in the script:

```python
EPICS = {
    "YOUR EPIC NAME": [
        "Story 1",
        "Story 2",
        # Add more stories...
    ],
    # Add more epics...
}
```

### Changing Confluence Pages

Modify the `CONFLUENCE_PAGES` list:

```python
CONFLUENCE_PAGES = [
    "Your Page 1",
    "Your Page 2",
    # Add more pages...
]
```

### Custom Field Configuration

Update `EXPECTED_FIELDS` to add new fields:

```python
EXPECTED_FIELDS = {
    "your_field_key": {
        "name": "Display Name",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
        "description": "Field description"
    }
}
```

## Security Notes

- **API tokens are never logged or stored**
- Input is hidden during token entry
- Tokens are encoded in memory only
- Use environment variables for automated deployments
- Regularly rotate API tokens
- Limit token permissions to minimum required

## Limitations

- **Jira Cloud only** (not compatible with Jira Server/Data Center)
- **Single project at a time** (no batch creation)
- **No rollback feature** (manual cleanup required if cancelled)
- **No automatic linking** between Jira and Confluence
- **Template dependency** optional (works without templates)
- **English only** (no internationalization support)

## Performance

Typical execution time:
- Project creation: ~15 seconds
- Custom fields: ~5-10 seconds
- Screen updates: ~10-20 seconds
- Epics + Stories (54 items): ~2-3 minutes
- Confluence pages (30 items): ~30-45 seconds

**Total: 4-6 minutes for complete setup**

## Best Practices

1. **Test in sandbox environment first**
2. **Use descriptive project and space names**
3. **Keep project keys short and memorable** (2-10 characters)
4. **Document any customizations**
5. **Backup existing data before large operations**
6. **Review created structure before team access**
7. **Customize stories to match your workflow**
8. **Archive unused epics rather than deleting**

## Future Enhancements

Potential improvements:
- [ ] Bulk project creation from CSV
- [ ] Custom template system
- [ ] Automatic Jira-Confluence linking
- [ ] Dashboard creation
- [ ] Automation rule setup
- [ ] User group management
- [ ] Project archival functionality
- [ ] Export/import configuration
- [ ] Web UI interface
- [ ] Docker containerization

## Contributing

To contribute improvements:
1. Test changes in isolated environment
2. Document new features in README
3. Maintain backward compatibility
4. Follow existing code style
5. Add error handling for new features

## License

[Add your license here]

## Support

For issues or questions:
- Check [Atlassian REST API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- Review [Confluence REST API docs](https://developer.atlassian.com/cloud/confluence/rest/v1/)
- Open an issue in this repository

## Acknowledgments

- Built for Atlassian Cloud Platform
- Uses Atlassian REST API v3 (Jira) and v1 (Confluence)
- Designed for Atlassian Cloud migration projects

---

**Version**: 1.0  
**Last Updated**: 2025  
**Author**: [Your Name/Organization]  
**Atlassian Platform**: Cloud
