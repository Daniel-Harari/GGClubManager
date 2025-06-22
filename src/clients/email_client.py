import os
import email
import imaplib
from email.header import decode_header
from datetime import datetime, timedelta
import logging
from pathlib import Path
from typing import List, Optional, Dict
from email.utils import parseaddr



class EmailClient:
    def __init__(self,
                 email_address: str,
                 password: str,
                 imap_server: str = "imap.gmail.com",
                 download_folder: str = "downloads"):
        """
        Initialize email client

        Args:
            email_address: Your email address
            password: Your email password or app-specific password
            imap_server: IMAP server address (default: Gmail)
            download_folder: Folder to save attachments
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Test connection
        self.connect()

    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def connect(self) -> imaplib.IMAP4_SSL:
        """Establish connection to email server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.password)
            self.logger.info(f"Successfully connected to {self.imap_server}")
            return self.mail
        except Exception as e:
            self.logger.error(f"Failed to connect to email server: {str(e)}")
            raise

    def disconnect(self):
        """Close the email connection"""
        try:
            self.mail.close()
            self.mail.logout()
            self.logger.info("Disconnected from email server")
        except Exception as e:
            self.logger.error(f"Error during disconnect: {str(e)}")

    def get_emails(self,
                   folder: str = "INBOX",
                   days: int = 1,
                   subject_filter: Optional[str] = None,
                   unread_only: bool = False) -> List[Dict]:
        """
        Fetch emails from specified folder

        Args:
            folder: Email folder to search
            days: Number of days to look back
            subject_filter: Filter emails by subject
            unread_only: Only fetch unread emails

        Returns:
            List of email dictionaries with metadata
        """
        try:
            # Select the mailbox
            self.mail.select(folder)

            # Build search criteria
            search_criteria = []

            # Date criterion
            date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
            search_criteria.append(f'SINCE {date}')

            # Subject filter
            if subject_filter:
                search_criteria.append(f'SUBJECT "{subject_filter}"')

            # Read/Unread filter
            if unread_only:
                search_criteria.append('UNSEEN')

            # Combine criteria
            search_string = ' '.join(search_criteria)

            # Search for emails
            _, message_numbers = self.mail.search(None, search_string)

            emails = []
            for num in message_numbers[0].split():
                _, msg_data = self.mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)

                # Get email metadata
                subject = decode_header(message["subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

                from_ = decode_header(message["from"])[0][0]
                if isinstance(from_, bytes):
                    from_ = from_.decode()

                date_ = email.utils.parsedate_to_datetime(message["date"])

                # Get attachments info
                attachments = []
                for part in message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    filename = part.get_filename()
                    if filename:
                        if isinstance(filename, bytes):
                            filename = filename.decode()
                        attachments.append(filename)

                emails.append({
                    'id': num,
                    'subject': subject,
                    'from': from_,
                    'date': date_,
                    'has_attachments': bool(attachments),
                    'attachments': attachments
                })

            self.logger.info(f"Found {len(emails)} emails matching criteria")
            return emails

        except Exception as e:
            self.logger.error(f"Error fetching emails: {str(e)}")
            raise

    def download_attachments(self,
                             email_id: bytes,
                             file_extensions: Optional[List[str]] = None) -> List[Path]:
        """
        Download attachments from specific email

        Args:
            email_id: Email ID to download attachments from
            file_extensions: List of file extensions to download (e.g., ['.csv', '.xlsx'])

        Returns:
            List of paths to downloaded files
        """
        try:
            _, msg_data = self.mail.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            message = email.message_from_bytes(email_body)

            downloaded_files = []

            for part in message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()
                if filename:
                    if isinstance(filename, bytes):
                        filename = filename.decode()

                    # Check file extension if filter is provided
                    if file_extensions:
                        if not any(filename.lower().endswith(ext.lower())
                                   for ext in file_extensions):
                            continue

                    filepath = self.download_folder / filename
                    with open(filepath, 'wb') as f:
                        f.write(part.get_payload(decode=True))

                    downloaded_files.append(filepath)
                    self.logger.info(f"Downloaded: {filename}")

            return downloaded_files

        except Exception as e:
            self.logger.error(f"Error downloading attachments: {str(e)}")
            raise

    def get_emails_from_sender(self,
                               sender_address: str,
                               folder: str = "INBOX",
                               limit: Optional[int] = None,
                               include_body: bool = True) -> List[Dict]:
        """
        Get all emails from a specific sender

        Args:
            sender_address: Email address to filter by
            folder: Email folder to search
            limit: Maximum number of emails to retrieve (None for all)
            include_body: Whether to include email body content

        Returns:
            List of email dictionaries
        """
        try:
            if not self.connect():
                return []

            # Select folder
            self.mail.select(folder)

            # Search for emails from sender
            _, message_numbers = self.mail.search(None, f'FROM "{sender_address}"')

            emails = []
            message_numbers = message_numbers[0].split()

            # Apply limit if specified
            if limit:
                message_numbers = message_numbers[-limit:]

            for num in message_numbers:
                _, msg_data = self.mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)

                # Get basic email info
                subject = self.decode_email_string(message["subject"] or "")
                from_header = self.decode_email_string(message["from"] or "")
                _, sender_email = parseaddr(from_header)

                # Parse date
                date_str = message["date"]
                try:
                    date = email.utils.parsedate_to_datetime(date_str)
                except:
                    date = None

                # Get attachments info
                attachments = []
                body_content = ""

                for part in message.walk():
                    # Handle attachments
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is not None:
                        filename = part.get_filename()
                        if filename:
                            if isinstance(filename, bytes):
                                filename = filename.decode()
                            attachments.append(filename)

                    # Handle email body
                    elif include_body and part.get_content_maintype() == 'text':
                        try:
                            content = part.get_payload(decode=True).decode()
                            if part.get_content_subtype() == 'plain':
                                body_content += content + "\n"
                            elif part.get_content_subtype() == 'html' and not body_content:
                                # Only use HTML if we don't have plain text
                                body_content += content + "\n"
                        except:
                            self.logger.warning(f"Could not decode email body for message {num}")

                email_data = {
                    'id': num,
                    'subject': subject,
                    'from': from_header,
                    'from_email': sender_email,
                    'date': date,
                    'has_attachments': bool(attachments),
                    'attachments': attachments,
                }

                if include_body:
                    email_data['body'] = body_content.strip()

                emails.append(email_data)

                self.logger.info(f"Retrieved email: {subject}")

            return emails

        finally:
            self.disconnect()

    def mark_as_read(self, email_id: bytes):
        """Mark email as read"""
        try:
            self.mail.store(email_id, '+FLAGS', '\\Seen')
        except Exception as e:
            self.logger.error(f"Error marking email as read: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = EmailClient(
        email_address="sheepit13@gmail.com",
        password="fsew prlr wkrt gyzs",
        download_folder="email_attachments"
    )

    try:
        # Get recent emails with CSV attachments
        emails = client.get_emails_from_sender("support@clubgg.com")

        # Download CSV attachments from each email
        for email in emails:
            print(f"\nProcessing email: {email['subject']}")
            print(f"From: {email['from']}")
            print(f"Date: {email['date']}")

            if email['has_attachments']:
                files = client.download_attachments(
                    email['id'],
                    file_extensions=['.csv']
                )
                print(f"Downloaded files: {[f.name for f in files]}")

                # Mark email as read
                client.mark_as_read(email['id'])

    finally:
        # Clean up
        client.disconnect()
