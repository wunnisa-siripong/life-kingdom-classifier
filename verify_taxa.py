"""Build-time verification only; never called by the deployed app."""
import concurrent.futures, json, urllib.request, urllib.parse
from pathlib import Path

PLANTS = '''Mangifera indica
Oryza sativa
Zea mays
Triticum aestivum
Solanum lycopersicum
Solanum tuberosum
Capsicum annuum
Cucumis sativus
Cucurbita pepo
Citrullus lanatus
Carica papaya
Ananas comosus
Cocos nucifera
Durio zibethinus
Garcinia mangostana
Nephelium lappaceum
Psidium guajava
Artocarpus heterophyllus
Dimocarpus longan
Litchi chinensis
Vitis vinifera
Malus domestica
Prunus persica
Helianthus annuus
Arabidopsis thaliana
Nicotiana tabacum
Camellia sinensis
Coffea arabica
Theobroma cacao
Glycine max
Arachis hypogaea
Pisum sativum
Vigna radiata
Manihot esculenta
Hevea brasiliensis
Tectona grandis
Nelumbo nucifera
Ocimum tenuiflorum
Azadirachta indica
Bambusa vulgaris'''.splitlines()
ANIMALS = '''Homo sapiens
Felis catus
Canis lupus
Panthera tigris
Panthera leo
Ursus arctos
Ailuropoda melanoleuca
Giraffa camelopardalis
Equus caballus
Bos taurus
Bubalus bubalis
Sus scrofa
Capra hircus
Ovis aries
Oryctolagus cuniculus
Mus musculus
Rattus norvegicus
Danio rerio
Oreochromis niloticus
Cyprinus carpio
Apis mellifera
Bombyx mori
Drosophila melanogaster
Danaus plexippus
Aedes aegypti
Octopus vulgaris
Sepia officinalis
Lumbricus terrestris
Caenorhabditis elegans
Xenopus laevis'''.splitlines()
BASE = Path(__file__).resolve().parent
def get(url):
    with urllib.request.urlopen(url, timeout=45) as r:
        return json.load(r)
def verify(pair):
    name, kingdom = pair
    url = 'https://api.gbif.org/v1/species/match?name='+urllib.parse.quote(name)
    data = get(url)
    if data.get('matchType') != 'EXACT' or data.get('kingdom') != kingdom:
        return {'requested':name, 'excluded':True, 'match':data}
    key = data.get('acceptedUsageKey',data['usageKey'])
    names_url = f'https://api.gbif.org/v1/species/{key}/vernacularNames?limit=1000'
    names = get(names_url)
    return {'requested':name,'kingdom':kingdom,'match_url':url,'names_url':names_url,
            'match':data,'vernaculars':names,'verified_on':'2026-10-27'}
if __name__ == '__main__':
    pairs = [(n,'Plantae') for n in PLANTS]+[(n,'Animalia') for n in ANIMALS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(verify,pairs))
    (BASE/'taxon_verification.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
    print('Verified',sum(not r.get('excluded') for r in rows),'of',len(rows))
    for r in rows:
        if r.get('excluded'): print('EXCLUDED',r['requested'],r['match'])
