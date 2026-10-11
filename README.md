# Guias de Estudo · LEI (Universidade de Aveiro)

Resumos, métodos e testes resolvidos das cadeiras do 1.º e 2.º ano da Licenciatura em Engenharia Informática.
O site é um único `index.html` com filtros por ano e semestre; cada guia também existe sozinho em `guias/`.

## Cadeiras

| Ano | Semestre | Cadeiras com guia |
|---|---|---|
| 1.º | 1.º | ALGA, C I, FP, AC, IEI |
| 1.º | 2.º | C II, MD, MSF, MAS, POO |
| 2.º | 1.º | AED, FBD, PDS, SO, CT I |
| 2.º | 2.º | CBD, IES, MPEI, RS (em preparação) |

## Estrutura

```
index.html          site completo (abre no browser, funciona offline)
guias/              um ficheiro HTML por cadeira (já gerado)
src/
  conteudo/         texto de cada guia (é aqui que se editam os resumos)
  make_guide.py     transforma um ficheiro de conteúdo num guia completo
  build.py          junta os guias num só index.html
  template.html     página inicial com os filtros
build.sh            reconstrói tudo
```

## Editar um resumo

1. Altera o ficheiro em `src/conteudo/` (por exemplo `src/conteudo/so.html`).
2. Corre `./build.sh` (só precisa de Python 3).
3. Faz commit de tudo, incluindo `guias/` e `index.html`.

O guia de ALGA não tem ficheiro de conteúdo: edita-se diretamente em `guias/alga.html` e depois corre-se `python3 src/build.py index.html`.

## Publicar

- **GitHub Pages:** no repositório, Settings → Pages → Source: *Deploy from a branch*, branch `main`, pasta `/ (root)`. O site fica em `https://<utilizador>.github.io/<repositório>/`.
- **Netlify:** liga o repositório (sem comando de build, pasta de publicação `.`) ou arrasta a pasta inteira para a zona de deploy.
