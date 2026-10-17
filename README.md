# Gerador de Roteiros de Retrospectiva

> Este projeto foi gerado automaticamente por IA e revisado por um agente automatizado, nao por uma pessoa. Leia o codigo antes de usar.

## Descrição

CLI em Python que lê um arquivo JSON local com itens de retrospectiva, valida sua estrutura e gera um roteiro em Markdown para reunião. O documento produzido inclui agenda por tema, seção de discussão e plano de ação.

## Objetivo

Converter dados estruturados de retrospectiva em um único arquivo Markdown, destacando itens abertos, decisões registradas, ações, responsáveis e prazos quando informados.

## Como funciona

1. A CLI recebe o caminho de um JSON de entrada e o caminho do Markdown de saída.
2. O JSON é lido em UTF-8 e validado.
3. Os temas são agrupados e ordenados alfabeticamente, sem diferenciar maiúsculas de minúsculas.
4. Os itens permanecem na ordem original dentro de cada tema.
5. O arquivo Markdown é gravado em UTF-8, com quebras de linha `\n`.

O contrato de entrada exige um objeto JSON com:

- `meeting_title`: texto não vazio;
- `meeting_date`: data válida no formato ISO `YYYY-MM-DD`;
- `items`: lista não vazia.

Cada item em `items` deve conter:

- `theme`: texto não vazio;
- `description`: texto não vazio;
- `status`: um dos valores `open`, `discussed` ou `resolved`.

Um item também pode conter:

- `decision`: texto não vazio ou `null`;
- `action`: objeto de ação.

Quando `action` estiver presente, deve conter:

- `description`: texto não vazio;
- `owner`: texto não vazio ou `null`, opcional;
- `due_date`: data válida no formato ISO `YYYY-MM-DD`, opcional.

No Markdown, status `open` é exibido como **Aberto** e marcado como **Pendente**. Ações de itens abertos recebem situação `Pendente`; ações dos demais itens recebem `Acompanhar`. Responsável e prazo ausentes são exibidos como `Não informado`.

## Arquitetura

- `requirements.txt`: arquivo de dependências do experimento.
- `src/retrospective_script/__init__.py`: expõe os modelos, a função de validação e o renderizador do pacote.
- `src/retrospective_script/__main__.py`: implementa a interface de linha de comando, leitura do JSON, gravação do Markdown e mensagens de erro.
- `src/retrospective_script/models.py`: define dataclasses imutáveis e valida o contrato dos dados de retrospectiva.
- `src/retrospective_script/renderer.py`: agrupa os itens e renderiza o roteiro Markdown de forma determinística.
- `tests/conftest.py`: arquivo de configuração compartilhada dos testes.
- `tests/test_cli.py`: testes da interface de linha de comando.
- `tests/test_models.py`: testes da validação e dos modelos.
- `tests/test_renderer.py`: testes da renderização Markdown.

## Tecnologias

- Python 3.11+
- Biblioteca padrão do Python: `argparse`, `json`, `pathlib`, `dataclasses`, `datetime`, `typing` e `collections`
- Markdown, como formato de saída
- pytest, fornecido pelo ambiente de execução

## Instalação

O experimento não possui dependências externas a instalar; o código usa a biblioteca padrão do Python. O arquivo `requirements.txt` não adiciona dependências.

O comando de instalação compatível com o projeto é:

```bash
python -m pip install -r requirements.txt
```

Como o pacote está no diretório `src/` e não há arquivo de instalação do projeto, é necessário disponibilizar esse diretório em `PYTHONPATH` ao executar a CLI.

## Configuração

Não há variáveis de ambiente lidas pelo código.

A configuração é feita pelos dois argumentos posicionais da CLI:

1. caminho do arquivo JSON de entrada;
2. caminho do arquivo Markdown de saída.

## Uso

No Linux/macOS:

```bash
PYTHONPATH=src python -m retrospective_script caminho/entrada.json caminho/roteiro.md
```

No Windows PowerShell:

```powershell
$env:PYTHONPATH="src"; python -m retrospective_script caminho\entrada.json caminho\roteiro.md
```

Em caso de sucesso, a CLI informa o caminho onde o roteiro foi gerado. Em falhas de leitura, codificação UTF-8, JSON inválido, validação ou gravação, ela exibe uma mensagem em português e retorna código diferente de zero.

## Exemplos

Exemplo de conteúdo para o arquivo JSON de entrada:

```json
{
  "meeting_title": "Retrospectiva da equipe",
  "meeting_date": "2025-01-31",
  "items": [
    {
      "theme": "Comunicação",
      "description": "Centralizar avisos importantes em um único canal.",
      "status": "open",
      "action": {
        "description": "Definir o canal oficial de avisos.",
        "owner": "Equipe de projeto",
        "due_date": "2025-02-07"
      }
    },
    {
      "theme": "Entrega",
      "description": "A revisão final foi concluída no prazo.",
      "status": "resolved",
      "decision": "Manter a revisão final antes da publicação."
    },
    {
      "theme": "Comunicação",
      "description": "Registrar decisões da reunião.",
      "status": "discussed",
      "action": {
        "description": "Criar um modelo de registro de decisões."
      }
    }
  ]
}
```

Com o exemplo salvo em `caminho/entrada.json`, execute no Linux/macOS:

```bash
PYTHONPATH=src python -m retrospective_script caminho/entrada.json caminho/roteiro.md
```

O roteiro resultante contém os temas `Comunicação` e `Entrega` na agenda, uma seção de discussão para cada tema e uma tabela de plano de ação. Na ação sem responsável e prazo, essas colunas são preenchidas com `Não informado`.

## Testes

Execute os testes com:

```bash
python -m pytest
```

Os testes usam dados em memória e arquivos locais temporários; não acessam a rede.

## Limitações

- A entrada aceita somente JSON local; não há importação de planilhas, texto livre ou ferramentas de reunião.
- Não há interface gráfica, servidor web, banco de dados, autenticação, notificações ou integrações externas.
- A ferramenta não gera automaticamente temas, responsáveis, prazos, decisões ou ações.
- Temas com textos diferentes são tratados como grupos diferentes, mesmo que sejam semanticamente equivalentes.
- Não há edição interativa nem atualização incremental de um roteiro já gerado.
- A saída não possui uma seção específica para observações.
- Itens sem ação não aparecem no plano de ação; quando não há ações em nenhum item, a tabela informa `Nenhuma ação registrada`.

## O que foi aprendido

O experimento demonstra como validar um contrato JSON com mensagens de erro voltadas ao uso em linha de comando, representar os dados validados com dataclasses imutáveis e gerar Markdown determinístico. Também evidencia a separação entre validação dos dados, coordenação da CLI e renderização do documento.

## Possível aplicação na FOX

Pode apoiar a preparação de retrospectivas internas ao transformar registros estruturados em uma agenda e plano de ação padronizados. Qualquer integração com ferramentas corporativas ou acompanhamento posterior das ações está fora do escopo implementado.

## Status

Concluído para o escopo implementado. O relatório de testes recebido informa: **14 testes coletados e 14 testes passaram**.
