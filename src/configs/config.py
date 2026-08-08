import torch
from pathlib import Path

# ============================================
# DATASET
# ============================================

DATASET_PATH = Path("dataset/train")

IMAGE_DIR = DATASET_PATH / "images"
MASK_DIR = DATASET_PATH / "masks"

# ============================================
# MODEL
# ============================================

NUM_CLASSES = 4
NUM_CHANNELS = 13
IMAGE_SIZE = 256

# ============================================
# TRAINING
# ============================================

BATCH_SIZE = 2
EPOCHS = 50
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4

# ============================================
# DEVICE
# ============================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# ============================================
# CHECKPOINTS
# ============================================

CHECKPOINT_DIR = Path("checkpoints")
CHECKPOINT_DIR.mkdir(exist_ok=True)

BEST_MODEL = CHECKPOINT_DIR / "best_model.pth"

# ============================================
# LOGGING
# ============================================

PRINT_EVERY = 10
SAVE_EVERY = 1

# ============================================
# RANDOM SEED
# ============================================

SEED = 42