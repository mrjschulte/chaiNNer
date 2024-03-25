from __future__ import annotations

import re
from pathlib import Path

from nodes.groups import optional_list_group
from nodes.properties.inputs import DirectoryInput, TextInput
from nodes.properties.outputs import DirectoryOutput

from .. import directory_group

INVALID_CHARS = re.compile(r"[<>:\"|?*\x00-\x1F]")


def is_abs(path: str) -> bool:
    return path.startswith(("/", "\\")) or Path(path).is_absolute()


def go_into(dir: Path, folder: str) -> Path:
    if is_abs(folder):
        raise ValueError("Absolute paths are not allowed as folders.")

    invalid = INVALID_CHARS.search(folder)
    if invalid is not None:
        raise ValueError(f"Invalid character '{invalid.group()}' in folder name.")

    return (dir / folder).resolve()


@directory_group.register(
    schema_id="chainner:utility:into_directory",
    name="Directory Go Into",
    description="Goes forward into a directory.",
    icon="BsFolder",
    inputs=[
        DirectoryInput(must_exist=False, label_style="hidden"),
        TextInput("Folder"),
        optional_list_group(
            *[TextInput(f"Folder {i}").make_optional() for i in range(2, 11)],
        ),
    ],
    outputs=[
        DirectoryOutput(
            output_type="""
                def into(dir: Directory | Error, folder: string | null): Directory | Error {
                    match dir {
                        Error as e => e,
                        Directory => {
                            match folder {
                                null => dir,
                                string => {
                                    let result = goIntoDirectory(dir.path, folder);
                                    match result {
                                        string => Directory { path: result },
                                        Error => result,
                                    }
                                },
                            }
                        },
                    }
                }

                let d1 = into(Input0, Input1);
                let d2 = into(d1, Input2);
                let d3 = into(d2, Input3);
                let d4 = into(d3, Input4);
                let d5 = into(d4, Input5);
                let d6 = into(d5, Input6);
                let d7 = into(d6, Input7);
                let d8 = into(d7, Input8);
                let d9 = into(d8, Input9);
                let d10 = into(d9, Input10);
                d10
            """,
        ),
    ],
)
def directory_go_into_node(directory: Path, *folders: str | None) -> Path:
    for folder in folders:
        if folder is not None:
            directory = go_into(directory, folder)
    return directory
