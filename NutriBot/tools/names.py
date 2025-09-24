# tools/names.py

# 영양소 표준 이름과 다양한 표현(동의어) 매핑
NUTRIENT_SYNONYMS = {
    "Vitamin B6": ["vitamin b6", "vit b6", "b6", "pyridoxine"],
    "Vitamin B12": ["vitamin b12", "vit b12", "b12", "cobalamin"],
    "Vitamin C": ["vitamin c", "vit c", "ascorbic acid"],
    "Magnesium": ["magnesium", "magnesium citrate", "magnesium oxide"],
    "Zinc": ["zinc", "zinc gluconate", "zinc citrate"],
    "Calcium": ["calcium", "calcium carbonate", "calcium citrate"],
    "Iron": ["iron", "ferrous sulfate", "ferrous gluconate"],
    "Folate": ["folate", "folic acid", "vitamin b9"],
    "Vitamin D": ["vitamin d", "vit d", "cholecalciferol", "ergocalciferol"],
    "Selenium": ["selenium", "selenomethionine"]
}

def clean_nutrient_name(text: str) -> str | None:
    """
    자유로운 텍스트에서 영양소 이름을 추출해 표준 이름으로 정규화합니다.

    예: "high in zinc gluconate" → "Zinc"
    """
    if not text:
        return None
    text = text.lower()

    for std_name, aliases in NUTRIENT_SYNONYMS.items():
        for alias in aliases:
            if alias in text:
                return std_name

    return None