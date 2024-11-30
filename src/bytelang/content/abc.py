from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Final
from typing import Iterable
from typing import Optional

from tools.filetool import FileTool


@dataclass(frozen=True, kw_only=True)
class Content:
    """Абстрактный контент, загружаемый реестрами"""

    parent: str
    """Родительский контент"""
    name: str
    """Наименование контента"""


class Registry[K, T](ABC):
    """
    Базовый реестр. Интерфейс реестра
    Можно получить данные по ключу
    """

    def __init__(self):
        self._data = dict[K, T]()

    def getValues(self) -> Iterable[T]:
        return self._data.values()

    @abstractmethod
    def get(self, __key: K) -> Optional[T]:
        """
        Получить контент
        :param __key:
        :return: None если контент не найден
        """


class JSONFileRegistry[RawDict: dict[str, Any], T](Registry[str, T]):
    """
    Файловый реестр. Заполняет из JSON файла
    RawDict - представление данных T в виде словаря
    """

    def __init__(self, target_file: Path):
        super().__init__()
        self._target_file: Path = target_file
        self._data = {
            name: self._parse(name, raw)
            for name, raw in FileTool.readJSON(self._target_file).items()
        }

    def get(self, __key: str) -> Optional[T]:
        if self._target_file is None:
            raise ValueError("Must select File")

        return self._data.get(__key)

    @abstractmethod
    def _parse(self, name: str, raw: RawDict) -> T:
        """
        Преобразовать сырое представление в объект контента
        :param raw:
        :return:
        """


class CatalogRegistry[T](Registry[str, T]):
    """
    Каталоговый Реестр[T] (ищет файл по имени в каталоге)
    """

    def __init__(self, target_folder: Path, file_ext: str) -> None:
        super().__init__()
        self.__TARGET_FOLDER: Final[Path] = target_folder

        if not self.__TARGET_FOLDER.is_dir():
            raise ValueError(f"Not a Folder: {target_folder}")

        self.__FILE_EXT: Final[str] = file_ext

    def get(self, name: str) -> T:
        if (ret := self._data.get(name)) is None:
            ret = self._data[name] = self._load(self.__TARGET_FOLDER / f"{name}.{self.__FILE_EXT}", name)

        return ret

    @abstractmethod
    def _load(self, path: Path, name: str) -> T:
        """
        Загрузить контент из файла
        :param path: путь к этому контенту
        :param name: его наименование
        :return:
        """
