import torch


class SegmentationMetrics:
    """
    Metrics for Multi-Class Semantic Segmentation
    """

    def __init__(self, num_classes=4):
        self.num_classes = num_classes

    # =====================================================
    # Pixel Accuracy
    # =====================================================
    def pixel_accuracy(self, logits, targets):

        preds = torch.argmax(logits, dim=1)

        correct = (preds == targets).sum().float()

        total = targets.numel()

        return (correct / total).item()

    # =====================================================
    # Dice Score
    # =====================================================
    def dice_score(self, logits, targets):

        preds = torch.argmax(logits, dim=1)

        dice_scores = []

        for cls in range(self.num_classes):

            pred_mask = (preds == cls).float()
            true_mask = (targets == cls).float()

            intersection = (pred_mask * true_mask).sum()

            denominator = pred_mask.sum() + true_mask.sum()

            dice = (2.0 * intersection + 1e-6) / (denominator + 1e-6)

            dice_scores.append(dice)

        return torch.mean(torch.stack(dice_scores)).item()

    # =====================================================
    # IoU Score
    # =====================================================
    def iou_score(self, logits, targets):

        preds = torch.argmax(logits, dim=1)

        iou_scores = []

        for cls in range(self.num_classes):

            pred_mask = (preds == cls)
            true_mask = (targets == cls)

            intersection = (pred_mask & true_mask).sum().float()

            union = (pred_mask | true_mask).sum().float()

            if union == 0:
                continue

            iou_scores.append(intersection / union)

        if len(iou_scores) == 0:
            return 0.0

        return torch.mean(torch.stack(iou_scores)).item()

    # =====================================================
    # Calculate All Metrics
    # =====================================================
    def calculate(self, logits, targets):

        return {
            "pixel_accuracy": self.pixel_accuracy(logits, targets),
            "dice_score": self.dice_score(logits, targets),
            "iou_score": self.iou_score(logits, targets),
        }


# =====================================================
# Test
# =====================================================

if __name__ == "__main__":

    metrics = SegmentationMetrics(num_classes=4)

    logits = torch.randn(2, 4, 256, 256)

    targets = torch.randint(0, 4, (2, 256, 256))

    result = metrics.calculate(logits, targets)

    print("=" * 50)
    print("METRICS TEST")
    print("=" * 50)

    for key, value in result.items():
        print(f"{key:20s}: {value:.4f}")

    print("\n✅ Metrics Working Successfully!")