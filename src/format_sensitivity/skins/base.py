"""The Skin container. A skin is a lexical filling of the skeleton in one domain."""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Skin:
    name: str

    # slot key (S1..S18) -> a plain-language statement of that fact in this domain.
    facts: dict

    # slot key -> list of all-of groups of any-of alternatives. A necessary
    # lexical condition, checked against every rendered format. Catches deletions;
    # does not prove a fact is present in the intended sense.
    anchors: dict

    # format code -> rendered text, for the single-block formats (F0/F1/F2/F5).
    single_block_formats: dict

    # (title, body) documents for F3. Rendered in randomized order per sample.
    bundle_documents: list

    # format code -> {slot key -> location}. For single-block formats the
    # location is the format name; for F3 it is the document letter.
    coverage: dict

    # The transformative reframe, in one sentence. Reference for graders only;
    # never shown to the model.
    reframe: str

    # Which formats this skin actually provides.
    supported_formats: tuple

    def render(self, format_code: str, seed: int) -> str:
        if format_code not in self.supported_formats:
            raise ValueError(
                f"FATAL: skin '{self.name}' does not provide format '{format_code}'. "
                f"Provides: {self.supported_formats}"
            )

        if format_code != "F3":
            return self.single_block_formats[format_code]

        documents = list(self.bundle_documents)
        random.Random(seed).shuffle(documents)
        return "\n\n---\n\n".join(f"### {title}\n\n{body}" for title, body in documents)
