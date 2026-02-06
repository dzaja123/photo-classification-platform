"""Image classifier using real ML model (ResNet50 via Keras)."""

import numpy as np
from typing import List, Dict
from io import BytesIO
from PIL import Image


class ImageClassifier:
    """
    Image classifier using ResNet50 (Keras Applications).
    
    Uses pre-trained ResNet50 model from Keras for real image classification.
    Falls back to simple heuristics if TensorFlow is not available.
    """
    
    def __init__(self):
        """Initialize the classifier."""
        self.model = None
        self.preprocess_input = None
        self.decode_predictions = None
        
        try:
            # Try to import TensorFlow/Keras
            from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
            
            print("Loading ResNet50 model...")
            self.model = ResNet50(weights='imagenet')
            self.preprocess_input = preprocess_input
            self.decode_predictions = decode_predictions
            print("ResNet50 model loaded successfully")
            
        except ImportError:
            print("TensorFlow not available, using fallback classifier")
            self.model = None
        except Exception as e:
            print(f"Error loading model: {e}, using fallback classifier")
            self.model = None
    
    def classify(self, image_bytes: bytes) -> List[Dict[str, any]]:
        """
        Classify an image and return top-3 predictions.
        
        Args:
            image_bytes: Image file as bytes
        
        Returns:
            List of top-3 predictions with class and confidence
            
        Example:
            >>> classifier = ImageClassifier()
            >>> results = classifier.classify(image_bytes)
            >>> print(results)
            [
                {"class": "golden_retriever", "confidence": 0.95},
                {"class": "Labrador_retriever", "confidence": 0.89},
                {"class": "dog", "confidence": 0.76}
            ]
        """
        try:
            # Load and validate image
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Use real model if available
            if self.model is not None:
                return self._classify_with_model(image)
            else:
                return self._fallback_classify(image)
            
        except Exception as e:
            raise ValueError(f"Failed to classify image: {str(e)}")
    
    def _classify_with_model(self, image: Image.Image) -> List[Dict[str, any]]:
        """
        Classify using ResNet50 model.
        
        Args:
            image: PIL Image
        
        Returns:
            List of top-3 predictions
        """
        # Resize image to 224x224 (ResNet50 input size)
        image_resized = image.resize((224, 224))
        
        # Convert to numpy array
        img_array = np.array(image_resized)
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        # Preprocess for ResNet50
        img_array = self.preprocess_input(img_array)
        
        # Make prediction
        predictions = self.model.predict(img_array, verbose=0)
        
        # Decode predictions (top 3)
        decoded = self.decode_predictions(predictions, top=3)[0]
        
        # Format results
        results = [
            {
                "class": label.replace('_', ' '),
                "confidence": round(float(score), 4)
            }
            for (_, label, score) in decoded
        ]
        
        return results
    
    def _fallback_classify(self, image: Image.Image) -> List[Dict[str, any]]:
        """
        Fallback classifier using simple heuristics.
        
        Analyzes image properties to make basic predictions.
        
        Args:
            image: PIL Image
        
        Returns:
            List of predictions based on image analysis
        """
        width, height = image.size
        aspect_ratio = width / height
        
        # Analyze dominant colors
        img_array = np.array(image.resize((100, 100)))
        avg_color = img_array.mean(axis=(0, 1))
        
        # Simple heuristic classification
        predictions = []
        
        # Landscape vs Portrait
        if aspect_ratio > 1.5:
            predictions.append({"class": "landscape", "confidence": 0.75})
        elif aspect_ratio < 0.7:
            predictions.append({"class": "portrait", "confidence": 0.72})
        else:
            predictions.append({"class": "square_photo", "confidence": 0.68})
        
        # Color-based guesses
        if avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]:  # Blue dominant
            predictions.append({"class": "sky_or_water", "confidence": 0.65})
        elif avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]:  # Green dominant
            predictions.append({"class": "nature_or_plants", "confidence": 0.63})
        else:
            predictions.append({"class": "indoor_scene", "confidence": 0.60})
        
        # Add a generic third prediction
        predictions.append({"class": "photograph", "confidence": 0.58})
        
        return predictions[:3]


# Singleton instance
_classifier_instance = None


def get_classifier() -> ImageClassifier:
    """
    Get singleton classifier instance.
    
    Returns:
        ImageClassifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = ImageClassifier()
    return _classifier_instance
