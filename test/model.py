from codehighlighter.model import ModelModifier, StringTransformer

__all__ = ["FakeModelModifier"]


class FakeModelModifier(ModelModifier):
    """A fake model modifier for testing purposes."""

    def __init__(self, templates: list[str] = [], csss: list[str] = []) -> None:
        self.templates: list[str] = templates
        self.csss: list[str] = csss

    def modify_templates(self, f: StringTransformer) -> None:
        for i, tmpl in enumerate(self.templates):
            self.templates[i] = f(tmpl)

    def modify_stylings(self, f: StringTransformer) -> None:
        for i, css in enumerate(self.csss):
            self.csss[i] = f(css)

    def add_template(self, tmpl: str) -> None:
        """Adds a template to the fake modifier."""
        self.templates.append(tmpl)
