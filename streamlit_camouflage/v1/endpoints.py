import logging

from fastapi import APIRouter, HTTPException, UploadFile, Response
from colorsys import rgb_to_hsv

from streamlit_camouflage.v1.objects import Clothing, Image
from streamlit_camouflage.v1.api_spec import Colors, Matches, Outfit
from streamlit_camouflage.v1.fuzzy_classifier import GetValidMatches, GetColorDesc

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/rembg", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def rembg(file: UploadFile):
    try:
        # Get image contents
        contents = file.file

        # Put the contents in an Image object
        image = Image(contents)

        # Remove the background
        image_rembg = image.rembg()

        # Build the response
        response = Response(content=image_rembg, media_type="image/png")
        contents.close()
        return response
    except Exception as e:
        file.file.close()
        logger.error(e)
        raise HTTPException(status_code=500, detail="Unable to extract colors")


@router.post("/colors", response_model=Colors)
async def colors(file: UploadFile):
    try:
        # Get image contents
        contents = file.file

        # Put the contents to a clothing object
        clothing = Clothing(contents)

        # Get color information
        clothing.extract_colors()
        colors = clothing.colors
        color_names = clothing.get_color_names()
        color_dicts = [
            {'r': rgb[0], 'g': rgb[1], 'b': rgb[2], 'pct': pct, 'name': color_names[i]}
            for i, (rgb, pct) in enumerate(colors.items())
        ]

        # Build the response
        response = Colors(colors=color_dicts)
        return response
    except Exception as e:
        file.file.close()
        logger.error(e)
        raise HTTPException(status_code=500, detail="Unable to extract colors")
        

@router.post("/matches", response_model=Matches)
async def matches(outfit: Outfit):
    try:
        # Get the HSV values for the primary colors
        primary_rgbs = [c.colors[0] for c in outfit.outfit]
        primary_rgb_norms = [(rgb.r/255.0, rgb.g/255.0, rgb.b/255.0) for rgb in primary_rgbs]
        primary_hsv_norms = [rgb_to_hsv(r, g, b) for r, g, b in primary_rgb_norms]
        primary_hsvs = [(h*360.0, s*100.0, v*100.0) for h, s, v in primary_hsv_norms]

        # Get a description of the color, in tuples of (TONE, TEMP)
        outfit_color_descs = [GetColorDesc(hsv) for hsv in primary_hsvs]

        # Get matches for the given colors
        matches = GetValidMatches(outfit_color_descs)

        # Build the response
        response = Matches(matches=matches)
        return response
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Unable to find matches")
