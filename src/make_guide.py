"""Gera um guia de estudo completo (mesmo formato do guia de ALGA) a partir do conteúdo.

Uso: python3 make_guide.py conteudo.html saida.html "Título curto" "Subtítulo" [mathjax]

O ficheiro de conteúdo tem um bloco <hero>...</hero> e várias secções:
  <section id="x" data-nav="Rótulo no índice" data-grp="Grupo" [data-track]> ... </section>
As secções com data-track ganham uma caixa "estudado" na barra lateral.
"""
import html
import re
import sys

CSS = r"""
:root{
  --paper:#F4F6F9; --card:#FFFFFF; --ink:#16202E; --muted:#5A6578; --line:#D8DEE8;
  --accent:#2340A8; --accent-soft:#E6EBFA;
  --def:#2340A8; --def-bg:#EAEEFB; --teo:#0F7B5F; --teo-bg:#E4F4EE;
  --met:#9A5700; --met-bg:#FBF0DC; --bad:#B3261E; --bad-bg:#FBE9E7;
  --exa:#6B3FA0; --exa-bg:#F1EAF8; --ex:#475569; --ex-bg:#EEF1F5;
  --code-bg:#F0F2F7; --kw:#7A2BB0; --str:#1C7A3A; --cm:#7A8494; --num:#9A5700;
  --grid:rgba(35,64,168,.07);
  --serif:"Literata",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --paper:#10151D; --card:#171E29; --ink:#E7ECF4; --muted:#9BA7BA; --line:#2A3445;
  --accent:#8FA8FF; --accent-soft:#1E2A4D; --def:#8FA8FF; --def-bg:#1B2544; --teo:#5FD0A8; --teo-bg:#14302A;
  --met:#F0B45A; --met-bg:#35290F; --bad:#FF8F85; --bad-bg:#3A1E1B; --exa:#C6A3F2; --exa-bg:#2A1F3D;
  --ex:#A9B6C9; --ex-bg:#1E2735; --code-bg:#121924; --kw:#D2A8FF; --str:#7EE0A0; --cm:#8592A6; --num:#F0B45A;
  --grid:rgba(143,168,255,.07); color-scheme:dark}}
:root[data-theme="dark"]{
  --paper:#10151D; --card:#171E29; --ink:#E7ECF4; --muted:#9BA7BA; --line:#2A3445;
  --accent:#8FA8FF; --accent-soft:#1E2A4D; --def:#8FA8FF; --def-bg:#1B2544; --teo:#5FD0A8; --teo-bg:#14302A;
  --met:#F0B45A; --met-bg:#35290F; --bad:#FF8F85; --bad-bg:#3A1E1B; --exa:#C6A3F2; --exa-bg:#2A1F3D;
  --ex:#A9B6C9; --ex-bg:#1E2735; --code-bg:#121924; --kw:#D2A8FF; --str:#7EE0A0; --cm:#8592A6; --num:#F0B45A;
  --grid:rgba(143,168,255,.07); color-scheme:dark}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:20px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:17px;line-height:1.66;-webkit-text-size-adjust:100%}
a{color:var(--accent)}
.layout{display:grid;grid-template-columns:272px minmax(0,1fr);min-height:100vh}
.side{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;padding:22px 18px 28px;border-right:1px solid var(--line);background:var(--card);font-family:var(--sans);font-size:14px}
.side h1{font-size:17px;margin:0 0 2px;font-weight:600}
.side .sub{color:var(--muted);font-size:12.5px;margin:0 0 14px}
.bar{height:6px;border-radius:3px;background:var(--line);overflow:hidden;margin:6px 0 4px}
.bar>i{display:block;height:100%;width:0;background:var(--teo);transition:width .25s}
.barlbl{font-size:12px;color:var(--muted);margin-bottom:12px}
.side nav a{display:flex;gap:8px;align-items:flex-start;padding:5px 8px;margin:1px -8px;border-radius:6px;color:var(--ink);text-decoration:none;line-height:1.35}
.side nav a:hover{background:var(--accent-soft)}
.side nav a.on{background:var(--accent-soft);color:var(--accent);font-weight:600}
.side nav .grp{margin:14px 0 4px;font-size:12px;color:var(--muted);font-weight:600}
.side nav input{margin-top:3px;accent-color:var(--teo)}
.side .tools{margin-top:16px;display:flex;gap:8px;flex-wrap:wrap}
.side button{font:inherit;font-size:12.5px;padding:5px 10px;border:1px solid var(--line);background:var(--paper);color:var(--ink);border-radius:6px;cursor:pointer}
.side button:hover{border-color:var(--accent)}
.confirm{font-size:12.5px;color:var(--muted);margin-top:8px}
.mnav{display:none}
main{padding:0 clamp(18px,4vw,56px) 80px;max-width:940px;width:100%;min-width:0}
.hero{margin:0 calc(-1 * clamp(18px,4vw,56px)) 34px;padding:46px clamp(18px,4vw,56px) 34px;border-bottom:1px solid var(--line);
  background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:28px 28px}
.hero h1{font-family:var(--sans);font-weight:600;font-size:clamp(30px,5vw,44px);line-height:1.08;margin:0 0 10px;letter-spacing:-.025em;text-wrap:balance}
.hero p{margin:0;max-width:62ch;color:var(--muted);font-size:18px}
h2{font-family:var(--sans);font-size:28px;line-height:1.2;margin:56px 0 6px;letter-spacing:-.015em;font-weight:600;text-wrap:balance}
h3{font-family:var(--sans);font-size:19px;margin:30px 0 8px;font-weight:600}
h4{font-family:var(--sans);font-size:15.5px;margin:20px 0 4px;font-weight:600;color:var(--muted)}
p{margin:0 0 12px}
ul,ol{margin:0 0 14px;padding-left:1.35em}
li{margin:3px 0}
section{border-top:1px solid var(--line)}
section:first-of-type{border-top:0}
.done-tag{font-family:var(--sans);font-size:12px;font-weight:500;color:var(--teo);margin-left:10px}
.box{margin:16px 0;padding:12px 16px 10px;border-left:4px solid var(--ex);background:var(--ex-bg);border-radius:0 8px 8px 0;min-width:0}
.box>.t{display:block;font-family:var(--sans);font-weight:600;font-size:13.5px;margin-bottom:4px}
.box>:last-child{margin-bottom:2px}
.box.def{border-color:var(--def);background:var(--def-bg)} .box.def>.t{color:var(--def)}
.box.teo{border-color:var(--teo);background:var(--teo-bg)} .box.teo>.t{color:var(--teo)}
.box.met{border-color:var(--met);background:var(--met-bg)} .box.met>.t{color:var(--met)}
.box.bad{border-color:var(--bad);background:var(--bad-bg)} .box.bad>.t{color:var(--bad)}
.box.exa{border-color:var(--exa);background:var(--exa-bg)} .box.exa>.t{color:var(--exa)}
.box.ex>.t{color:var(--ex)}
code{font-family:var(--mono);font-size:.86em;background:var(--code-bg);padding:1px 5px;border-radius:4px}
pre{font-family:var(--mono);font-size:13.5px;line-height:1.55;background:var(--code-bg);border:1px solid var(--line);border-radius:8px;padding:12px 14px;overflow-x:auto;margin:12px 0;max-width:100%}
pre code{background:none;padding:0;font-size:inherit}
.box pre{background:var(--card)}
pre .k{color:var(--kw);font-weight:500} pre .s{color:var(--str)} pre .c{color:var(--cm);font-style:italic} pre .n{color:var(--num)}
.out{border-left:3px solid var(--teo)}
.tw{overflow-x:auto;margin:14px 0}
table{border-collapse:collapse;font-family:var(--sans);font-size:14.5px;width:100%;background:var(--card)}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
td code,th code{white-space:nowrap}
th{background:var(--accent-soft);font-weight:600}
td.c,th.c{text-align:center}
details{margin:12px 0;border:1px solid var(--line);border-radius:8px;background:var(--card)}
summary{cursor:pointer;padding:9px 14px;font-family:var(--sans);font-weight:600;font-size:14.5px;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"▸";display:inline-block;margin-right:8px;color:var(--accent);transition:transform .15s}
details[open]>summary::before{transform:rotate(90deg)}
details[open]>summary{border-bottom:1px solid var(--line)}
details>.in{padding:10px 16px 6px;min-width:0}
.chk{list-style:none;padding-left:0}
.chk li{display:flex;gap:10px;align-items:flex-start;font-family:var(--sans);font-size:15px}
.chk input{margin-top:5px;accent-color:var(--teo)}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.cols>div{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 16px 4px;min-width:0}
.cols h4{margin-top:0}
.sheet{columns:2 340px;column-gap:28px}
.sheet .box{break-inside:avoid}
.ov{text-decoration:overline;text-decoration-thickness:1px}
.bits td{font-family:var(--mono);text-align:center;font-size:13px}
.fig{margin:16px 0;overflow-x:auto}
.fig svg{display:block;max-width:100%;height:auto}
.fig figcaption{font-family:var(--sans);font-size:13px;color:var(--muted);margin-top:6px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:900px){
  .layout{display:block}
  .side{display:none}
  .mnav{display:block;position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--card);border-bottom:1px solid var(--line);font-family:var(--sans);font-size:14px}
  .mnav summary{padding:10px 16px}
  .mnav .list{max-height:60vh;overflow:auto;padding:4px 16px 12px}
  .mnav a{display:block;padding:6px 0;color:var(--ink);text-decoration:none}
  body{font-size:16.5px}
  h2{font-size:24px}
}
@media print{
  .side,.mnav{display:none}.layout{display:block}
  body{background:#fff;color:#000;font-size:11pt}
  .hero{background:none}
  details>summary{display:none}
  .box,pre{break-inside:avoid}
}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.bar>i{transition:none}}
"""

JS = r"""
(function(){
  var KEY='%(key)s', state={};
  try{ state=JSON.parse(localStorage.getItem(KEY)||'{}')||{}; }catch(e){ state={}; }
  function save(){ try{ localStorage.setItem(KEY,JSON.stringify(state)); }catch(e){} }
  var secBoxes=document.querySelectorAll('#nav input[data-sec]');
  var chkBoxes=document.querySelectorAll('.chk input[data-k]');
  var pbar=document.getElementById('pbar'), plbl=document.getElementById('plbl');
  function refresh(){
    var n=0;
    secBoxes.forEach(function(cb){
      var id=cb.getAttribute('data-sec'), on=!!state['s:'+id];
      cb.checked=on; if(on) n++;
      var tag=document.querySelector('#'+id+' .done-tag'); if(tag) tag.hidden=!on;
    });
    pbar.style.width=(secBoxes.length?100*n/secBoxes.length:0)+'%%';
    plbl.textContent=n+' de '+secBoxes.length+' capítulos estudados';
    chkBoxes.forEach(function(cb){ cb.checked=!!state['k:'+cb.getAttribute('data-k')]; });
  }
  secBoxes.forEach(function(cb){
    cb.addEventListener('click',function(e){ e.stopPropagation(); });
    cb.addEventListener('change',function(){ state['s:'+cb.getAttribute('data-sec')]=cb.checked; save(); refresh(); });
  });
  chkBoxes.forEach(function(cb){ cb.addEventListener('change',function(){ state['k:'+cb.getAttribute('data-k')]=cb.checked; save(); }); });
  var rst=document.getElementById('rst'), cf=document.getElementById('cf');
  rst.addEventListener('click',function(){
    if(cf.hidden){ cf.hidden=false; rst.textContent='Confirmar limpeza'; return; }
    state={}; save(); refresh(); cf.hidden=true; rst.textContent='Limpar progresso';
  });
  var root=document.documentElement;
  document.getElementById('thm').addEventListener('click',function(){
    var dark=root.getAttribute('data-theme')==='dark' || (!root.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    root.setAttribute('data-theme',dark?'light':'dark');
  });
  var ml=document.getElementById('mlist');
  document.querySelectorAll('#nav a').forEach(function(a){
    var l=document.createElement('a'); l.href=a.getAttribute('href'); l.textContent=a.textContent.trim();
    l.addEventListener('click',function(){ document.getElementById('mnav').removeAttribute('open'); });
    ml.appendChild(l);
  });
  var links={}; document.querySelectorAll('#nav a').forEach(function(a){ links[a.getAttribute('href').slice(1)]=a; });
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){
      es.forEach(function(en){ if(en.isIntersecting){
        Object.keys(links).forEach(function(k){ links[k].classList.remove('on'); });
        if(links[en.target.id]) links[en.target.id].classList.add('on'); } });
    },{rootMargin:'-20%% 0px -70%% 0px'});
    document.querySelectorAll('main section[id]').forEach(function(s){ io.observe(s); });
  }
  window.addEventListener('beforeprint',function(){ document.querySelectorAll('details').forEach(function(d){ d.setAttribute('open',''); }); });
  refresh();
})();
"""

KWS = {
    "py": "def|return|if|elif|else|for|while|in|not|and|or|import|from|as|with|class|lambda|try|except|finally|raise|break|continue|pass|None|True|False|is|yield|assert|global|del",
    "java": "public|private|protected|static|final|void|int|double|float|boolean|char|long|short|byte|new|this|super|extends|implements|interface|abstract|enum|throws|throw|try|catch|finally|null|true|false|instanceof|package|import|default|switch|case|break|continue|return|if|else|for|while|do|class|var|record",
    "c": "int|char|double|float|void|return|if|else|for|while|do|switch|case|break|continue|struct|typedef|enum|union|unsigned|signed|long|short|const|static|sizeof|NULL|bool|true|false|auto|default|goto|extern|size_t|include|define",
    "sql": "SELECT|FROM|WHERE|GROUP|BY|HAVING|ORDER|ASC|DESC|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|VIEW|INDEX|DROP|ALTER|ADD|PRIMARY|KEY|FOREIGN|REFERENCES|UNIQUE|NOT|NULL|DEFAULT|CHECK|CONSTRAINT|AS|ON|JOIN|INNER|LEFT|RIGHT|FULL|OUTER|NATURAL|CROSS|UNION|INTERSECT|EXCEPT|ALL|DISTINCT|IN|EXISTS|BETWEEN|LIKE|IS|AND|OR|COUNT|SUM|AVG|MIN|MAX|CASE|WHEN|THEN|ELSE|END|BEGIN|COMMIT|ROLLBACK|TRANSACTION|PROCEDURE|FUNCTION|TRIGGER|RETURNS|RETURN|DECLARE|IF|WHILE|EXEC|GRANT|REVOKE|TO|WITH|CASCADE|INT|VARCHAR|CHAR|DATE|DECIMAL|IDENTITY|AFTER|INSTEAD|OF|FOR|TOP|ANY|SOME|INT|OUTPUT|PRINT|USE|GO|CURSOR|FETCH|NEXT|OPEN|CLOSE|DEALLOCATE|SCHEMA|ROLE|USER|OPTION",
    "asm": "li|la|lw|sw|lb|sb|lbu|lh|sh|addi|addiu|add|addu|sub|subu|and|andi|or|ori|xor|xori|nor|slt|slti|sltu|sltiu|sll|srl|sra|sllv|srlv|beq|bne|beqz|bnez|j|jal|jr|jalr|mult|multu|div|divu|mfhi|mflo|move|syscall|blt|bgt|ble|bge|lui|nop|mul|rem|neg|not",
}


def highlight(code: str, lang: str) -> str:
    """Realce muito simples: comentários, strings, palavras-chave e números."""
    out, i = [], 0
    cm = {"py": "#", "asm": "#", "sql": "--"}.get(lang, "//")
    if lang == "txt":
        return html.escape(code, quote=False)
    pat = re.compile(
        r'(?P<c>' + re.escape(cm) + r'[^\n]*)'
        r'|(?P<s>"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\')'
        r'|(?P<k>\b(?:' + KWS.get(lang, KWS["py"]) + r')\b)'
        r'|(?P<n>\b\d+(?:\.\d+)?\b)'
    )
    for m in pat.finditer(code):
        out.append(html.escape(code[i:m.start()], quote=False))
        cls = m.lastgroup
        out.append(f'<span class="{cls}">{html.escape(m.group(0), quote=False)}</span>')
        i = m.end()
    out.append(html.escape(code[i:], quote=False))
    return "".join(out)


def render_code(body: str) -> str:
    # <pre data-lang="py">código cru</pre>  -> escapado e realçado
    def rep(m):
        lang, extra, code = m.group(1), m.group(2) or "", m.group(3)
        code = html.unescape(code.strip("\n"))
        return f'<pre{extra}><code>{highlight(code, lang)}</code></pre>'
    return re.sub(r'<pre data-lang="(\w+)"([^>]*)>(.*?)</pre>', rep, body, flags=re.S)


def main(src, dst, title, sub, use_mathjax=False):
    raw = open(src, encoding="utf-8").read()
    hero = re.search(r"<hero>(.*?)</hero>", raw, re.S).group(1)
    body = re.sub(r"<hero>.*?</hero>", "", raw, flags=re.S)
    extra = re.search(r"<extracss>(.*?)</extracss>", body, re.S)
    extra_css = extra.group(1) if extra else ""
    body = re.sub(r"<extracss>.*?</extracss>", "", body, flags=re.S)
    body = render_code(body)
    nav, last_grp, tracked = [], None, 0
    for m in re.finditer(r'<section id="([\w-]+)"([^>]*)>', body):
        sid, attrs = m.group(1), m.group(2)
        label = re.search(r'data-nav="([^"]*)"', attrs).group(1)
        grp = re.search(r'data-grp="([^"]*)"', attrs)
        grp = grp.group(1) if grp else None
        if grp and grp != last_grp:
            nav.append(f'<div class="grp">{grp}</div>')
            last_grp = grp
        if "data-track" in attrs:
            tracked += 1
            nav.append(f'<a href="#{sid}"><input type="checkbox" data-sec="{sid}" aria-label="Marcar {label} como estudado"><span>{label}</span></a>')
        else:
            nav.append(f'<a href="#{sid}">{label}</a>')
    # etiqueta "estudado" no título das secções acompanhadas
    body = re.sub(r'(<section id="[\w-]+"[^>]*data-track[^>]*>\s*<h2>)(.*?)(</h2>)',
                  r'\1\2<span class="done-tag" hidden>estudado ✓</span>\3', body, flags=re.S)
    key = "guia-" + re.sub(r"\W+", "-", title.lower())
    mj = ""
    if use_mathjax:
        mj = ('<script>window.MathJax={tex:{inlineMath:[["$","$"],["\\\\(","\\\\)"]]},svg:{fontCache:"global"}};</script>\n'
              '<script async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.min.js"></script>')
    page = f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)} — guia de estudo</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Literata:opsz,wght@7..72,400;7..72,600&display=swap">
{mj}
<style>{CSS}{extra_css}</style>
</head>
<body>
<details class="mnav" id="mnav"><summary>Índice</summary><div class="list" id="mlist"></div></details>
<div class="layout">
<aside class="side">
  <h1>{html.escape(title)} — guia de estudo</h1>
  <p class="sub">{html.escape(sub)}</p>
  <div class="bar"><i id="pbar"></i></div>
  <div class="barlbl" id="plbl">0 de {tracked} capítulos estudados</div>
  <nav id="nav">
{chr(10).join(nav)}
  </nav>
  <div class="tools"><button id="thm" type="button">Tema claro/escuro</button><button id="rst" type="button">Limpar progresso</button></div>
  <div class="confirm" id="cf" hidden>Carrega outra vez para apagar o progresso guardado neste navegador.</div>
</aside>
<main>
<div class="hero" id="top">{hero}</div>
{body}
</main>
</div>
<script>{JS % {"key": key}}</script>
</body>
</html>
"""
    open(dst, "w", encoding="utf-8").write(page)
    print(f"{dst}: {len(page)//1024} KB, {tracked} capítulos")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], a[4], len(a) > 5 and a[5] == "mathjax")
