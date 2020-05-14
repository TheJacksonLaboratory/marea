import xml.etree.ElementTree as ET
import sys
import gzip


def sanitize(string):
	"""
	Remove whitespace from ends of the string, and replace any line breaks
	within the string by a single space.
	:param string: string to be cleaned up
	:return: sanitized string
	"""
	retval = string.strip()
	# eliminate line breaks within the string
	return " ".join(retval.splitlines())


tree = ET.parse(gzip.open(sys.argv[1]))
root = tree.getroot()

parsed = []

for article in root:
	for elem in article.iter('PMID'):
		id = elem.text

	string = f'{id}## '

	year = 'unknown'
	# TODO: compare PubDate to PubMedPubDate if any, ArticleDate if any,
	# take the earliest date see head1015
	for pdate in article.iter('PubDate'):
		child = pdate.find('Year')
		if child is not None:
			year = child.text
		else:
			child = pdate.find('MedlineDate')
			if child is not None:
				year = child.text.split()[0]
	string += f'{year}## '

	descriptorPresent = False
	for heading in article.iter('DescriptorName'):
		if heading.text is not None:
			string += \
				f"{heading.get('UI')} {sanitize(heading.text)} {heading.get('MajorTopicYN')} | "
			descriptorPresent = True

	if not descriptorPresent:
		string += '## '
	else:
		string = f'{string[:-3]}## '  # eliminate the final | separator

	keywordPresent = False
	for keyword in article.iter('Keyword'):
		if keyword.text is not None:
			string += f"{sanitize(keyword.text)} {keyword.get('MajorTopicYN')} | "
		keywordPresent = True

	if not keywordPresent:
		string += '## '
	else:
		string = f'{string[:-3]}## '

	# TODO: get rid of "OtherAbstract" foreign language text
	for abstract in article.iter('AbstractText'):
		if abstract.text is not None:
			string += f'{sanitize(abstract.text)} '
	
	parsed.append(string)

f = open(f'{sys.argv[1].replace("xml.gz","txt")}', 'w')
for string in parsed:
	f.write(f'{string}\n')
f.close()
