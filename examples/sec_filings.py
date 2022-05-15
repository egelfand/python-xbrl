from pathlib import Path
from xbrl import XBRLParser, GAAPSerializer
import requests
import edgar
import pandas as pd
import html_to_json

download_directory = 'C:\\Users\\Wiwaxia\\Downloads\\'
since_year = 2020
user_agent = 'Edgar oit@sec.gov'
edgar.download_index(download_directory, since_year, user_agent, skip_all_present_except_last=False)
d_file_glob = Path(download_directory).glob('*.tsv')
files = [x for x in d_file_glob]
test = pd.read_table(files[0], sep='|', header = None)
print(test.head())
sec_site = 'https://www.sec.gov/Archives/' + test.iloc[0, 5]
f = requests.get(sec_site, headers={'User-agent': user_agent})
result = f.text
# what forms get published for a given company and how comprehensive is the detail in those forms.
# form comes as xbrl, check if it's there. Mostly needs quarterly reporting but all is good. S8?

start_idx = result.find('class="tableFile" summary="Data Files"')
end_idx = result.find('<!-- END DOCUMENT DIV -->')
relevant_files = result[start_idx:end_idx]
filing_df = pd.DataFrame(columns=['description', 'document', 'doc_type'])
# print(relevant_files)
output_json = html_to_json.convert(relevant_files)
for x in output_json['tr']:
    if 'td' in list(x.keys()):
        desc = x['td'][1]['_value']
        doc = x['td'][2]['a'][0]['_attributes']['href']
        doc_type = x['td'][3]['_value']
        filing_df.loc[len(filing_df), filing_df.columns] = desc, doc, doc_type
# print(filing_df.head())

xrbl_instance = 'https://www.sec.gov/' + filing_df.loc[0, 'document']
# print(xrbl_instance)
xrbl_req = requests.get(xrbl_instance, headers= {'User-agent': user_agent})
filename = filing_df.loc[2, 'description'].replace(' ', '_')+'.xml'
# print(filename)
with open(filename, 'w+') as f:
    f.write(xrbl_req.text)

# pdb
xbrl_parser = XBRLParser(0)
xbrl = xbrl_parser.parse('XBRL_TAXONOMY_EXTENSION_CALCULATION_LINKBASE.xml')
# Parse just the GAAP data from the xbrl object
gaap_obj = xbrl_parser.parseGAAP(xbrl, ignore_errors=2)
# Serialize the GAAP data
serializer = GAAPSerializer()
result = serializer.dump(gaap_obj)
print(result)

