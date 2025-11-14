from OpusV.core.bot import Space
from OpusV.core.dir import dirr
from OpusV.core.git import git
from OpusV.core.userbot import Userbot
from OpusV.misc import dbb, heroku
from OpusV.logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Space()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
