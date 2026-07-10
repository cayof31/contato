This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

---

# Micro-SaaS Organizador de Contatos

Este projeto consiste em um frontend Next.js e um backend Python (FastAPI) para limpar e formatar arquivos CSV de contatos.

## Como Rodar Localmente

Você precisará de dois terminais abertos para rodar o backend e o frontend simultaneamente.

### 1. Backend (FastAPI + Python)

O servidor do backend rodará em `http://localhost:8000`.

**Passo 1: Navegue até o diretório do backend**
```bash
cd backend
```

**Passo 2: Crie e ative um ambiente virtual**
Recomendado para isolar as dependências do projeto.

*No macOS/Linux:*
```bash
python3 -m venv venv
source venv/bin/activate
```

*No Windows:*
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Passo 3: Instale as dependências**
```bash
pip install -r requirements.txt
```

**Passo 4: Inicie o servidor**
```bash
uvicorn main:app --reload
```
Você verá uma mensagem indicando que o servidor está rodando em `http://localhost:8000`. Deixe este terminal aberto.

### 2. Frontend (Next.js)

Em um **novo terminal**, navegue até a raiz do projeto.

**Passo 1: Instale as dependências (se ainda não o fez)**
```bash
npm install
```

**Passo 2: Inicie o servidor de desenvolvimento**
```bash
npm run dev
```
O frontend estará disponível em `http://localhost:3000`. Abra este endereço no seu navegador para usar a aplicação.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
# contato
