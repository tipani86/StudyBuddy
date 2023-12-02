# Debug switch
DEBUG = False

# Generic internet settings
TIMEOUT = 60
RETRIES = 3
DELAY = 5
BACKOFF = 2

# Basic prompt settings (more customized need to be imported through config files)

PRE_SUMMARY_PROMPT = "The above is the conversation so far between you, the AI assistant, and a human user. Please summarize the topics discussed for your own reference. Remember, do not write a direct reply to the user."

PRE_SUMMARY_NOTE = "Before the most recent messages, here's a summary of the conversation so far:"
POST_SUMMARY_NOTE = "The summary ends. And here are the most recent two messages from the conversation. You should generate the next response based on the conversation so far."
