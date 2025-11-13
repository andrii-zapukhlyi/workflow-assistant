import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from config.settings import CONFLUENCE_DOMAIN, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN

## Fetch public titles of pages (for all employees)
def get_public_titles():
    url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/space/PUBLIC/content/page"
    auth = HTTPBasicAuth(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        result = response.json().get("results", [])
        pages = [{"id": page["id"], "title": page["title"]} for page in result]
        return pages
    else:
        print("Error fetching public pages:", response.status_code, response.text)
        return []

## Fetch only titles for a specific department/space
def get_available_titles(space_key):
    url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/space/{space_key}/content/page"
    auth = HTTPBasicAuth(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        result = response.json().get("results", [])
        pages = [{"id": page["id"], "title": page["title"]} for page in result]
        return [page for page in pages if page['title'] != "Main Page"]
    else:
        print("Error fetching pages:", response.status_code, response.text)
        return []

## Fetch and process page
def get_content_of_page(page_id):
    url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/{page_id}?expand=body.storage"
    auth = HTTPBasicAuth(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        data = response.json()
        content = data['body']['storage']['value']
        soup = BeautifulSoup(content, "html.parser")
        formated_content = extract_text_and_images(soup, page_id)
        return formated_content
    else:
        print("Error fetching content:", response.status_code, response.text)
        return None

## Fetch all space keys in the Confluence domain
def get_all_spaces():
    url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/space"
    auth = HTTPBasicAuth(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        result = response.json().get("results", [])
        spaces = [{"key": space["key"], "name": space["name"]} for space in result]
        return spaces
    else:
        print("Error fetching spaces:", response.status_code, response.text)
        return []

## Fetch all pages across all spaces for vector database building
def get_all_pages():
    pages = []
    spaces = get_all_spaces()
    for space in spaces:
        page_titles = [page["title"] for page in get_available_titles(space["key"])]
        page_text = [content["text"] for content in [get_content_of_page(page["id"]) for page in get_available_titles(space["key"])] if content]
        pages.extend([{"title": title, "text": text} for title, text in zip(page_titles, page_text)])
    return pages

## Parse HTML content from Confluence API to transform into plain text for LLM and extract images
def extract_text_and_images(soup, page_id):
    texts = []
    images = []

    def recurse(elem):
        for child in elem.children:
            if child.name in ['h1','h2','h3','h4', 'h5', 'h6']:
                text = child.get_text(strip=True)
                if text:
                    heading = int(child.name[1])
                    texts.append("\n" + "#" * heading + f" {text}\n")

            elif child.name == 'p':
                text = format_inline(child)
                if text:
                    texts.append(text)

            elif child.name == 'ol':
                for idx, li in enumerate(child.find_all('li', recursive=False), start=1):
                    li_text = format_inline(li)
                    if li_text:
                        texts.append(f"{idx}. {li_text}")

            elif child.name == 'ul':
                for li in child.find_all('li', recursive=False):
                    li_text = format_inline(li)
                    if li_text:
                        texts.append(f"- {li_text}")

            elif child.name == 'table':
                table_text = extract_table(child)
                if table_text:
                    texts.append(f"{table_text}\n")

            elif child.name == 'ac:structured-macro' and child.get('ac:name') == 'code':
                code_text = extract_code_block(child)
                if code_text:
                    texts.append(code_text)

            elif 'emoticon' in (child.name or ''):
                emoji_name = child.get('ac:emoji-shortname', '').strip(':')
                if emoji_name:
                    texts.append(f":{emoji_name}:")

            elif child.name in ['ac:image', 'img']:
                url = None
                caption = None

                if child.name == 'img':
                    if child.get('src'):
                        url = child['src']
                    if child.get('alt'):
                        caption = child['alt']

                elif child.name == 'ac:image':
                    ri = child.find('ri:attachment')
                    if ri and ri.get('ri:filename'):
                        filename = ri['ri:filename']
                        url = f"https://{CONFLUENCE_DOMAIN}/wiki/download/attachments/{page_id}/{filename}"

                    cap = child.find('ac:caption')
                    if cap and cap.get_text(strip=True):
                        caption = cap.get_text(strip=True)

                if url:
                    entry = f"[Image: {url}]"
                    if caption:
                        entry = f"[Image ({caption}): {url}]"
                    texts.append(entry)
                    images.append(url)

            elif child.name in ['script', 'style']:
                continue

            elif hasattr(child, 'children'):
                recurse(child)

    def format_inline(tag):
        s = tag.decode_contents()
        for b in tag.find_all(['strong','b']):
            b_text = b.get_text(strip=True)
            s = s.replace(b_text, f"**{b_text}**")
        for i in tag.find_all(['em','i']):
            i_text = i.get_text(strip=True)
            s = s.replace(i_text, f"*{i_text}*")
        for c in tag.find_all('code'):
            c_text = c.get_text(strip=True)
            s = s.replace(c_text, f"`{c_text}`")
        for emo in tag.find_all(lambda t: 'emoticon' in (t.name or '')):
            short = emo.get('ac:emoji-shortname', '').strip(':')
            if short:
                s = s.replace(str(emo), f":{short}:")
        for link in tag.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            link_url = link['href']
            s = s.replace(str(link), f"[{link_text}: {link_url}]")
        for link in tag.find_all('ac:link'):
            user_tag = link.find('ri:user')
            if user_tag:
                account_id = user_tag.get('ri:account-id')
                url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/user"
                params = {"accountId": account_id}
                response = requests.get(url, params=params, auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN))
                if response.status_code == 200:
                    user_name = response.json().get("displayName")
                else:
                    user_name = "Unknown User"
                s = s.replace(str(link), f"@{user_name}")
        plain = BeautifulSoup(s, 'html.parser').get_text()
        return plain.strip()

    def extract_table(table_tag):
        rows = []
        header = table_tag.find('tr')
        if header:
            headers = [th.get_text(strip=True) for th in header.find_all(['th','td'])]
            rows.append("| " + " | ".join(headers) + " |")
            rows.append("|" + "|".join(['---']*len(headers)) + "|")
        for tr in table_tag.find_all('tr')[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all(['td','th'])]
            if cells:
                rows.append("| " + " | ".join(cells) + " |")
        return "\n".join(rows)

    def extract_code_block(tag):
        lang_tag = tag.find('ac:parameter', {'ac:name': 'language'})
        code_tag = tag.find('ac:plain-text-body')
        if code_tag:
            code = code_tag.get_text()
            lang = lang_tag.get_text(strip=True).lower() if lang_tag else ''
            if lang:
                return f"```{lang}\n{code}\n```"
            else:
                return f"\n```\n{code}\n```"
        return None

    recurse(soup)
    return {"text": "\n".join(texts), "images": images}