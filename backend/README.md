# SuperCRM Backend - Fase 1 (Infraestrutura)

Este backend fornece a base tecnica para o SuperCRM usando FastAPI + SQL Server.

## Requisitos
- Python 3.11+
- SQL Server local (SQLEXPRESS)
- ODBC Driver 17 for SQL Server
- Windows Authentication habilitada

## Stack
- FastAPI
- SQLAlchemy 2.x
- Alembic
- pyodbc

## Como executar
1) Criar ambiente virtual e instalar dependencias:

   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt

2) Subir a API (cria o banco `crm_db` se nao existir e roda migrations):

   uvicorn app.main:app --reload

3) Testar:

   GET http://127.0.0.1:8000/health
   Resposta esperada: {"status": "ok"}

## Banco de dados
- Servidor: localhost\SQLEXPRESS
- Banco: crm_db
- Autenticacao: Windows Authentication
- Driver: ODBC Driver 17 for SQL Server

A aplicacao cria o banco automaticamente se nao existir e aplica as migrations no startup.

## Estrutura
backend/
  app/
    main.py
    core/
      config.py
      database.py
    models/
      base.py
      proposal.py
      proposal_detail.py
      import_batch.py
    api/
      health.py
    migrations/
      env.py
      versions/
        0001_initial.py

## Observacoes
- Esta fase nao implementa regras de negocio.
- Nenhuma importacao, mapping ou leitura de Excel esta presente.
