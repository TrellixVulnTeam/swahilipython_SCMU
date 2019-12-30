# Import the email modules we'll need
kutoka email.parser agiza BytesParser, Parser
kutoka email.policy agiza default

# If the e-mail headers are kwenye a file, uncomment these two lines:
# ukijumuisha open(messagefile, 'rb') kama fp:
#     headers = BytesParser(policy=default).parse(fp)

#  Or kila parsing headers kwenye a string (this ni an uncommon operation), use:
headers = Parser(policy=default).parsestr(
        'From: Foo Bar <user@example.com>\n'
        'To: <someone_else@example.com>\n'
        'Subject: Test message\n'
        '\n'
        'Body would go here\n')

#  Now the header items can be accessed kama a dictionary:
andika('To: {}'.format(headers['to']))
andika('From: {}'.format(headers['kutoka']))
andika('Subject: {}'.format(headers['subject']))

# You can also access the parts of the addresses:
andika('Recipient username: {}'.format(headers['to'].addresses[0].username))
andika('Sender name: {}'.format(headers['kutoka'].addresses[0].display_name))
