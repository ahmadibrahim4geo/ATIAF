"""Scene and directory scanner for discovering satellite products."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from atyaf_core.discovery.aster import AsterParser
from atyaf_core.discovery.landsat import LandsatParser
from atyaf_core.discovery.models import SceneInfo
from atyaf_core.discovery.sentinel2 import Sentinel2Parser


@dataclass
class ScanResult:
    input_path: Path
    is_single_scene: bool
    scenes: List[SceneInfo]
    ignored_paths: List[Path]
    errors: List[str]


class SceneScanner:
    """Scans an unpacked scene folder or a parent directory for valid satellite products."""

    IGNORED_DIR_NAMES = {
        "WORK",
        "RESULTS",
        "REPORTS",
        ".GIT",
        ".GITHUB",
        "__PYCACHE__",
        ".AGENT-DEVELOPMENT-LOG",
        ".AGENT_RESOURCES",
    }

    @classmethod
    def should_ignore(cls, folder: Path) -> bool:
        """Checks if directory should be skipped during scene scanning."""
        name = folder.name.upper()
        if name in cls.IGNORED_DIR_NAMES:
            return True
        if name.startswith(".") or name.startswith("__"):
            return True
        return False

    @classmethod
    def identify_scene(cls, folder: Path) -> Optional[SceneInfo]:
        """Attempts to identify a single directory as a recognized satellite scene."""
        if not folder.is_dir() or cls.should_ignore(folder):
            return None

        # 1. Landsat
        if LandsatParser.can_parse(folder):
            scene = LandsatParser.parse(folder)
            if scene and scene.bands:
                return scene

        # 2. Sentinel-2
        if Sentinel2Parser.can_parse(folder):
            scene = Sentinel2Parser.parse(folder)
            if scene and scene.bands:
                return scene

        # 3. ASTER
        if AsterParser.can_parse(folder):
            scene = AsterParser.parse(folder)
            if scene and scene.bands:
                return scene

        return None

    @classmethod
    def scan(cls, input_path: Path) -> ScanResult:
        """Scans the path: if it's a single scene, parses it directly;
        if it's a parent directory, iterates immediate child directories.
        """
        input_path = input_path.resolve()
        if not input_path.exists():
            return ScanResult(
                input_path=input_path,
                is_single_scene=False,
                scenes=[],
                ignored_paths=[],
                errors=[f"Input path does not exist: {input_path}"],
            )

        if not input_path.is_dir():
            return ScanResult(
                input_path=input_path,
                is_single_scene=False,
                scenes=[],
                ignored_paths=[],
                errors=[f"Input path is not a directory: {input_path}"],
            )

        # Test if input_path itself is a valid single scene
        single_scene = cls.identify_scene(input_path)
        if single_scene:
            return ScanResult(
                input_path=input_path,
                is_single_scene=True,
                scenes=[single_scene],
                ignored_paths=[],
                errors=[],
            )

        # If not a single scene, inspect subdirectories
        scenes: List[SceneInfo] = []
        ignored: List[Path] = []
        errors: List[str] = []

        for child in sorted(input_path.iterdir()):
            if not child.is_dir():
                continue
            if cls.should_ignore(child):
                ignored.append(child)
                continue

            scene = cls.identify_scene(child)
            if scene:
                scenes.append(scene)
            else:
                ignored.append(child)

        return ScanResult(
            input_path=input_path,
            is_single_scene=False,
            scenes=scenes,
            ignored_paths=ignored,
            errors=errors,
        )
