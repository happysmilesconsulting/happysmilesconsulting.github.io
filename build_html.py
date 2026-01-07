#!/usr/bin/env python3
import os
import re
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_MARKER_RE = re.compile('{{.*?}}')
TEMPLATE_ENV = {}

def read_file(fpath):
    with open(fpath) as fh:
        data = fh.read()
        return data
    raise ValueError(f'Could not read from {fpath}')

def write_file(fpath, doc_data):
    if os.path.exists(fpath):
        ts = time.time()
        bkp_path = f"/tmp/{os.path.basename(fpath)}.{ts}.bkp"
        print(f"moving existing {fpath} to {bkp_path}")
        # os.rename(fpath, bkp_path)
    with open(fpath, 'w') as fh:
        fh.write(doc_data)

def update_header_template(doc, outpath):
    """
    Update the doc for nav bar based on basename(outpath)
        <li><a href="index.html"> -> <li><a class="active" href="index.html">
    """
    href_path = os.path.basename(outpath)
    search_str = f'<li><a href="{href_path}">'
    replace_str = f'<li><a class="active" href="{href_path}">'
    if doc.find(search_str) > 0:
        return doc.replace(search_str, replace_str)
    return doc

def handle_include_marker(marker, doc, template_dir, outpath):
    # marker = {{include header(foo=param_value, bar=value)}}
    m = extract_marker_text(marker).replace('include', '').strip().split('(')[0]
    # TODO handle param_values
    # tenative plan: copy the global template_dir, update with param_values
    template_path = os.path.join(template_dir, f"{m}.template.html")
    if not os.path.exists(template_path):
        raise ValueError(f"template not found: {template_path}")
    t_doc = read_file(template_path)
    if m == 'header':
        t_doc = update_header_template(t_doc, outpath)
    doc = doc.replace(marker, t_doc)
    return doc

def extract_key_value(env_line):
    """ return {key: value} for input of 'key=value' str """
    arr = env_line.split('=')
    k = arr[0].strip()
    v = '='.join(arr[1:]).strip()
    return {k: v}

def handle_setenv_marker(marker, doc):
    # marker = '{{setenv title=My favorite site}}'
    global TEMPLATE_ENV
    m = extract_marker_text(marker).strip().replace('setenv', '', 1)
    d = extract_key_value(m)
    print(f"setting env: {d}")
    TEMPLATE_ENV.update(d)
    return doc.replace(marker, '')

def handle_get_marker(marker, doc):
    # marker = {{get foo}}
    # apply all variable from templateenv
    m = extract_marker_text(marker)
    val = ''
    # todo get value from TEMPLATE_ENV
    key = m.replace('get', '').strip()
    if key in TEMPLATE_ENV:
        val = TEMPLATE_ENV[key]
    else:
        print(f"Couldn't find value for {m}. using ''...")
    return doc.replace(marker, val)


def extract_marker_text(marker):
    return marker.strip('{} ')

def main(fpath, outpath, template_dir):
    """
        fpath: input file with template markers
        outpath: file path to overwrite with compiled output
        template_dir: dir path where templates live
    """
    # TODO make sure paths exists
    print(f"processing {fpath}")
    doc = read_file(fpath)
    markers = TEMPLATE_MARKER_RE.findall(doc)
    if not markers:
        print(f"no markers found. Saving {outpath}")
        write_file(outpath, doc)
        return
    
    # need to make this a while() loop as more markers may appear
    # when templates are included in the doc
    while (markers:= TEMPLATE_MARKER_RE.findall(doc)):
        marker = markers[0]
        m = extract_marker_text(marker)
        print(f"updating marker '{m}'")
        if m.startswith('include'):
            doc = handle_include_marker(marker, doc, template_dir, outpath)
        if m.startswith('setenv'):
            doc = handle_setenv_marker(marker, doc)
        if m.startswith('get'):
            doc = handle_get_marker(marker, doc)
    doc = doc.lstrip()
    write_file(outpath, doc)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {os.path.basename(__file__)} templated_html_fpath")
        sys.exit(1)

    input_file = sys.argv[1]
    in_base_name = os.path.basename(input_file)
    output_file = os.path.join(SCRIPT_DIR, in_base_name)
    template_dir = os.path.join(SCRIPT_DIR, 'template_src')
    main(input_file, output_file, template_dir)
