import torch
import torch.nn.functional as F
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm

from src.training.metrics import SegmentationMetrics


class Trainer:

    def __init__(
        self,
        model,
        criterion,
        optimizer,
        device,
        num_classes=4
    ):

        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device

        self.metrics = SegmentationMetrics(num_classes)

        # Mixed Precision
        self.scaler = GradScaler(enabled=torch.cuda.is_available())

    # =====================================================
    # TRAIN
    # =====================================================

    def train_epoch(self, dataloader):

        self.model.train()

        total_loss = 0.0
        total_pixel_acc = 0.0
        total_dice = 0.0
        total_iou = 0.0

        progress = tqdm(
            dataloader,
            desc="Training",
            leave=False
        )

        for images, masks in progress:

            images = images.to(self.device)
            masks = masks.to(self.device)

            self.optimizer.zero_grad()

            # Mixed Precision Forward Pass
            with autocast(enabled=torch.cuda.is_available()):

                outputs = self.model(images)

                outputs = F.interpolate(
                    outputs,
                    size=masks.shape[-2:],
                    mode="bilinear",
                    align_corners=False
                )

                loss = self.criterion(outputs, masks)

            # Backpropagation
            self.scaler.scale(loss).backward()

            self.scaler.step(self.optimizer)

            self.scaler.update()

            # Metrics
            result = self.metrics.calculate(outputs, masks)

            total_loss += loss.item()
            total_pixel_acc += result["pixel_accuracy"]
            total_dice += result["dice_score"]
            total_iou += result["iou_score"]

            progress.set_postfix(
                loss=f"{loss.item():.4f}",
                dice=f"{result['dice_score']:.4f}",
                iou=f"{result['iou_score']:.4f}"
            )

        n = len(dataloader)

        return {
            "loss": total_loss / n,
            "pixel_accuracy": total_pixel_acc / n,
            "dice_score": total_dice / n,
            "iou_score": total_iou / n
        }

    # =====================================================
    # VALIDATION
    # =====================================================

    @torch.no_grad()
    def validate_epoch(self, dataloader):

        self.model.eval()

        total_loss = 0.0
        total_pixel_acc = 0.0
        total_dice = 0.0
        total_iou = 0.0

        progress = tqdm(
            dataloader,
            desc="Validation",
            leave=False
        )

        for images, masks in progress:

            images = images.to(self.device)
            masks = masks.to(self.device)

            with autocast(enabled=torch.cuda.is_available()):

                outputs = self.model(images)

                outputs = F.interpolate(
                    outputs,
                    size=masks.shape[-2:],
                    mode="bilinear",
                    align_corners=False
                )

                loss = self.criterion(outputs, masks)

            result = self.metrics.calculate(outputs, masks)

            total_loss += loss.item()
            total_pixel_acc += result["pixel_accuracy"]
            total_dice += result["dice_score"]
            total_iou += result["iou_score"]

            progress.set_postfix(
                loss=f"{loss.item():.4f}",
                dice=f"{result['dice_score']:.4f}",
                iou=f"{result['iou_score']:.4f}"
            )

        n = len(dataloader)

        return {
            "loss": total_loss / n,
            "pixel_accuracy": total_pixel_acc / n,
            "dice_score": total_dice / n,
            "iou_score": total_iou / n
        }