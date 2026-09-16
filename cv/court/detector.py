from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision import models


class CourtLineDetector:
    """
    ResNet50 court keypoint detector (14 points).

    Same architecture used by Tennis-Analysis-System /
    abdullahtarek/tennis_analysis.
    """

    NUM_KEYPOINTS = 14

    def __init__(self, model_path: str | Path) -> None:
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Court keypoint model not found at {model_path}. "
                "Download it to models/keypoints_model.pth"
            )

        self.device = torch.device("cpu")
        self.model = models.resnet50(weights=None)
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, self.NUM_KEYPOINTS * 2)
        state = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state)
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    def predict(self, image_bgr: np.ndarray) -> np.ndarray:
        """Return flat array [x0,y0,x1,y1,...] in original image coordinates."""
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        image_tensor = self.transform(image_rgb).unsqueeze(0).to(self.device)
        with torch.no_grad():
            outputs = self.model(image_tensor)
        keypoints = outputs.squeeze().detach().cpu().numpy().astype(np.float32)
        original_h, original_w = image_bgr.shape[:2]
        keypoints[::2] *= original_w / 224.0
        keypoints[1::2] *= original_h / 224.0
        return keypoints

    def predict_points(self, image_bgr: np.ndarray) -> list[list[float]]:
        flat = self.predict(image_bgr)
        points: list[list[float]] = []
        for i in range(0, len(flat), 2):
            points.append([float(flat[i]), float(flat[i + 1])])
        return points
