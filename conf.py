import datetime
from atlassian import Confluence

# Confluence configuration
CONFLUENCE_URL = 'https://your-confluence-instance.com'
USERNAME = 'your_username'
API_TOKEN = 'your_api_token'
SPACE_KEY = 'YOUR_SPACE_KEY'

# Initialize Confluence
confluence = Confluence(url=CONFLUENCE_URL, username=USERNAME, password=API_TOKEN)

# Get current month and year
current_month = datetime.datetime.now().strftime('%B %Y')  # e.g., 'June 2024'

# Page title and content
child_page_title = "Your New Page Title"
child_page_content = """
<h1>Welcome to the New Page</h1>
<p>This is the content of the page created or updated under the monthly parent page.</p>
"""

# Function to check if the monthly parent page exists
def get_or_create_parent_page(space_key, parent_title):
    """Find or create the parent page for the current month."""
    # Search for the page
    parent_page = confluence.get_page_by_title(space_key, parent_title)
    if parent_page:
        print(f"Parent page '{parent_title}' already exists.")
        return parent_page['id']
    else:
        print(f"Creating new parent page '{parent_title}'.")
        # Create the parent page
        parent_page_id = confluence.create_page(
            space=space_key,
            title=parent_title,
            body=f"<h1>Monthly Pages for {parent_title}</h1>",
            parent_id=None  # No parent, top-level
        )['id']
        return parent_page_id

# Function to create or update a child page
def create_or_update_child_page(space_key, parent_id, title, content):
    """Create or update a child page under a specific parent."""
    existing_page = confluence.get_page_by_title(space_key, title)
    if existing_page:
        print(f"Updating existing page '{title}'.")
        confluence.update_page(
            page_id=existing_page['id'],
            title=title,
            body=content,
            parent_id=parent_id
        )
    else:
        print(f"Creating new page '{title}'.")
        confluence.create_page(
            space=space_key,
            title=title,
            body=content,
            parent_id=parent_id
        )

if __name__ == "__main__":
    # Step 1: Get or create the parent page for the current month
    parent_page_id = get_or_create_parent_page(SPACE_KEY, current_month)

    # Step 2: Create or update the child page under the parent page
    create_or_update_child_page(SPACE_KEY, parent_page_id, child_page_title, child_page_content)

    print("Page creation/updation completed successfully.")
