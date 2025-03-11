from atlassian import Confluence
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# Confluence credentials and URL
CONFLUENCE_URL = 'https://your-domain.atlassian.net/wiki'
USERNAME = 'your-email@example.com'
API_TOKEN = 'your-api-token'
SPACE_KEY = 'your-space-key'
PAGE_TITLE = 'Automated Task Usage Report'

# Connect to Confluence
confluence = Confluence(
    url=CONFLUENCE_URL,
    username=USERNAME,
    password=API_TOKEN
)

# Load Excel data
excel_file = 'path_to_your_excel_file.xlsx'
df = pd.read_excel(excel_file)

# Generate charts
def create_chart(df, chart_title):
    plt.figure(figsize=(10, 6))
    for column in df.columns[1:]:
        plt.bar(df['Date'], df[column], label=column)
    plt.xlabel('Date')
    plt.ylabel('Values')
    plt.title(chart_title)
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

# Create charts
img_base64 = create_chart(df, 'Task Usage Report')

# Prepare content for Confluence
content = f"""
<h1>Overall Monthly Task Usage Report</h1>
<p>Here is the detailed report based on the uploaded data:</p>
<h2>Data Table</h2>
{df.to_html(index=False)}
<h2>Charts</h2>
<p><img src="data:image/png;base64,{img_base64}" alt="Task Usage Chart"/></p>
"""

# Create or update Confluence page
existing_page = confluence.get_page_by_title(SPACE_KEY, PAGE_TITLE)

if existing_page:
    confluence.update_page(
        page_id=existing_page['id'],
        title=PAGE_TITLE,
        body=content
    )
    print(f'Page "{PAGE_TITLE}" updated successfully.')
else:
    confluence.create_page(
        space=SPACE_KEY,
        title=PAGE_TITLE,
        body=content
    )
    print(f'Page "{PAGE_TITLE}" created successfully.')


    Call Flow Explanation
Initiation:

The process starts with a user initiating a decommission request from the User Portal.
A Master Change Request (CR) is created as part of this initiation.
Workflow Creation:

The system generates a workflow with an initial state.
This workflow moves through different categories such as Admin UI, Category, Subcategory, Database, SF endpoint, and other systems.
User Action & Validation (Week 1):

The user takes action (usually on Thursday/Friday).
The system performs Validation.
If successful, it proceeds to further steps; otherwise, the workflow is reset.
Raising CRs & Approval Checks:

Change Requests (CRs) are raised for hosts.
The system continuously checks if the Master Record (MR) is approved or if the status has changed.
Database Updates & Workflow Reset:

If validation passes, the workflow updates the database.
If any step fails, the system updates the database with failure and resets the workflow.
Final Verification:

The system verifies whether the workflow items have moved to validation.
If confirmed, no further action is required.
State Changes in the Workflow
Previous State	Action/Event	New State
Initial Workflow Created	User submits decommission request	Workflow Initialized
Workflow Initialized	User takes action (Thursday/Friday)	Validation
Validation	Passed	Ready to Validate
Ready to Validate	User clicks on action	CRs Raised for Hosts
CRs Raised for Hosts	Master Record (MR) approved/status changed	Reset workflow status
Reset Workflow Status	Verify workflow items if moved to validation	Updated Status in DB
Validation	Failed	Reset Workflow
Any Step Failure	System updates database with failure	Reset Workflow State
Updated Status in DB	No further action needed	Workflow Completed

