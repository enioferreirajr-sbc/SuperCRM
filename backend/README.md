# SuperCRM Backend

Backend desenvolvido em Python com FastAPI, MongoDB (Motor) e Beanie.

## Pré-requisitos

*   **Python 3.10+**
*   **MongoDB** (rodando na porta 27017 por padrão)

## Configuração do Ambiente

1.  Crie e ative um ambiente virtual:
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configure as variáveis de ambiente:
    *   Certifique-se de que o arquivo `.env` existe na raiz do backend (já criado com configurações padrão).
    *   Exemplo de `.env`:
        ```env
        MONGODB_URL=mongodb://localhost:27017
        DATABASE_NAME=crm_db
        ```

## Executando a Aplicação (Hot Reload)

Para iniciar o servidor com recarregamento automático (hot reload) habilitado (útil durante o desenvolvimento):

```bash
uvicorn main:app --reload
```

*   Acesse a API em: `http://localhost:8000`
*   Documentação interativa (Swagger): `http://localhost:8000/docs`

## Scripts Úteis

*   **Verificar Conexão com Banco de Dados:**
    ```bash
    python scripts/check_db_connection.py
    ```
