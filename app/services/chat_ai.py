def generate_correction(text: str) -> dict[str, str]:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return {
            "correction": "Digite uma frase para corrigir.",
            "explanation": "A frase enviada estava vazia.",
            "corrected_text": "",
        }

    corrected_text = cleaned[0].upper() + cleaned[1:]
    if not corrected_text.endswith((".", "!", "?")):
        corrected_text += "."

    explanation = "Padronizamos espaçamento, capitalização inicial e pontuação final."
    correction = f"Sugestão: {corrected_text}"
    return {
        "correction": correction,
        "explanation": explanation,
        "corrected_text": corrected_text,
    }
