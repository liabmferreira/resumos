"""Junta o índice e todos os guias num único ficheiro HTML.

Cada guia fica embutido como string JSON dentro de um <script type="application/json">,
e é aberto num iframe (srcdoc) quando se clica na cadeira. Não há ficheiros externos,
por isso não pode haver 404.
"""
import json
import os
import sys

BUILD = os.path.dirname(os.path.abspath(__file__))
GUIAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "guias")

CADEIRAS = [
    {"id": "alga", "s": "ALGA", "n": "Álgebra Linear e Geometria Analítica", "ano": 1, "sem": 1},
    {"id": "c1", "s": "C I", "n": "Cálculo I", "ano": 1, "sem": 1},
    {"id": "fp", "s": "FP", "n": "Fundamentos de Programação", "ano": 1, "sem": 1},
    {"id": "ac", "s": "AC", "n": "Arquitetura de Computadores", "ano": 1, "sem": 1},
    {"id": "iei", "s": "IEI", "n": "Introdução à Engenharia Informática", "ano": 1, "sem": 1},
    {"id": "c2", "s": "C II", "n": "Cálculo II", "ano": 1, "sem": 2},
    {"id": "md", "s": "MD", "n": "Matemática Discreta", "ano": 1, "sem": 2},
    {"id": "msf", "s": "MSF", "n": "Modelação de Sistemas Físicos", "ano": 1, "sem": 2},
    {"id": "mas", "s": "MAS", "n": "Modelação e Análise de Sistemas", "ano": 1, "sem": 2},
    {"id": "poo", "s": "POO", "n": "Programação Orientada a Objetos", "ano": 1, "sem": 2},
    {"id": "aed", "s": "AED", "n": "Algoritmos e Estruturas de Dados", "ano": 2, "sem": 1},
    {"id": "fbd", "s": "FBD", "n": "Fundamentos de Bases de Dados", "ano": 2, "sem": 1},
    {"id": "pds", "s": "PDS", "n": "Padrões e Desenho de Software", "ano": 2, "sem": 1},
    {"id": "so", "s": "SO", "n": "Sistemas Operativos", "ano": 2, "sem": 1},
    {"id": "cti", "s": "CT I", "n": "Competências Transferíveis I", "ano": 2, "sem": 1},
    {"id": "cbd", "s": "CBD", "n": "Complementos de Bases de Dados", "ano": 2, "sem": 2},
    {"id": "ies", "s": "IES", "n": "Introdução à Engenharia de Software", "ano": 2, "sem": 2},
    {"id": "mpei", "s": "MPEI", "n": "Métodos Probabilísticos para Engenharia Informática", "ano": 2, "sem": 2},
    {"id": "rs", "s": "RS", "n": "Redes e Serviços", "ano": 2, "sem": 2},
]


# Dentro de um iframe srcdoc, um link "#secao" resolve-se contra o URL da página-mãe e
# recarregaria o site dentro do iframe. Este script trata os links internos à mão.
ANCHOR_FIX = """<script>
document.addEventListener('click',function(e){
  if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey) return;
  if(e.target.closest('input,label,summary')) return;
  var a=e.target.closest('a[href^="#"]'); if(!a) return;
  e.preventDefault();
  var id=decodeURIComponent(a.getAttribute('href').slice(1));
  var t=id?(document.getElementById(id)||document.getElementsByName(id)[0]):null;
  var m=document.getElementById('mnav'); if(m&&m.open) m.open=false;
  requestAnimationFrame(function(){
    if(t){ t.scrollIntoView({behavior:'smooth',block:'start'}); }
    else { window.scrollTo({top:0,behavior:'smooth'}); }
  });
},true);
try{parent.postMessage('guia-pronto','*')}catch(e){}
</script>
<style>@media (max-width:900px){html{scroll-padding-top:64px}}</style>"""


def with_anchor_fix(html: str) -> str:
    # A folha de estilos das fontes bloqueava o desenho do guia até chegar da rede
    # (ecrã branco ~1 s). Com media="print" carrega em segundo plano e o texto aparece logo.
    html = html.replace('<link rel="stylesheet" href="https://fonts.googleapis.com',
                        '<link rel="stylesheet" media="print" onload="this.media=\'all\'" href="https://fonts.googleapis.com')
    i = html.lower().rfind("</body>")
    return html[:i] + ANCHOR_FIX + html[i:] if i >= 0 else html + ANCHOR_FIX


def embed(html: str) -> str:
    # JSON string; escapar "<" impede que "</script>" dentro do guia feche o bloco.
    return json.dumps(html, ensure_ascii=False).replace("<", "\\u003c")


def main(out_path: str) -> None:
    tpl = open(os.path.join(BUILD, "template.html"), encoding="utf-8").read()
    blocks, prontos = [], []
    for c in CADEIRAS:
        p = os.path.join(GUIAS, c["id"] + ".html")
        if os.path.exists(p):
            html = open(p, encoding="utf-8").read()
            blocks.append(f'<script type="application/json" id="guia-{c["id"]}">{embed(with_anchor_fix(html))}</script>')
            prontos.append(c["s"])
    tpl = tpl.replace("<!--GUIAS-->", "\n".join(blocks))
    tpl = tpl.replace("/*CADEIRAS*/[]", json.dumps(CADEIRAS, ensure_ascii=False))
    open(out_path, "w", encoding="utf-8").write(tpl)
    print(f"{out_path}: {os.path.getsize(out_path)/1024:.0f} KB, guias: {', '.join(prontos)}")


if __name__ == "__main__":
    main(sys.argv[1])
