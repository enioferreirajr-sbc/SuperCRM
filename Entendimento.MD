# Entendimento do Projeto SuperCRM

## Visão Geral
- Monorepo com `backend` (API FastAPI + MongoDB/Beanie) e `frontend` (React 19 + Vite + MUI, baseado no template Mantis).
- Objetivo principal: importar propostas comerciais a partir de planilhas Excel, persistir no MongoDB e disponibilizar listagem/edição e detalhamento para o front.
- Não há autenticação implementada no backend; CORS liberado para qualquer origem (uso dev). Front possui telas de login/register apenas como template.

## Backend (FastAPI)
### Stack & Entrada
- Python 3.10+, dependências em `backend/requirements.txt` (FastAPI, Uvicorn, Motor, Beanie, Pandas, OpenPyXL, pydantic-settings, etc.).
- `backend/main.py`: cria `FastAPI` com middleware CORS (origens abertas), registra router de propostas com prefixo `/api/v1`, e define ciclo de vida que inicializa o Mongo e semeia mappings de importação.
- Startup assíncrona chama `init_db()` e `seed_import_mappings()`.

### Configuração e Banco
- `app/core/config.py`: `Settings` via `pydantic-settings`; variáveis de ambiente (arquivo `.env` opcional). Defaults: `MONGODB_URL="mongodb://localhost:27017"`, `DATABASE_NAME="crm_db"`.
- `app/core/database.py`: cria `AsyncIOMotorClient` e inicializa Beanie com documentos `ImportMapping` e `Proposal`.

### Modelos & Tipos
- `app/core/types.py`: `SafeDecimal` (Annotated + validador `sanitize_decimal`) limpa strings/currency, normaliza para `Decimal` com 2 casas.
- `app/core/constants.py`: funções `parse_currency`/`parse_date` para import; dicionário `PROPOSAL_IMPORT_SCHEMA` descreve colunas esperadas de Excel.
- `app/features/importer/models.py` (`ImportMapping`): documento Beanie (`name` único, `target_model`, `column_map`, `created_at`). Coleção `import_mappings`.
- `app/features/proposals/models.py`:
  - `ProposalItem`: campos opcionais (product_name, proposal_type_name, team_name, owner) e valores numéricos com `SafeDecimal` (license_of_use, training, monthly_fee, professional_services, monthly_fee_annualized, total_sales).
  - `Proposal` (coleção `proposals`): `external_id` (string única), `customer_name`, `value`, `closing_date`, `probability` (int), `is_dirty` (bool), `updated_at`, `items` (lista de `ProposalItem`), `proposal_name` (alias `business_proposal_name`). Indexes em `external_id` e `customer_name`.

### Schemas (DTOs)
- `ProposalBaseDTO` declarado mas vazio (apenas campos comentados — precisa revisão).
- `ProposalUpdateDTO`: todos os campos opcionais (`proposal_name`, `client_name`, `funnel_stage`, `total_value`, `probability`, `closing_date`).
- `ProposalReadDTO`: acrescenta `proposal_id`, `is_dirty`, `created_at`, `updated_at`, além de `probability` e `closing_date`.
- Import helpers: `ImportSummary`, `ImportErrorDetail`, `ImportResponse`, `ProposalImportRow`.

### Repositório
- `ProposalRepository.fetch_all_paginated(query, sort_field, sort_order, skip, limit)`: usa `Proposal.find` com paginação e ordenação; retorna itens + total.
- `get_metadata_aggregates`: distinct em `customer_name` e `items.product_name` para filtros.
- `upsert_proposal`: upsert por `external_id`; respeita flag `is_dirty` (atualmente só ignora). Usa `datetime.now()` (módulo não importado — bug).
- `find_by_id`: busca por `external_id`.

### Serviços de Propostas (`app/features/proposals/service.py`)
- `import_proposals_from_excel(file)`: 
  - Carrega mapping default `padrao_sistema_erp` (coleção `import_mappings`); se não existir, retorna `failed`.
  - Lê Excel via Pandas (dtype=object), itera linhas, mapeia colunas conforme `column_map`, exige `business_proposal_id` e monta `proposals_map` (usa `Proposal` e `ProposalItem`).
  - Cria arquivo de log JSONL em `backend/logs/import_proposals_<timestamp>.jsonl` com eventos START/COMPLETE/erros.
  - Calcula `total_sales` somando itens; atribui `proposal.total_value_aggregated` (campo não existe no modelo — risco). Upsert manual por `Proposal.business_proposal_id` (campo também não existe, deverá ser `external_id`).
  - Retorna `ImportResponse` com `status` (`success` ou `completed_with_warnings`/`failed`), `summary` (contagem de linhas, propostas upserted, itens, clientes, erros) e lista de erros por linha.
- `get_all_proposals(...)`: monta filtro por `external_id`, `customer_name`, faixa de `value` e `search` (regex), define mapeamento de ordenação, chama repositório e converte para `ProposalReadDTO` (usa `closing_date` como `created_at` fallback).
- `get_proposal_items(proposal_id)`: busca `Proposal` por `external_id` (string), devolve itens como `ProposalItemDTO` (usa `total_sales` como `value`).
- `update_proposal_by_external_id(external_id, data)`: atualiza campos permitidos, marca `is_dirty=True`, seta `updated_at`, salva e retorna DTO. 
- `get_proposals_metadata()`: delega ao repositório.

### Serviço Importer (`app/features/importer/service.py`)
- Contém código duplicado/desatualizado: funções `get_all_proposals`, `get_proposal_items`, `update_proposal_by_external_id`, `get_proposals_metadata` referenciam `ProposalRepository` sem importar; inclui bloco de importação Excel comentado/obsoleto após um `return` (provável resquício).
- `seed_import_mappings()`: lido em `main.py`; carrega fixture JSON (`fixtures/import_definitions.json`) e cria/atualiza mapping `padrao_sistema_erp` com colunas → campos (`Business Proposal ID`→`external_id`, `Customer Reference`→`customer_name`, `Funnel Percentage`→`probability`, `Business Proposal Date`→`closing_date`, `R$ Total Sales`→`value`).

### Rotas / Endpoints
- `app/features/proposals/controller.py` com prefixo `/proposals` (montado em `/api/v1`):
  - `POST /proposals/import` → `import_proposals_from_excel` (Upload de arquivo Excel multipart).
  - `GET /proposals/` → listagem paginada com filtros `skip`, `limit`, `external_id`, `customer_name`, `amount_min/max`, `search`, `sort_by`, `sort_order`.
  - `GET /proposals/{external_id}/items` → itens vinculados.
  - `PATCH /proposals/{external_id}` → atualização manual; converte `client_name`→`customer_name` e `total_value`→`value`; marca sujo.
  - `GET /proposals/metadata` → metadados de clientes/produtos.

### Scripts e Logs
- `backend/scripts/seed_mappings.py`, `debug_repo.py` (utilitários de debug/seed).
- Pastas `backend/logs/` recebem JSONL de importações.
- Documento auxiliar `_docs/ImportProposal.md` descreve versão antiga do fluxo (aba "Grid 1", chave única por ID+Produto).

### Pontos de Atenção / Riscos
- Divergência de campos: serviço de import usa `business_proposal_id` e `total_value_aggregated`, ausentes no modelo atual (`external_id`, `value`). Pode gerar `AttributeError` e não persistir corretamente.
- `ProposalRepository.upsert_proposal` não importa `datetime` e ignora `is_dirty` sem aviso.
- Código duplicado/obsoleto em `app/features/importer/service.py`; blocos após `return` nunca executam.
- Schema `ProposalBaseDTO` contém `pass`; falta validação/documentação consistente.
- Sem autenticação ou controle de origem; CORS totalmente liberado.
- Ausência de testes automatizados.

## Frontend (React + Vite + MUI)
### Stack & Build
- React 19 + React Router 7 + SWR + Material UI 7 + Material React Table 3. Build com Vite (`yarn start`, `yarn build`, `yarn preview`). API base configurada em `src/config/api.js` (env `VITE_API_URL`, fallback `http://localhost:8000/api/v1`).
- Template Mantis (CodedThemes) com temas customizados em `src/themes` (paleta, tipografia, sombras, overrides de componentes) e contexto `ConfigContext` persistido em `localStorage`.

### Rotas e Layout
- `src/routes/index.jsx`: `createBrowserRouter` com `MainRoutes` (dashboard) e `LoginRoutes` (login/register templates). `basename` opcional via `VITE_APP_BASE_NAME`.
- `DashboardLayout` (sidebar/header) embrulha páginas principais; rota `/proposals` leva à tela de propostas. Padrão inicial `APP_DEFAULT_PATH = /dashboard/default`.

### Fluxo de Propostas
- `pages/proposals/index.jsx`: card "Propostas Comerciais" com botão de importação e tabela.
- `components/ImportProposalBtn.jsx`:
  - Input oculto aceita `.xlsx` (<=10 MB); valida extensão e tamanho.
  - Usa hook `useImportProposals` para `POST /proposals/import` (multipart). Feedback via Snackbar; abre `ImportResultModal` ao receber resposta.
- `hooks/useImportProposals.js`: executa fetch, interpreta `ImportResponse`; considera falha quando `errors_count>0` e `proposals_upserted===0`; expõe `isLoading`, `error`, `success`.
- `pages/proposals/ImportResultModal.jsx`:
  - Mostra KPIs do resumo (linhas lidas, propostas, itens, clientes, erros) com cores/status.
  - Lista erros em tabela e permite exportar CSV (`import_errors_log.csv`).
- `pages/proposals/ProposalsTable.jsx`:
  - Paginação/ordenação/filtragem manuais com `MaterialReactTable` (localização pt-BR).
  - Busca dados via SWR em `GET /proposals?skip&limit&sort_by&sort_order&search`.
  - Colunas: `proposal_id`, `client_name` (com ícone se `is_dirty`), `closing_date` (formatado pt-BR), `total_value` (formato monetário), `probability`.
  - Ação de linha "Detalhes" abre `ProposalDetailsModal`.
- `ProposalDetailsModal` (dentro do mesmo arquivo):
  - Faz SWR para `GET /proposals/{id}/items` enquanto o modal está aberto.
  - Exibe cabeçalho (cliente, probabilidade, data de fechamento, valor, flag editado) e tabela de itens (produto, tipo, time, valor).

### Outros Componentes/Páginas
- Telas de login/registro (`pages/auth/*`) e dashboard de exemplo (`pages/dashboard/default`) vêm do template; não integram backend.
- Estilos adicionais em `src/assets` (apex charts, react-table) e overrides extensos em `src/themes/overrides`.

### Pontos de Atenção
- `muitablePaperProps` em `ProposalsTable` parece erro de digitação (deveria ser `muiTablePaperProps`) — override de estilo não aplicado.
- SWR `fetcher` não trata HTTP 4xx/5xx como erro (faz `res.json` direto); erros de status podem aparecer como sucesso com payload de erro do backend.
- Nenhum controle de sessão/auth; telas de login são apenas UI.
- Dependência forte da API em `/api/v1`; manter `VITE_API_URL` alinhado ao backend.

## Fluxo Ponta a Ponta (Importar → Listar → Detalhar)
1) Usuário clica "Importar Propostas" (`ImportProposalBtn`), seleciona `.xlsx` válido.
2) Hook `useImportProposals` envia `POST /api/v1/proposals/import` (multipart). Backend lê mapping `import_mappings`, processa linhas, grava log JSONL e devolve `ImportResponse` com contagens/erros.
3) Modal `ImportResultModal` mostra KPIs e erros; opção de exportar CSV.
4) Listagem em `ProposalsTable` consulta `GET /api/v1/proposals` com paginação/ordenção/ busca; mostra flag `is_dirty`.
5) Ao clicar em "Detalhes", modal consulta `GET /api/v1/proposals/{external_id}/items` e exibe itens e valores.
6) Atualizações manuais possíveis via `PATCH /api/v1/proposals/{external_id}` (não há UI pronta; endpoint aceita probability/closing_date/value/customer_name com marcação `is_dirty`).

## Como Executar (informações existentes)
- Backend: criar venv, `pip install -r backend/requirements.txt`, rodar MongoDB local em `27017` ou ajustar `.env`, iniciar com `uvicorn main:app --reload` dentro de `backend/`.
- Frontend: em `frontend/`, `yarn install` ou `npm install`; definir `VITE_API_URL` se backend não estiver em `http://localhost:8000`; rodar `yarn start` (Vite dev server) ou `yarn build`.

## Lacunas e Próximos Passos sugeridos
- Alinhar modelos x importação: alterar serviço para usar `external_id` e campo `value` existentes; remover `total_value_aggregated` ou adicioná-lo ao modelo.
- Limpar código duplicado/obsoleto em `app/features/importer/service.py` e `ProposalBaseDTO`; corrigir imports ausentes (`datetime`).
- Tratar status HTTP no frontend (`fetcher`) e corrigir `muiTablePaperProps` para aplicar estilos.
- Considerar autenticação/autorização e CORS restrito para produção.
- Adicionar testes (unitários e integração) para importação, listagem e PATCH.
