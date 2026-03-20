import xml.etree.ElementTree as ET
import pandas as pd

def parse_nyc_hedge_funds(xml_file_path):
    """
    Parses the SEC's bulk Investment Adviser XML file to find NYC hedge funds
    with $10M - $1000M in AUM.
    """
    print("Parsing SEC XML... this might take a moment.")
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    target_funds = []
    
    # The SEC XML groups each registered entity under a <Firm> tag
    print("Found firms: ", len(root.findall('.//Firm')))
    for firm in root.findall('.//Firm'):
        info = firm.find('Info')
        if info is None: 
            continue
            
        # 1. Location Filter: Isolate New York City
        main_addr = firm.find('MainAddr')
        if main_addr is None:
            continue

        city = main_addr.get('City', '').strip().upper()
        state = main_addr.get('State', '').strip().upper()
        if city != 'NEW YORK' or state != 'NY':
            continue
            
        # 2. AUM Filter: Extract Regulatory Assets Under Management (Item 5.F)
        aum_element = firm.find('.//Item5F')
        if aum_element is None: 
            continue
            
        try:
            # Q5F2C represents total regulatory AUM in US dollars
            aum_dollars = float(aum_element.get('Q5F2C', 0)) 
        except ValueError:
            aum_dollars = 0.0
            
        aum_millions = aum_dollars / 1_000_000
        
        if not (10 <= aum_millions <= 1000):
            continue
            
        # 3. Strategy Filter: Check if they advise Private Funds (Item 7.B)
        private_fund = firm.find('.//Item7B')
        if private_fund is None or private_fund.get('Q7B', 'N') == 'N':
            continue

        # 4. Website Filter: Extract Websites
        web_addrs = []
        web_addr_elements = firm.findall('.//FormInfo/Part1A/Item1/WebAddrs/WebAddr')
        for addr in web_addr_elements:
            if addr.text:
                web_addrs.append(addr.text.strip())
        
        website = ", ".join(web_addrs) if web_addrs else 'N/A'

        # Compile the target
        target_funds.append({
            'Firm Name': info.get('LegalNm'),
            'CRD Number': info.get('FirmCrdNb'), # Unique SEC identifier
            'AUM (Millions)': round(aum_millions, 2),
            'Website': website
        })
        
    return pd.DataFrame(target_funds)

def df_to_markdown(df):
    """ Converts a pandas DataFrame to a Markdown table string """
    columns = df.columns.tolist()
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(val) for val in row) + " |")
    return "\n".join([header, separator] + rows)

# Usage: Replace the string with the name of the file you downloaded
df_funds = parse_nyc_hedge_funds("data.xml")

# Sort the targets by AUM and print
df_funds_sorted = df_funds.sort_values(by="AUM (Millions)", ascending=False)
print(df_funds_sorted.to_string(index=False))
df_funds_sorted.to_csv("hedge_funds.csv", index=False)

# Save to Markdown
with open("hedge_funds.md", "w") as f:
    f.write(df_to_markdown(df_funds_sorted))