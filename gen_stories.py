#!/usr/bin/env python3
"""Content file for the news-image-20261118 entry: Tuesday 18 November
2026's world news, reconstructed from named outlets actually read
(leaderboard top-3 images read in full + wire checks via web search).

Date discipline: every story below is an 18 Nov 2026 event. Excluded
on date grounds (they sit in the page's cutting-room box instead):
the Kerch Bridge span collapse (Tue 17 Nov), the Kemerovo An-12 crash
(Tue 17 Nov), Nvidia's quarterly results themselves (reported Tue
17 Nov; Wednesday's share moves are Wednesday's), Peltola's Alaska
Senate win, the Knesset speaker vote, the Prague train crash, the US
strike on Qeshm - all Tue 17 Nov per the leaders' own date-checks.
Not-yet items (Thu/Fri) are named as such in the footer box.

Corrections vs the leaders: Bangladesh garment stoppage is 535
factories (The Business Standard, BGMEA sources, 18 Nov), not the
"55 factories" REF1/REF2 print. The Van Gogh record (Sotheby's New
York, Wed 18 Nov, $190.4m with fees - Reuters) is missing from all
three leaders; it is a full dispatch here.
"""
import json
from pathlib import Path

# place, lat, lon, region, headline, summary, source
S = [
    # ---- dispatches (12 stories on 11 cards; Kyiv card carries two)
    ("Shenzhen, China", 22.54, 114.06, "asia",
     "Xi greets Trump on the tarmac as APEC opens in Shenzhen",
     "The Chinese and US presidents met face to face as the APEC summit opened in Shenzhen, with Putin also in town and a first three-way meeting set for Thursday.",
     "AP"),
    ("Kuwait City, Kuwait", 29.38, 47.99, "middle-east",
     "Iran fires on a US base in Kuwait; Bahrain intercepts hostile drones",
     "Iran fired on a US base in Kuwait overnight in the region's sharpest escalation in months; Bahrain said its defences intercepted hostile drones.",
     "Reuters"),
    ("Pasadena, California", 34.15, -118.14, "north-america",
     "Voyager 1 reaches one light-day from Earth",
     "At 10:16 UTC the probe's radio signals took a full day to reach Earth: 25.9 billion km out, a first for any human-made object.",
     "NASA JPL"),
    ("Kyiv, Ukraine", 50.45, 30.52, "europe",
     "Russia fires 141 drones at Ukraine in one night",
     "Kyiv says 126 drones were shot down; the strikes killed five people, four of them in Odesa's historic centre.",
     "AP"),
    ("Kerch Strait, Crimea", 45.31, 36.47, "europe",
     "Kerch Bridge shuts after a third strike in four days",
     "The bridge linking Crimea to Russia closed again after the third strike on it in four days.",
     "Reuters"),
    ("Brussels, Belgium", 50.85, 4.35, "europe",
     "EU offers Kyiv a €45bn loan for 2027",
     "Brussels offered Ukraine a €45bn loan for 2027, to be repaid only once Russia pays reparations for the invasion.",
     "Reuters"),
    ("Nuseirat, Gaza", 31.45, 34.39, "middle-east",
     "Israel makes its first ground push in central Gaza since the truce",
     "Israeli tanks crossed the Yellow Line toward Nuseirat in the first ground push since the truce; Palestinian officials said three people were killed.",
     "Reuters"),
    ("Washington, DC", 38.90, -77.04, "north-america",
     "Fed minutes point to more rate rises",
     "Federal Reserve minutes pointed to further rate rises ahead; the Dow fell 561 points while the Nasdaq rose 0.4%.",
     "Reuters"),
    ("New York, US", 40.71, -74.01, "north-america",
     "Anthropic prices the biggest IPO on record",
     "The AI company raised $81.3bn at $83 a share, above its guide range, in the largest IPO ever priced; trading starts Thursday.",
     "Reuters"),
    ("Odisha, India", 20.30, 85.80, "asia",
     "Cyclone Akvan turns toward India's Odisha coast",
     "The severe storm veered toward Odisha on Wednesday; nearly 50,000 people were moved to shelters ahead of a Friday landfall.",
     "IMD"),
    ("New York, US", 40.71, -74.01, "north-america",
     "Van Gogh sells for a record $190.4m at Sotheby's",
     "'Blossoming Chestnut Trees' (1890) sold for $190.4m with fees, an auction record for the artist, after a Nazi-era provenance settlement.",
     "Reuters"),
    ("Auckland, New Zealand", -36.85, 174.76, "oceania",
     "GTA VI's midnight launch begins in New Zealand",
     "The game went on sale at midnight in New Zealand, 13 years after GTA V, starting a global rollout that follows the time zones.",
     "Rockstar Games"),
    # ---- leg one: Asia & the Pacific briefs
    ("Dhaka, Bangladesh", 23.81, 90.41, "asia",
     "Wage protests halt 535 garment factories",
     "Production halted at around 535 garment factories as wage protests spread; 132 shut in Ashulia alone and two labour leaders were arrested (BGMEA sources).",
     "The Business Standard"),
    ("Chattogram, Bangladesh", 22.36, 91.78, "asia",
     "Protesters set fire to Yunus's ancestral home",
     "A mob set fire to the ancestral home of interim leader Muhammad Yunus in Chattogram late on Wednesday.",
     "Reuters"),
    ("Seoul, South Korea", 37.57, 126.98, "asia",
     "Kospi jumps 2% on chip shares",
     "South Korea's Kospi index jumped 2% as chip shares rallied.",
     "Yonhap"),
    ("Manila, Philippines", 14.60, 120.98, "asia",
     "Trump hails 'biggest' Philippine trade deal",
     "Trump hailed a new trade deal with the Philippines as the biggest yet during his Manila stop.",
     "AP"),
    ("Manila, Philippines", 14.60, 120.98, "asia",
     "Quad foreign ministers meet for the first time in two years",
     "The Quad's foreign ministers met in Manila for the first time in two years.",
     "Reuters"),
    ("Shenzhen, China", 22.54, 114.06, "asia",
     "Xi holds sideline meetings with Sheinbaum, Fujimori and Kast",
     "On the summit's sidelines Xi met Mexico's Sheinbaum, Peru's Fujimori and Chile's Kast.",
     "Xinhua"),
    ("Tokyo, Japan", 35.68, 139.69, "asia",
     "Takaichi meets Putin, a first since 2022",
     "Japan's Prime Minister Takaichi met Putin, a first for a Japanese leader since 2022.",
     "Kyodo"),
    ("Yongbyon, North Korea", 40.03, 125.75, "asia",
     "IAEA says North Korea extended its Yongbyon enrichment plant",
     "IAEA chief Grossi told the board on Wednesday that a further extension to the Yongbyon enrichment plant was externally complete by late October.",
     "Reuters"),
    ("Port Moresby, Papua New Guinea", -9.48, 147.15, "oceania",
     "Magnitude 6.0 earthquake strikes Papua New Guinea",
     "A magnitude 6.0 earthquake struck Papua New Guinea on Wednesday.",
     "USGS"),
    ("Suva, Fiji", -18.14, 178.44, "oceania",
     "Fiji declares a state of disaster over El Niño drought",
     "Prime Minister Rabuka's Wednesday address declared a national state of disaster over the El Niño drought and set aside FJ$20m for the response.",
     "Reuters"),
    ("Sydney, Australia", -33.87, 151.21, "oceania",
     "Tame Impala sweeps the ARIA Awards with seven wins",
     "Tame Impala won seven ARIA Awards in Sydney, including album of the year for Deadbeat.",
     "AAP"),
    ("Avarua, Cook Islands", -21.24, -159.78, "oceania",
     "Cyclone Xavier reaches Category 5",
     "Cyclone Xavier strengthened to Category 5 in the South Pacific.",
     "RNZ Pacific"),
    # ---- leg two: Europe, Africa, Middle East briefs
    ("London, UK", 51.51, -0.13, "europe",
     "UK inflation climbs to 3.6%",
     "UK inflation climbed to 3.6%, a one-year high, official figures showed.",
     "ONS"),
    ("Berlin, Germany", 52.52, 13.40, "europe",
     "Germany's coalition agrees a power-tax cut",
     "Germany's coalition agreed a cut to the electricity tax for households.",
     "Reuters"),
    ("Berlin, Germany", 52.52, 13.40, "europe",
     "Germany pledges air defences and F-16 arms for Kyiv",
     "Berlin pledged air defences and F-16 arms for Kyiv.",
     "Reuters"),
    ("Balabyne, Ukraine", 47.65, 35.35, "europe",
     "85 children ordered out of Balabyne",
     "Authorities ordered 85 children out of Balabyne, a frontline village in the Zaporizhzhia region.",
     "Reuters"),
    ("Krasnodar, Russia", 45.04, 38.98, "europe",
     "Ukraine hits two Krasnodar oil refineries",
     "Ukrainian drones hit two oil refineries in Russia's Krasnodar region.",
     "Reuters"),
    ("Addis Ababa, Ethiopia", 9.03, 38.74, "africa",
     "Ethiopia and Eritrea mass troops on their border",
     "Ethiopia and Eritrea massed troops along their shared border, raising fears of a new war.",
     "Reuters"),
    ("El Obeid, Sudan", 13.18, 30.22, "africa",
     "Amnesty says RSF drones killed 37 in El Obeid",
     "Amnesty International said RSF drones killed 37 people in El Obeid.",
     "Amnesty International"),
    ("Antalya, Türkiye", 36.88, 30.70, "europe",
     "COP31 split over a fossil-fuel phase-out",
     "COP31 in Antalya remained split over a fossil-fuel phase-out, with Friday the deadline for a deal.",
     "Reuters"),
    ("The Hague, Netherlands", 52.08, 4.30, "europe",
     "ICJ to deliver its Rohingya genocide ruling on Thursday",
     "The International Court of Justice set Thursday for its ruling in the Rohingya genocide case.",
     "ICJ"),
    ("Kinshasa, DR Congo", -4.32, 15.31, "africa",
     "WHO keeps DR Congo's Ebola outbreak a global emergency",
     "The WHO kept DR Congo's Ebola outbreak classified as a global emergency.",
     "WHO"),
    ("Maputo, Mozambique", -25.97, 32.58, "africa",
     "Exxon's $30bn Rovuma LNG project approved",
     "Mozambique approved Exxon's $30bn Rovuma LNG project.",
     "Reuters"),
    # ---- leg three: Americas briefs
    ("Ottawa, Canada", 45.42, -75.70, "north-america",
     "Carney and Xi agree tariff relief",
     "Canada's Carney and China's Xi agreed relief on tariffs in their Shenzhen meeting.",
     "Reuters"),
    ("Washington, DC", 38.90, -77.04, "north-america",
     "House Democrats pick Jeffries for Speaker, 251-11",
     "House Democrats picked Hakeem Jeffries as their Speaker nominee by 251 votes to 11, the first Black nominee; the full House votes on 3 January.",
     "AP"),
    ("Caracas, Venezuela", 10.48, -66.90, "south-america",
     "US and Venezuela announce a defence partnership",
     "After Hegseth's surprise trip to Caracas, the US and Venezuela announced a defence partnership with intelligence sharing.",
     "Al Jazeera"),
    ("Washington, DC", 38.90, -77.04, "north-america",
     "Rubio sees 'zero evidence' the power outages were an attack",
     "Secretary of State Rubio said there was 'zero evidence' the power outages were an attack.",
     "AP"),
    ("Jackson, Mississippi", 32.30, -90.18, "north-america",
     "Top US egg producer to cull 1.8m birds over bird flu",
     "The largest US egg producer said it would cull 1.8 million birds over bird flu.",
     "Reuters"),
    ("New York, US", 40.71, -74.01, "north-america",
     "Nvidia falls 2.9% after results; AMD jumps 5.3%",
     "Nvidia shares fell 2.9% in Wednesday trading after its results, while AMD jumped 5.3%.",
     "Reuters"),
    ("New York, US", 40.71, -74.01, "north-america",
     "Gold falls to a 14-month low under $3,750",
     "Gold fell to a 14-month low, dropping under $3,750 an ounce.",
     "Reuters"),
    ("Mexico City, Mexico", 19.43, -99.13, "north-america",
     "Sheinbaum says US trade talks are 'very far along'",
     "President Sheinbaum said Mexico's trade talks with the US were 'very far along'.",
     "Reuters"),
    ("Brasilia, Brazil", -15.79, -47.88, "south-america",
     "Senate passes Lula's $10bn fiscal package",
     "Brazil's Senate passed President Lula's $10bn fiscal package.",
     "Reuters"),
    ("Port-au-Prince, Haiti", 18.54, -72.34, "north-america",
     "Salvadoran troops raze a gang chief's house",
     "Salvadoran troops in Haiti razed a gang chief's house in Port-au-Prince.",
     "AP"),
    ("Bogotá, Colombia", 4.71, -74.07, "south-america",
     "US plans joint strikes on Colombian gangs",
     "The US set out a plan for joint strikes on Colombian gangs.",
     "AP"),
]

STATS = [
    {"value": "141", "label": "Russian drones fired at Ukraine in one night",
     "story_ref": "Russia fires 141 drones at Ukraine in one night"},
    {"value": "25.9bn km", "label": "Voyager 1's distance from Earth",
     "story_ref": "Voyager 1 reaches one light-day from Earth"},
    {"value": "$81.3bn", "label": "raised by Anthropic in its record IPO",
     "story_ref": "Anthropic prices the biggest IPO on record"},
    {"value": "$190.4m", "label": "record auction price for a Van Gogh",
     "story_ref": "Van Gogh sells for a record $190.4m at Sotheby's"},
    {"value": "251-11", "label": "House Democrats' vote for Jeffries",
     "story_ref": "House Democrats pick Jeffries for Speaker, 251-11"},
    {"value": "535", "label": "garment factories halted in Bangladesh",
     "story_ref": "Wage protests halt 535 garment factories"},
]


def sun_key(row):
    lon = row[2]
    return (0, -lon) if lon >= 0 else (1, -lon)


stories = []
for n, (place, lat, lon, region, headline, summary, source) in enumerate(
        sorted(S, key=sun_key)):
    stories.append({
        "n": n, "region": region, "place": place, "lat": lat, "lon": lon,
        "headline": headline, "detail": summary, "source": source,
        "summary": summary, "fact": headline,
    })

out = {"stories": stories, "stats": STATS}
p = Path(__file__).with_name("stories-18.json")
p.write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("wrote", p, "stories:", len(stories))
from collections import Counter
print(Counter(s["region"] for s in stories))
