import sys
import torch
from sentence_transformers import SentenceTransformer

print(f"PyTorch version: {torch.__version__}, CUDA available: {torch.cuda.is_available()}")

print(">>> Starting download: BAAI/bge-m3")
try:
    m_bge = SentenceTransformer("BAAI/bge-m3")
    print(">>> BAAI/bge-m3 downloaded and verified successfully!")
    # Quick test
    test_emb = m_bge.encode(["مرحبا بكم في الهاكاثون"])
    print(f"BGE-M3 test embedding shape: {test_emb.shape}")
except Exception as e:
    print(f"ERROR downloading BAAI/bge-m3: {e}")

print("\n>>> Starting download: google/embeddinggemma-2")
try:
    m_gemma = SentenceTransformer("google/embeddinggemma-2")
    print(">>> google/embeddinggemma-2 downloaded and verified successfully!")
    test_emb2 = m_gemma.encode(["مرحبا بكم في الهاكاثون"])
    print(f"EmbeddingGemma-2 test embedding shape: {test_emb2.shape}")
except Exception as e:
    print(f"ERROR downloading google/embeddinggemma-2: {e}")

print("\n>>> ALL REQUESTED EMBEDDING MODELS DOWNLOADED!")
