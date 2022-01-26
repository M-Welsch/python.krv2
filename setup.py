from setuptools import setup

setup(
    name="python.krv2",
    version="0.1",
    packages=[
        "krv2",
        "krv2.hmi",
        "krv2.common",
        "krv2.music_collection",
        "test",
        "test.unit",
        "test.unit.music_collection",
        "test.mockups",
        "test.deprecated",
        "test.deprecated.cmus",
        "test.deprecated.hardware",
        "test.integration",
    ],
    url="",
    license="",
    author="max",
    author_email="maxiwelsch@posteo.de",
    description="neat little music player based on a rapsberry pi 1 sbc",
)
