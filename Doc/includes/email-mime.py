# Import smtplib kila the actual sending function
agiza smtplib

# And imghdr to find the types of our images
agiza imghdr

# Here are the email package modules we'll need
kutoka email.message agiza EmailMessage

# Create the container email message.
msg = EmailMessage()
msg['Subject'] = 'Our family reunion'
# me == the sender's email address
# family = the list of all recipients' email addresses
msg['From'] = me
msg['To'] = ', '.join(family)
msg.preamble = 'You will sio see this kwenye a MIME-aware mail reader.\n'

# Open the files kwenye binary mode.  Use imghdr to figure out the
# MIME subtype kila each specific image.
kila file kwenye pngfiles:
    ukijumuisha open(file, 'rb') kama fp:
        img_data = fp.read()
    msg.add_attachment(img_data, maintype='image',
                                 subtype=imghdr.what(Tupu, img_data))

# Send the email via our own SMTP server.
ukijumuisha smtplib.SMTP('localhost') kama s:
    s.send_message(msg)
