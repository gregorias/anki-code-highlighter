"""This module handles Anki models."""

from collections.abc import Callable
from typing import Protocol

from anki.models import ModelManager

StringTransformer = Callable[[str], str]


class ModelModifier(Protocol):
    """The streamlined interface for Anki models (note types)."""

    def modify_templates(self, f: StringTransformer) -> None:
        """Modifies all model HTML templates."""
        pass


class AnkiModelModifier(ModelModifier):

    def __init__(self, model_manager: ModelManager):
        self.model_manager: ModelManager = model_manager

    def modify_templates(self, f: StringTransformer) -> None:
        for model in self.model_manager.all():
            for tmpl in model["tmpls"]:
                tmpl["afmt"] = f(tmpl["afmt"])
                tmpl["qfmt"] = f(tmpl["qfmt"])
            self.model_manager.save(model)
