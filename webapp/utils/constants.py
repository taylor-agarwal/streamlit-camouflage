import os

from dotenv import load_dotenv

if os.environ.get("ENVIRONMENT") is None:
    load_dotenv()

ENVIRONMENT = os.environ.get("ENVIRONMENT")

DIRECTORY_PATH = os.path.dirname(os.path.dirname(__file__))

# Declare API endpoints
if ENVIRONMENT == "prod":
    API_ENDPOINT = os.environ.get("API_ENDPOINT")
else:
    API_ENDPOINT = "http://localhost:8080/v1"
API_ROUTES = {
    "colors": API_ENDPOINT + "/colors",
    "matches": API_ENDPOINT + "/matches",
    "rembg": API_ENDPOINT + "/rembg"
}

# Write outfit descriptions
OUTFIT_DESCRIPTIONS = {
    "Basic": """
- No more than one bright color
- No high contrast between colors (bright warm + dark cool)
- Any number of neutral colors
""",
    "Neutral": """
- Only neutral colors
""",
    "Analogous": """
- All colors must be within the same temp.
- Any number of neutral colors
""",
    "Contrast": """
- At least one warm color
- Both dark and bright colors present
""",
    "Summer": """
- At least two warm colors
- At least one bright color
- At most one dark color
""",
    "Winter": """
- At least one dark color
- No bright colors
"""
}

HIDE_FOOTER_STYLE = """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;} 
    #MainMenu {visibility: hidden;} 
    .block-container {
                    padding-top: 1rem;
                    padding-bottom: 1rem;
                }
    </style>  
"""

# From https://github.com/streamlit/streamlit/issues/5003#issuecomment-1276611218
COLUMN_STYLE = '''<style>
[data-testid="column"] {
    width: calc(25% - 1rem) !important;
    flex: 1 1 calc(25% - 1rem) !important;
    min-width: calc(25% - 1rem) !important;
}
</style>'''

TITLE_HTML = """
<center>
<img src="app/static/logo.png" width=50% /><br>
<em>Helping the Colorblind Blend In</em>
</center>
"""

CLOTHING_NUMBER_CHOICES = [2, 3, 4]

STATEMENT_OUTFITS = ["Contrast", "Summer", "Winter"]