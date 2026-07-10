"use client";

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, File as FileIcon, Loader2, AlertTriangle } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filterMode, setFilterMode] = useState<'all' | 'has_email' | 'has_phone'>('all');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setError(null);
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];

      const allowedTypes = [
        'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
      ];
      const allowedExt = ['.csv', '.xlsx', '.xls'];

      const name = selectedFile.name.toLowerCase();
      const hasValidType = allowedTypes.includes(selectedFile.type);
      const hasValidExt = allowedExt.some((ext) => name.endsWith(ext));

      if (hasValidType || hasValidExt) {
        setFile(selectedFile);
      } else {
        setError('Formato de arquivo inválido. Por favor, envie .csv, .xlsx ou .xls');
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
  });
  
  const handleUpload = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('filter', filterMode);

    try {
      const response = await fetch('http://localhost:8000/api/format-contacts', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ocorreu um erro no servidor.');
      }

      const blob = await response.blob();
      
      // Forçar download do arquivo
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'contacts_formatted.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      
      setFile(null); // Limpa o arquivo após o sucesso

    } catch (err: unknown) {
      setError((err as Error).message || 'Não foi possível conectar ao servidor. Verifique se a API está rodando.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-8">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800">Organizador de Contatos</h1>
          <p className="text-gray-600 mt-2">Limpe e formate seus arquivos .csv/.xlsx/.xls para importação no Google Contacts.</p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-md">
          {error && (
            <div className="mb-4 flex items-center justify-center bg-red-100 text-red-700 p-3 rounded-lg">
              <AlertTriangle className="h-5 w-5 mr-2" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {!file && (
            <div
              {...getRootProps()}
              className={`flex flex-col items-center justify-center p-10 border-2 border-dashed rounded-lg cursor-pointer transition-colors
                ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
            >
              <input {...getInputProps()} />
              <UploadCloud className="h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-700 font-semibold">Arraste e solte o arquivo .csv aqui</p>
              <p className="text-gray-500 text-sm">ou clique para selecionar</p>
            </div>
          )}
          
          {file && !isLoading && (
            <div className="text-center">
              <div className="flex items-center justify-center bg-gray-100 p-4 rounded-lg mb-4">
                <FileIcon className="h-6 w-6 text-gray-600" />
                <p className="ml-3 font-medium text-gray-800">{file.name}</p>
              </div>
              <div className="flex justify-center gap-4 mb-4">
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="radio"
                    name="filter"
                    value="all"
                    checked={filterMode === 'all'}
                    onChange={() => setFilterMode('all')}
                    className="accent-blue-600"
                  />
                  Todos
                </label>
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="radio"
                    name="filter"
                    value="has_phone"
                    checked={filterMode === 'has_phone'}
                    onChange={() => setFilterMode('has_phone')}
                    className="accent-blue-600"
                  />
                  Apenas com telefone
                </label>
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="radio"
                    name="filter"
                    value="has_email"
                    checked={filterMode === 'has_email'}
                    onChange={() => setFilterMode('has_email')}
                    className="accent-blue-600"
                  />
                  Apenas com e-mail
                </label>
              </div>
              <div className="flex justify-center gap-4">
                <button
                  onClick={() => { setFile(null); setError(null); }}
                  className="px-6 py-2 rounded-lg bg-gray-200 text-gray-800 font-semibold hover:bg-gray-300 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleUpload}
                  className="px-6 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-colors"
                >
                  Formatar Arquivo
                </button>
              </div>
            </div>
          )}

          {isLoading && (
            <div className="flex flex-col items-center justify-center text-center">
              <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
              <p className="mt-4 text-gray-600 font-medium">Processando seu arquivo...</p>
              <p className="text-gray-500 text-sm">Isso pode levar alguns segundos.</p>
            </div>
          )}
        </div>
        <footer className="text-center mt-8">
            <p className="text-sm text-gray-500">
                Desenvolvido por <Link href="https://micro-sass/" target="_blank" className="text-blue-600 hover:underline">
                    Cayo
                </Link>
            </p>
        </footer>
      </div>
    </main>
  );
}
