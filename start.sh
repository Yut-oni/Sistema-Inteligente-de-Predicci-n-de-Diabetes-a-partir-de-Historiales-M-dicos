#!/bin/bash
# Entrar a la carpeta web y correr app.py
streamlit run web/app.py --server.port $PORT --server.headless true
