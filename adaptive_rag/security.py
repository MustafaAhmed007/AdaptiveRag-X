import re


class SecurityGate:
    PATTERNS = (
        r"ignore (all|previous|prior) instructions",
        r"reveal (the )?(system|developer) prompt",
        r"print (your|the) hidden prompt",
        r"show (me )?(your|the) system prompt",
        r"disregard (all|previous|prior) instructions",
        r"jailbreak",
    )

    def inspect(self, query: str) -> tuple[bool, str]:
        for pattern in self.PATTERNS:
            if re.search(pattern, query.lower()):
                return False, "prompt-injection pattern detected"
        return True, "ok"
