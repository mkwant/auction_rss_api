from camoufox import pkgman

LOCAL_ZIP = r"P:\Downloads\camoufox-158.0.1-beta.41-win.x86_64.zip"  # your manual download


def _local_download(file, url, *args, **kwargs):
    pkgman.rprint(f"Using local file instead of downloading {url}")
    with open(LOCAL_ZIP, "rb") as f:
        while chunk := f.read(1024 * 1024):
            file.write(chunk)
    file.seek(0)
    return file


pkgman.CamoufoxFetcher.download_file = staticmethod(_local_download)
pkgman.CamoufoxFetcher().install()
