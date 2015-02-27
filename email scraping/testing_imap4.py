import sys
import imaplib
import email
import datetime
import getpass
from pprint import pprint
import re

#To see the complete interaction between the client and server

list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

def parse_list_response(line):
	flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
	mailbox_name = mailbox_name.strip('"')
	return (flags, delimiter, mailbox_name)


if __name__ == '__main__':

	#First step is to create an IMAP4 instance, preferably the SSL variant for security, 
	#connected to the Gmail server at imap.gmail.com:
	M = imaplib.IMAP4_SSL('imap.gmail.com')

	# this will only work if you enable gmail to allow "access of less secure apps"
	# the proper way of doing it is putting an oath2
	try:
		M.login('ortizantoniocarlos@gmail.com', getpass.getpass())
	except Exception, e:
		print 'LOGIN FAILED!!'
		print e
	'''
	rv, mailboxes = M.list()

	if rv == 'OK':
		print "Response Code: ", rv
		print "Mailboxes: "
		pprint(mailboxes)

	print ''
	print ''

	# to separate data to flags, delimiters, and names.
	for line in mailboxes:
		print 'Server response', line
		flags, delimiter, mailbox_name = parse_list_response(line)
		print 'Parsed Response:', (flags, delimiter, mailbox_name)
#--------------------------------------------------------------------------
# list() takes arguments to let you ask for mailboxes in part of the hierarchy. For example, to list sub-folders of Archive, you can pass a value as the directory argument:
# Alternately, to list folders matching a pattern you can pass the pattern argument:

	rv, data = M.list(directory='Archive')
	if rv == 'OK':
		print 'Response code: ', rv
		print 'Archives:'
		pprint(data)
#--------------------------------------------------------------------------
#Use status() to ask for aggregated information about the contents. The standard defines these status conditions:

#MESSAGES
#The number of messages in the mailbox.
#RECENT
#The number of messages with the Recent flag set.
#UIDNEXT
#The next unique identifier value of the mailbox.
#UIDVALIDITY
#The unique identifier validity value of the mailbox.
#UNSEEN
#The number of messages which do not have the Seen flag set.
#The status conditions must be formatted as a space separated string enclosed in parentheses, the encoding for a "list" in the IMAP4 specification.
	rv, data = M.list()
	if rv == 'OK':
		print 'Response code: ', rv
		print 'Mailbox Status: '
		for line in data:
			flags, delimiter, mailbox_name = parse_list_response(line)
			print M.status(mailbox_name, '(MESSAGES RECENT UIDVALIDITY UNSEEN)')

#--------------------------------------------------------------------------
#Selecting a Mailbox
#The basic mode of operation, once the client is authenticated, is to select a mailbox and then interrogate the server regarding messages in the 
#mailbox. The connection is stateful, so once a mailbox is selected all commands operate on messages in that mailbox until a new mailbox is 
#selected.
	rv, data = M.select('INBOX')
	if rv == 'OK':
		print 'Response code: ', rv
		print 'Response: '
		print data
		num_msgs = int(data[0])
		print 'There are %d messages in INBOX' % num_msgs

#--------------------------------------------------------------------------
#If an mailbox does not exist, The response code is NO
	rv, data = M.select('Some random name that im sure is not a mailbox')
	print 'Response code: ', rv
	print 'Response: '
	print data


#--------------------------------------------------------------------------
# Searching for Messages
# use search() to retrieve the ids of messages in the mailbox.
	
	rv, mailbox_data = M.list()
	print 'Response code: ', rv
	if rv == 'OK':
		for line in mailbox_data:
			flags, delimiter, mailbox_name = parse_list_response(line)
			M.select(mailbox_name, readonly=True)
			type, msg_ids = M.search(None, 'ALL')
			print mailbox_name, type, msg_ids
	
#--------------------------------------------------------------------------
# Search messages specific to their subject
	rv, mailbox_data = M.list()
	print 'Response code: ', rv
	if rv == 'OK':
			M.select('INBOX', readonly=True)
			typ, msg_ids = M.search(None, '(SUBJECT "Term Sheet")')
			print 'INBOX', typ, msg_ids
	'''
#--------------------------------------------------------------------------
#Fetching Messages
#The identifiers returned by search() are used to retrieve the contents, or partial contents, of messages for further processing via fetch(). fetch()
#takes 2 arguments, the message ids to fetch and the portion(s) of the message to retrieve.

	M.select('INBOX', readonly=True)
	typ, msg_data = M.fetch('5663', '(BODY.PEEK[HEADER])')
	pprint(msg_data)

#The response from the FETCH command starts with the flags, then indicates that there are 595 bytes of header data. The client contructs a tuple 
#with the response for the message, and then closes the sequence with a single string containing the ) the server sends at the end of the fetch 
#response. Because of this formatting, it may be easier to fetch different pieces of information separately, or to recombine the response and parse it
#yourself.
#--------------------------------------------------------------------------

	print 'Header'
	typ, msg_data = M.fetch('5663', '(BODY.PEEK[HEADER])')
	for response_part in msg_data:
		
		#checks to see if the response part is a tuple or not. isinstance is a built in python function.
		if isinstance(response_part, tuple):
			print response_part[1]

	print '\nBODY TEXT'
	typ, msg_data = M.fetch('5663', '(BODY.PEEK[TEXT])')
	for response_part in msg_data:
		if isinstance(response_part, tuple):
			print response_part[1]

			strings = str(response_part[1])

			fil = open("bodypeek.txt", "w")
			fil.write(response_part[1])
			fil.close()

	#etching values separately has the added benefit of making it easy to use ParseFlags() to parse the flags from the response.
	print '\nFLAGS'
	typ, msg_data = M.fetch('5663', '(FLAGS)')
	for response_part in msg_data:
		print response_part
		print imaplib.ParseFlags(response_part)

#--------------------------------------------------------------------------
# To fetch whole messages
	#RFC822 is the message. Im still not sure what the current standard is now.
	typ, msg_data = M.fetch('5663', 'RFC822')
	for response_part in msg_data:
		if isinstance(response_part, tuple):
			# Return a message object structure from a string
			msg = email.message_from_string(response_part[1])
			for header in ['subject', 'to', 'from']:
				print '%s: %s' % (header.upper(), msg[header])