"""This module handles Anki models."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from anki.models import ModelManager

StringTransformer = Callable[[str], str]


class ModelModifier(ABC):
    """The streamlined interface for Anki models (note types)."""

    @abstractmethod
    def modify_templates(self, f: StringTransformer) -> None:
        """Modifies all model HTML templates."""
        pass

    @abstractmethod
    def modify_stylings(self, f: StringTransformer) -> None:
        """Modifies all model CSS stylings."""
        pass


class AnkiModelModifier(ModelModifier):

    def __init__(self, model_manager: ModelManager):
        self.model_manager: ModelManager = model_manager

    def modify_templates(self, f: StringTransformer) -> None:
        for model in self.model_manager.all():
            for tmpl in model["tmpls"]:
                tmpl["qfmt"] = f(tmpl["qfmt"])
                tmpl["afmt"] = f(tmpl["afmt"])
            self.model_manager.update_dict(model)

    def modify_stylings(self, f: StringTransformer) -> None:
        for model in self.model_manager.all():
            model["css"] = f(model["css"])
            self.model_manager.update_dict(model)
