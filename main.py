from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import csv

f = open('sra_data.csv', 'w')
writer = csv.writer(f)

headers = ['Accession number', 'Source', 'Tissue', 'Development stage', 'Country']

writer.writerow(headers)
f.close()


def uid_fetcher():
    main_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
    query = 'db=sra&term=solanum+tuberosum+AND+"biomol rna"[Properties]&retmax=4000&retmode=json'

    url = main_url + query

    resp = requests.post(url)
    data = resp.json()

    ids = data["esearchresult"]["idlist"]

    return ids


def uid_searcher(id_):
    url = f'https://www.ncbi.nlm.nih.gov/sra/?term={id_}[uid]'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'xml')
    accession_number = soup.find('p', class_='details expand e-hidden').find('a').get_text()

    sample_link = f"https://www.ncbi.nlm.nih.gov/{soup.find('a', title='Link to BioSample')['href']}"
    resp1 = requests.get(sample_link)
    soup1 = BeautifulSoup(resp1.content, 'xml')
    all_info = soup1.find('table', class_='docsum').find_all('tr')
    age, dev_stage, country, tissue, source = '', '', '', '', ''
    for info in all_info:
        if info.find('th').get_text() == 'development stage':
            dev_stage = info.find("td").get_text().strip()
        if info.find('th').get_text() == 'geographic location':
            country = info.find("td").get_text().strip()
        if info.find('th').get_text() == 'tissue':
            tissue = info.find("td").get_text().strip()
    strategy = soup.find('div', class_='expand showed sra-full-data').find('div').find_all('div')
    for row in strategy:
        if 'Strategy' in row.get_text():
            source = row.find('span').get_text().strip()

    '''run_link = f"https:{soup.find('table').find('a')['href']}"
        print(run_link)
        resp2 = requests.get(run_link)
        soup2 = BeautifulSoup(resp2.content, 'xml')
        all_org = soup2.find('div', class_='ph taxon_analysis').find('script').find_next_sibling('script')
        print(all_org.prettify())
        virus_percent = ''
        for virus in all_org_span:
            if 'Viruses: ' in all_org_span:
                virus_percent = virus.get_text()
        print(virus_percent)'''

    columns = [accession_number, source, tissue, dev_stage, country]
    with open('sra_data.csv', 'a') as f_:
        writer_ = csv.writer(f_)
        writer_.writerow(columns)


def multi_threaded():
    jobs_ = uid_fetcher()
    with ThreadPoolExecutor() as executor:
        executor.map(uid_searcher, jobs_)


multi_threaded()
