import xml.etree.ElementTree as ET
import os

urls = []

'''
PROTHOM ALO
'''
# def print_loc_tags(xml_file_path):
#     tree = ET.parse(xml_file_path)
#     root = tree.getroot()
#     namespace = {'ns': root.tag.split('}')[0].strip('{')}
#     for loc in root.findall('.//ns:loc', namespace):
#         if loc.text:
#             text = loc.text.strip()
#             if "prothomalo.com" not in text or "media" in text or "video" in text:
#                 continue
#             urls.append(text)
#     print(len(urls))

# if __name__ == "__main__":
#     for root, _, files in os.walk("./Prothom Alo"):
#         for filename in files:
#             print_loc_tags("./Prothom Alo/" + filename)
#         urls = list(set(urls))

#         with open("prothom_alo.txt", "w", encoding="utf-8") as f:
#             for url in urls:
#                 f.write(url + "\n")



'''
DHAKA TRIBUNE
'''
# def print_loc_tags(xml_file_path):
#     tree = ET.parse(xml_file_path)
#     root = tree.getroot()
#     namespace = {'ns': root.tag.split('}')[0].strip('{')}
#     for loc in root.findall('.//ns:loc', namespace):
#         if loc.text:
#             text = loc.text.strip()
#             urls.append(text)
#     print(len(urls))

# if __name__ == "__main__":
#     print_loc_tags("Dhaka Tribune/2025-12-01.xml")
#     print_loc_tags("Dhaka Tribune/2026-01-01.xml")

#     urls = list(set(urls))

#     with open("dhaka_tribune.txt", "w") as f:
#         for url in urls:
#             f.write(url + "\n")