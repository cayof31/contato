import re
import io
import os
from dotenv import load_dotenv
import pandas as pd
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="Contato Micro-SaaS API",
    description="API para limpar e formatar arquivos CSV de contatos.",
    version="1.0.0"
)
load_dotenv()
origins = os.getenv("ALLOWED_ORIGINS").split(",")
# Configura o CORS para permitir requisições do frontend (Next.js)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_and_format_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e formata o DataFrame de contatos para o padrão do Google Contacts.
    Auto-detecta colunas de origem e mapeia para o template correto.
    """
    # Template completo do Google Contacts
    google_template_columns = [
        'Name Prefix', 'First Name', 'Middle Name', 'Last Name', 'Name Suffix',
        'Phonetic First Name', 'Phonetic Middle Name', 'Phonetic Last Name',
        'Nickname', 'File As', 
        'E-mail 1 - Label', 'E-mail 1 - Value', 'E-mail 2 - Label', 'E-mail 2 - Value',
        'Phone 1 - Label', 'Phone 1 - Value', 'Phone 2 - Label', 'Phone 2 - Value',
        'Address 1 - Label', 'Address 1 - Country', 'Address 1 - Street',
        'Address 1 - Extended Address', 'Address 1 - City', 'Address 1 - Region',
        'Address 1 - Postal Code', 'Address 1 - PO Box',
        'Organization Name', 'Organization Title', 'Organization Department',
        'Birthday', 'Event 1 - Label', 'Event 1 - Value',
        'Relation 1 - Label', 'Relation 1 - Value',
        'Website 1 - Label', 'Website 1 - Value',
        'Custom Field 1 - Label', 'Custom Field 1 - Value',
        'Notes', 'Labels'
    ]

    def find_column(df, patterns):
        """Encontra uma coluna no DataFrame que corresponda a qualquer um dos padrões."""
        df_cols_lower = {col.lower(): col for col in df.columns}
        for pattern in patterns:
            if pattern.lower() in df_cols_lower:
                return df_cols_lower[pattern.lower()]
        return None

    # Auto-detecção de colunas de entrada
    col_first_name = find_column(df, ['first name', 'primeiro nome', 'nome', 'first'])
    col_last_name = find_column(df, ['last name', 'último nome', 'sobrenome', 'last'])
    col_phone1 = find_column(df, ['phone 1 - value', 'telefone 1', 'telefone', 'phone', 'celular', 'phone 1'])
    col_phone2 = find_column(df, ['phone 2 - value', 'telefone 2', 'phone 2'])
    col_email1 = find_column(df, ['e-mail 1 - value', 'email 1', 'email', 'e-mail', 'mail'])
    col_email2 = find_column(df, ['e-mail 2 - value', 'email 2', 'e-mail 2', 'mail 2'])
    col_organization = find_column(df, ['organization name', 'empresa', 'organization', 'companhia'])
    col_notes = find_column(df, ['notes', 'observações', 'obs', 'comments'])

    google_contacts_df = pd.DataFrame()
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Processa e formata cada campo
    if col_first_name:
        cleaned = df[col_first_name].astype(str).str.replace(r'[^\w\sÀ-ÖØ-öø-ÿ]', '', regex=True).str.strip()
        google_contacts_df['First Name'] = cleaned.str.title()
    else:
        google_contacts_df['First Name'] = ""

    if col_last_name:
        cleaned = df[col_last_name].astype(str).str.replace(r'[^\w\sÀ-ÖØ-öø-ÿ]', '', regex=True).str.strip()
        google_contacts_df['Last Name'] = cleaned.str.title()
        print(f"Last Name column found: {google_contacts_df['Last Name']}")
    else:
        google_contacts_df['Last Name'] = ""

    if col_phone1:
        google_contacts_df['Phone 1 - Value'] = df[col_phone1].astype(str).str.replace(r'[^\d\-\+\s\(\)]', '', regex=True).str.strip()
        google_contacts_df['Phone 1 - Type'] = 'Mobile'
    else:
        google_contacts_df['Phone 1 - Value'] = ""
        google_contacts_df['Phone 1 - Type'] = ""

    if col_phone2:
        google_contacts_df['Phone 2 - Value'] = df[col_phone2].astype(str).str.replace(r'[^\d\-\+\s\(\)]', '', regex=True).str.strip()
        google_contacts_df['Phone 2 - Type'] = 'Work'
    else:
        google_contacts_df['Phone 2 - Value'] = ""
        google_contacts_df['Phone 2 - Type'] = ""

    if col_email1:
        google_contacts_df['E-mail 1 - Value'] = df[col_email1].astype(str).str.strip()
        google_contacts_df['E-mail 1 - Type'] = 'Work'
    else:
        google_contacts_df['E-mail 1 - Value'] = ""
        google_contacts_df['E-mail 1 - Type'] = ""

    if col_email2:
        google_contacts_df['E-mail 2 - Value'] = df[col_email2].astype(str).str.strip()
        google_contacts_df['E-mail 2 - Type'] = 'Personal'
    else:
        google_contacts_df['E-mail 2 - Value'] = ""
        google_contacts_df['E-mail 2 - Type'] = ""

    if col_organization:
        google_contacts_df['Organization Name'] = df[col_organization].astype(str).str.title()
    else:
        google_contacts_df['Organization Name'] = ""

    if col_notes:
        google_contacts_df['Notes'] = df[col_notes].astype(str).str.strip()
    else:
        google_contacts_df['Notes'] = ""

    # Garante que todas as colunas esperadas existam (preenchidas com vazio quando não há dados)
    for col in google_template_columns:
        if col not in google_contacts_df.columns:
            google_contacts_df[col] = ""
    google_contacts_df['Last Name'] += " [" + data + "]"
    return google_contacts_df[google_template_columns]


async def format_contacts_file(file: UploadFile = File(...), filter: str = 'all'):
    """
    Recebe um arquivo CSV, limpa os dados e retorna um novo CSV formatado.
    """
    # Aceita CSV e formatos Excel (.xlsx, .xls)
    filename = file.filename.lower()
    if not (filename.endswith('.csv') or filename.endswith('.xlsx') or filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Por favor, envie .csv, .xlsx ou .xls")

    try:
        # Lê CSV ou Excel usando pandas
        if filename.endswith('.csv') or file.content_type == 'text/csv':
            file.file.seek(0)
            df = pd.read_csv(file.file)
        elif filename.endswith('.xlsx') or file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            file.file.seek(0)
            df = pd.read_excel(file.file, engine='openpyxl')
        elif filename.endswith('.xls') or file.content_type == 'application/vnd.ms-excel':
            file.file.seek(0)
            df = pd.read_excel(file.file, engine='xlrd')
        else:
            raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")

        # Limpa e formata os dados
        cleaned_df = clean_and_format_data(df)

        # Aplica filtro solicitado: 'all' | 'has_email' | 'has_phone'
        if filter == 'has_email':
            cleaned_df = cleaned_df[cleaned_df['E-mail 1 - Value'].astype(str).str.strip() != ""]
        elif filter == 'has_phone':
            cleaned_df = cleaned_df[cleaned_df['Phone 1 - Value'].astype(str).str.strip() != ""]
        # reset index to keep CSV tidy
        cleaned_df = cleaned_df.reset_index(drop=True)

        # Converte o DataFrame limpo para um arquivo CSV em memória
        stream = io.StringIO()
        cleaned_df.to_csv(stream, index=False)
        
        response = StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = "attachment; filename=contacts_formatted.csv"
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar o arquivo: {str(e)}")

def read_root():
    return {"status": "API is running"}


# Rotas
@app.post('/api/format-contacts')
async def post_format_contacts(file: UploadFile = File(...), filter: str = Form('all')):
    return await format_contacts_file(file, filter=filter)


@app.get('/')
def get_root():
    return read_root()


if __name__ == "__main__":
    # uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)