def apply_policy(model_name, user_input, llm_output, risk):

    severity = risk.get("severity", "LOW")

    if severity == "HIGH":
        action = "BLOCK"
        response = "Blocked due to high-risk content."

    elif severity == "MEDIUM":
        action = "WARN"
        response = "Warning: potential policy violation."

    else:
        action = "ALLOW"
        response = llm_output

    return {
        "model_name": model_name,
        "action": action,
        "response": response,
        "risk": risk
    }