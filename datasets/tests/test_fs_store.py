from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from threading import Thread
from uuid import uuid4

import pytest

from datasets.FsStore import FsSettings, FsStore


@dataclass
class SampleMetadata:
    name: str
    version: int


def test_store_and_fetch_metadata_mapping(tmp_path: Path) -> None:
    dataset_id = uuid4()
    store = FsStore(FsSettings(root=str(tmp_path)))
    metadata = {"name": "demo", "version": 1}

    store.store_metadata(dataset_id, metadata)
    loaded = store.fetch_metadata(dataset_id)

    assert loaded == metadata

    dataset_dir = tmp_path / str(dataset_id)
    symlink = dataset_dir / "metadata.json"
    version_files = list(dataset_dir.glob("metadata-*.json"))
    assert len(version_files) == 1
    assert symlink.is_symlink()
    assert symlink.resolve() == version_files[0]
    assert json.loads(version_files[0].read_text(encoding="utf-8")) == metadata


def test_store_metadata_accepts_dataclass(tmp_path: Path) -> None:
    dataset_id = uuid4()
    store = FsStore(FsSettings(root=str(tmp_path)))
    metadata = SampleMetadata(name="demo", version=2)

    store.store_metadata(dataset_id, metadata)
    loaded = store.fetch_metadata(dataset_id)

    assert loaded == {"name": "demo", "version": 2}


def test_fetch_metadata_missing(tmp_path: Path) -> None:
    store = FsStore(FsSettings(root=str(tmp_path)))

    with pytest.raises(FileNotFoundError):
        store.fetch_metadata(uuid4())
    assert store.dataset_dir_exists(uuid4()) is False


def test_dataset_dir_exists(tmp_path: Path) -> None:
    dataset_id = uuid4()
    store = FsStore(FsSettings(root=str(tmp_path)))

    assert store.dataset_dir_exists(dataset_id) is False

    store.store_metadata(dataset_id, {"name": "demo"})

    assert store.dataset_dir_exists(dataset_id) is True


def test_store_and_fetch_data_bytes(tmp_path: Path) -> None:
    dataset_id = uuid4()
    store = FsStore(FsSettings(root=str(tmp_path)))
    payload = b"hello world"

    store.store_metadata(dataset_id, {"init": True})
    version_path = store.store_data(dataset_id, payload)
    loaded = store.fetch_data(dataset_id)

    assert loaded == payload
    dataset_dir = tmp_path / str(dataset_id)
    symlink = dataset_dir / "data.bin"
    version_files = list(dataset_dir.glob("data-*.bin"))
    assert version_path in version_files
    assert symlink.is_symlink()
    assert symlink.resolve() == version_path


def test_store_and_fetch_data_text(tmp_path: Path) -> None:
    dataset_id = uuid4()
    store = FsStore(FsSettings(root=str(tmp_path)))
    payload = "some text"

    store.store_metadata(dataset_id, {"init": True})
    version_path = store.store_data(dataset_id, payload)
    loaded = store.fetch_data(dataset_id, as_text=True)

    assert loaded == payload
    dataset_dir = tmp_path / str(dataset_id)
    symlink = dataset_dir / "data.bin"
    version_files = list(dataset_dir.glob("data-*.bin"))
    assert version_path in version_files
    assert symlink.resolve() == version_path


def test_fetch_data_missing(tmp_path: Path) -> None:
    store = FsStore(FsSettings(root=str(tmp_path)))

    with pytest.raises(FileNotFoundError):
        store.fetch_data(uuid4())


def test_update_metadata_overlay(tmp_path: Path) -> None:
    dataset_id = uuid4()
    store = FsStore(FsSettings(root=str(tmp_path)))
    store.store_metadata(dataset_id, {"a": 1, "b": 1})

    dataset_dir = tmp_path / str(dataset_id)
    first_version = next(dataset_dir.glob("metadata-*.json"))

    updated = store.update_metadata(dataset_id, {"b": 2, "c": 3}, overlay=True)

    assert updated == {"a": 1, "b": 2, "c": 3}
    assert store.fetch_metadata(dataset_id) == {"a": 1, "b": 2, "c": 3}
    version_files = sorted(
        dataset_dir.glob("metadata-*.json"),
        key=lambda p: int(p.stem.split("-", 1)[1]),
    )
    assert len(version_files) == 2
    assert version_files[-1] != first_version
    symlink = dataset_dir / "metadata.json"
    assert symlink.resolve() == version_files[-1]


def test_update_metadata_override(tmp_path: Path) -> None:
    dataset_id = uuid4()
    store = FsStore(FsSettings(root=str(tmp_path)))
    store.store_metadata(dataset_id, {"a": 1})

    updated = store.update_metadata(dataset_id, {"b": 2}, overlay=False)

    assert updated == {"b": 2}
    assert store.fetch_metadata(dataset_id) == {"b": 2}
    dataset_dir = tmp_path / str(dataset_id)
    version_files = sorted(
        dataset_dir.glob("metadata-*.json"),
        key=lambda p: int(p.stem.split("-", 1)[1]),
    )
    assert len(version_files) == 2
    symlink = dataset_dir / "metadata.json"
    assert symlink.resolve() == version_files[-1]


def test_update_metadata_missing_dataset(tmp_path: Path) -> None:
    store = FsStore(FsSettings(root=str(tmp_path)))

    with pytest.raises(FileNotFoundError):
        store.update_metadata(uuid4(), {"key": "value"}, overlay=True)


def test_update_metadata_thread_safety(tmp_path: Path) -> None:
    dataset_id = uuid4()
    store = FsStore(FsSettings(root=str(tmp_path)))
    store.store_metadata(dataset_id, {"counter": 0})

    def worker(value: int) -> None:
        store.update_metadata(dataset_id, {"counter": value}, overlay=False)

    threads = [Thread(target=worker, args=(i,)) for i in range(1, 6)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    metadata = store.fetch_metadata(dataset_id)
    assert "counter" in metadata
    dataset_dir = tmp_path / str(dataset_id)
    version_files = list(dataset_dir.glob("metadata-*.json"))
    assert len(version_files) == 1 + len(threads)
    symlink = dataset_dir / "metadata.json"
    latest = max(version_files, key=lambda p: int(p.stem.split("-", 1)[1]))
    assert symlink.resolve() == latest


def test_store_data_requires_existing_dataset(tmp_path: Path) -> None:
    dataset_id = uuid4()
    store = FsStore(FsSettings(root=str(tmp_path)))

    with pytest.raises(FileNotFoundError):
        store.store_data(dataset_id, b"bytes")
