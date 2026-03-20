import xml.etree.ElementTree as ET
import pandas as pd

def parse_hedge_funds(xml_file_path):
    """
    Parses the SEC's bulk Investment Adviser XML file to find hedge funds
    with $10M - $1000M in AUM.
    """
    print("Parsing SEC XML... this might take a moment.")
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    target_funds = []
    for firm in root.findall('.//Firm'):
        info = firm.find('Info')
        if info is None: 
            continue
            
        main_addr = firm.find('MainAddr')
        if main_addr is None:
            continue

        city = main_addr.get('City', '').strip().upper()
        state = main_addr.get('State', '').strip().upper()
            
        aum_element = firm.find('.//Item5F')
        if aum_element is None: 
            continue
            
        try:
            aum_dollars = float(aum_element.get('Q5F2C', 0)) 
        except ValueError:
            aum_dollars = 0.0
            
        aum_millions = aum_dollars / 1_000_000
        if not (10 <= aum_millions <= 1000):
            continue
            
        private_fund = firm.find('.//Item7B')
        if private_fund is None or private_fund.get('Q7B', 'N') == 'N':
            continue

        web_addrs = []
        web_addr_elements = firm.findall('.//FormInfo/Part1A/Item1/WebAddrs/WebAddr')
        for addr in web_addr_elements:
            if addr.text:
                web_addrs.append(addr.text.strip().lower())
        
        website = ", ".join(web_addrs) if web_addrs else 'N/A'

        target_funds.append({
            'Firm Name': info.get('LegalNm'),
            'CRD Number': info.get('FirmCrdNb'),
            'AUM (Millions)': round(aum_millions, 2),
            'City': city,
            'State': state,
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
        formatted_row = []
        for col, val in zip(columns, row):
            if col == 'Website' and val != 'N/A':
                # Parse comma separated web addresses and make them clickable
                links = [l.strip() for l in str(val).split(',')]
                clickable_links = ", ".join([f"[{l}]({l})" for l in links])
                formatted_row.append(clickable_links)
            else:
                formatted_row.append(str(val))
        rows.append("| " + " | ".join(formatted_row) + " |")
    return "\n".join([header, separator] + rows)

def df_to_sortable_html(df, title):
    """ Converts a pandas DataFrame to a Sortable HTML table string """
    columns = df.columns.tolist()
    header = "<thead><tr>" + "".join([f"<th onclick='sortTable({i})' style='cursor:pointer'>{c} ↕</th>" for i, c in enumerate(columns)]) + "</tr></thead>"
    rows = []
    for _, row in df.iterrows():
        formatted_row = []
        for col, val in zip(columns, row):
            if col == 'Website' and val != 'N/A':
                links = [l.strip() for l in str(val).split(',')]
                clickable_links = ", ".join([f"<a href='{l}' target='_blank'>{l}</a>" for l in links])
                formatted_row.append(f"<td>{clickable_links}</td>")
            else:
                formatted_row.append(f"<td>{val}</td>")
        rows.append("<tr>" + "".join(formatted_row) + "</tr>")
    body = "<tbody>" + "".join(rows) + "</tbody>"
    
    script = """
    <script>
    function sortTable(n) {
      var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
      table = document.getElementById("myTable");
      switching = true; dir = "asc"; 
      while (switching) {
        switching = false; rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
          shouldSwitch = false;
          x = rows[i].getElementsByTagName("TD")[n];
          y = rows[i + 1].getElementsByTagName("TD")[n];
          if (n == 2) { var xVal = parseFloat(x.innerText || x.textContent); var yVal = parseFloat(y.innerText || y.textContent); }
          else { var xVal = (x.innerText || x.textContent).toLowerCase(); var yVal = (y.innerText || y.textContent).toLowerCase(); }
          if (dir == "asc") { if (xVal > yVal) { shouldSwitch = true; break; } }
          else if (dir == "desc") { if (xVal < yVal) { shouldSwitch = true; break; } }
        }
        if (shouldSwitch) { rows[i].parentNode.insertBefore(rows[i + 1], rows[i]); switching = true; switchcount ++; }
        else { if (switchcount == 0 && dir == "asc") { dir = "desc"; switching = true; } }
      }
    }
    </script>
    """
    style = "<style>body { font-family: sans-serif; margin: 20px; } table { border-collapse: collapse; width: 100%; } th, td { text-align: left; padding: 8px; border: 1px solid #ddd; } tr:nth-child(even) { background-color: #f2f2f2; } th { background-color: #4CAF50; color: white; }</style>"
    return f"<!DOCTYPE html><html><head><title>{title}</title>{style}</head><body><h2>{title}</h2><table id='myTable'>{header}{body}</table>{script}</body></html>"

import os

# Create Folders
os.makedirs("nyc", exist_ok=True)
os.makedirs("full", exist_ok=True)

df_funds = parse_hedge_funds("data.xml")

# Save Full Data
df_full = df_funds.sort_values(by="AUM (Millions)", ascending=False)
df_full.to_csv("full/hedge_funds.csv", index=False)
with open("full/hedge_funds.md", "w") as f:
    f.write(df_to_markdown(df_full))
with open("full_hedge_funds.html", "w") as f:
    f.write(df_to_sortable_html(df_full, "All Hedge Funds"))

# Save NYC Data
df_nyc = df_funds[(df_funds['City'] == 'NEW YORK') & (df_funds['State'] == 'NY')].sort_values(by="AUM (Millions)", ascending=False)
df_nyc.to_csv("nyc/hedge_funds.csv", index=False)
with open("nyc/hedge_funds.md", "w") as f:
    f.write(df_to_markdown(df_nyc))
with open("nyc_hedge_funds.html", "w") as f:
    f.write(df_to_sortable_html(df_nyc, "NYC Hedge Funds"))

print("Reports saved into 'full/' and 'nyc/' folders, and HTML dashboards in root.")