#!/usr/bin/python3

"""
    File_Email: sr_sender plugin. Once a file is posted, the plugin matches the
    topic(what the filename begins with) to the file name and sends the appropriate emails.

    Usage:
      1. Need the following variables in an sr_sender config defined: file_email_to, file_email_relay
        ex. file_email_to AACN27 muhammad.taseer@canada.ca, test@test.com
        ex. file_email_relay email.relay.server.ca
          if file_email_relay is not defined it will resort to using smtp.cmc.ec.gc.ca
      2. sr_sender foreground emails.conf

    Last modified: Wahaj Taseer - June, 2019
"""


class File_Email(object):

    def __init__(self, parent):
        parent.declare_option('file_email_command')
        parent.declare_option('file_email_to')
        parent.declare_option('file_email_relay')
        self.registered_list = ['ftp', 'ftps', 'sftp']

    def registered_as(self):
        return self.registered_list

    def on_start(self, parent):
        if not hasattr(parent, 'file_email_command'):
            parent.file_mail_command = ['/usr/bin/mail']

    def do_send(self, parent):

        import os.path
        import re

        # have a list of email destinations...
        parent.logger.debug("email: %s" % parent.file_email_to)
        ipath = os.path.normpath(parent.msg.relpath)

        # loop over all the variables from config file, if files match, send via email
        for header in parent.file_email_to:
            file_type, emails = header.split(' ', 1)
            emails = [x.strip(' ') for x in emails.split(',')]

            # check if the file arrived matches any email rules
            if re.search('^' + file_type + '.*', parent.new_file):

                import smtplib
                from email.message import EmailMessage

                for recipient in emails:
                    parent.logger.debug('sending bulletin %s to %s' % (ipath, recipient))

                    with open(ipath) as fp:
                        emsg = EmailMessage()
                        emsg.set_content(fp.read())

                    emsg['Subject'] = parent.new_file
                    emsg['From'] = 'sarra-emailer@canada.ca'
                    emsg['To'] = recipient

                    try:
                        email_relay = parent.file_email_relay[0]
                        if not email_relay:
                            raise AttributeError('sr_sender object has no or incorrect file_email_relay')
                    except:
                        email_relay = 'smtp.cmc.ec.gc.ca'

                    parent.logger.info("Using email relay server: " + email_relay)
                    s = smtplib.SMTP(email_relay)
                    s.send_message(emsg)
                    s.quit()

                    parent.logger.info('sent file %s to %s' % (ipath, recipient))

        return True


file_email = File_Email(self)
self.do_send = file_email.do_send



