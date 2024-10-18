import email
import base64
import datetime

from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from aioimaplib import aioimaplib
from .models import Profile, Message, Attachment


async def save_attachment(attachment_name, attachment_bytes, message):
    new_attachment = await Attachment.objects.acreate(
        message=message
    )

    await sync_to_async(new_attachment.data.save)(
        str(attachment_name),
        ContentFile(attachment_bytes))


async def get_connection():
    # Server options
    profile = await Profile.objects.aget()
    user = profile.login
    password = profile.password
    port = 993

    if "yandex" in profile.email:
        host = "imap.yandex.ru"
    elif "gmail" in profile.email:
        host = "imap.gmail.com"
    else:
        host = "imap.mail.ru"

    # Enter the server
    imap_client = aioimaplib.IMAP4_SSL(host=host, port=port)
    await imap_client.wait_hello_from_server()
    auth = await imap_client.login(user=user, password=password)
    if auth.result != "NO":
        imap_client.user = profile
        return imap_client
    else:
        raise Exception(auth.lines)


async def get_info():
    pass


async def get_progress():
    pass


async def get_messages():
    # Server options
    imap_client = await get_connection()

    # Search messages
    res, data = await imap_client.select()
    res, data = await imap_client.search('ALL')
    message_numbers = data[0].split()

    for message_number in message_numbers[:5]:
        # Print messages
        res, data = await imap_client.fetch(int(message_number), '(RFC822)')

        # Get message
        msg = email.message_from_bytes(data[1])

        letter_date = email.utils.parsedate_to_datetime(msg["Date"])
        letter_id = msg["Message-ID"]
        # letter_from = msg["Return-path"]

        if await Message.objects.filter(message_id__contains=letter_id).acount():
            continue

        if msg["Subject"]:
            letter_subject = email.header.decode_header(msg["Subject"])[
                0][0].decode()

        letter_attachments = []
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                letter_attachments.append(
                    (email.header.decode_header(part.get_filename())[0][0],
                     part.as_bytes())
                )
            if (part.get_content_maintype() == 'text' and
                part.get_content_subtype() in (
                    'plain', 'html')):
                letter_text = base64.b64decode(part.get_payload()).decode()

            # TODO: add BeautifulSoup parsing for html

        message = await Message.objects.acreate(
            message_id=letter_id,
            user=imap_client.user,
            subject=letter_subject,
            text=letter_text,
            sended_at=letter_date,
            received_at=datetime.datetime.now()
        )

        for letter_attachment in letter_attachments:
            await save_attachment(*letter_attachment, message)

    # Logout
    await imap_client.logout()
