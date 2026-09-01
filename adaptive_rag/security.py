import re

INJECTION_PATTERNS = (
    r"ignore (all|any|previous|prior) instructions",
    r"reveal (the )?(system|developer) prompt",
    r"disable (your|the) safety",
)

class SecurityGate:
    def inspect(self, text: str) -> tuple[bool, str]:
        normalized = " ".join(text.lower().split())
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, normalized):
                return False, "potential_prompt_injection"
        return True, "ok"
