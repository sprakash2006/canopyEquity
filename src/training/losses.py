import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    """
    Dice Loss for Multi-Class Semantic Segmentation
    """

    def __init__(self, smooth=1e-6):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits, targets):

        # Convert logits to probabilities
        probs = F.softmax(logits, dim=1)

        num_classes = probs.shape[1]

        # One-hot encode target mask
        targets_one_hot = F.one_hot(
            targets,
            num_classes=num_classes
        ).permute(0, 3, 1, 2).float()

        # Flatten
        probs = probs.contiguous().view(probs.size(0), num_classes, -1)
        targets_one_hot = targets_one_hot.contiguous().view(
            targets_one_hot.size(0),
            num_classes,
            -1
        )

        intersection = (probs * targets_one_hot).sum(dim=2)

        union = probs.sum(dim=2) + targets_one_hot.sum(dim=2)

        dice = (2 * intersection + self.smooth) / (union + self.smooth)

        loss = 1 - dice.mean()

        return loss


class SegmentationLoss(nn.Module):
    """
    Cross Entropy + Dice Loss
    """

    def __init__(self):

        super().__init__()

        self.ce = nn.CrossEntropyLoss()

        self.dice = DiceLoss()

    def forward(self, logits, targets):

        ce_loss = self.ce(logits, targets)

        dice_loss = self.dice(logits, targets)

        total_loss = ce_loss + dice_loss

        return total_loss