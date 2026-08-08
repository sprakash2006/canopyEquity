import torch
import torch.nn as nn

from transformers import SegformerForSemanticSegmentation


class CanopySegFormer(nn.Module):

    def __init__(self, num_classes=4):

        super().__init__()

        # Load pretrained SegFormer
        self.model = SegformerForSemanticSegmentation.from_pretrained(
            "nvidia/mit-b0",
            num_labels=num_classes,
            ignore_mismatched_sizes=True
        )

        # -------------------------------------------------
        # Replace first Conv layer (3 channels -> 13 channels)
        # -------------------------------------------------

        old_proj = self.model.segformer.stages[0].patch_embeddings.proj

        new_proj = nn.Conv2d(
            in_channels=13,
            out_channels=old_proj.out_channels,
            kernel_size=old_proj.kernel_size,
            stride=old_proj.stride,
            padding=old_proj.padding,
            bias=False
        )

        with torch.no_grad():

            # Copy pretrained RGB weights
            new_proj.weight[:, :3] = old_proj.weight

            # Initialize remaining 10 channels
            avg_weight = old_proj.weight.mean(dim=1, keepdim=True)

            for i in range(3, 13):
                new_proj.weight[:, i:i+1] = avg_weight

        # Replace original layer
        self.model.segformer.stages[0].patch_embeddings.proj = new_proj

    def forward(self, x):

        output = self.model(pixel_values=x)

        return output.logits