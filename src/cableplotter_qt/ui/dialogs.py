from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QFileDialog


class FileDialog(QFileDialog):

    def __init__(self, name_filter: str = None):
        super().__init__()
        self.setFileMode(QFileDialog.FileMode.ExistingFiles)
        self.setNameFilter(name_filter)
        self.setViewMode(QFileDialog.ViewMode.List)

    def get(self) -> Optional[list[Path]]:
        if self.exec() and (paths := self.selectedFiles()):
            return list(Path(p) for p in paths)
