"""A fuzzy finder dialog for selecting items."""

from typing import Any, List, Optional

from aqt.qt import (
    QDialog,
    QDialogButtonBox,
    QEvent,
    QLabel,
    QLineEdit,
    QListWidget,
    Qt,
    QVBoxLayout,
)


class FuzzyFinderDialog(QDialog):
    def __init__(
        self,
        parent,
        title: str,
        label_text: str,
        options: List[str],
        current: Optional[str] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(350)
        self.setMinimumHeight(450)

        self.options = options
        self.selected_value: Optional[str] = None

        layout = QVBoxLayout(self)

        # Help / Label text
        self.label = QLabel(label_text, self)
        layout.addWidget(self.label)

        # Search input
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Type to filter...")
        layout.addWidget(self.search_input)

        # List of items
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        # Standard buttons compatibility
        try:
            ok_button = QDialogButtonBox.StandardButton.Ok
            cancel_button = QDialogButtonBox.StandardButton.Cancel
        except AttributeError:
            ok_button = getattr(QDialogButtonBox, "Ok")
            cancel_button = getattr(QDialogButtonBox, "Cancel")

        # Buttons
        self.button_box = QDialogButtonBox(
            ok_button | cancel_button,
            self,
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        # Connect signals
        self.search_input.textChanged.connect(self.filter_options)
        self.list_widget.itemDoubleClicked.connect(self.accept)
        self.search_input.installEventFilter(self)

        # Initial population
        self.filter_options("")

        # Select current/default if provided
        try:
            match_flag = Qt.MatchFlag.MatchExactly
        except AttributeError:
            match_flag = getattr(Qt, "MatchExactly")

        if current:
            items = self.list_widget.findItems(current, match_flag)
            if items:
                self.list_widget.setCurrentItem(items[0])
                self.list_widget.scrollToItem(items[0])
        elif self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

        self.search_input.setFocus()

    def handle_navigation_key(self, key: int) -> bool:
        # Keys compatibility
        if hasattr(Qt, "Key"):
            Key_Up = Qt.Key.Key_Up
            Key_Down = Qt.Key.Key_Down
            Key_Enter = Qt.Key.Key_Enter
            Key_Return = Qt.Key.Key_Return
            Key_Escape = Qt.Key.Key_Escape
        else:
            Key_Up = getattr(Qt, "Key_Up")
            Key_Down = getattr(Qt, "Key_Down")
            Key_Enter = getattr(Qt, "Key_Enter")
            Key_Return = getattr(Qt, "Key_Return")
            Key_Escape = getattr(Qt, "Key_Escape")

        if key == Key_Up:
            row = self.list_widget.currentRow()
            if row > 0:
                self.list_widget.setCurrentRow(row - 1)
            return True
        elif key == Key_Down:
            row = self.list_widget.currentRow()
            if row < self.list_widget.count() - 1:
                self.list_widget.setCurrentRow(row + 1)
            return True
        elif key in (Key_Return, Key_Enter):
            self.accept()
            return True
        elif key == Key_Escape:
            self.reject()
            return True

        return False

    def keyPressEvent(self, event):
        if self.handle_navigation_key(event.key()):
            event.accept()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, obj: Any, event: Any) -> bool:
        try:
            event_type = QEvent.Type.KeyPress
        except AttributeError:
            event_type = getattr(QEvent, "KeyPress")

        if obj is self.search_input and event.type() == event_type:
            if self.handle_navigation_key(event.key()):
                return True

        return super().eventFilter(obj, event)

    def filter_options(self, text: str):
        self.list_widget.clear()

        filtered = filter_and_sort_options(text, self.options)
        for opt in filtered:
            self.list_widget.addItem(opt)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def accept(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            self.selected_value = current_item.text()
            super().accept()
        else:
            super().reject()

    @classmethod
    def ask(
        cls,
        parent,
        title: str,
        label_text: str,
        options: List[str],
        current: Optional[str] = None,
    ) -> Optional[str]:
        dialog = cls(parent, title, label_text, options, current)
        if hasattr(dialog, "exec"):
            res = dialog.exec()
        else:
            res = getattr(dialog, "exec_")()

        if res:
            return dialog.selected_value
        return None


def is_subsequence(query: str, target: str) -> bool:
    """Check if query is a subsequence of target, case-insensitively."""
    query = query.lower()
    target = target.lower()
    t_idx = 0
    for char in query:
        t_idx = target.find(char, t_idx)
        if t_idx == -1:
            return False
        t_idx += 1
    return True


def score_match(query: str, target: str) -> int:
    """Calculate match score for ranking:
    4: Exact case-insensitive match
    3: Prefix case-insensitive match
    2: Substring case-insensitive match
    1: Subsequence case-insensitive match (default/fallback)
    0: No match (not a subsequence)
    """
    if not is_subsequence(query, target):
        return 0

    target_lower = target.lower()
    query_lower = query.lower()
    if target_lower == query_lower:
        return 4
    elif target_lower.startswith(query_lower):
        return 3
    elif query_lower in target_lower:
        return 2
    else:
        return 1


def filter_and_sort_options(query: str, options: List[str]) -> List[str]:
    """Filters the options using subsequence matching and sorts them by relevance, then alphabetically."""
    scored_options = []
    for opt in options:
        score = score_match(query, opt)
        if score > 0:
            scored_options.append((score, opt))

    # Sort by score descending, then case-insensitive alphabetically
    scored_options.sort(key=lambda x: (-x[0], x[1].lower()))
    return [opt for _, opt in scored_options]
