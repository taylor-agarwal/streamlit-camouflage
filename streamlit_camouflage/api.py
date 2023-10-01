from fastapi import FastAPI, HTTPException, UploadFile, Response
from streamlit_camouflage.objects import Clothing, Image
from typing import List
from colorsys import rgb_to_hsv
import logging
import uvicorn
from pydantic import BaseModel

from streamlit_camouflage.fuzzy_classifier import GetValidMatches, GetColorDesc

app = FastAPI()

logger = logging.getLogger(__name__)

logger.info("test")

class Color(BaseModel):
    r: float
    g: float
    b: float
    pct: float
    name: str

class Colors(BaseModel):
    colors: List[Color]

class Outfit(BaseModel):
    outfit: List[Colors]

class Matches(BaseModel):
    matches: List[str]

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/rembg", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def rembg(file: UploadFile):
    try:
        contents = file.file
        image = Image(contents)
        image_rembg = image.rembg()
        response = Response(content = image_rembg, media_type="image/png")
        contents.close()
        return response
    except Exception as e:
        file.file.close()
        logger.error(e)
        raise HTTPException(status_code=500, detail="Unable to extract colors")


@app.post("/colors")
async def colors(file: UploadFile):
    try:
        contents = file.file
        clothing = Clothing(contents)
        clothing.extract_colors()
        colors = clothing.colors
        color_names = clothing.get_color_names()
        response = {
            "colors": [
                {'r': rgb[0], 'g': rgb[1], 'b': rgb[2], 'pct': pct, 'name': color_names[i]}
                for i, (rgb, pct) in enumerate(colors.items())
            ]
        }
        contents.close()
        return response
    except Exception as e:
        file.file.close()
        logger.error(e)
        raise HTTPException(status_code=500, detail="Unable to extract colors")
        

@app.post("/matches")
async def matches(outfit: Outfit):
    logger.info(outfit)
    try:
        primary_rgbs = [c.colors[0] for c in outfit.outfit]
        logger.info(primary_rgbs)
        primary_rgb_norms = [(rgb.r/255.0, rgb.g/255.0, rgb.b/255.0) for rgb in primary_rgbs]
        logger.info(primary_rgb_norms)
        primary_hsv_norms = [rgb_to_hsv(r, g, b) for r, g, b in primary_rgb_norms]
        logger.info(primary_hsv_norms)
        primary_hsvs = [(h*360.0, s*100.0, v*100.0) for h, s, v in primary_hsv_norms]
        logger.info(primary_hsvs)

        outfit_color_descs = [GetColorDesc(hsv) for hsv in primary_hsvs]
        logger.info(outfit_color_descs)

        matches = GetValidMatches(outfit_color_descs)
        logger.info(matches)
        return matches
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Unable to find matches")

    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="localhost", port=80)