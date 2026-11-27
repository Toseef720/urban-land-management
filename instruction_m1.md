# Git commit attribution

- Keep commits authored under the human developer's configured Git identity.
- Do not add a `Co-authored-by: Copilot` trailer or otherwise credit Copilot as an author or co-author unless the user explicitly asks for it.
- Before pushing, verify the commit message and author metadata so Copilot is not listed as a contributor by mistake.

# Project Handoff: Conflict Management Module
## Urban Land Record Management System

You are helping develop the **Conflict Management module** of an existing Django-based Urban Land Record Management System.

Your responsibility is to develop this module independently while ensuring it integrates properly with the existing project. Before writing code, understand the existing architecture and inspect the relevant files.

## 1. Project overview

The system collects property-related information from three departments:

1. Land Department
2. Property Tax Department
3. Utility Department

The objective is to combine their records into a common system, identify inconsistencies and help users resolve conflicting information.

The project uses:
- Python
- Django
- SQLite (current development database)
- HTML
- CSS
- Django Templates

Authentication is a **dummy login system**. Do not implement real authentication, registration, permissions management or a new user-management system.

## 2. Existing modules

The following modules have already been developed or implemented:

1. Dashboard
2. Dummy Authentication
3. Property Management
4. Dataset Management
5. Data Standardization
6. Data Harmonization

The GIS / Property Map module has been dropped from the project roadmap.

The shared `base.html` template already contains a navigation bar with links to the existing modules. Every new page should extend this template.

## 3. Existing database architecture

### Master Property model

Located in `properties/models.py`.

The existing model contains:

- `parcel_id`
- `property_name`
- `owner_name`
- `address`
- `area`
- `description`
- `photo`
- `created_at`

The master Property table is the central reference for property information.

**Important:** Do not modify or delete existing master property records.

### Dataset Management

Located in the `datasets` app.

The system imports records from three departments and stores them using:

- `DatasetImport`
- `ImportedRecord`

Each imported record contains:
- Source department
- Original imported data
- Normalized data
- Acceptance status
- Validation errors

### Data Standardization

Located in the `standardization` app.

The `StandardizationResult` model contains:

- `source_record` — OneToOneField to ImportedRecord
- `standardized_data` — JSONField
- `is_valid` — BooleanField
- `errors`
- `processed_at`

The standardized records follow a common structure.

Example:

```python
{
    'property_id': 'P-001',
    'person_name': 'Rahul Sharma',
    'name_role': 'owner',
    'address': 'Example Address',
}
```

Additional fields depend on the department.

### Data Harmonization

Located in the `harmonization` app.

The `HarmonizedRecord` model connects a standardized record to a master property.

It contains:

- `standardization_result`
- `property`
- `match_status`
- `match_method`
- `processed_at`

Matching statuses include:
- matched
- unmatched
- invalid

Manual matching has already been implemented.

## 4. Objective of Conflict Management

Build a module that identifies conflicting information between departmental records belonging to the same master property.

For example:

| Department | Property ID | Owner Name |
|---|---|---|
| Land | P-001 | Rahul Sharma |
| Tax | P-001 | Rahul Kumar |
| Utility | P-001 | Rahul Sharma |

The system should identify that the owner names differ for property P-001.

Another example could be:

| Department | Property ID | Address |
|---|---|---|
| Tax | P-002 | Street A |
| Utility | P-002 | Street B |

The system should detect the address inconsistency.

## 5. Required functionality

### A. Conflict Detection

- Retrieve records that have successfully been standardized and harmonized.
- Group records by their linked master property.
- Compare common fields between departments.
- Identify differences in fields such as:
  - Owner/person name
  - Address
  - Property area, wherever available
- Avoid treating missing or blank values as conflicts.
- Avoid comparing unrelated fields, such as a utility meter ID against a tax property number.
- Identify the departments reporting each conflicting value.

### B. Conflict Dashboard

Create a dashboard displaying:

- Total conflicts
- Pending conflicts
- Resolved conflicts
- Conflicts grouped by field
- A table listing detected conflicts

Each conflict should show:
- Conflict ID
- Master Property ID
- Conflicting field
- Department values
- Conflict status
- Action to view details

### C. Conflict Details

Create a detail page showing the conflicting information side by side.

For example:

| Field | Land | Tax | Utility |
|---|---|---|---|
| Owner Name | Rahul Sharma | Rahul Kumar | Rahul Sharma |
| Address | Not available | Street A | Street A |

The page should make it easy to understand what information differs and where it originated.

### D. Manual Conflict Resolution

Allow the user to:

- Review the conflicting values.
- Select the correct value.
- Enter a corrected value if necessary.
- Provide a resolution note.
- Confirm the resolution.

Store the resolution information in the database.

**Important:** Resolving a conflict must not automatically overwrite the original imported records or master Property data. Keep the original source information intact.

### E. Resolution History

Maintain:
- Conflicting field
- Original departmental values
- Selected or corrected value
- Resolution note
- Resolution date
- Resolution status

## 6. Suggested database design

First inspect the existing models and then propose suitable models.

A possible starting design is:

**Conflict**
- Master property (ForeignKey to Property)
- Field name
- Conflict description
- Status (pending/resolved)
- Detected date

**ConflictValue**
- Conflict (ForeignKey to Conflict)
- Source record (ForeignKey to StandardizationResult)
- Department
- Field value

**ConflictResolution**
- Conflict (OneToOneField to Conflict)
- Resolved value
- Resolution note
- Resolved date

You may improve this design if necessary, but explain the reasons before changing it.

## 7. Important development rules

1. Inspect the existing project before coding.
2. Do not recreate existing modules.
3. Do not modify the existing Property, Dataset, Standardization or Harmonization logic without a clear reason and approval.
4. Do not delete or overwrite existing records.
5. Reuse existing models and relationships wherever possible.
6. Follow the existing Django app structure.
7. Use Django templates and the existing `base.html`.
8. Create separate CSS for Conflict Management where appropriate.
9. Follow the existing dummy login approach.
10. Do not introduce unnecessary external packages.
11. Do not implement GIS or mapping functionality.

## 8. Development workflow

Work step by step.

Follow this order:

1. Inspect the project structure and existing models.
2. Understand how HarmonizedRecord connects to Property and StandardizationResult.
3. Propose the Conflict Management database models.
4. Wait for confirmation before implementing the models.
5. Create and test migrations.
6. Implement conflict detection services.
7. Test detection using existing project data.
8. Create the Conflict Management dashboard.
9. Create the conflict detail and comparison page.
10. Implement manual conflict resolution.
11. Implement resolution history.
12. Test the complete workflow.
13. Run Django system checks.
14. Prepare the module for GitHub integration.

For every step:
- Explain what is being developed.
- Provide the exact file path.
- Provide complete code when necessary.
- Give commands one step at a time.
- Wait for the developer to confirm the result before moving forward.

## 9. Final objective

The finished module should allow the Urban Land Record Management System to identify inconsistent property information across departments, present those differences clearly, and allow a user to review and resolve them without destroying the original departmental data.

The module must integrate cleanly with the existing Django project and be suitable for an academic project demonstration.

**Start by inspecting the existing project structure and the models in `properties`, `datasets`, `standardization`, and `harmonization`. Do not start coding immediately.**