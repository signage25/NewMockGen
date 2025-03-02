import cv2
import numpy as np

class ImageProcessor:
    def process(self, image_path: str):
        # Load image
        image = cv2.imread(image_path)
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection using Canny
        edges = cv2.Canny(gray, 100, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Extract colors from original image
        colors = self._extract_colors(image, contours)
        
        return contours, colors
    
    def _extract_colors(self, image, contours):
        # Create mask for each contour and extract mean color
        colors = []
        for contour in contours:
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            mean_color = cv2.mean(image, mask=mask)[:3]
            colors.append(mean_color)
        return colors 