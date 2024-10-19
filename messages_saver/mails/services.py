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


async def get_auth_info():
    is_exists = await Profile.objects.aexists()
    return is_exists


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


async def get_messages():
    messages = []
    async for message in Message.objects.all():
        messages.append({
            "id": message.id,
            "message_id": message.message_id,
            "subject": message.subject,
            "text": message.text[:20],
            "sended_at": f"{message.sended_at:%d.%m.%Y %H:%M}",
            "received_at": f"{message.received_at:%d.%m.%Y %H:%M}",
            "attachments": []
        })
        async for attachment in message.attachment_set.all():
            messages[-1]["attachments"].append({
                "name": str(attachment.data.name),
                "data": str(attachment.data.read())
            })

    return messages


async def get_progress():
    # Server options
    imap_client = await get_connection()

    # Search messages
    res, data = await imap_client.select()
    res, data = await imap_client.search('ALL')
    message_numbers = data[0].split()
    n_message_numbers = len(message_numbers)

    progress = n_message_numbers
    for i, message_number in enumerate(message_numbers):
        # Print messages
        res, data = await imap_client.fetch(int(message_number), '(RFC822)')

        # Get message
        msg = email.message_from_bytes(data[1])

        letter_id = msg["Message-ID"]

        if not await Message.objects.filter(
                message_id__contains=letter_id).acount():
            progress = f"Downloading data {i} of {n_message_numbers}"
            break

    if (progress == n_message_numbers):
        progress = "Showing data"

    # Logout
    await imap_client.logout()

    return progress


async def download_messages():
    # Server options
    imap_client = await get_connection()

    # Search messages
    res, data = await imap_client.select()
    res, data = await imap_client.search('ALL')
    message_numbers = data[0].split()

    for message_number in message_numbers:
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
            part_charset = part.get_content_charset()
            if part.get_content_disposition() == 'attachment':
                letter_attachment_filename = email.header.decode_header(
                    part.get_filename())[0]
                if (type(letter_attachment_filename[0]) is bytes):
                    letter_attachment_filename = \
                        letter_attachment_filename[0].decode(
                            letter_attachment_filename[1])
                else:
                    letter_attachment_filename = \
                        letter_attachment_filename[0]

                letter_attachment_data = part.get_payload()
                if (type(letter_attachment_data) is bytes):
                    letter_attachment_data = \
                        base64.b64decode(letter_attachment_data)
                letter_attachments.append(
                    (letter_attachment_filename,
                     letter_attachment_data)
                )
            if (part.get_content_maintype() == 'text' and
                part.get_content_subtype() in (
                    'plain', 'html')):
                letter_text = part.get_payload()
                if type(letter_text) is bytes:
                    letter_text = base64.b64decode(
                        part.get_payload()).decode(part_charset)

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

    return "OK"
