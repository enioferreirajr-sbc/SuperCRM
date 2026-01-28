# Importação de Propostas Comerciais

Este documento detalha o funcionamento do endpoint de importação de propostas via Excel, focado na integração com o Frontend.

## 📡 Endpoint

*   **URL:** `/proposals/import`
*   **Método:** `POST`
*   **Content-Type:** `multipart/form-data`

## 📤 Parâmetros de Envio

O endpoint espera o envio de um **arquivo** no corpo da requisição.

| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `file` | File (.xlsx, .xls) | Sim | O arquivo Excel contendo os dados. |

### Exemplo de Requisição (JavaScript / FormData)

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch("http://localhost:8000/proposals/import", {
  method: "POST",
  body: formData,
});
```

## 📥 Resposta (Response)

### Sucesso (200 OK)

Retorna um resumo do processamento.

```json
{
  "status": "success",
  "processed_count": 150,
  "errors": []
}
```

*   `processed_count`: Número de linhas importadas ou atualizadas com sucesso.
*   `errors`: Lista de strings com erros específicos (ex: falha de leitura em uma linha). Se vazio, tudo correu bem.

### Erro de Validação (400 Bad Request)

Ocorre se o arquivo não for enviado ou não for um Excel válido.

```json
{
  "detail": "Invalid file format. Please upload an Excel file."
}
```

### Erro no Servidor (500 Internal Server Error)

Ocorre se houver um erro crítico ao ler o arquivo (ex: arquivo corrompido ou aba "Grid 1" inexistente).

```json
{
  "detail": "Failed to read Excel file: ..."
}
```

## 🧠 Regras de Negócio Importantes

1.  **Aba Obrigatória:** O sistema lê **apenas** a aba chamada `Grid 1`. Se o Excel não tiver essa aba, dará erro.
2.  **Chave Única (Upsert):** A unicidade é definida por **ID da Proposta** + **Nome do Produto**.
    *   Se você subir uma linha com ID `100` e Produto `Consultoria`, e ela já existir no banco, os dados serão **atualizados**.
    *   Se não existir, será criada.
    *   Isso permite reimportar o mesmo arquivo múltiplas vezes para atualizar dados sem duplicar registros.
3.  **Campos Obrigatórios:** Linhas sem `Business Proposal ID` ou `Product Name` serão silenciosamente ignoradas (não sobem pro banco).
