# Declare API endpoints
API_ENDPOINT = "http://localhost:80/v1"
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
    footer {visibility: hidden;} 
    #MainMenu {visibility: hidden;} 
    </style>  
"""

TITLE_HTML = """
<center>
<h1>Welcome to Camouflage!</h1>
<h5><em>Helping the Colorblind Blend In</em></h5>
<text>If you do not see the logo above, please refresh the page</text>
</center>
"""

CLOTHING_NUMBER_CHOICES = [0, 1, 2, 3, 4]