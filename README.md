# Encontro 11 — laboratório: fatia vertical da API de cálculo emergético

Esqueleto **executável e incompleto, de propósito**. A aplicação sobe e o caminho
feliz vai até o fim; o que falta são os cinco `TODO PASSO N` que você fecha em aula.
Cada TODO corresponde a um passo do laboratório e está marcado no arquivo onde mora.

**Os slides são referência; este repositório é a fonte.** Onde divergirem, o
repositório está certo — os slides de código cabem em 18 linhas, aqui não há esse limite.

```
11-backend-api/
├── requirements.txt
├── app/
│   ├── main.py                       ← monta a app, middleware de request_id, handlers  ▲ TODO 3
│   ├── api/v1/
│   │   ├── dto.py                    ← a fronteira: parse, não validação              ▲ TODO 3
│   │   ├── rotas_calculo.py          ← traduz HTTP e domínio, e nada mais
│   │   └── rotas_demo.py             ← a rota-armadilha do passo 4                     ▲ TODO 4
│   ├── dominio/
│   │   ├── motor_emergia.py          ← NÚCLEO PURO: sem I/O, sem relógio, sem estado
│   │   ├── tipos.py                  ← frozen dataclasses; recusa float na construção
│   │   └── erros.py                  ← três erros de domínio, zero conhecimento de HTTP
│   ├── servicos/servico_calculo.py   ← orquestra; nenhuma fórmula
│   ├── repositorios/
│   │   ├── interfaces.py             ← as portas (Protocol)
│   │   └── memoria.py                ← implementação trocável
│   └── infra/
│       ├── providers.py              ← o único ponto de montagem
│       └── log.py                    ← todo o não-determinismo: relógio, IDs, stdout
└── tests/
    ├── conftest.py                   ← inventário de referência e cliente HTTP
    ├── test_erros_dominio.py         ← PRONTO (exemplo 1)
    ├── test_determinismo.py          ← PRONTO (exemplo 2)
    ├── test_contrato_dto.py          ← PRONTO (exemplo 3)
    └── test_tarefas_aluno.py         ← cinco testes seus                              ▲ TODO 5
```

## Antes da aula

Clone e instale **em casa**. Fazer `pip install` com trinta pessoas na mesma rede
custa quinze minutos do laboratório.

```bash
cd 11-backend-api
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q                                  # 15 passam, 5 skipped
```

Rode sempre **da raiz de `11-backend-api`**. `ModuleNotFoundError: app` quase sempre
é diretório errado; confirme com `python -c "import app"`.

## Os cinco passos

### Passo 1 — Ambiente

```bash
uvicorn app.main:app --reload
```

Abra <http://127.0.0.1:8000/docs>. Ninguém escreveu esse Swagger: ele saiu dos tipos
declarados nos DTOs. Localize o `POST /v1/safras/{safra_id}/calculos`, veja o schema
do corpo e o do 201, e confira que `categoria` já aparece como lista fechada de seis
valores.

`uvicorn: command not found` é venv não ativado — diagnostique com `which python`.
Porta ocupada por outro grupo resolve-se com `--port 8001`.

### Passo 2 — Caminho feliz

```bash
curl -s -X POST http://127.0.0.1:8000/v1/safras/42/calculos \
  -H 'content-type: application/json' \
  -d '{"fluxos":[
        {"recurso":"chuva","categoria":"R","emergia_sej":"100"},
        {"recurso":"solo","categoria":"N","emergia_sej":"50"},
        {"recurso":"fertilizante","categoria":"MR","emergia_sej":"10"},
        {"recurso":"diesel","categoria":"MN","emergia_sej":"20"},
        {"recurso":"mao_de_obra","categoria":"SR","emergia_sej":"5"},
        {"recurso":"frete","categoria":"SN","emergia_sej":"15"}],
      "energia_produto_j":"1000"}'
```

201 com os seis índices. Agora **inverta a ordem dos fluxos** no mesmo corpo e
compare as duas respostas caractere por caractere. Observe também as duas linhas de
log no terminal do uvicorn: `calculo.iniciado` e `calculo.concluido`, com o mesmo
`request_id`.

Esse inventário é o de referência dos testes: Y = 200, F = 50, renováveis = 115,
não renováveis = 85. Os seis valores de saída **não estão escritos neste README** de
propósito — derivá-los à mão é a primeira metade do teste de regressão do passo 5.

### Passo 3 — Quebrar

Três requisições inválidas, três lições. Faça uma por vez e leia o corpo da resposta.

| | requisição | hoje | depois do TODO |
|---|---|---|---|
| a | `"categoria": "X"` | **422** do Pydantic | já correto: o Enum fecha a porta |
| b | inventário só com `N` e `MN` | **500** | 422 em `application/problem+json` |
| — | `GET /v1/safras/999/indices` | 404 já em `problem+json` | nada a fazer: o esqueleto padroniza os erros do framework |
| c | `"energia_produto_jj": "1000"` | **201** com o typo ignorado | 422 na hora |

O (b) e o (c) são os TODOs deste passo: os dois handlers que faltam em `app/main.py`
e o `extra="forbid"` ausente em `CalculoRequestDTO`, em `app/api/v1/dto.py`. O (c) é
exatamente o typo que a planilha aceitava sem reclamar.

### Passo 4 — Congelar

Com o servidor rodando, chame a rota-armadilha num terminal e, **imediatamente**,
recarregue `/docs` no navegador:

```bash
curl http://127.0.0.1:8000/v1/demo/travada
```

O Swagger não carrega. Nada carrega. O servidor está refém de um `time.sleep(10)`
dentro de uma função `async`. Aplique uma das duas correções descritas no TODO de
`app/api/v1/rotas_demo.py` e repita: o servidor responde normalmente durante a espera.

Higiene ao final: apague `rotas_demo.py` e a linha que o inclui em `app/main.py`, ou
mova a rota para um branch de demonstração. Código que ensina errado não fica em `main`.

### Passo 5 — Motor sem servidor

Desligue o uvicorn e rode:

```bash
python -m pytest -q
```

Verde em milissegundos, sem servidor, sem banco, sem rede — porque o motor não conhece
ninguém. Os cinco testes em `test_tarefas_aluno.py` estão com `pytest.skip` e nome,
docstring e critério já escritos: apague o skip e escreva o corpo. Dois deles só passam
depois de fechados os TODOs do passo 3.

## O que este esqueleto já resolve

Vale saber o que **não** é tarefa sua, para não refazer:

- contexto `Decimal` local com precisão 28 e `ROUND_HALF_EVEN`, e **uma única
  quantização no final** (`1E-6`);
- `float` recusado na construção de `FluxoEmergetico` — não é bug, é invalidação
  científica, e morre antes da fórmula;
- erros de domínio separados de erros de infraestrutura;
- **um único formato de erro na API**: os handlers de `StarletteHTTPException` e
  `RequestValidationError` levam o 400, o 404 e o 422 do próprio framework para o
  mesmo corpo RFC 9457 — inclusive a distinção 400 (corpo não é JSON) × 422
  (JSON válido, valor fora do domínio), que o FastAPI por padrão não faz;
- não-determinismo confinado em `app/infra/log.py`: relógio, geração de ID e stdout;
- `request_id` por requisição, propagado no log e devolvido no header `x-request-id`;
- ponto de montagem único em `app/infra/providers.py` — trocar memória por Postgres
  é uma linha e nenhuma outra camada sabe.

## Simplificações declaradas

- **Sem persistência real.** `IndicesEmMemoria` perde tudo ao reiniciar. O assunto de
  hoje é a fronteira, não o pipeline de dados.
- **Sem autenticação, sem CORS, sem paginação.** O prefixo `/v1` já materializa o
  versionamento por URI; o resto é decisão de outra camada.
- **As transformidades de `memoria.py` são didáticas.** Na entrega elas saem da
  `Planilha_base.xlsx`, e é aí que a tolerância de `1E-6` por índice passa a valer.
- **F = M + S** (insumos comprados da economia), definição usual na literatura
  emergética. Se a planilha validada usar outra composição, **a planilha manda**.
- **`FatorConversaoNaoEncontrado` existe e não é lançado por ninguém ainda.** Ele entra
  em uso quando o inventário passar a chegar em unidade física em vez de sej — o
  exercício E1 é o primeiro passo nessa direção.

## O entregável

Cinco critérios, e todos são verificáveis por `pytest`:

1. nenhum `float` no caminho do dado científico;
2. nenhuma fórmula fora do motor; nenhum import de framework no domínio;
3. **≥ 8 testes**: determinismo sob permutação, os três erros de domínio e regressão numérica;
4. todo erro em `application/problem+json`;
5. todo cálculo emite `calculo.iniciado` e `calculo.concluido` com `request_id`.

Os três arquivos de teste prontos cobrem (1), (3) parcialmente, (4) para os erros do
framework e (5). Fechar os cinco TODOs cobre o resto — de (4) falta apenas o erro de
domínio, que é o TODO do passo 3. Entrega em PR revisado por outro membro, CI local verde, até
**domingo 25/10, 23h59**.
