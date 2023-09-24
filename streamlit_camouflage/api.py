from fastapi import FastAPI, HTTPException, UploadFile
from streamlit_camouflage.objects import Clothing
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

class Colors(BaseModel):
    colors: List[Color]

class Outfit(BaseModel):
    outfit: List[Colors]

class Matches(BaseModel):
    matches: List[str]

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/colors")
async def colors(file: UploadFile) -> Colors:
    try:
        contents = file.file
        clothing = Clothing(contents)
        clothing.extract_colors()
        colors = clothing.colors
        colors_json = {
            "colors": [
                {'r': rgb[0], 'g': rgb[1], 'b': rgb[2], 'pct': pct}
                for rgb, pct in colors.items()
            ]
        }
        file.file.close()
        return colors_json
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Unable to extract colors")
    finally:
        file.file.close()

@app.post("/matches")
async def matches(outfit: Outfit) -> Matches:
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