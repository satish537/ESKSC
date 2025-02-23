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
