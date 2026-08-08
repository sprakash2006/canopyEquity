from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# =====================================================
# LOAD PREDICTION
# =====================================================

prediction_path = Path("outputs/prediction.png")

assert prediction_path.exists(), \
    "Prediction image not found!"

prediction = np.array(
    Image.open(prediction_path)
)

print("=" * 60)
print("CANOPY AI VISUALIZATION")
print("=" * 60)

print("Prediction Shape :", prediction.shape)
print("Classes :", np.unique(prediction))


# =====================================================
# COLOR MAP
# =====================================================

# 0 = Background
# 1 = Trees
# 2 = Water
# 3 = Built-up

colors = np.array([

    [0, 0, 0],          # Background -> Black

    [34, 139, 34],      # Trees -> Green

    [30, 144, 255],     # Water -> Blue

    [220, 20, 60]       # Built-up -> Red

], dtype=np.uint8)


colored_prediction = colors[prediction]


# =====================================================
# SAVE
# =====================================================

output_dir = Path("outputs")

save_path = output_dir / "prediction_colored.png"

Image.fromarray(colored_prediction).save(save_path)

print(f"\n✅ Colored Prediction Saved : {save_path}")


# =====================================================
# DISPLAY
# =====================================================

plt.figure(figsize=(8, 8))

plt.imshow(colored_prediction)

plt.title("Predicted Segmentation")

plt.axis("off")

plt.show()

print("=" * 60)