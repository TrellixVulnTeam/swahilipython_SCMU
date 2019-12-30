#!/usr/bin/env python3

agiza smtplib

kutoka email.message agiza EmailMessage
kutoka email.headerregistry agiza Address
kutoka email.utils agiza make_msgid

# Create the base text message.
msg = EmailMessage()
msg['Subject'] = "Ayons asperges pour le déjeuner"
msg['From'] = Address("Pepé Le Pew", "pepe", "example.com")
msg['To'] = (Address("Penelope Pussycat", "penelope", "example.com"),
             Address("Fabrette Pussycat", "fabrette", "example.com"))
msg.set_content("""\
Salut!

Cela ressemble à un excellent recipie[1] déjeuner.

[1] http://www.yummly.com/recipe/Roasted-Asparagus-Epicurious-203718

--Pepé
""")

# Add the html version.  This converts the message into a multipart/alternative
# container, ukijumuisha the original text message kama the first part na the new html
# message kama the second part.
asparagus_cid = make_msgid()
msg.add_alternative("""\
<html>
  <head></head>
  <body>
    <p>Salut!</p>
    <p>Cela ressemble à un excellent
        <a href="http://www.yummly.com/recipe/Roasted-Asparagus-Epicurious-203718">
            recipie
        </a> déjeuner.
    </p>
    <img src="cid:{asparagus_cid}" />
  </body>
</html>
""".format(asparagus_cid=asparagus_cid[1:-1]), subtype='html')
# note that we needed to peel the <> off the msgid kila use kwenye the html.

# Now add the related image to the html part.
ukijumuisha open("roasted-asparagus.jpg", 'rb') kama img:
    msg.get_payload()[1].add_related(img.read(), 'image', 'jpeg',
                                     cid=asparagus_cid)

# Make a local copy of what we are going to send.
ukijumuisha open('outgoing.msg', 'wb') kama f:
    f.write(bytes(msg))

# Send the message via local SMTP server.
ukijumuisha smtplib.SMTP('localhost') kama s:
    s.send_message(msg)
