# R4 Audit Report — UP realism (Lane C)

## Deliverable paths

- `docs/research/R4-up-realism.md` (sections exactly: Findings, Recommendation for our build, Risks, Sources)
- `docs/research/up_districts.json` (exactly 20 UP districts; per-district source URL and source_record_id; synthetic_data_label)
- `docs/lanes/C-research/reports/R4-report.md` (this file)

## Files written

| File | Tool | Result |
|---|---|---|
| `docs/research/up_districts.json` | write_file | bytes_written 6396, verified true, lint ok |
| `docs/research/R4-up-realism.md` | write_file | bytes_written 20654, verified true |
| `docs/lanes/C-research/reports/` | terminal `mkdir -p` | REPORTS_DIR_READY, `docs/lanes/C-research/reports` |
| `docs/lanes/C-research/reports/R4-report.md` | write_file | this report |

No files outside Lane C's owned paths were modified. No pip/npm install was run.

## Commands run and real output

**Command A — fetch the coordinate source into scratch and check it (terminal):**

```
C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import urllib.request,json,os;u='https://raw.githubusercontent.com/open-admin-data/india-administrative-divisions/master/data/all-district.json';p=os.path.join(os.environ['TMPDIR'],'oad_all_district.json');urllib.request.urlretrieve(u,p);d=json.load(open(p,encoding='utf-8'));up=[x for x in d if x.get('parent',{}).get('name',{}).get('en')=='Uttar Pradesh'];print('TOTAL',len(d),'UP',len(up));print([(x['name']['en'],x['geo']['lat'],x['geo']['lon']) for x in up[:12]])"
```

Real output (exit_code 0):

```
TOTAL 635 UP 69
[('Kanpur Nagar', '26.298', '80.325'), ('Saharanpur', '29.897', '77.486'), ('Lucknow', '26.843', '80.907'), ('Kanpur Dehat', '26.437', '79.862'), ('Sultanpur', '26.274', '82.02'), ('Muzaffarnagar', '29.431', '77.478'), ('Jaunpur', '25.711', '82.568'), ('Mahoba', '25.32', '79.694'), ('Gautam Buddha Nagar', '28.508', '77.533'), ('Meerut', '29.021', '77.787'), ('Agra', '27.083', '78.01'), ('Bareilly', '28.44', '79.422')]
```

**Command B — list every UP record in the opened source, to choose the 20 districts (terminal):**

```
C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import json,os;d=json.load(open(os.path.join(os.environ['TMPDIR'],'oad_all_district.json'),encoding='utf-8'));up=[x for x in d if x.get('parent',{}).get('name',{}).get('en')=='Uttar Pradesh'];print('UP_COUNT',len(up));[print(x['name']['en'],'|',x['geo']['lat'],'|',x['geo']['lon'],'|',x['id']) for x in sorted(up,key=lambda y:y['name']['en'])]"
```

Real output (exit_code 0):

```
UP_COUNT 69
Agra | 27.083 | 78.01 | IN19D011
Aligarh | 27.93 | 78.07 | IN19D022
Allahabad | 25.342 | 82.021 | IN19D048
Ambedkar Nagar | 26.426 | 82.624 | IN19D050
Auraiya | 26.66 | 79.483 | IN19D042
Ayodhya | 26.64 | 82.078 | IN19D018
Azamgarh | 26.003 | 83.077 | IN19D060
Baghpat | 29.09 | 77.309 | IN19D029
Bahraich | 27.708 | 81.482 | IN19D051
Ballia | 25.904 | 84.033 | IN19D062
Balrampur | 27.504 | 82.352 | IN19D053
Banda | 25.465 | 80.555 | IN19D045
Bara Banki | 26.948 | 81.327 | IN19D049
Bareilly | 28.44 | 79.422 | IN19D012
Basti | 26.794 | 82.637 | IN19D056
Bijnor | 29.357 | 78.406 | IN19D027
Budaun | 28.167 | 78.886 | IN19D013
Bulandshahr | 28.393 | 77.978 | IN19D030
Chandauli | 24.943 | 83.212 | IN19D064
Chitrakoot | 25.2 | 81.096 | IN19D023
Deoria | 26.458 | 83.753 | IN19D059
Etah | 27.509 | 78.767 | IN19D068
Etawah | 26.805 | 79.132 | IN19D016
Farrukhabad | 27.403 | 79.487 | IN19D040
Fatehpur | 25.876 | 80.769 | IN19D046
Firozabad | 27.175 | 78.545 | IN19D024
Gautam Buddha Nagar | 28.508 | 77.533 | IN19D009
Ghaziabad | 28.757 | 77.575 | IN19D025
Ghazipur | 25.623 | 83.601 | IN19D063
Gonda | 27.08 | 81.988 | IN19D054
Gorakhpur | 26.68 | 83.366 | IN19D026
Hardoi | 27.328 | 80.123 | IN19D038
Jalaun | 26.09 | 79.336 | IN19D043
Jaunpur | 25.711 | 82.568 | IN19D007
Jhansi | 25.587 | 79.149 | IN19D020
Jyotiba Phule Nagar | 28.876 | 78.284 | IN19D017
Kannauj | 27.025 | 79.695 | IN19D041
Kanpur Dehat | 26.437 | 79.862 | IN19D004
Kanpur Nagar | 26.298 | 80.325 | IN19D001
Kansiram Nagar | 27.759 | 78.82 | IN19D069
Kaushambi | 25.472 | 81.449 | IN19D047
Kheri | 28.171 | 80.667 | IN19D036
Kushinagar | 26.906 | 83.891 | IN19D021
Lalitpur | 24.65 | 78.521 | IN19D044
Lucknow | 26.843 | 80.907 | IN19D003
Mahamaya Nagar | 27.614 | 78.13 | IN19D031
Maharajganj | 27.236 | 83.567 | IN19D058
Mahoba | 25.32 | 79.694 | IN19D008
Mainpuri | 27.193 | 79.03 | IN19D033
Mathura | 27.596 | 77.601 | IN19D032
Mau | 26.013 | 83.533 | IN19D061
Meerut | 29.021 | 77.787 | IN19D010
Mirzapur | 25.021 | 82.627 | IN19D066
Moradabad | 28.585 | 78.647 | IN19D028
Muzaffarnagar | 29.431 | 77.478 | IN19D006
Pilibhit | 28.525 | 79.933 | IN19D034
Rae Bareli | 26.208 | 81.278 | IN19D015
Rampur | 28.807 | 79.149 | IN19D014
Saharanpur | 29.897 | 77.486 | IN19D002
Sant Kabir Nagar | 26.866 | 83.016 | IN19D057
Sant Ravi Das Nagar(bhadohi) | 25.349 | 82.468 | IN19D065
Shahjahanpur | 27.919 | 79.809 | IN19D035
Shrawasti | 27.676 | 81.884 | IN19D052
Siddharth Nagar | 27.261 | 82.908 | IN19D055
Sitapur | 27.516 | 80.813 | IN19D037
Sonbhadra | 24.385 | 83.061 | IN19D067
Sultanpur | 26.274 | 82.02 | IN19D005
Unnao | 26.636 | 80.51 | IN19D039
Varanasi | 25.388 | 82.891 | IN19D019
```

**Command C — REQUIRED PROOF: JSON validation and per-district print (terminal, workdir `C:/Users/shubh/Projects/sewacircle`):**

```
C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import json;d=json.load(open('docs/research/up_districts.json',encoding='utf-8'));ds=d['districts'];assert len(ds)==20, len(ds);assert all(23.5<=x['lat']<=30.5 and 77<=x['lon']<=84.5 for x in ds);print('VALIDATED district_count=',len(ds));[print(x['name'],'| lat',x['lat'],'| lon',x['lon'],'|',x['source_record_id']) for x in ds]"
```

Real output (exit_code 0):

```
VALIDATED district_count= 20
Lucknow | lat 26.843 | lon 80.907 | IN19D003
Kanpur Dehat | lat 26.437 | lon 79.862 | IN19D004
Kanpur Nagar | lat 26.298 | lon 80.325 | IN19D001
Varanasi | lat 25.388 | lon 82.891 | IN19D019
Gorakhpur | lat 26.68 | lon 83.366 | IN19D026
Agra | lat 27.083 | lon 78.01 | IN19D011
Meerut | lat 29.021 | lon 77.787 | IN19D010
Allahabad | lat 25.342 | lon 82.021 | IN19D048
Azamgarh | lat 26.003 | lon 83.077 | IN19D060
Ballia | lat 25.904 | lon 84.033 | IN19D062
Basti | lat 26.794 | lon 82.637 | IN19D056
Bareilly | lat 28.44 | lon 79.422 | IN19D012
Gonda | lat 27.08 | lon 81.988 | IN19D054
Jhansi | lat 25.587 | lon 79.149 | IN19D020
Mirzapur | lat 25.021 | lon 82.627 | IN19D066
Saharanpur | lat 29.897 | lon 77.486 | IN19D002
Sonbhadra | lat 24.385 | lon 83.061 | IN19D067
Sultanpur | lat 26.274 | lon 82.02 | IN19D005
Unnao | lat 26.636 | lon 80.51 | IN19D039
Gautam Buddha Nagar | lat 28.508 | lon 77.533 | IN19D009
```

**Command D — create reports directory:**

```
mkdir -p docs/lanes/C-research/reports && echo REPORTS_DIR_READY && ls -d docs/lanes/C-research/reports
```

Real output (exit_code 0):

```
REPORTS_DIR_READY
docs/lanes/C-research/reports
```

**Other tool calls (not shell commands), with real outcomes:**

- `browser_exec` on the Lucknow Hindi tehsil page: `wait_for_load()` then `js("document.body.innerText.slice(0,2500)")` returned the five tehsil names (सदर, सरोजनी नगर, बख्शी का तालाब, मलीहाबाद, मोहनलाल गंज) and footer "पिछला संशोधन: 27.01.2026".
- `search_files` on the saved YAS Annual Report text for `Literacy|literacy|health camp|Health|Blood Donation|Disaster|shramdaan|Plantation`: total_count 10 (lines 717, 789, 1117, 1170, 1175, 1221, 1371, 1375, 1504, 1514).
- `read_file` on that saved text at offsets 1160 and 1360 returned the NYKS activity table (Blood Donation, Health Check-up Camps, etc.) and NSS core activity categories (adult literacy; immunisation, blood donation, health education; plantation, street/drain cleaning; social service).
- `search_files` on that saved text for `District Youth Coordinator|NYKS has its presence|100 student volunteers|Programme Officer|SLO|National Youth Corps`: total_count 11.
- `search_files` for `*LSI*` and for `80.16|38,50,906|38, 50,906` in the web cache: total_count 0 for both — the LSI PDF extract did not expose those numbers, so they were not used.
- All `web_extract` and `web_search` calls are enumerated in the next two sections with their URLs/queries and outcomes.

## Web searches run (14 queries)

1. `Uttar Pradesh districts latitude longitude centroid csv github` — found Open Admin Data repository, COVID district CSV gist.
2. `site:kanpurdehat.nic.in blocks tehsils Kanpur Dehat district` — organisation chart, tehsil and blocks pages.
3. `site:lucknow.nic.in tehsil blocks Lucknow district administration` — CDO block list.
4. `site:varanasi.nic.in blocks tehsils Varanasi district` — administrative setup, DEO portal.
5. `site:gorakhpur.nic.in blocks tehsils Gorakhpur district` — subdivisions/blocks, blocks pages.
6. `site:yas.nic.in National Service Scheme NSS District Youth Officer NYKS District Youth Coordinator structure` — YAS annual reports and NYKS PDFs.
7. `site:mybharat.gov.in skill categories volunteers shramdaan blood donation literacy plantation` — youth profiles, ELP, Seva Sankalp, blood donation.
8. `Uttar Pradesh Census 2011 language speakers Hindi Awadhi Bhojpuri Urdu percentage official` — Census C-16, LSI PDF, Wikipedia.
9. `site:varanasi.nic.in "development blocks" Arajiline Cholapur ...` — DEO/Hindi education pages.
10. `site:lucknow.nic.in tehsil Malihabad Kakori Mohanlalganj Lucknow subdivision` — Hindi tehsil page.
11. `MY Bharat volunteer age limit 15 29 years official NSS volunteer age 15 30` — Digital India, NeGD press note, NYKS eligibility PDF.
12. `site:varanasi.nic.in block Kashi Vidyapeeth Cholapur Arajiline Chiraigaon Harhua Pindra ...` — confirmed named blocks.
13. `site:mybharat.gov.in "SKILLS" "LEADERSHIP SKILLS" volunteer skill categories registration` — youth profile skill strings.
14. `site:mybharat.gov.in disaster relief camp flood volunteer event Uttar Pradesh MY Bharat` — NSS/NDRF disaster event, Lucknow disaster training listing.

## Pages opened (30 URL attempts; 28 yielded usable content)

| # | Title | URL | Date shown / accessed |
|---|---|---|---|
| 1 | Districtwise_India.csv (Gist page) | https://gist.github.com/meghamodi/6a49554f26b3d5b7097a9f08841e4241 | accessed 2026-11-18 |
| 2 | Open Admin Data repository README | https://github.com/open-admin-data/india-administrative-divisions | updated 2026-08-20; accessed 2026-11-18 |
| 3 | Open Admin Data all-district.json | https://raw.githubusercontent.com/open-admin-data/india-administrative-divisions/master/data/all-district.json | updated 2026-08-20; accessed 2026-11-18 |
| 4 | GitHub Gist API metadata (raw CSV URL) | https://api.github.com/gists/6a49554f26b3d5b7097a9f08841e4241 | accessed 2026-11-18 |
| 5 | Development Blocks — Kanpur Dehat | https://kanpurdehat.nic.in/subdivision-blocks/ | accessed 2026-11-18 |
| 6 | Tehsil — Kanpur Dehat | https://kanpurdehat.nic.in/tehsil/ | accessed 2026-11-18 |
| 7 | Organisation Chart — Kanpur Dehat | https://kanpurdehat.nic.in/organisation-chart/ | accessed 2026-11-18 |
| 8 | Office of CDO — Lucknow | https://lucknow.nic.in/details-of-officers-posted-in-district-development-block/ | accessed 2026-11-18 |
| 9 | तहसील का नाम — Lucknow | https://lucknow.nic.in/hi/%E0%A4%A4%E0%A4%B9%E0%A4%B8%E0%A5%80%E0%A4%B2-%E0%A4%95%E0%A4%BE-%E0%A4%A8%E0%A4%BE%E0%A4%AE/ | footer 27.01.2026; accessed 2026-11-18 |
| 10 | Administrative Setup — Varanasi | https://varanasi.nic.in/administrative-setup/ | accessed 2026-11-18 |
| 11 | DEO Portal — Varanasi | https://varanasi.nic.in/deo-portal/ | accessed 2026-11-18 |
| 12 | शिक्षा — Varanasi | https://varanasi.nic.in/hi/%E0%A4%B6%E0%A4%BF%E0%A4%95%E0%A5%8D%E0%A4%B7%E0%A4%BE/ | accessed 2026-11-18 |
| 13 | Subdivisions & Blocks — Gorakhpur | https://gorakhpur.nic.in/subdivisions-blocks/ | accessed 2026-11-18 |
| 14 | Blocks — Gorakhpur | https://gorakhpur.nic.in/blocks/ | accessed 2026-11-18 |
| 15 | MY Bharat Youth Public Profile | https://mybharat.gov.in/ypp/youth-public-profile/ | accessed 2026-11-18 |
| 16 | MY Bharat sample profile (rajat kumar) | https://mybharat.gov.in/ypp/youth-public-profile/details/rajat48360 | accessed 2026-11-18 |
| 17 | NSS 7-Days Special Camp 2026-27 | https://mybharat.gov.in/elp/listing/158448 | event 15–21 Oct 2026; accessed 2026-11-18 |
| 18 | Seva Sankalp Abhiyan, Pilibhit | https://mybharat.gov.in/vo/pages/event_detail?event_name=Seva-Sankalp-Abhiyan-aewam-Seva-Pakhwara&key=510216192510 | event 2026; accessed 2026-11-18 |
| 19 | Blood Donation Camp events page | https://mybharat.gov.in/mega_events/blood-donation-camp-07/events | page last updated 18-11-2026 |
| 20 | Disaster awareness/preparedness session | https://mybharat.gov.in/vo/pages/event_detail?event_name=Disaster&key=115214641240 | event 2026; accessed 2026-11-18 |
| 21 | NSS Day 2026, National P.G. College, Lucknow | https://mybharat.gov.in/vo/pages/event_detail?event_name=NSS-DAY-2026-at-National-PG-College&key=510219004510 | event 23 Sep 2026; accessed 2026-11-18 |
| 22 | Community Engagement (MY Bharat) | https://mybharat.gov.in/pages/ce?mode=A | extraction FAILED (timeout); not used |
| 23 | MY Bharat — Digital India initiative page | https://www.digitalindia.gov.in/initiative/my-bharat/ | launched 31 Oct 2023; accessed 2026-11-18 |
| 24 | YAS Annual Report 2013-14 | https://yas.nic.in/sites/default/files/Annual%20Report13-14.pdf | published 2013-14; accessed 2026-11-18 |
| 25 | NYKS document nyks_0.pdf | https://www.yas.nic.in/sites/default/files/nyks_0.pdf | extraction FAILED (timeout); not used |
| 26 | Census C-16 mother tongue, UP 2011 | https://censusindia.gov.in/nada/index.php/catalog/10224 | 2011; accessed 2026-11-18 |
| 27 | Linguistic Survey of India — UP | https://censusindia.gov.in/nada/index.php/catalog/45240/download/48950/LSI_UTTAR_PRADESH.pdf | no date shown; accessed 2026-11-18 |
| 28 | Languages of Uttar Pradesh | https://en.wikipedia.org/wiki/Languages_of_Uttar_Pradesh | accessed 2026-11-18 |
| 29 | Uttar Pradesh | https://en.wikipedia.org/wiki/Uttar_Pradesh | published 2026-11-01; accessed 2026-11-18 |
| 30 | NeGD Ask Our Experts Episode 51 press note | https://negd.gov.in/wp-content/uploads/2026/10/PR_Ep-51_NSS_V1.pdf | episode 6 Aug 2026; accessed 2026-11-18 |

## Counts

- Web search queries: **14**
- Page-open attempts: **30**; usable pages opened: **28** (2 extraction failures: MY Bharat Community Engagement, YAS `nyks_0.pdf`)
- Distinct URLs with usable content (distinct sources): **28**
- Distinct source hosts: **14** (raw.githubusercontent.com, github.com, api.github.com, gist.github.com, kanpurdehat.nic.in, lucknow.nic.in, varanasi.nic.in, gorakhpur.nic.in, mybharat.gov.in, digitalindia.gov.in, yas.nic.in, censusindia.gov.in, en.wikipedia.org, negd.gov.in)
- Official/government primary URLs among usable pages: **21** (4 UP district administration sites, MY Bharat, Digital India, YAS, Census of India, NeGD); these represent at least **3 independent primary bodies**: UP district administrations (NIC), Census of India/ORGI, and Ministry of Youth Affairs & Sports / Digital India / NeGD.
- Districts in delivered JSON: **20** (asserted by Command C); coordinate bounding box asserted: lat 23.5–30.5, lon 77–84.5; all 20 rows passed.
- Skill taxonomy entries proposed: **24**; per the delivered table, **21** rows are anchored to observed official-platform strings or activities and **3** are marked inferred (`first_aid`, `crowd_safety`, `translation`). 21 + 3 = 24.

## UNRESOLVED items

- **Centroid method:** Open Admin Data does not state how its district points were produced; they are documented in our deliverables as approximate locator points, not verified centroids. A true polygon-centroid source was NOT FOUND in this pass.
- **Coverage:** the coordinate source has 69 UP rows while Wikipedia says 75 districts; our file is an intentional 20-row demo slice. The 55 omitted districts are not denied to exist.
- **Gorakhpur block count:** official prose says 19 blocks; the official blocks table has 20 rows including Bharohiya. Left flagged; Bharohiya excluded from demo recommendations.
- **Varanasi exhaustive block list:** 3 tehsils and 8 blocks are confirmed, but a single official page enumerating all 8 blocks was NOT FOUND; only named blocks seen on official pages are recommended.
- **Language percentages:** a numeric 2011 share for Hindi/Awadhi was NOT retrievable from the opened Census LSI PDF or the opened Wikipedia pages; only Bhojpuri ~11%, Urdu ~5.4%, Punjabi 0.3%, Bengali 0.1% and Hindi "most widely spoken" were used as FACT. All synthetic language shares remain INFERENCE.
- **Age distribution:** no measured within-15–29 histogram found; synthetic skew is INFERENCE.
- **Two fetch failures:** `nyks_0.pdf` and MY Bharat Community Engagement page timed out; NYKS structure was taken from the opened YAS Annual Report instead. No claim relies on the failed pages.
- **Skill vocabulary:** MY Bharat profiles are user-entered with an on-page disclaimer; there is no official closed skill list on the opened pages, so the 24-skill taxonomy is explicitly our proposal.
