# -*- coding: utf-8 -*-

import sys
import os
import optparse

VERSION = "1.0"



"""

VCARD PART

"""

import vobject


def read_vcard(vcard_path):
	""" read the vcard file and extract contacts from it """

	# open/read the input file
	vcard_data = None
	try:
		vcard_data = open(vcard_path, "rb").read()
	except:
		print("[-] open %s failed" % vcard_path)
		return None

	vcard_data = vcard_data.decode('utf-8', 'ignore')

	# use the vobject library to parse the input file data
	vcard_list = vobject.readComponents(vcard_data)
	contacts = []

	for vcard in vcard_list:
		new_contact = {}

		# contact name
		new_contact['name'] = vcard.contents['fn'][0].value

		# addresses
		new_contact['adr'] = []
		if 'adr' in vcard.contents: 
			for adr in vcard.contents['adr']:
				new_contact['adr'].append(str(adr.value))

		# phone numbers
		new_contact['tel'] = []
		if 'tel' in vcard.contents: 
			for tel in vcard.contents['tel']:
				t = tel.value
				if "TYPE" in tel.params:
					typ = tel.params["TYPE"][0]
					if typ in conversion:
						t += " (%s)" % conversion[typ]
					else:
						t += " (%s)" % typ
				new_contact['tel'].append(t)

		# email
		new_contact['email'] = []
		if 'email' in vcard.contents: 
			for email in vcard.contents['email']:
				new_contact['email'].append(str(email.value))

		# photo
		new_contact['photo'] = ""
		if 'photo' in vcard.contents:
			new_contact['photo'] = vcard.contents['photo'][0].value

		contacts.append(new_contact)

	print("[+] %d contact(s) found" % len(contacts))
	return contacts


"""

	HTML PART 

"""

import cgi
import base64

conversion = {
	"HOME" : "maison",
	"CELL" : "mobile",
	"WORK" : "travail"
}

css_data = """
body {
	background-color: #e8f9ea;
	font-family: Arial,sans-serif;
}

.contact {
	float: left;
	margin: 5px;
	padding: 5px;
	background-color: #c4fcca;
	height: 125px;
}
.contact:hover {
    background-color: yellow;
}

.photo {
	float: left;
}

.photo_img {
	width: 100px;
	height: 100px;
}

.description {
	float: left;
	margin-left: 5px;
}

.name {
	font-weight: bold;
	margin-bottom: 5px;
}

.elt {
	margin-bottom: 2px;
	clear: both;
}

.elt_title {
	color: gray;
	float: left;
	font-style: italic;
	margin-right: 5px;
}

.elt_data {

}
"""

template = """<!DOCTYPE html>
<html>
	<head>
		<title>CONTACTS</title>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<style>%s</style>
	</head>
<body>
	<div class="contact_list">
		%s
		<div style="clear:both">
	</div>
</body>
"""

template_one_entry = """
		<div class="contact">
			<div class="name">
				%s
			</div>
			<div class="photo">
				%s
			</div>
			<div class="description">
				<div class="elt">
					<div class="elt_title">
						tel:
					</div>
					<div class="elt_data">
						%s
					</div>
				</div>
				<div class="elt">
					<div class="elt_title">
						email:
					</div>
					<div class="elt_data">
						%s
					</div>
				</div>
				<div class="elt">
					<div class="elt_title">
						adr:
					</div>
					<div class="elt_data">
						%s
					</div>
				</div>
			</div>
		</div>
"""

def _escape(text):
	out = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
	out = out.decode('utf8')
	return out



def convert2html(contacts, output_path):
	""" generate an HTML file using the input vcard file """

	html_content = ""
	for contact in contacts:
		name = contact['name']
		tel = ", ".join(contact['tel'])
		adr = ", ".join(contact['adr'])
		email = ", ".join(contact['email'])
		photo = ""
		if contact['photo']:
			photo_data = base64.b64encode(contact['photo'])
			photo_data = photo_data.decode('utf8')
			photo = "<img src='data:image/jpeg;base64,%s' class='photo_img' />" % photo_data

		html_content += template_one_entry % (_escape(name), photo, tel, email, _escape(adr))

	html = template % (css_data, html_content)
	html = html.encode('utf8')

	try:
		open(output_path, "wb").write(html)
		print("[+] %d bytes written into %s" % (len(html), output_path))
	except Exception as e:
		print("[-] failed to write the html data in %s" % output_path)
		print("  [-] %s" % e)


"""

	CSV PART

"""

def convert2csv(contacts, output_path):
	""" generate an HTML file using the input vcard file """

	print("[!] not implemented yet")


"""
	MAIN
"""

def _main():
	parser = optparse.OptionParser(version=VERSION, usage="%s: [option] <vcard_filepath>" % sys.argv[0], description="Convert a VCard file nto a csv file or an HTML web page")
	parser.add_option("--html", action="store_true", dest="html", default=False, help="convert the input vcard into an HTML")
	parser.add_option("--csv", action="store_true", dest="csv", default=False, help="convert the input vcard into a CSV file")
	(options, args) = parser.parse_args()

	if len(args) != 1 or (not options.html and not options.csv):
		print(parser.print_help())
		return

	print("%s - %s" % (sys.argv[0], VERSION))

	vcard_path = args[0]
	contacts = read_vcard(vcard_path)
	if contacts is None:
		print("[-] read vcard failed")
		return

	if options.html:
		output_file = os.path.splitext(vcard_path)[0] + ".html"
		convert2html(contacts, output_file)
	if options.csv:
		output_file = os.path.splitext(vcard_path)[0] + ".html"
		convert2csv(contacts, output_file)

	print("Done.")


if __name__ == "__main__":
	_main()