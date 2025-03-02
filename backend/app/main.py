from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import logging
from app.processor.image_processor import ImageProcessor
from app.processor.depth_estimator import DepthEstimator
from app.processor.mesh_generator import MeshGenerator
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a test endpoint
@app.get("/")
async def root():
    return {"message": "Backend is running"}

# Make sure temp directory exists
os.makedirs("temp", exist_ok=True)

# Initialize processors
image_processor = ImageProcessor()
depth_estimator = DepthEstimator()
mesh_generator = MeshGenerator()

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        logger.info(f"Processing file: {file.filename}")
        
        # Save uploaded image
        temp_path = os.path.join("temp", file.filename)
        logger.info(f"Saving to: {temp_path}")
        
        try:
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                if not content:
                    raise HTTPException(status_code=400, detail="Empty file")
                buffer.write(content)
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
        
        logger.info("File saved successfully")
        
        # Process image
        try:
            logger.info("Processing image with OpenCV")
            contours, colors = image_processor.process(temp_path)
            if not contours:
                raise HTTPException(status_code=400, detail="No contours found in image")
        except Exception as e:
            logger.error(f"Error in image processing: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error in image processing: {str(e)}")
        
        try:
            logger.info("Generating depth map")
            depth_map = depth_estimator.predict(temp_path)
            if depth_map is None:
                raise HTTPException(status_code=500, detail="Failed to generate depth map")
        except Exception as e:
            logger.error(f"Error in depth estimation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error in depth estimation: {str(e)}")
        
        try:
            logger.info("Generating 3D mesh")
            mesh_path = mesh_generator.generate(contours, depth_map, colors)
            if not os.path.exists(mesh_path):
                raise HTTPException(status_code=500, detail="Failed to generate 3D model")
        except Exception as e:
            logger.error(f"Error in mesh generation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error in mesh generation: {str(e)}")
        
        logger.info(f"Returning mesh file: {mesh_path}")
        try:
            return FileResponse(
                mesh_path, 
                media_type="model/gltf-binary",
                headers={
                    "Access-Control-Allow-Origin": "https://signage-3d-frontend.onrender.com"
                }
            )
        except Exception as e:
            logger.error(f"Error sending file response: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error sending file response: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e)) 