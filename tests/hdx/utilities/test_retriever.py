"""Retriever Tests"""
import random
import string
from os import mkdir
from os.path import join
from shutil import rmtree

import pytest

from hdx.utilities.downloader import Download, DownloadError
from hdx.utilities.retriever import Retrieve
from hdx.utilities.useragent import UserAgent


class TestRetriever:
    retrieverfoldername = "retriever"

    @pytest.fixture(scope="class", autouse=True)
    def useragent(self):
        UserAgent.set_global("test")
        yield
        UserAgent.clear_global()

    @pytest.fixture(scope="class")
    def retrieverfolder(self, fixturesfolder):
        return join(fixturesfolder, self.retrieverfoldername)

    @pytest.fixture(scope="class")
    def fallback_dir(self, retrieverfolder):
        return join(retrieverfolder, "fallbacks")

    @pytest.fixture(scope="function")
    def dirs(self, tmpdir):
        tmpdir = str(tmpdir)
        saved_dir = join(tmpdir, "saved")
        temp_dir = join(tmpdir, "temp")
        rmtree(temp_dir, ignore_errors=True)
        mkdir(temp_dir)
        return saved_dir, temp_dir

    def test_error(self, dirs, retrieverfolder, fallback_dir):
        saved_dir, temp_dir = dirs
        with Download() as downloader:
            with pytest.raises(ValueError):
                Retrieve(
                    downloader,
                    fallback_dir,
                    saved_dir,
                    temp_dir,
                    save=True,
                    use_saved=True,
                )

    def test_download_nosave(self, dirs, retrieverfolder, fallback_dir):
        saved_dir, temp_dir = dirs
        with Download() as downloader:
            with Retrieve(
                downloader,
                fallback_dir,
                saved_dir,
                temp_dir,
                save=False,
                use_saved=False,
            ) as retriever:
                filename = "test.txt"
                url = join(retrieverfolder, filename)
                path = retriever.download_file(
                    url, filename, logstr="test file", fallback=True
                )
                assert path == join(temp_dir, filename)
                path = retriever.download_file(
                    "NOTEXIST", filename, logstr="test file", fallback=True
                )
                assert path == join(fallback_dir, filename)
                with pytest.raises(DownloadError):
                    retriever.download_file(
                        "NOTEXIST", filename, fallback=False
                    )
                with pytest.raises(DownloadError):
                    long_url = "".join(
                        random.SystemRandom().choice(
                            string.ascii_uppercase + string.digits
                        )
                        for _ in range(150)
                    )
                    retriever.download_file(long_url, filename, fallback=False)
                text = retriever.download_text(
                    url, filename, logstr="test file", fallback=False
                )
                assert text == "hello"
                text = retriever.download_text(
                    "NOTEXIST", filename, logstr="test file", fallback=True
                )
                assert text == "goodbye"
                with pytest.raises(DownloadError):
                    retriever.download_text(
                        "NOTEXIST", filename, fallback=False
                    )
                filename = "test.yaml"
                url = join(retrieverfolder, filename)
                data = retriever.download_yaml(
                    url, filename, logstr="test file", fallback=False
                )
                assert data["param_1"] == "ABC"
                data = retriever.download_yaml(
                    "NOTEXIST", filename, logstr="test file", fallback=True
                )
                assert data["param_1"] == "XYZ"
                with pytest.raises(DownloadError):
                    retriever.download_yaml(
                        "NOTEXIST", filename, fallback=False
                    )
                filename = "test.json"
                url = join(retrieverfolder, filename)
                data = retriever.download_json(
                    url, filename, logstr="test file", fallback=False
                )
                assert data["my_param"] == "abc"
                data = retriever.download_json(
                    "NOTEXIST", filename, logstr="test file", fallback=True
                )
                assert data["my_param"] == "xyz"
                with pytest.raises(DownloadError):
                    retriever.download_json(
                        "NOTEXIST", filename, fallback=False
                    )

    def test_download_save(self, dirs, retrieverfolder, fallback_dir):
        saved_dir, temp_dir = dirs
        with Download() as downloader:
            with Retrieve(
                downloader,
                fallback_dir,
                saved_dir,
                temp_dir,
                save=True,
                use_saved=False,
            ) as retriever:
                filename = "test.txt"
                url = join(retrieverfolder, filename)
                path = retriever.download_file(
                    url, filename, logstr="test file", fallback=True
                )
                assert path == join(saved_dir, filename)
                path = retriever.download_file(
                    "NOTEXIST", filename, logstr="test file", fallback=True
                )
                assert path == join(fallback_dir, filename)
                with pytest.raises(DownloadError):
                    retriever.download_file(
                        "NOTEXIST", filename, fallback=False
                    )
                text = retriever.download_text(
                    url, filename, logstr="test file", fallback=False
                )
                assert text == "hello"
                text = retriever.download_text(
                    "NOTEXIST", filename, logstr="test file", fallback=True
                )
                assert text == "goodbye"
                with pytest.raises(DownloadError):
                    retriever.download_text(
                        "NOTEXIST", filename, fallback=False
                    )
                filename = "test.yaml"
                url = join(retrieverfolder, filename)
                data = retriever.download_yaml(
                    url, filename, logstr="test file", fallback=False
                )
                assert data["param_1"] == "ABC"
                data = retriever.download_yaml(
                    "NOTEXIST", filename, logstr="test file", fallback=True
                )
                assert data["param_1"] == "XYZ"
                with pytest.raises(DownloadError):
                    retriever.download_yaml(
                        "NOTEXIST", filename, fallback=False
                    )
                filename = "test.json"
                url = join(retrieverfolder, filename)
                data = retriever.download_json(
                    url, filename, logstr="test file", fallback=False
                )
                assert data["my_param"] == "abc"
                data = retriever.download_json(
                    "NOTEXIST", filename, logstr="test file", fallback=True
                )
                assert data["my_param"] == "xyz"
                with pytest.raises(DownloadError):
                    retriever.download_json(
                        "NOTEXIST", filename, fallback=False
                    )

    def test_download_usesaved(self, dirs, retrieverfolder, fallback_dir):
        _, temp_dir = dirs
        saved_dir = retrieverfolder
        with Download() as downloader:
            retriever = Retrieve(
                downloader,
                fallback_dir,
                saved_dir,
                temp_dir,
                save=False,
                use_saved=True,
            )
            filename = "test.txt"
            url = join(retrieverfolder, filename)
            path = retriever.download_file(
                url, filename, logstr="test file", fallback=True
            )
            assert path == join(saved_dir, filename)
            path = retriever.download_file(
                "NOTEXIST", filename, logstr="test file", fallback=True
            )
            assert path == join(saved_dir, filename)
            path = retriever.download_file(
                "NOTEXIST", filename, fallback=False
            )
            assert path == join(saved_dir, filename)
            text = retriever.download_text(
                url, filename, logstr="test file", fallback=False
            )
            assert text == "hello"
            text = retriever.download_text(
                "NOTEXIST", filename, logstr="test file", fallback=True
            )
            assert text == "hello"
            text = retriever.download_text(
                "NOTEXIST", filename, fallback=False
            )
            assert text == "hello"
            filename = "test.yaml"
            url = join(retrieverfolder, filename)
            data = retriever.download_yaml(
                url, filename, logstr="test file", fallback=False
            )
            assert data["param_1"] == "ABC"
            data = retriever.download_yaml(
                "NOTEXIST", filename, logstr="test file", fallback=True
            )
            assert data["param_1"] == "ABC"
            data = retriever.download_yaml(
                "NOTEXIST", filename, fallback=False
            )
            assert data["param_1"] == "ABC"
            filename = "test.json"
            url = join(retrieverfolder, filename)
            data = retriever.download_json(
                url, filename, logstr="test file", fallback=False
            )
            assert data["my_param"] == "abc"
            data = retriever.download_json(
                "NOTEXIST", filename, logstr="test file", fallback=True
            )
            assert data["my_param"] == "abc"
            data = retriever.download_json(
                "NOTEXIST", filename, fallback=False
            )
            assert data["my_param"] == "abc"
