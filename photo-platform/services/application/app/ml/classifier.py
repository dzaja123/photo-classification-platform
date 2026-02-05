"""Image classifier using TensorFlow Lite (Mock for now)."""

import random
from typing import List, Dict
from io import BytesIO
from PIL import Image


class ImageClassifier:
    """
    Image classifier using TensorFlow Lite MobileNetV2.
    
    For now, this is a mock implementation that returns random classifications.
    TODO: Replace with actual TensorFlow Lite model.
    """
    
    # Mock ImageNet classes
    MOCK_CLASSES = [
        "golden_retriever", "cat", "sports_car", "coffee_mug", "laptop",
        "smartphone", "bicycle", "airplane", "boat", "tree",
        "flower", "mountain", "beach", "building", "person",
        "dog", "bird", "fish", "horse", "elephant",
        "tiger", "lion", "bear", "zebra", "giraffe"
    ]
    
    def __init__(self):
        """Initialize the classifier."""
        print("Initializing Image Classifier (Mock)")
        # TODO: Load TensorFlow Lite model
        # self.interpreter = tf.lite.Interpreter(model_path=model_path)
        # self.interpreter.allocate_tensors()
    
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
                {"class": "dog", "confidence": 0.89},
                {"class": "labrador", "confidence": 0.76}
            ]
        """
        try:
            # Validate image
            image = Image.open(BytesIO(image_bytes))
            image.verify()
            
            # TODO: Actual TensorFlow Lite inference
            # For now, return mock predictions
            predictions = self._mock_classify()
            
            return predictions
            
        except Exception as e:
            raise ValueError(f"Failed to classify image: {str(e)}")
    
    def _mock_classify(self) -> List[Dict[str, any]]:
        """
        Mock classification - returns random predictions.
        
        TODO: Replace with actual TensorFlow Lite inference.
        """
        # Select 3 random classes
        selected_classes = random.sample(self.MOCK_CLASSES, 3)
        
        # Generate mock confidences (descending order)
        confidences = sorted([random.uniform(0.6, 0.99) for _ in range(3)], reverse=True)
        
        predictions = [
            {
                "class": cls,
                "confidence": round(conf, 4)
            }
            for cls, conf in zip(selected_classes, confidences)
        ]
        
        return predictions


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
