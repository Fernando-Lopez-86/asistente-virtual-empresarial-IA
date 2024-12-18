# 1. Imagen base oficial de Python
FROM python:3.10.8

# 2. Configurar el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo requirements.txt con las dependencias
COPY requirements.txt .

# 4. Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Descargar el modelo de spaCy para español
RUN python -m spacy download es_core_news_sm

# 5. Copiar el resto de los archivos de la aplicación al contenedor
COPY . .

# 6. Exponer el puerto donde se ejecutará Streamlit
EXPOSE 8501

# 7. Ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]