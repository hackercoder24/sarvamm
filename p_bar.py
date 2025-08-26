import time
import math
from pyrogram.types import Message

async def progress_bar(current, total, text, message: Message, start_time):
    """Display download/upload progress"""
    now = time.time()
    diff = now - start_time
    
    if round(diff % 5.00) == 0 or current == total:  # Update every 5 seconds
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        time_to_completion = round((total - current) / speed) if speed > 0 else 0

        progress = "[{0}{1}] \n".format(
            ''.join(["█" for _ in range(math.floor(percentage / 5))]),
            ''.join(["░" for _ in range(20 - math.floor(percentage / 5))])
        )

        tmp = progress + "**Progress:** {0:.1f}%\n".format(percentage)
        tmp += "**Speed:** {0}/s\n".format(humanbytes(speed))
        tmp += "**Downloaded:** {0} of {1}\n".format(humanbytes(current), humanbytes(total))
        tmp += "**ETA:** {0}".format(time_formatter(time_to_completion))

        try:
            await message.edit(
                text="{}\n\n{}".format(text, tmp)
            )
        except:
            pass

def humanbytes(size):
    """Convert bytes to human readable format"""
    if not size:
        return ""
    power = 2**10
    n = 0
    power_dict = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + power_dict[n] + 'B'

def time_formatter(seconds: int) -> str:
    """Convert seconds to human readable time"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s") if seconds else "")
    
    return tmp if tmp else "0s"
