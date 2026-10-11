#!/usr/bin/env bash
# Reconstrói todos os guias a partir de src/conteudo e gera o index.html do site.
# Uso: ./build.sh            (precisa só de Python 3, sem bibliotecas extra)
set -euo pipefail
cd "$(dirname "$0")"

# id | sigla | subtítulo | mathjax (opcional)
GUIAS=(
  "ac|AC|Arquitetura de Computadores · MIPS · UA|"
  "fp|FP|Fundamentos de Programação · Python · UA|"
  "iei|IEI|Introdução à Engenharia Informática · UA|"
  "c1|C I|Cálculo I · UA|"
  "c2|C II|Cálculo II · UA|"
  "md|MD|Matemática Discreta · UA|"
  "msf|MSF|Modelação de Sistemas Físicos · UA|mathjax"
  "mas|MAS|Modelação e Análise de Sistemas · UML · UA|"
  "poo|POO|Programação Orientada a Objetos · Java · UA|"
  "aed|AED|Algoritmos e Estruturas de Dados · UA|"
  "fbd|FBD|Fundamentos de Bases de Dados · UA|"
  "pds|PDS|Padrões e Desenho de Software · UA|"
  "so|SO|Sistemas Operativos · UA|"
  "cti|CT I|Competências Transferíveis I · UA|"
)

for g in "${GUIAS[@]}"; do
  IFS='|' read -r id sigla sub mj <<< "$g"
  python3 src/make_guide.py "src/conteudo/$id.html" "guias/$id.html" "$sigla" "$sub" $mj
done
# guias/alga.html não tem ficheiro de conteúdo: é mantido tal como está.

python3 src/build.py index.html
