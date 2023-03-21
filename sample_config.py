# MIT License

# Copyright (c) 2022 Hash Minner


# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

# edit this file with your veriable if you'r deploy bot via locally | vps

class Config(object):

    # get a token from @BotFather
    BOT_TOKEN = ""

    # Get these values from my.telegram.org
    API_ID = 1234567
    API_HASH = ""

    # No need to change
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    ADL_BOT_RQ = {}
    CHUNK_SIZE = 128
    TG_MAX_FILE_SIZE = 4194304000
    HTTP_PROXY = ""
    PROCESS_MAX_TIMEOUT = 3700

    # TG Ids
    LOG_CHANNEL = -1007119867241
    OWNER_ID = 1288398723

    # bot username without @
    BOT_USERNAME = "AdvanceUrlUploaderBot"

    # auth users
    AUTH_USERS = [OWNER_ID]
