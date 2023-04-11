def check_unclosed_formatting(text):
    count = text.count('```')
    return count % 2 == 1
