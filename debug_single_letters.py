from knowledge_base import COMMON_WORDS

single_letters = [w for w in COMMON_WORDS if len(w) == 1]
print(f"Single letter words: {sorted(single_letters)}")
