#!/usr/bin/env python3
import os
import re
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_MARKER_RE = re.compile('{{{.*?}}}')

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
        os.rename(fpath, bkp_path)
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
    
    for marker in markers:
        m = marker.strip('{} ')
        print(f"updating marker '{m}'")
        template_path = os.path.join(template_dir, f"{m}.template.html")
        if not os.path.exists(template_path):
            raise ValueError(f"template not found: {template_path}")
        t_doc = read_file(template_path)
        if m == 'header':
            t_doc = update_header_template(t_doc, outpath)
        doc = doc.replace(marker, t_doc)
    
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
