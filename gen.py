#!/opt/local/bin/python
import os, pathlib

papers = {}
emojify = {'CORE':'🔬', 'DIVE':'🚀', 'REAP':'🔁', 'SHOW':'🌟'}
fulltype = {'CORE':'Cutting-edge Original Research on Evolution', 'DIVE':'Disruptive Ideas and Visionary Explorations', 'REAP':'Reproduced, Examined, or Analysed Papers', 'SHOW':'Summary of Highlights and Outstanding Work'}
pagecount = 0

def clean_authors(authors):
  result = []
  for author in authors:
    if author.startswith('https://'):
      continue
    elif author.startswith('!'):
      result.append(author[1:])
    else:
      result.append(author)
  return result

def transform(args):
  global pagecount
  if len(args) == 0:
    return []
  elif len(args) == 2:
    if args[0] == 'schedule':
      code = args[1]
      type = papers[code][0]
      title = papers[code][1]
      authors = papers[code][3:]
      result = [f'<td>{emojify[type]}</td>','<td>']
      if os.path.exists(f'pre/paper{code}.pdf'):
        result.append(f'  <span class="talk">')
        result.append(f'    <a href="pre/paper{code}.pdf">{title}</a>')
        if authors[0].startswith('https'):
          cf = []
          while authors[0].startswith('https'):
            link, name = authors[0].split('@')
            cf.append(f'<a href="{link}" class="ext">{name}</a>')
            authors = authors[1:]
          result.append(f'    (cf. {" &amp; ".join(cf)})')
        if os.path.exists(f'slides/deck{code}.pdf'):
          result.append(f'    (<a href="slides/deck{code}.pdf" class="ext">🖥️slides</a>)')
        result.append(f'  </span>')
      else:
        result.append(f'  <span class="talk"><em>{title}</em></span>')
      result.append('  <br>')
      for author in authors:
        if author.startswith('!'):
          result.append(f'  <span class="author presenter">{author[1:]}</span>,')
        else:
          result.append(f'  <span class="author">{author}</span>,')
      # kill the last comma
      result[-1] = result[-1][:-1]
      result.append('</td>')
      return result
    if args[0] == 'skippages':
      pagecount += int(args[1])
      return []
    if args[0] == 'append':
      # 01;DIVE;An Introduction to Indirect Code Completion;!Nhat;Vadim Zaytsev
      code = args[1]
      type = papers[code][0]
      title = papers[code][1]
      numpages = int(papers[code][2])
      pages = f'{pagecount+1}–{pagecount+numpages}'
      pagecount += numpages
      authors = clean_authors(papers[code][3:])
      key = authors[0].split()[-1]
      if len(authors) > 1:
        for author in authors[1:]:
          key += author.split()[-1][0]
      with open(f'pre/paper{code}.bib', 'w', encoding='utf-8') as bib:
        bib.write(f'''@inproceedings{{{key}2025,
\tauthor    = "{" and ".join(authors)}",
\ttitle     = "{{{title}}}",
\tbooktitle = "{{Pre-proceedings of the 24th Belgium-Netherlands Software Evolution Workshop (BENEVOL)}}",
\tpages     = "{pages}",
\teditor    = "Vadim Zaytsev and Fernando Castor",
\turl       = "https://benevol2025.github.io/pre/paper{code}.pdf",
\tyear      = 2025,
}}
''')
      return ['<li>',\
        f'  <a href="paper{code}.pdf" class="title">{title}</a>',\
        f'  <span class="pages"><a href="paper{code}.bib">{pages}</a></span>',\
        f'  <div class="authors">{", ".join(authors)}</div>',\
        f'  <div class="class">{emojify[type]}<span>{type} ({fulltype[type]})</span></div>',\
        '</li>'
      ]
  return [f'<!-- not transformed: "{line}" -->']

def explain(s):
  return s\
    .replace('AI', '<abbr title="Artificial Intelligence">AI</abbr>')\
    .replace('CPU', '<abbr title="Central Processing Unit">CPU</abbr>')\
    .replace('GPU', '<abbr title="Graphics Processing Unit">GPU</abbr>')\
    .replace('LLM', '<abbr title="Large Language Model">LLM</abbr>')\
    .replace('LaTeX', '<span class="latex">L<span class="a">A</span>T<span class="e">E</span>X</span>')\
    .replace('CPS', '<abbr title="Cyber-Physical System">CPS</abbr>')\
    .replace('npm', '<code>npm</code>')

if __name__ == "__main__":
  dx = 0
  with open('data.csv', 'r', encoding='utf-8') as data:
    for line in data.readlines():
      if line:
        record = line.strip().split(';')
        papers[record[0]] = record[1:]
        dx += 1
  cx = 0
  for almost in pathlib.Path('.').rglob('*.ahtml'):
    html = almost.with_suffix('.html')
    with almost.open('r', encoding='utf-8') as src, html.open('w', encoding='utf-8') as dst:
      for line in src:
        sline = line.strip()
        if not sline or sline.startswith('<!--') and sline.endswith('-->'):
          continue
        if line.find('¶') > 0:
          before, after = line.split('¶')
          for tline in transform(after.rstrip().split(':')):
            dst.write(before + explain(tline) + '\n')
        else:
          dst.write(line)
    cx += 1
  print(f'Read {dx} data records, transformed {cx} almost-HTML files to HTML')
