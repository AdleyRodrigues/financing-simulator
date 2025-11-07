# Servidor JSON Server

Backend local para persistência dos dados do Controle de Dívida.

## 🚀 Instalação

```bash
# Com pnpm (recomendado)
pnpm install

# Com npm
npm install

# Com yarn
yarn install
```

## ▶️ Executar

```bash
# Modo normal
pnpm start

# Modo desenvolvimento (com delay de 500ms para simular rede)
pnpm run dev

# Porta customizada
pnpm run start:custom-port
```

## 📡 Endpoints Disponíveis

Servidor roda em: `http://localhost:3000`

- `GET /registros` - Listar todos os registros
- `GET /registros/:id` - Buscar registro específico
- `POST /registros` - Criar novo registro
- `PATCH /registros/:id` - Atualizar registro
- `PUT /registros/:id` - Substituir registro
- `DELETE /registros/:id` - Deletar registro
- `GET /config` - Obter configuração

## 🗄️ Estrutura do db.json

```json
{
  "registros": [],
  "config": [
    {
      "id": 1,
      "divida_inicial": 50000,
      "taxa": 0.01
    }
  ]
}
```

## 🔧 Configuração da Aplicação Cliente

No arquivo `persistence.py`, a URL base está configurada para:

```python
BASE_URL = "http://localhost:3000"
```

Se você mudar a porta do servidor, atualize essa constante.

## 📝 Observações

- Os dados são salvos automaticamente em `db.json`
- O arquivo é watched - mudanças manuais são detectadas
- Interface web disponível em `http://localhost:3000`
- Suporta todas as operações REST padrão
