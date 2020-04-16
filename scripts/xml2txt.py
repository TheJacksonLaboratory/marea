import xml.etree.ElementTree as ET
import sys
import gzip

tree = ET.parse(gzip.open(sys.argv[1]))
root = tree.getroot()

parsed = []

for article in root:
	for elem in article.iter('PMID'):
		id = elem.text

	string = f'{id}; '		

	descriptorPresent = False
	for heading in article.iter('DescriptorName'):
		string += f"{heading.get('UI')} {heading.text} {heading.get('MajorTopicYN')} | "
		descriptorPresent = True

	if not descriptorPresent:
		string += '; '
	else:
		string = f'{string[:-3]}; ' # eliminate the final | separator

	keywordPresent = False
	for keyword in article.iter('Keyword'):
		string += f'{keyword.text}, '
		keywordPresent = True

	if not keywordPresent:
		string += '; '
	else:
		string = f'{string[:-2]}; '

	for abstract in article.iter('AbstractText'):
		string += f'{abstract.text} '
	
	parsed.append(string)

f = open(f'{sys.argv[1].replace("xml.gz","txt")}', 'w')
for string in parsed:
	f.write(f'{string}\n')
f.close()
