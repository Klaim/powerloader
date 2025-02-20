from fixtures import *


class TestAll:
    # Download the expected file
    def test_working_download(
        self, file, powerloader_binary, mock_server_working, checksums
    ):
        remove_all(file)

        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                f"{mock_server_working}/static/packages/{file['name']}",
                "-o",
                file["output_path"],
            ]
        )

        assert calculate_sha256(file["output_path"]) == checksums[file["name"]]
        assert Path(file["output_path"]).exists()
        assert not Path(file["output_path_pdpart"]).exists()
        assert os.path.getsize(file["output_path"]) == file["size"]

    # Download the expected file
    def test_working_download_pwd(
        self, file, powerloader_binary, mock_server_password, checksums
    ):
        remove_all(file)

        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                f"{mock_server_password}/static/packages/{file['name']}",
                "-o",
                file["output_path"],
            ]
        )

        assert calculate_sha256(file["output_path"]) == checksums[file["name"]]
        assert Path(file["output_path"]).exists()
        assert not Path(file["output_path_pdpart"]).exists()
        assert os.path.getsize(file["output_path"]) == file["size"]

    # Download from a path that works on the third try
    def test_broken_for_three_tries(
        self, file, powerloader_binary, mock_server_working, checksums
    ):
        remove_all(file)
        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                f"{mock_server_working}/broken_counts/static/packages/{file['name']}",
                "-o",
                file["output_path"],
            ]
        )
        assert calculate_sha256(file["output_path"]) == checksums[file["name"]]
        assert os.path.getsize(file["output_path"]) == file["size"]

    def test_working_download_broken_checksum(
        self, file, powerloader_binary, mock_server_working
    ):
        remove_all(file)
        try:
            out = subprocess.check_output(
                [
                    powerloader_binary,
                    "download",
                    f"{mock_server_working}/static/packages/{file['name']}",
                    "--sha",
                    "broken_checksum",
                    "-o",
                    file["output_path"],
                ]
            )
        except subprocess.CalledProcessError as e:
            print(e)
        assert not Path(file["output_path_pdpart"]).exists()
        assert not Path(file["output_path"]).exists()

    def test_broken_file(self, file, powerloader_binary, mock_server_working):
        p = Path("randomnonexist.txt")
        ppart = Path("randomnonexist.txt.pdpart")
        assert not p.exists()
        assert not ppart.exists()

        with pytest.raises(subprocess.CalledProcessError):
            out = subprocess.check_output(
                [
                    powerloader_binary,
                    "download",
                    f"{mock_server_working}/randomnonexist.txt",
                ]
            )

        assert not p.exists()
        assert not ppart.exists()

    # Download a broken file
    def test_broken_download_good_checksum(
        self, file, powerloader_binary, mock_server_working
    ):
        remove_all(file)
        try:
            out = subprocess.check_output(
                [
                    powerloader_binary,
                    "download",
                    f"{mock_server_working}/harm_checksum/static/packages/{file['name']}",
                    "--sha",
                    "broken_checksum",
                    "-o",
                    file["output_path"],
                ]
            )
        except subprocess.CalledProcessError as e:
            print(e)

        assert not Path(file["output_path_pdpart"]).exists()
        assert not Path(file["output_path"]).exists()

    def test_part_resume(
        self, file, powerloader_binary, mock_server_working, checksums
    ):
        # Download the expected file
        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                f"{mock_server_working}/static/packages/{file['name']}",
                "-o",
                file["output_path"],
            ]
        )

        with open(file["output_path"], "rb") as fi:
            data = fi.read()
        with open(file["output_path_pdpart"], "wb") as fo:
            fo.write(data[0:400])

        # Resume the download
        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                "-r",
                f"{mock_server_working}/static/packages/{file['name']}",
                "-o",
                file["output_path"],
            ]
        )
        assert calculate_sha256(file["output_path"]) == checksums[file["name"]]
        assert os.path.getsize(file["output_path"]) == file["size"]

        sent_headers = get_prev_headers(mock_server_working)
        assert "Range" in sent_headers
        assert sent_headers["Range"] == "bytes=400-"

    def test_yml_download_working(
        self,
        file,
        mirrors_with_names,
        checksums,
        powerloader_binary,
        mock_server_working,
        mock_server_404,
        mock_server_lazy,
        mock_server_broken,
        mock_server_password,
    ):
        remove_all(file)

        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                "-f",
                file["mirrors"],
                "-d",
                file["tmp_path"],
            ]
        )

        for fn in mirrors_with_names["names"]:
            assert calculate_sha256(file["tmp_path"] / fn) == checksums[str(fn)]

    def test_yml_content_based_behavior(
        self,
        file,
        sparse_mirrors_with_names,
        checksums,
        powerloader_binary,
        mock_server_working,
        mock_server_404,
        mock_server_lazy,
        mock_server_broken,
        mock_server_password,
    ):
        remove_all(file)

        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                "-f",
                file["local_mirrors"],
                "-d",
                file["tmp_path"],
            ]
        )

        for fn in sparse_mirrors_with_names["names"]:
            assert calculate_sha256(file["tmp_path"] / fn) == checksums[str(fn)]

    def test_yml_password_format_one(
        self,
        file,
        sparse_mirrors_with_names,
        checksums,
        powerloader_binary,
        mock_server_working,
        mock_server_404,
        mock_server_lazy,
        mock_server_broken,
        mock_server_password,
    ):
        remove_all(file)

        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                "-f",
                file["authentication"],
                "-d",
                file["tmp_path"],
            ]
        )

        for fn in sparse_mirrors_with_names["names"]:
            assert calculate_sha256(file["tmp_path"] / fn) == checksums[str(fn)]

    # TODO: Parse outputs?, Randomized tests?
    def test_yml_with_interruptions(
        self,
        file,
        sparse_mirrors_with_names,
        checksums,
        powerloader_binary,
        mock_server_working,
        mock_server_404,
        mock_server_lazy,
        mock_server_broken,
        mock_server_password,
    ):
        remove_all(file)
        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                "-f",
                file["local_mirrors"],
                "-d",
                file["tmp_path"],
                "-v",
            ]
        )

        pdp = ".pdpart"
        for fn in sparse_mirrors_with_names["names"]:
            fp = file["tmp_path"] / fn
            with open(fp, "rb") as fi:
                data = fi.read()

            with open(str(fp) + pdp, "wb") as fo:
                fo.write(data[0:400])
            fp.unlink()

        # The servers is reliable now
        for broken_file in filter_broken(get_files(file), pdp):
            fn = path_to_name(broken_file.replace(pdp, ""))
            fp = Path(file["tmp_path"]) / Path(fn)
            out = subprocess.check_output(
                [
                    powerloader_binary,
                    "download",
                    "-r",
                    f"{mock_server_working}/static/packages/{fn}",
                    "-o",
                    fp,
                ]
            )

        for fn in sparse_mirrors_with_names["names"]:
            assert calculate_sha256(file["tmp_path"] / fn) == checksums[str(fn)]

    def test_zchunk_basic(file, powerloader_binary, mock_server_working):
        # Download the expected file
        assert not Path("lorem.txt.zck").exists()

        args = [
            powerloader_binary,
            "download",
            f"{mock_server_working}/static/zchunk/lorem.txt.zck",
            "--zck-header-size",
            "257",
            "--zck-header-sha",
            "57937bf55851d111a497c1fe2ad706a4df70e02c9b8ba3698b9ab5f8887d8a8b",
            "-v",
        ]

        out = subprocess.check_output(args)

        headers = get_prev_headers(mock_server_working, 2)
        assert headers[0]["Range"] == "bytes=0-256"
        assert headers[1]["Range"] == "bytes=257-4822"
        assert Path("lorem.txt.zck").exists()
        assert Path("lorem.txt.zck").stat().st_size == 4823
        assert not Path("lorem.txt.zck.pdpart").exists()

        clear_prev_headers(mock_server_working)
        out = subprocess.check_output(args)
        headers = get_prev_headers(mock_server_working, 100)
        assert headers is None

        assert Path("lorem.txt.zck").exists()
        assert Path("lorem.txt.zck").stat().st_size == 4823
        assert not Path("lorem.txt.zck.pdpart").exists()

        # grow the file by tripling the original
        root = proj_root()
        new_file = (
            root / "test" / "conda_mock" / "static" / "zchunk" / "lorem.txt.x3.zck"
        )

        clear_prev_headers(mock_server_working)

        args_o3 = [
            powerloader_binary,
            "download",
            f"{mock_server_working}/static/zchunk/lorem.txt.x3.zck",
            "-v",
            "-o",
            "lorem.txt.zck",
        ]
        out = subprocess.check_output(args_o3)

        headers = get_prev_headers(mock_server_working, 100)

        # lead
        assert headers[0]["Range"] == "bytes=0-88"
        # header
        assert headers[1]["Range"] == "bytes=0-257"
        range_start = int(headers[2]["Range"][len("bytes=") :].split("-")[0])
        assert range_start > 4000

        assert Path("lorem.txt.zck").stat().st_size == new_file.stat().st_size
        assert calculate_sha256(new_file) == calculate_sha256("lorem.txt.zck")
        assert Path("lorem.txt.zck").exists()
        assert not Path("lorem.txt.zck.pdpart").exists()

        Path("lorem.txt.zck").unlink()

    def test_zchunk_basic_nochksum(file, powerloader_binary, mock_server_working):
        # Download the expected file
        assert not Path("lorem.txt.zck").exists()

        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                f"{mock_server_working}/static/zchunk/lorem.txt.zck",
            ]
        )

        headers = get_prev_headers(mock_server_working, 3)
        assert headers[0]["Range"] == "bytes=0-88"
        assert headers[1]["Range"] == "bytes=0-256"
        assert headers[2]["Range"] == "bytes=257-4822"
        assert Path("lorem.txt.zck").exists()
        Path("lorem.txt.zck").unlink()

    def test_zchunk_basic_extract(file, powerloader_binary, mock_server_working):
        # Download the expected file
        assert not Path("lorem.txt.zck").exists()
        assert not Path("lorem.txt").exists()

        out = subprocess.check_output(
            [
                powerloader_binary,
                "download",
                f"{mock_server_working}/static/zchunk/lorem.txt.zck",
                "-x",
                "--zck-header-size",
                "257",
                "--zck-header-sha",
                "57937bf55851d111a497c1fe2ad706a4df70e02c9b8ba3698b9ab5f8887d8a8b",
            ]
        )

        assert Path("lorem.txt.zck").exists()
        assert Path("lorem.txt").exists()
        Path("lorem.txt.zck").unlink()
        Path("lorem.txt").unlink()

    def test_zchunk_random_file(self, file):
        remove_all(file)
        name = "_random_file"

        path1 = str(
            Path(file["tmp_path"]) / Path(str(platform.system()) + name + "1.txt")
        )
        path2 = str(
            Path(file["tmp_path"]) / Path(str(platform.system()) + name + "2.txt")
        )
        path3 = str(
            Path(file["tmp_path"]) / Path(str(platform.system()) + name + "3.txt")
        )
        exponent = 20
        generate_random_file(path1, size=2 ** exponent)
        generate_random_file(path2, size=2 ** exponent)

        # opening first file in append mode and second file in read mode
        f1 = open(path1, "rb")
        f2 = open(path2, "rb")
        f3 = open(path3, "a+b")

        # appending the contents of the second file to the first file
        f3.write(f1.read())
        f3.write(f2.read())

        # Comput zchunks
        out1 = subprocess.check_output(["zck", path1, "-o", path1 + ".zck"])
        out2 = subprocess.check_output(["zck", path2, "-o", path2 + ".zck"])
        out3 = subprocess.check_output(["zck", path3, "-o", path3 + ".zck"])

        # Check delta size
        dsize1 = subprocess.check_output(
            ["zck_delta_size", path1 + ".zck", path3 + ".zck"]
        )
        dsize2 = subprocess.check_output(
            ["zck_delta_size", path2 + ".zck", path3 + ".zck"]
        )

        pf_1, pch_1, num_chunks_1 = get_percentage(dsize1)
        pf_2, pch_2, num_chunks_2 = get_percentage(dsize2)

        print(
            "Will download "
            + str(round(pf_1))
            + "% of file1, that's "
            + str(round(pch_1))
            + "% of chunks. Total: "
            + str(num_chunks_1)
            + " chunks."
        )
        print(
            "Will download "
            + str(round(pf_2))
            + "% of file2, that's "
            + str(round(pch_2))
            + "% of chunks. Total: "
            + str(num_chunks_2)
            + " chunks."
        )

        assert round(pf_1) < 65
        assert round(pf_2) < 65
