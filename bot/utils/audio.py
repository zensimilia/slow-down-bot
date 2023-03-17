import asyncio

from bot.config import AppConfig
from bot.utils.logger import get_logger
from bot.utils.tagging import Tagging

from .soxex import ExtTransformer

config = AppConfig()
log = get_logger()


async def slow_down(file_path: str, speed: float = 33 / 45) -> str | None:
    """This function slow down audio file."""

    slowed_file_path = f"{file_path[:-4]}_slow.mp3"

    try:
        chain = ExtTransformer()
        chain.speed(speed)
        chain.highpass(100)
        chain.lowpass(8000)
        chain.norm(-1)
        chain.reverb(
            reverberance=50,
            high_freq_damping=0,
            room_scale=100,
            stereo_depth=50,
        )

        # Run function in separate thread to non-blocking stack
        await asyncio.to_thread(
            chain.build,
            input_filepath=file_path,
            output_filepath=slowed_file_path,
            bitrate=320.0,
        )

        await fill_id3_tags(file_path, slowed_file_path)

    except Exception as error:  # pylint: disable=broad-except
        log.error(error)
        slowed_file_path = None

    return slowed_file_path


async def fill_id3_tags(src_path: str, dst_path: str) -> None:
    """
    It opies the ID3 tags from the source file to the destination file,
    adds a brand text, and attach album art image.
    """

    tags = Tagging(dst_path)
    tags.copy_from(src_path)
    await tags.add_brand()
    tags.add_cover(config.ALBUM_ART)
    tags.save()
