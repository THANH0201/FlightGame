import textwrap

story = ('''You are a young airline pilot who loves adventure travel . After working for a while, you buy the private jet of your dreams. You decide to take your first flight on the weekend from your local airport to the domestic airport where your parents live. On the way to the target airport, the plane lost signal and you chose emergency landing on the closest airport. At this, you heard about the story of the cave that was opened only once every 50 years when the sun was shining directly on the cave at 9 o'clock on September 9th. You are inherently curious and courageous, so you decide to participate in the journey to locate the stone.
At the airports you choose to land; there are tasks such as refuelling and collecting information about the stone. You meet many new friends and make a team with them. At least your team finds the stone and repurchases it.
Be faster! There are more people who will find the stone as you...''')

# Set column width to 80 characters
wrapper = textwrap.TextWrapper(width=100, break_long_words=False, replace_whitespace=False)
# Wrap text
word_list = wrapper.wrap(text=story)


def getStory():
    return word_list