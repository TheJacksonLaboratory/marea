import xml.etree.ElementTree as ET
import sys

tree = ET.parse(sys.argv[1])
root = tree.getroot()

parsed = []

for article in root:
	for elem in article.iter('PMID'):
		id = elem.text

	string = f'{id}; '		

	descriptorPresent = False
	for heading in article.iter('DescriptorName'):
		string += f'{heading.text}, '
		descriptorPresent = True

	if descriptorPresent == False:
		string += '; '
	else:
		string = f'{string[:-2]}; '

	keywordPresent = False
	for keyword in article.iter('Keyword'):
		string += f'{keyword.text}, '
		keywordPresent = True

	if keywordPresent == False:
		string += '; '
	else:
		string = f'{string[:-2]}; '

	for abstract in article.iter('AbstractText'):
		string += f'{abstract.text} '
	
	parsed.append(string)

f = open(f'{sys.argv[1][:-3]}txt', 'w')
for string in parsed:
	f.write(f'{string}\n')
f.close()
